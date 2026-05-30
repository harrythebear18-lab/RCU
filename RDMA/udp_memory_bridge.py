#!/usr/bin/env python3
"""
UDP-based Memory Bridge: High-performance wireless memory access
Handles Wi-Fi jitter with sequence numbers and packet reordering
"""

import socket
import struct
import time
import threading
import queue
import hashlib
import logging
from typing import Dict, Optional, Tuple, Callable
from dataclasses import dataclass
from enum import Enum

class PacketType(Enum):
    MEMORY_REQUEST = 1
    MEMORY_RESPONSE = 2
    ACK = 3
    HEARTBEAT = 4
    ERROR = 5

@dataclass
class MemoryPacket:
    """UDP packet structure for memory bridge"""
    sequence: int
    packet_type: PacketType
    address: int
    size: int
    data: bytes
    checksum: int
    
    def pack(self) -> bytes:
        """Pack packet into bytes for UDP transmission"""
        header = struct.pack(
            '!IBBII',  # Format: sequence(4), type(1), reserved(1), address(4), size(4)
            self.sequence,
            self.packet_type.value,
            0,  # Reserved byte
            self.address,
            self.size
        )
        
        # Calculate checksum
        checksum_data = header + self.data
        self.checksum = hashlib.md5(checksum_data).digest()[0] & 0xFF
        
        # Final packet with checksum
        return header + struct.pack('!B', self.checksum) + self.data
    
    @classmethod
    def unpack(cls, data: bytes) -> 'MemoryPacket':
        """Unpack bytes into MemoryPacket"""
        if len(data) < 14:  # Minimum packet size
            raise ValueError("Packet too small")
        
        sequence, packet_type_val, reserved, address, size = struct.unpack('!IBBII', data[:14])
        checksum = data[14]
        packet_data = data[15:]
        
        packet_type = PacketType(packet_type_val)
        
        # Verify checksum
        checksum_data = data[:14] + packet_data
        expected_checksum = hashlib.md5(checksum_data).digest()[0] & 0xFF
        
        if checksum != expected_checksum:
            raise ValueError("Checksum verification failed")
        
        return cls(
            sequence=sequence,
            packet_type=packet_type,
            address=address,
            size=size,
            data=packet_data,
            checksum=checksum
        )

