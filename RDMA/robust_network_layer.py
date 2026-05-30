#!/usr/bin/env python3
"""
Robust Network Layer: Advanced error handling and packet reordering
Handles network failures, packet loss, and out-of-order delivery
"""

import socket
import threading
import time
import queue
import heapq
from collections import defaultdict, deque
from typing import Dict, List, Optional, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
import random

class NetworkError(Enum):
    TIMEOUT = "timeout"
    PACKET_LOSS = "packet_loss"
    CONNECTION_FAILED = "connection_failed"
    CHECKSUM_ERROR = "checksum_error"
    BUFFER_OVERFLOW = "buffer_overflow"
    UNKNOWN_ERROR = "unknown_error"

@dataclass
class NetworkMetrics:
    """Network performance metrics"""
    packets_sent: int = 0
    packets_received: int = 0
    packets_lost: int = 0
    packets_reordered: int = 0
    retransmissions: int = 0
    avg_latency: float = 0.0
    jitter: float = 0.0
    throughput: float = 0.0
    error_rate: float = 0.0

@dataclass
class PacketBuffer:
    """Ordered packet buffer with reordering support"""
    buffer: Dict[int, bytes] = field(default_factory=dict)
    expected_seq: int = 0
    max_gap: int = 100  # Maximum sequence gap before giving up
    buffer_size: int = 1000
    
    def add_packet(self, seq: int, data: bytes) -> Optional[bytes]:
        """Add packet and return ordered data if available"""
        if len(self.buffer) >= self.buffer_size:
            # Buffer overflow, drop oldest packets
            oldest_seq = min(self.buffer.keys())
            del self.buffer[oldest_seq]
        
        self.buffer[seq] = data
        
        # Check if we can deliver ordered packets
        ordered_data = b""
        while self.expected_seq in self.buffer:
            ordered_data += self.buffer[self.expected_seq]
            del self.buffer[self.expected_seq]
            self.expected_seq += 1
        
        return ordered_data if ordered_data else None
    
    def cleanup_old_packets(self, current_seq: int):
        """Remove packets that are too old"""
        cutoff = current_seq - self.max_gap
        old_packets = [seq for seq in self.buffer if seq < cutoff]
        for seq in old_packets:
            del self.buffer[seq]
        return len(old_packets)

