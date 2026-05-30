#!/usr/bin/env python3
"""
Advanced DMA Service with Synchronization and Ordering Guarantees
High-performance remote memory writer with enterprise-grade reliability
"""

import asyncio
import socket
import struct
import time
import threading
import queue
import heapq
from collections import defaultdict, deque
from typing import Dict, List, Optional, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
import hashlib
import mmap
import os

class PacketType(Enum):
    DMA_WRITE = 1
    DMA_READ = 2
    DMA_RESPONSE = 3
    ACK = 4
    SYNC = 5
    ERROR = 6

@dataclass
class DMAPacket:
    """Ordered DMA packet with synchronization support"""
    sequence: int
    packet_type: PacketType
    address: int
    size: int
    data: bytes
    checksum: int
    timestamp: float = field(default_factory=time.time)
    retry_count: int = 0
    
    def pack(self) -> bytes:
        """Pack packet for network transmission"""
        header = struct.pack(
            '!IBBIIQ',  # seq(4), type(1), reserved(1), addr(4), size(4), timestamp(8)
            self.sequence,
            self.packet_type.value,
            0,  # reserved
            self.address,
            self.size,
            int(self.timestamp * 1000000)  # microseconds
        )
        
        # Calculate checksum
        checksum_data = header + self.data
        self.checksum = hashlib.md5(checksum_data).digest()[0] & 0xFF
        
        return header + struct.pack('!B', self.checksum) + self.data
    
    @classmethod
    def unpack(cls, data: bytes) -> 'DMAPacket':
        """Unpack packet from network data"""
        if len(data) < 22:  # Minimum packet size
            raise ValueError("Packet too small")
        
        seq, type_val, reserved, addr, size, timestamp_us = struct.unpack('!IBBIIQ', data[:22])
        checksum = data[22]
        packet_data = data[23:]
        
        # Verify checksum
        checksum_data = data[:22] + packet_data
        expected_checksum = hashlib.md5(checksum_data).digest()[0] & 0xFF
        
        if checksum != expected_checksum:
            raise ValueError("Checksum verification failed")
        
        return cls(
            sequence=seq,
            packet_type=PacketType(type_val),
            address=addr,
            size=size,
            data=packet_data,
            checksum=checksum,
            timestamp=timestamp_us / 1000000.0
        )

@dataclass
class MemoryRegion:
    """Memory region with access control and synchronization"""
    start_addr: int
    size: int
    data: bytearray
    lock: threading.RLock = field(default_factory=threading.RLock)
    access_count: int = 0
    last_access: float = field(default_factory=time.time)
    write_queue: queue.Queue = field(default_factory=queue.Queue)
    
    def write(self, offset: int, data: bytes) -> bool:
        """Thread-safe write to memory region"""
        if offset < 0 or offset + len(data) > self.size:
            return False
        
        with self.lock:
            self.data[offset:offset+len(data)] = data
            self.access_count += 1
            self.last_access = time.time()
            return True
    
    def read(self, offset: int, size: int) -> Optional[bytes]:
        """Thread-safe read from memory region"""
        if offset < 0 or offset + size > self.size:
            return None
        
        with self.lock:
            self.access_count += 1
            self.last_access = time.time()
            return bytes(self.data[offset:offset+size])

class OrderedPacketBuffer:
    """Buffer that ensures packet ordering and handles gaps"""
    
    def __init__(self, max_gap: int = 1000):
        self.max_gap = max_gap
        self.buffer = {}  # sequence -> DMAPacket
        self.expected_seq = 0
        self.lock = threading.RLock()
        self.total_received = 0
        self.out_of_order_count = 0
    
    def add_packet(self, packet: DMAPacket) -> bool:
        """Add packet and return True if it can be delivered"""
        with self.lock:
            self.total_received += 1
            
            # Check if packet is too old
            if packet.sequence < self.expected_seq:
                return False
            
            # Check if gap is too large
            if packet.sequence - self.expected_seq > self.max_gap:
                # Skip ahead, drop old packets
                self.expected_seq = packet.sequence
                self.buffer.clear()
            
            # Add to buffer
            self.buffer[packet.sequence] = packet
            
            # Check if this is out of order
            if packet.sequence != self.expected_seq:
                self.out_of_order_count += 1
            
            return packet.sequence == self.expected_seq
    
    def get_ordered_packets(self) -> List[DMAPacket]:
        """Get all packets that can be delivered in order"""
        with self.lock:
            ordered_packets = []
            
            while self.expected_seq in self.buffer:
                packet = self.buffer[self.expected_seq]
                ordered_packets.append(packet)
                del self.buffer[self.expected_seq]
                self.expected_seq += 1
            
            return ordered_packets
    
    def get_stats(self) -> Dict[str, int]:
        """Get buffer statistics"""
        with self.lock:
            return {
                'total_received': self.total_received,
                'out_of_order': self.out_of_order_count,
                'buffered_packets': len(self.buffer),
                'expected_sequence': self.expected_seq
            }