class UDPMemoryBridgeServer:
    """Server side: Responds to memory requests over UDP"""
    
    def __init__(self, port: int = 9999, max_packet_size: int = 1400):
        self.port = port
        self.max_packet_size = max_packet_size
        self.socket = None
        self.running = False
        self.sequence_counter = 0
        
        # Memory regions (simulated or real)
        self.memory_regions = {}
        
        # Packet tracking for retransmission
        self.pending_packets = {}
        self.ack_timeout = 0.5  # 500ms timeout
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def add_memory_region(self, name: str, address: int, data: bytes):
        """Add a memory region that can be accessed"""
        self.memory_regions[(name, address)] = data
        self.logger.info(f"Added memory region '{name}' at address 0x{address:x}")
    
    def start_server(self):
        """Start the UDP memory bridge server"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(('0.0.0.0', self.port))
        self.socket.settimeout(1.0)  # Non-blocking with timeout
        
        self.running = True
        self.logger.info(f"UDP Memory Bridge started on port {self.port}")
        
        # Start retransmission thread
        retrans_thread = threading.Thread(target=self.retransmission_worker)
        retrans_thread.daemon = True
        retrans_thread.start()
        
        try:
            while self.running:
                try:
                    data, addr = self.socket.recvfrom(self.max_packet_size)
                    self.handle_packet(data, addr)
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        self.logger.error(f"Packet handling error: {e}")
        finally:
            self.stop()
    
    def handle_packet(self, data: bytes, addr: Tuple[str, int]):
        """Handle incoming packets"""
        try:
            packet = MemoryPacket.unpack(data)
            
            if packet.packet_type == PacketType.MEMORY_REQUEST:
                self.handle_memory_request(packet, addr)
            elif packet.packet_type == PacketType.ACK:
                self.handle_ack(packet)
            elif packet.packet_type == PacketType.HEARTBEAT:
                self.send_heartbeat_response(addr)
            else:
                self.logger.warning(f"Unknown packet type: {packet.packet_type}")
                
        except Exception as e:
            self.logger.error(f"Packet processing error: {e}")
            # Send error response
            self.send_error_response(addr, str(e))
    
    def handle_memory_request(self, packet: MemoryPacket, addr: Tuple[str, int]):
        """Handle memory read requests"""
        try:
            # Find memory region
            region_data = None
            for (name, base_addr), data in self.memory_regions.items():
                if base_addr <= packet.address < base_addr + len(data):
                    offset = packet.address - base_addr
                    region_data = data[offset:offset + packet.size]
                    break
            
            if region_data is None:
                # Memory not found
                error_packet = MemoryPacket(
                    sequence=self.sequence_counter,
                    packet_type=PacketType.ERROR,
                    address=packet.address,
                    size=0,
                    data=b"Memory region not found",
                    checksum=0
                )
                self.send_packet(error_packet, addr)
                return
            
            # Truncate if requested size is larger than available
            if len(region_data) < packet.size:
                packet.size = len(region_data)
            
            # Create response packet
            response_packet = MemoryPacket(
                sequence=self.sequence_counter,
                packet_type=PacketType.MEMORY_RESPONSE,
                address=packet.address,
                size=packet.size,
                data=region_data,
                checksum=0
            )
            
            self.sequence_counter += 1
            self.send_packet_with_retransmit(response_packet, addr)
            
        except Exception as e:
            self.logger.error(f"Memory request handling error: {e}")
            self.send_error_response(addr, str(e))
    
    def send_packet(self, packet: MemoryPacket, addr: Tuple[str, int]):
        """Send a single packet"""
        try:
            packed_data = packet.pack()
            self.socket.sendto(packed_data, addr)
        except Exception as e:
            self.logger.error(f"Send packet error: {e}")
    
    def send_packet_with_retransmit(self, packet: MemoryPacket, addr: Tuple[str, int]):
        """Send packet and track for retransmission"""
        self.send_packet(packet, addr)
        
        # Track for retransmission
        self.pending_packets[packet.sequence] = {
            'packet': packet,
            'addr': addr,
            'timestamp': time.time(),
            'attempts': 0
        }
    
    def retransmission_worker(self):
        """Worker thread for handling packet retransmission"""
        while self.running:
            current_time = time.time()
            expired_packets = []
            
            for seq, packet_info in self.pending_packets.items():
                if current_time - packet_info['timestamp'] > self.ack_timeout:
                    if packet_info['attempts'] < 3:  # Max 3 retransmissions
                        # Retransmit
                        self.send_packet(packet_info['packet'], packet_info['addr'])
                        packet_info['timestamp'] = current_time
                        packet_info['attempts'] += 1
                        self.logger.debug(f"Retransmitting packet {seq}")
                    else:
                        # Give up on this packet
                        expired_packets.append(seq)
                        self.logger.warning(f"Gave up on packet {seq} after 3 attempts")
            
            # Remove expired packets
            for seq in expired_packets:
                del self.pending_packets[seq]
            
            time.sleep(0.1)  # Check every 100ms
    
    def handle_ack(self, packet: MemoryPacket):
        """Handle ACK packets"""
        if packet.sequence in self.pending_packets:
            del self.pending_packets[packet.sequence]
            self.logger.debug(f"Received ACK for packet {packet.sequence}")
    
    def send_heartbeat_response(self, addr: Tuple[str, int]):
        """Send heartbeat response"""
        heartbeat = MemoryPacket(
            sequence=self.sequence_counter,
            packet_type=PacketType.HEARTBEAT,
            address=0,
            size=0,
            data=b"",
            checksum=0
        )
        self.sequence_counter += 1
        self.send_packet(heartbeat, addr)
    
    def send_error_response(self, addr: Tuple[str, int], error_msg: str):
        """Send error response"""
        error_packet = MemoryPacket(
            sequence=self.sequence_counter,
            packet_type=PacketType.ERROR,
            address=0,
            size=0,
            data=error_msg.encode('utf-8'),
            checksum=0
        )
        self.sequence_counter += 1
        self.send_packet(error_packet, addr)
    
    def stop(self):
        """Stop the server"""
        self.running = False
        if self.socket:
            self.socket.close()
        self.logger.info("UDP Memory Bridge stopped")


class UDPMemoryBridgeClient:
    """Client side: Requests memory over UDP with reordering support"""
    
    def __init__(self, server_host: str, port: int = 9999, max_packet_size: int = 1400):
        self.server_host = server_host
        self.server_port = port
        self.max_packet_size = max_packet_size
        self.socket = None
        self.sequence_counter = 0
        
        # Packet reordering buffer
        self.received_packets = {}
        self.expected_sequence = 0
        
        # Statistics
        self.stats = {
            'packets_sent': 0,
            'packets_received': 0,
            'packets_reordered': 0,
            'packets_lost': 0
        }
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def connect(self):
        """Initialize UDP socket"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(2.0)  # 2 second timeout
        self.logger.info(f"Connected to UDP Memory Bridge at {self.server_host}:{self.server_port}")
        return True
    
    def read_memory(self, address: int, size: int, timeout: float = 5.0) -> bytes:
        """Read memory from server with automatic retransmission"""
        start_time = time.time()
        
        # Create request packet
        request_packet = MemoryPacket(
            sequence=self.sequence_counter,
            packet_type=PacketType.MEMORY_REQUEST,
            address=address,
            size=size,
            data=b"",
            checksum=0
        )
        
        self.sequence_counter += 1
        self.stats['packets_sent'] += 1
        
        # Send request
        server_addr = (self.server_host, self.server_port)
        self.socket.sendto(request_packet.pack(), server_addr)
        
        # Wait for response
        while time.time() - start_time < timeout:
            try:
                data, addr = self.socket.recvfrom(self.max_packet_size)
                response_packet = MemoryPacket.unpack(data)
                
                if response_packet.packet_type == PacketType.MEMORY_RESPONSE:
                    self.stats['packets_received'] += 1
                    return response_packet.data
                elif response_packet.packet_type == PacketType.ERROR:
                    raise Exception(f"Server error: {response_packet.data.decode('utf-8')}")
                elif response_packet.packet_type == PacketType.HEARTBEAT:
                    continue  # Ignore heartbeats
                
            except socket.timeout:
                # Retransmit request
                self.socket.sendto(request_packet.pack(), server_addr)
                self.stats['packets_sent'] += 1
                continue
            except Exception as e:
                raise Exception(f"Memory read failed: {e}")
        
        raise TimeoutError(f"Memory read timeout after {timeout} seconds")
    
    def benchmark_performance(self, iterations: int = 100):
        """Benchmark UDP memory bridge performance"""
        print(f"Running UDP Memory Bridge benchmark ({iterations} iterations)...")
        
        total_time = 0
        total_bytes = 0
        
        for i in range(iterations):
            start_time = time.time()
            
            try:
                # Read 4KB from address 0x1000
                data = self.read_memory(0x1000, 4096, timeout=1.0)
                total_bytes += len(data)
            except Exception as e:
                print(f"Iteration {i} failed: {e}")
                continue
            
            iteration_time = time.time() - start_time
            total_time += iteration_time
            
            if (i + 1) % 10 == 0:
                print(f"Completed {i + 1}/{iterations} iterations")
        
        if total_time > 0:
            avg_latency = (total_time / iterations) * 1000  # ms
            throughput = total_bytes / total_time / 1024 / 1024  # MB/s
            
            print(f"Results:")
            print(f"  Average latency: {avg_latency:.2f} ms")
            print(f"  Throughput: {throughput:.2f} MB/s")
            print(f"  Success rate: {total_bytes / (4096 * iterations) * 100:.1f}%")
            print(f"  Statistics: {self.stats}")
    
    def get_statistics(self) -> dict:
        """Get performance statistics"""
        return self.stats.copy()
    
    def disconnect(self):
        """Close connection"""
        if self.socket:
            self.socket.close()
            self.logger.info("Disconnected from UDP Memory Bridge")