class RobustNetworkLayer:
    """Advanced network layer with error handling and reordering"""
    
    def __init__(self, 
                 max_retries: int = 5,
                 timeout: float = 1.0,
                 buffer_size: int = 1000,
                 enable_adaptive_timeout: bool = True):
        
        self.max_retries = max_retries
        self.base_timeout = timeout
        self.current_timeout = timeout
        self.buffer_size = buffer_size
        self.enable_adaptive_timeout = enable_adaptive_timeout
        
        # Packet management
        self.sequence_counter = 0
        self.pending_packets = {}  # seq -> (timestamp, attempts, data)
        self.packet_buffer = PacketBuffer(buffer_size=buffer_size)
        
        # Metrics and monitoring
        self.metrics = NetworkMetrics()
        self.latency_samples = deque(maxlen=100)  # Keep last 100 samples
        self.last_activity = time.time()
        
        # Error handling
        self.error_handlers = defaultdict(list)
        self.fallback_strategies = []
        
        # Threading
        self.lock = threading.RLock()
        self.retransmission_thread = None
        self.metrics_thread = None
        self.running = False
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def register_error_handler(self, error_type: NetworkError, handler: Callable):
        """Register a handler for specific error types"""
        self.error_handlers[error_type].append(handler)
    
    def register_fallback_strategy(self, strategy: Callable):
        """Register a fallback strategy for network failures"""
        self.fallback_strategies.append(strategy)
    
    def send_with_reliability(self, 
                            send_func: Callable,
                            data: bytes,
                            addr: Tuple[str, int],
                            timeout: Optional[float] = None) -> bool:
        """Send data with automatic retries and error handling"""
        if timeout is None:
            timeout = self.current_timeout
        
        seq = self.sequence_counter
        self.sequence_counter += 1
        
        start_time = time.time()
        attempts = 0
        
        while attempts < self.max_retries:
            try:
                # Send packet
                send_func(data, addr)
                self.metrics.packets_sent += 1
                
                # Track for retransmission
                with self.lock:
                    self.pending_packets[seq] = (start_time, attempts, data)
                
                # Wait for ACK or timeout
                if self._wait_for_ack(seq, timeout):
                    # Success
                    latency = time.time() - start_time
                    self._update_latency(latency)
                    return True
                
                # Timeout, retry
                attempts += 1
                self.metrics.retransmissions += 1
                self.logger.warning(f"Packet {seq} timeout, retry {attempts}/{self.max_retries}")
                
                # Adaptive timeout
                if self.enable_adaptive_timeout:
                    self._adjust_timeout()
                
            except Exception as e:
                attempts += 1
                self.logger.error(f"Send error for packet {seq}: {e}")
                
                # Try error handlers
                if not self._handle_error(NetworkError.UNKNOWN_ERROR, e, seq):
                    break
        
        # All retries failed
        self.metrics.packets_lost += 1
        self.logger.error(f"Packet {seq} failed after {attempts} attempts")
        
        # Try fallback strategies
        return self._try_fallback_strategies(data, addr)
    
    def receive_with_reordering(self, 
                               receive_func: Callable,
                               timeout: Optional[float] = None) -> Tuple[Optional[bytes], Optional[Tuple[str, int]]]:
        """Receive packets with automatic reordering"""
        if timeout is None:
            timeout = self.current_timeout
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                data, addr = receive_func(timeout=0.1)  # Short timeout for responsiveness
                
                if data:
                    # Parse sequence number (assuming first 4 bytes are sequence)
                    if len(data) >= 4:
                        seq = int.from_bytes(data[:4], byteorder='big')
                        packet_data = data[4:]
                        
                        # Add to buffer
                        ordered_data = self.packet_buffer.add_packet(seq, packet_data)
                        
                        if ordered_data:
                            self.metrics.packets_received += 1
                            return ordered_data, addr
                        else:
                            # Packet received but out of order
                            self.metrics.packets_reordered += 1
                            continue
                
            except socket.timeout:
                continue
            except Exception as e:
                self.logger.error(f"Receive error: {e}")
                self._handle_error(NetworkError.UNKNOWN_ERROR, e)
                break
        
        return None, None
    
    def _wait_for_ack(self, seq: int, timeout: float) -> bool:
        """Wait for ACK for a specific sequence number"""
        deadline = time.time() + timeout
        
        while time.time() < deadline:
            with self.lock:
                if seq not in self.pending_packets:
                    return True  # ACK received
            time.sleep(0.01)  # 10ms granularity
        
        return False
    
    def _update_latency(self, latency: float):
        """Update latency measurements and adjust timeout"""
        self.latency_samples.append(latency)
        
        if len(self.latency_samples) >= 10:
            avg_latency = sum(self.latency_samples) / len(self.latency_samples)
            self.metrics.avg_latency = avg_latency
            
            # Calculate jitter
            variance = sum((x - avg_latency) ** 2 for x in self.latency_samples) / len(self.latency_samples)
            self.metrics.jitter = variance ** 0.5
            
            # Adaptive timeout: 3x average latency + jitter
            if self.enable_adaptive_timeout:
                self.current_timeout = min(max(avg_latency * 3 + self.metrics.jitter, 0.1), 5.0)
    
    def _adjust_timeout(self):
        """Adjust timeout based on network conditions"""
        if len(self.latency_samples) >= 5:
            avg_latency = sum(self.latency_samples) / len(self.latency_samples)
            
            # Increase timeout if high loss rate
            loss_rate = self.metrics.packets_lost / max(self.metrics.packets_sent, 1)
            if loss_rate > 0.1:  # >10% loss
                self.current_timeout = min(self.current_timeout * 1.5, 5.0)
            else:
                # Gradually decrease timeout
                self.current_timeout = max(self.current_timeout * 0.95, self.base_timeout)
    
    def _handle_error(self, error_type: NetworkError, error: Exception, seq: Optional[int] = None):
        """Handle network errors with registered handlers"""
        handled = False
        
        for handler in self.error_handlers[error_type]:
            try:
                if handler(error, seq):
                    handled = True
                    break
            except Exception as e:
                self.logger.error(f"Error handler failed: {e}")
        
        return handled
    
    def _try_fallback_strategies(self, data: bytes, addr: Tuple[str, int]) -> bool:
        """Try fallback strategies when primary method fails"""
        for strategy in self.fallback_strategies:
            try:
                if strategy(data, addr):
                    return True
            except Exception as e:
                self.logger.error(f"Fallback strategy failed: {e}")
        
        return False
    
    def acknowledge_packet(self, seq: int):
        """Mark packet as acknowledged"""
        with self.lock:
            if seq in self.pending_packets:
                del self.pending_packets[seq]
    
    def start_background_tasks(self):
        """Start background threads for retransmission and metrics"""
        self.running = True
        
        # Retransmission thread
        self.retransmission_thread = threading.Thread(target=self._retransmission_worker)
        self.retransmission_thread.daemon = True
        self.retransmission_thread.start()
        
        # Metrics thread
        self.metrics_thread = threading.Thread(target=self._metrics_worker)
        self.metrics_thread.daemon = True
        self.metrics_thread.start()
    
    def _retransmission_worker(self):
        """Background worker for handling retransmissions"""
        while self.running:
            current_time = time.time()
            expired_packets = []
            
            with self.lock:
                for seq, (timestamp, attempts, data) in self.pending_packets.items():
                    if current_time - timestamp > self.current_timeout:
                        if attempts < self.max_retries:
                            # Retransmit
                            self.metrics.retransmissions += 1
                            # Note: In real implementation, you'd call send_func here
                            self.pending_packets[seq] = (current_time, attempts + 1, data)
                            self.logger.debug(f"Retransmitting packet {seq}")
                        else:
                            # Give up
                            expired_packets.append(seq)
                            self.metrics.packets_lost += 1
            
            # Remove expired packets
            with self.lock:
                for seq in expired_packets:
                    if seq in self.pending_packets:
                        del self.pending_packets[seq]
            
            time.sleep(0.1)  # Check every 100ms
    
    def _metrics_worker(self):
        """Background worker for updating metrics"""
        while self.running:
            # Update error rate
            total_packets = max(self.metrics.packets_sent, 1)
            self.metrics.error_rate = self.metrics.packets_lost / total_packets
            
            # Update throughput (packets per second)
            if self.last_activity > 0:
                time_diff = time.time() - self.last_activity
                if time_diff > 0:
                    self.metrics.throughput = self.metrics.packets_received / time_diff
            
            self.last_activity = time.time()
            time.sleep(1.0)  # Update every second
    
    def get_metrics(self) -> NetworkMetrics:
        """Get current network metrics"""
        with self.lock:
            return NetworkMetrics(
                packets_sent=self.metrics.packets_sent,
                packets_received=self.metrics.packets_received,
                packets_lost=self.metrics.packets_lost,
                packets_reordered=self.metrics.packets_reordered,
                retransmissions=self.metrics.retransmissions,
                avg_latency=self.metrics.avg_latency,
                jitter=self.metrics.jitter,
                throughput=self.metrics.throughput,
                error_rate=self.metrics.error_rate
            )
    
    def reset_metrics(self):
        """Reset all metrics"""
        with self.lock:
            self.metrics = NetworkMetrics()
            self.latency_samples.clear()
            self.packet_buffer = PacketBuffer(buffer_size=self.buffer_size)
    
    def stop(self):
        """Stop background threads"""
        self.running = False
        
        if self.retransmission_thread:
            self.retransmission_thread.join(timeout=1.0)
        
        if self.metrics_thread:
            self.metrics_thread.join(timeout=1.0)