class AdvancedDMAService:
    """High-performance DMA service with enterprise features"""
    
    def __init__(self, 
                 listen_port: int = 9999,
                 max_memory_regions: int = 64,
                 enable_encryption: bool = False,
                 enable_compression: bool = False):
        
        self.listen_port = listen_port
        self.max_memory_regions = max_memory_regions
        self.enable_encryption = enable_encryption
        self.enable_compression = enable_compression
        
        # Memory management
        self.memory_regions: Dict[int, MemoryRegion] = {}
        self.regions_lock = threading.RLock()
        
        # Packet management
        self.packet_buffer = OrderedPacketBuffer()
        self.pending_acks = {}  # sequence -> (timestamp, retry_count)
        
        # Network
        self.socket = None
        self.running = False
        
        # Performance metrics
        self.metrics = {
            'packets_received': 0,
            'packets_processed': 0,
            'bytes_transferred': 0,
            'errors': 0,
            'retransmissions': 0,
            'avg_latency': 0.0,
            'throughput': 0.0
        }
        self.metrics_lock = threading.RLock()
        self.latency_samples = deque(maxlen=1000)
        
        # Worker threads
        self.packet_processor_thread = None
        self.ack_sender_thread = None
        self.metrics_thread = None
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def add_memory_region(self, start_addr: int, size: int) -> bool:
        """Add a memory region for DMA operations"""
        with self.regions_lock:
            if len(self.memory_regions) >= self.max_memory_regions:
                return False
            
            if start_addr in self.memory_regions:
                return False
            
            # Create memory-mapped region for performance
            try:
                # Try to use mmap for large regions
                if size >= 1024 * 1024:  # 1MB+
                    temp_file = f"/tmp/dma_region_{start_addr}_{os.getpid()}"
                    with open(temp_file, 'wb') as f:
                        f.truncate(size)
                    
                    fd = os.open(temp_file, os.O_RDWR)
                    mapped_data = mmap.mmap(fd, size)
                    region_data = bytearray(mapped_data)
                    mapped_data.close()
                    os.close(fd)
                    os.unlink(temp_file)
                else:
                    region_data = bytearray(size)
                
                region = MemoryRegion(
                    start_addr=start_addr,
                    size=size,
                    data=region_data
                )
                
                self.memory_regions[start_addr] = region
                self.logger.info(f"Added memory region: 0x{start_addr:x}-0x{start_addr+size:x} ({size:,} bytes)")
                return True
                
            except Exception as e:
                self.logger.error(f"Failed to create memory region: {e}")
                return False
    
    def remove_memory_region(self, start_addr: int) -> bool:
        """Remove a memory region"""
        with self.regions_lock:
            if start_addr in self.memory_regions:
                del self.memory_regions[start_addr]
                self.logger.info(f"Removed memory region: 0x{start_addr:x}")
                return True
            return False
    
    def start(self):
        """Start the advanced DMA service"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('0.0.0.0', self.listen_port))
        self.socket.settimeout(0.1)  # Non-blocking
        
        self.running = True
        
        # Start worker threads
        self.packet_processor_thread = threading.Thread(target=self._packet_processor_worker)
        self.packet_processor_thread.daemon = True
        self.packet_processor_thread.start()
        
        self.ack_sender_thread = threading.Thread(target=self._ack_sender_worker)
        self.ack_sender_thread.daemon = True
        self.ack_sender_thread.start()
        
        self.metrics_thread = threading.Thread(target=self._metrics_worker)
        self.metrics_thread.daemon = True
        self.metrics_thread.start()
        
        self.logger.info(f"Advanced DMA Service started on port {self.listen_port}")
        
        try:
            while self.running:
                try:
                    data, addr = self.socket.recvfrom(2048)
                    self._handle_received_packet(data, addr)
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        self.logger.error(f"Receive error: {e}")
        finally:
            self.stop()
    
    def _handle_received_packet(self, data: bytes, addr: Tuple[str, int]):
        """Handle incoming DMA packet"""
        try:
            packet = DMAPacket.unpack(data)
            
            with self.metrics_lock:
                self.metrics['packets_received'] += 1
                self.metrics['bytes_transferred'] += len(data)
            
            # Add to ordered buffer
            if self.packet_buffer.add_packet(packet):
                # Packet can be processed immediately
                self._process_packet(packet, addr)
            else:
                # Packet buffered for ordering
                pass
            
            # Process any buffered packets that are now in order
            ordered_packets = self.packet_buffer.get_ordered_packets()
            for ordered_packet in ordered_packets:
                self._process_packet(ordered_packet, addr)
            
        except Exception as e:
            self.logger.error(f"Packet handling error: {e}")
            with self.metrics_lock:
                self.metrics['errors'] += 1
    
    def _process_packet(self, packet: DMAPacket, addr: Tuple[str, int]):
        """Process a single DMA packet"""
        try:
            if packet.packet_type == PacketType.DMA_WRITE:
                self._handle_dma_write(packet, addr)
            elif packet.packet_type == PacketType.DMA_READ:
                self._handle_dma_read(packet, addr)
            elif packet.packet_type == PacketType.SYNC:
                self._handle_sync(packet, addr)
            else:
                self.logger.warning(f"Unknown packet type: {packet.packet_type}")
            
            # Send ACK
            self._send_ack(packet.sequence, addr)
            
            with self.metrics_lock:
                self.metrics['packets_processed'] += 1
                # Update latency
                latency = time.time() - packet.timestamp
                self.latency_samples.append(latency)
                
        except Exception as e:
            self.logger.error(f"Packet processing error: {e}")
            with self.metrics_lock:
                self.metrics['errors'] += 1
    
    def _handle_dma_write(self, packet: DMAPacket, addr: Tuple[str, int]):
        """Handle DMA write packet"""
        with self.regions_lock:
            # Find target memory region
            target_region = None
            for region in self.memory_regions.values():
                if region.start_addr <= packet.address < region.start_addr + region.size:
                    target_region = region
                    break
            
            if target_region:
                offset = packet.address - target_region.start_addr
                if target_region.write(offset, packet.data):
                    self.logger.debug(f"DMA write: {len(packet.data)} bytes to 0x{packet.address:x}")
                else:
                    self.logger.error(f"DMA write failed: invalid offset {offset}")
            else:
                self.logger.error(f"DMA write failed: no region for address 0x{packet.address:x}")
    
    def _handle_dma_read(self, packet: DMAPacket, addr: Tuple[str, int]):
        """Handle DMA read packet"""
        with self.regions_lock:
            # Find target memory region
            target_region = None
            for region in self.memory_regions.values():
                if region.start_addr <= packet.address < region.start_addr + region.size:
                    target_region = region
                    break
            
            if target_region:
                offset = packet.address - target_region.start_addr
                data = target_region.read(offset, packet.size)
                if data:
                    # Send response packet
                    response = DMAPacket(
                        sequence=packet.sequence,
                        packet_type=PacketType.DMA_RESPONSE,
                        address=packet.address,
                        size=len(data),
                        data=data,
                        checksum=0
                    )
                    self._send_packet(response, addr)
                else:
                    self.logger.error(f"DMA read failed: invalid offset {offset}")
            else:
                self.logger.error(f"DMA read failed: no region for address 0x{packet.address:x}")
    
    def _handle_sync(self, packet: DMAPacket, addr: Tuple[str, int]):
        """Handle synchronization packet"""
        # Send sync response
        response = DMAPacket(
            sequence=packet.sequence,
            packet_type=PacketType.SYNC,
            address=0,
            size=0,
            data=b"",
            checksum=0
        )
        self._send_packet(response, addr)
    
    def _send_packet(self, packet: DMAPacket, addr: Tuple[str, int]):
        """Send packet to remote address"""
        try:
            packed_data = packet.pack()
            self.socket.sendto(packed_data, addr)
        except Exception as e:
            self.logger.error(f"Send packet error: {e}")
    
    def _send_ack(self, sequence: int, addr: Tuple[str, int]):
        """Queue ACK for sending"""
        self.pending_acks[sequence] = (time.time(), addr)
    
    def _ack_sender_worker(self):
        """Worker thread for sending ACKs"""
        while self.running:
            current_time = time.time()
            acks_to_send = []
            
            # Collect ACKs to send
            for seq, (timestamp, addr) in list(self.pending_acks.items()):
                if current_time - timestamp > 0.001:  # 1ms delay
                    acks_to_send.append((seq, addr))
                    del self.pending_acks[seq]
            
            # Send ACKs
            for seq, addr in acks_to_send:
                ack_packet = DMAPacket(
                    sequence=seq,
                    packet_type=PacketType.ACK,
                    address=0,
                    size=0,
                    data=b"",
                    checksum=0
                )
                self._send_packet(ack_packet, addr)
            
            time.sleep(0.0001)  # 100μs granularity
    
    def _packet_processor_worker(self):
        """Worker thread for processing background tasks"""
        while self.running:
            # Process memory region write queues
            with self.regions_lock:
                for region in self.memory_regions.values():
                    try:
                        while not region.write_queue.empty():
                            offset, data = region.write_queue.get_nowait()
                            region.write(offset, data)
                    except queue.Empty:
                        pass
            
            time.sleep(0.001)  # 1ms processing interval
    
    def _metrics_worker(self):
        """Worker thread for updating metrics"""
        while self.running:
            with self.metrics_lock:
                # Update average latency
                if self.latency_samples:
                    self.metrics['avg_latency'] = sum(self.latency_samples) / len(self.latency_samples)
                
                # Calculate throughput (packets per second)
                if self.metrics['packets_processed'] > 0:
                    self.metrics['throughput'] = self.metrics['packets_processed'] / time.time()
            
            time.sleep(1.0)  # Update every second
    
    def get_memory_data(self, start_addr: int, size: int) -> Optional[bytes]:
        """Get data from memory region"""
        with self.regions_lock:
            for region in self.memory_regions.values():
                if region.start_addr <= start_addr < region.start_addr + region.size:
                    offset = start_addr - region.start_addr
                    return region.read(offset, size)
        return None
    
    def get_statistics(self) -> Dict:
        """Get comprehensive statistics"""
        with self.metrics_lock:
            stats = self.metrics.copy()
        
        # Add packet buffer stats
        buffer_stats = self.packet_buffer.get_stats()
        stats.update(buffer_stats)
        
        # Add memory region stats
        with self.regions_lock:
            region_stats = {
                'total_regions': len(self.memory_regions),
                'total_memory': sum(r.size for r in self.memory_regions.values()),
                'total_accesses': sum(r.access_count for r in self.memory_regions.values())
            }
            stats.update(region_stats)
        
        return stats
    
    def stop(self):
        """Stop the DMA service"""
        self.running = False
        
        if self.socket:
            self.socket.close()
        
        # Wait for worker threads
        if self.packet_processor_thread:
            self.packet_processor_thread.join(timeout=1.0)
        if self.ack_sender_thread:
            self.ack_sender_thread.join(timeout=1.0)
        if self.metrics_thread:
            self.metrics_thread.join(timeout=1.0)
        
        self.logger.info("Advanced DMA Service stopped")


def demo_advanced_dma():
    """Demonstration of advanced DMA service"""
    print("Advanced DMA Service Demo")
    print("=" * 40)
    
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python advanced_dma_service.py [server|client] [options]")
        sys.exit(1)
    
    mode = sys.argv[1]
    
    if mode == "server":
        # Advanced DMA server
        service = AdvancedDMAService(
            listen_port=9999,
            max_memory_regions=32,
            enable_encryption=False,
            enable_compression=False
        )
        
        # Add memory regions
        service.add_memory_region(0x10000000, 16*1024*1024)  # 16MB
        service.add_memory_region(0x20000000, 32*1024*1024)  # 32MB
        service.add_memory_region(0x30000000, 64*1024*1024)  # 64MB
        
        print("Starting Advanced DMA Service...")
        print("Memory regions added:")
        print("  0x10000000 - 16MB")
        print("  0x20000000 - 32MB")
        print("  0x30000000 - 64MB")
        print("\nPress Ctrl+C to stop")
        
        try:
            service.start()
        except KeyboardInterrupt:
            print("\nStopping service...")
            service.stop()
            
            # Print final statistics
            stats = service.get_statistics()
            print("\nFinal Statistics:")
            for key, value in stats.items():
                print(f"  {key}: {value}")
    
    elif mode == "client":
        # Simple client for testing
        print("Advanced DMA Client Demo")
        print("This would connect to the server and perform DMA operations")
        print("For a full client implementation, see virtual_dma_userspace.py")
    
    else:
        print("Unknown mode. Use 'server' or 'client'")


if __name__ == "__main__":
    demo_advanced_dma()