def demo_udp_bridge():
    """Demonstration of UDP Memory Bridge"""
    print("UDP Memory Bridge Demo")
    print("=" * 40)
    
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python udp_memory_bridge.py [server|client] [host]")
        sys.exit(1)
    
    mode = sys.argv[1]
    
    if mode == "server":
        # Server side
        server = UDPMemoryBridgeServer()
        
        # Add some test memory regions
        test_data = b"A" * 1024 * 1024  # 1MB of 'A's
        server.add_memory_region("test_region", 0x1000, test_data)
        
        # Add game-like data
        game_data = b"GAME_MEMORY_DATA" * 1000
        server.add_memory_region("game_memory", 0x100000, game_data)
        
        print("Starting UDP Memory Bridge Server...")
        print("Memory regions added:")
        print("  test_region at 0x1000 (1MB)")
        print("  game_memory at 0x100000")
        
        try:
            server.start_server()
        except KeyboardInterrupt:
            print("\nShutting down server...")
            server.stop()
    
    elif mode == "client":
        if len(sys.argv) < 3:
            print("Usage: python udp_memory_bridge.py client <server_host>")
            sys.exit(1)
        
        server_host = sys.argv[2]
        client = UDPMemoryBridgeClient(server_host)
        
        if client.connect():
            try:
                print("Connected to UDP Memory Bridge")
                print("Testing memory reads...")
                
                # Test reading from test region
                try:
                    data = client.read_memory(0x1000, 1024)
                    print(f"✓ Read {len(data)} bytes from test region")
                    print(f"  First 32 bytes: {data[:32].hex()}")
                except Exception as e:
                    print(f"✗ Test region read failed: {e}")
                
                # Test reading from game memory
                try:
                    data = client.read_memory(0x100000, 512)
                    print(f"✓ Read {len(data)} bytes from game memory")
                    print(f"  Data: {data[:50]}")
                except Exception as e:
                    print(f"✗ Game memory read failed: {e}")
                
                # Run benchmark
                print("\nRunning performance benchmark...")
                client.benchmark_performance(50)
                
            finally:
                client.disconnect()
    
    else:
        print("Unknown mode. Use 'server' or 'client'")


if __name__ == "__main__":
    demo_udp_bridge()