# Example error handlers and fallback strategies
def default_timeout_handler(error: Exception, seq: Optional[int]) -> bool:
    """Default handler for timeout errors"""
    logging.getLogger(__name__).warning(f"Timeout for packet {seq}: {error}")
    return False  # Don't handle, allow retry

def fallback_to_tcp(data: bytes, addr: Tuple[str, int]) -> bool:
    """Fallback strategy: switch to TCP if UDP fails"""
    try:
        # Create TCP socket and send data
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_socket.settimeout(5.0)
        tcp_socket.connect(addr)
        tcp_socket.send(data)
        tcp_socket.close()
        logging.getLogger(__name__).info("Fallback to TCP successful")
        return True
    except Exception as e:
        logging.getLogger(__name__).error(f"TCP fallback failed: {e}")
        return False

def simulate_network_conditions(layer: RobustNetworkLayer, 
                               loss_rate: float = 0.1,
                               latency_ms: float = 50,
                               jitter_ms: float = 10):
    """Simulate poor network conditions for testing"""
    def simulated_send(data: bytes, addr: Tuple[str, int]):
        # Simulate packet loss
        if random.random() < loss_rate:
            raise socket.timeout("Simulated packet loss")
        
        # Simulate latency and jitter
        delay = latency_ms / 1000 + random.uniform(-jitter_ms/1000, jitter_ms/1000)
        time.sleep(max(delay, 0))
        
        # Actual send (placeholder)
        pass
    
    return simulated_send


def demo_robust_layer():
    """Demonstration of robust network layer"""
    print("Robust Network Layer Demo")
    print("=" * 40)
    
    # Create robust layer
    layer = RobustNetworkLayer(
        max_retries=5,
        timeout=1.0,
        enable_adaptive_timeout=True
    )
    
    # Register error handlers
    layer.register_error_handler(NetworkError.TIMEOUT, default_timeout_handler)
    
    # Register fallback strategy
    layer.register_fallback_strategy(fallback_to_tcp)
    
    # Start background tasks
    layer.start_background_tasks()
    
    # Simulate network conditions
    simulated_send = simulate_network_conditions(layer, loss_rate=0.2, latency_ms=100)
    
    print("Testing robust network layer with simulated conditions...")
    print("Loss rate: 20%, Latency: 100ms ±10ms")
    
    # Test sending packets
    success_count = 0
    total_packets = 100
    
    for i in range(total_packets):
        data = f"Test packet {i}".encode()
        addr = ("localhost", 9999)
        
        if layer.send_with_reliability(simulated_send, data, addr):
            success_count += 1
        
        if (i + 1) % 20 == 0:
            metrics = layer.get_metrics()
            print(f"Progress: {i+1}/{total_packets}")
            print(f"  Success rate: {success_count/(i+1)*100:.1f}%")
            print(f"  Avg latency: {metrics.avg_latency*1000:.1f}ms")
            print(f"  Error rate: {metrics.error_rate*100:.1f}%")
    
    # Final metrics
    final_metrics = layer.get_metrics()
    print(f"\nFinal Results:")
    print(f"  Packets sent: {final_metrics.packets_sent}")
    print(f"  Packets received: {final_metrics.packets_received}")
    print(f"  Packets lost: {final_metrics.packets_lost}")
    print(f"  Retransmissions: {final_metrics.retransmissions}")
    print(f"  Success rate: {success_count/total_packets*100:.1f}%")
    print(f"  Average latency: {final_metrics.avg_latency*1000:.1f}ms")
    print(f"  Jitter: {final_metrics.jitter*1000:.1f}ms")
    
    layer.stop()


if __name__ == "__main__":
    demo_robust_layer()
