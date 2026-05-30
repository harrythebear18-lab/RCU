#!/usr/bin/env python3
"""
Raw Network Bypass for Ultra-Low Latency
Bypasses kernel network stack for direct hardware access
"""

import socket
import struct
import os
import mmap
import time
import threading
import ctypes
import fcntl
from typing import Optional, Tuple, Dict
import numpy as np

# Network constants
ETH_P_IP = 0x0800
ETH_P_ARP = 0x0806
IPPROTO_UDP = 17
IPPROTO_TCP = 6

# Hardware timestamping
SOF_TIMESTAMPING_TX_HARDWARE = 1
SOF_TIMESTAMPING_TX_SOFTWARE = 2
SOF_TIMESTAMPING_RX_HARDWARE = 4
SOF_TIMESTAMPING_RX_SOFTWARE = 8

class RawPacketBuilder:
    """Pre-builds packets for maximum speed"""
    
    def __init__(self, src_mac: bytes, dst_mac: bytes, src_ip: bytes, dst_ip: bytes, 
                 src_port: int, dst_port: int):
        self.src_mac = src_mac
        self.dst_mac = dst_mac
        self.src_ip = src_ip
        self.dst_ip = dst_ip
        self.src_port = src_port
        self.dst_port = dst_port
        
        # Pre-compute static headers
        self.eth_header = struct.pack('!6s6sH', dst_mac, src_mac, ETH_P_IP)
        
        # IP header template (length and checksum will be updated)
        self.ip_header_template = struct.pack('!BBHHHBBH4s4s',
                                             0x45,  # Version (4) + IHL (5)
                                             0x00,  # Type of Service
                                             0,     # Total Length (filled later)
                                             0,     # Identification
                                             0x4000, # Flags + Fragment Offset (Don't Fragment)
                                             64,    # TTL
                                             IPPROTO_UDP, # Protocol
                                             0,     # Header Checksum (filled later)
                                             src_ip,
                                             dst_ip)
        
        # UDP header template (length and checksum will be updated)
        self.udp_header_template = struct.pack('!HHHH',
                                              src_port,
                                              dst_port,
                                              0,     # Length (filled later)
                                              0)     # Checksum (optional for IPv4)
    
    def build_packet(self, payload: bytes) -> bytes:
        """Build complete packet with payload"""
        udp_len = len(payload) + 8  # UDP header + payload
        ip_len = 20 + udp_len  # IP header + UDP
        
        # Update UDP header
        udp_header = struct.pack('!HHHH',
                               self.src_port,
                               self.dst_port,
                               udp_len,
                               0)  # Checksum (optional)
        
        # Update IP header
        ip_header = struct.pack('!BBHHHBBH4s4s',
                              0x45,  # Version + IHL
                              0x00,  # Type of Service
                              ip_len,  # Total Length
                              0,     # Identification
                              0x4000, # Flags + Fragment Offset
                              64,    # TTL
                              IPPROTO_UDP, # Protocol
                              0,     # Header Checksum (calculated below)
                              self.src_ip,
                              self.dst_ip)
        
        # Calculate IP checksum
        ip_checksum = self._calculate_ip_checksum(ip_header)
        ip_header = ip_header[:10] + struct.pack('!H', ip_checksum) + ip_header[12:]
        
        return self.eth_header + ip_header + udp_header + payload
    
    def _calculate_ip_checksum(self, ip_header: bytes) -> int:
        """Calculate IP header checksum"""
        # Convert to 16-bit words
        words = struct.unpack('!10H', ip_header[:20])
        
        # Sum all words
        total = sum(words)
        
        # Add carry
        while total >> 16:
            total = (total & 0xFFFF) + (total >> 16)
        
        # One's complement
        return ~total & 0xFFFF

class MemoryMappedRingBuffer:
    """Memory-mapped ring buffer for zero-copy operations"""
    
    def __init__(self, size: int, item_size: int):
        # Ensure size is power of 2
        if size & (size - 1):
            size = 1 << (size - 1).bit_length()
        
        self.size = size
        self.mask = size - 1
        self.item_size = item_size
        self.total_size = size * item_size
        
        # Create shared memory
        self.shm_fd = os.open('/dev/shm/ultra_dma_ring', os.O_CREAT | os.O_RDWR | O_TRUNC, 0o666)
        os.ftruncate(self.shm_fd, self.total_size)
        
        # Memory map
        self.buffer = mmap.mmap(self.shm_fd, self.total_size)
        
        # Head and tail pointers (shared between processes)
        self.head_ptr = mmap.mmap(-1, 8)  # 8 bytes for head
        self.tail_ptr = mmap.mmap(-1, 8)  # 8 bytes for tail
        
        # Initialize pointers
        self.head_ptr.write(struct.pack('!Q', 0))
        self.tail_ptr.write(struct.pack('!Q', 0))
    
    def push(self, data: bytes) -> bool:
        """Push data to ring buffer (lock-free)"""
        if len(data) > self.item_size:
            return False
        
        # Read current head and tail
        self.head_ptr.seek(0)
        head = struct.unpack('!Q', self.head_ptr.read(8))[0]
        
        self.tail_ptr.seek(0)
        tail = struct.unpack('!Q', self.tail_ptr.read(8))[0]
        
        # Check if ring is full
        next_head = (head + 1) & self.mask
        if next_head == tail:
            return False
        
        # Write data to buffer
        offset = head * self.item_size
        self.buffer.seek(offset)
        self.buffer.write(data.ljust(self.item_size, b'\0'))
        
        # Update head pointer
        self.head_ptr.seek(0)
        self.head_ptr.write(struct.pack('!Q', next_head))
        
        return True
    
    def pop(self) -> Optional[bytes]:
        """Pop data from ring buffer (lock-free)"""
        # Read current head and tail
        self.head_ptr.seek(0)
        head = struct.unpack('!Q', self.head_ptr.read(8))[0]
        
        self.tail_ptr.seek(0)
        tail = struct.unpack('!Q', self.tail_ptr.read(8))[0]
        
        # Check if ring is empty
        if tail == head:
            return None
        
        # Read data from buffer
        offset = tail * self.item_size
        self.buffer.seek(offset)
        data = self.buffer.read(self.item_size)
        
        # Update tail pointer
        next_tail = (tail + 1) & self.mask
        self.tail_ptr.seek(0)
        self.tail_ptr.write(struct.pack('!Q', next_tail))
        
        return data.rstrip(b'\0')
    
    def close(self):
        """Close ring buffer"""
        self.buffer.close()
        self.head_ptr.close()
        self.tail_ptr.close()
        os.close(self.shm_fd)

class UltraFastNIC:
    """Ultra-fast NIC interface with hardware timestamping"""
    
    def __init__(self, interface: str = "eth0"):
        self.interface = interface
        self.raw_socket = None
        self.packet_builder = None
        self.enable_timestamping = True
        
        # NIC capabilities
        self.supports_hardware_timestamps = False
        self.supports_checksum_offload = False
        self.supports_tso = False
        
        # Performance counters
        self.packets_sent = 0
        self.packets_received = 0
        self.bytes_sent = 0
        self.bytes_received = 0
        self.timestamp_errors = 0
    
    def setup(self, dst_ip: str, dst_port: int, src_port: int = 0) -> bool:
        """Setup ultra-fast NIC interface"""
        try:
            # Create raw socket
            self.raw_socket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(ETH_P_IP))
            self.raw_socket.bind((self.interface, 0))
            
            # Enable hardware timestamping if available
            if self.enable_timestamping:
                self._enable_hardware_timestamping()
            
            # Get interface information
            src_mac = self._get_interface_mac()
            src_ip = self._get_interface_ip()
            dst_mac = self._arp_resolve(dst_ip)
            dst_ip_bytes = socket.inet_aton(dst_ip)
            
            # Create packet builder
            self.packet_builder = RawPacketBuilder(
                src_mac, dst_mac, src_ip, dst_ip_bytes, src_port, dst_port
            )
            
            # Detect NIC capabilities
            self._detect_nic_capabilities()
            
            return True
        except Exception as e:
            print(f"Failed to setup ultra-fast NIC: {e}")
            return False
    
    def _enable_hardware_timestamping(self):
        """Enable hardware timestamping"""
        try:
            # Set timestamping options
            timestamping_flags = SOF_TIMESTAMPING_TX_HARDWARE | SOF_TIMESTAMPING_RX_HARDWARE
            self.raw_socket.setsockopt(socket.SOL_SOCKET, socket.SO_TIMESTAMPING, timestamping_flags)
            self.supports_hardware_timestamps = True
        except OSError:
            # Hardware timestamping not supported
            self.supports_hardware_timestamps = False
    
    def _get_interface_mac(self) -> bytes:
        """Get MAC address of interface"""
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        info = fcntl.ioctl(s.fileno(), 0x8927, struct.pack('256s', bytes(self.interface, 'utf-8')[:15]))
        return info[18:24]
    
    def _get_interface_ip(self) -> bytes:
        """Get IP address of interface"""
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', bytes(self.interface, 'utf-8')[:15]))[20:24]
    
    def _arp_resolve(self, ip: str) -> bytes:
        """Resolve IP to MAC address (simplified)"""
        # In production, this would do proper ARP resolution
        # For demo, use broadcast
        return b'\xff\xff\xff\xff\xff\xff'
    
    def _detect_nic_capabilities(self):
        """Detect NIC capabilities"""
        try:
            # Check for checksum offload
            ethtool_output = os.popen(f'ethtool -k {self.interface} 2>/dev/null').read()
            if 'tx-checksumming: on' in ethtool_output:
                self.supports_checksum_offload = True
            
            # Check for TCP segmentation offload
            if 'tcp-segmentation-offload: on' in ethtool_output:
                self.supports_tso = True
                
        except:
            pass
    
    def send_packet_ultra_fast(self, payload: bytes) -> Tuple[bool, Optional[int]]:
        """Send packet with ultra-low latency and timestamping"""
        if not self.packet_builder:
            return False, None
        
        # Build packet
        packet = self.packet_builder.build_packet(payload)
        
        # Get timestamp before send
        send_time = self._get_timestamp()
        
        try:
            # Send packet
            bytes_sent = self.raw_socket.send(packet)
            
            # Get timestamp after send
            send_time_end = self._get_timestamp()
            
            # Update counters
            self.packets_sent += 1
            self.bytes_sent += bytes_sent
            
            # Calculate send latency
            send_latency = send_time_end - send_time
            
            return True, send_latency
            
        except Exception as e:
            print(f"Send failed: {e}")
            return False, None
    
    def _get_timestamp(self) -> int:
        """Get high-precision timestamp"""
        if self.supports_hardware_timestamps:
            # Use hardware timestamp
            try:
                return time.time_ns()
            except:
                pass
        
        # Fallback to RDTSC or high-resolution timer
        try:
            # Try RDTSC on x86
            class RDTSC(ctypes.Structure):
                _fields_ = [('low', ctypes.c_uint32), ('high', ctypes.c_uint32)]
            
            rdtsc_asm = ctypes.CDLL(None)
            rdtsc = rdtsc_asm.rdtsc
            rdtsc.argtypes = []
            rdtsc.restype = RDTSC
            
            result = rdtsc()
            return (result.high << 32) | result.low
        except:
            # Fallback to nanoseconds
            return time.time_ns()
    
    def receive_packet_ultra_fast(self) -> Tuple[Optional[bytes], Optional[int]]:
        """Receive packet with ultra-low latency"""
        try:
            # Use recvmsg for timestamping
            packet, ancdata, flags, addr = self.raw_socket.recvmsg(65535, 1024)
            
            # Extract timestamp from ancillary data
            recv_time = None
            for cmsg_level, cmsg_type, cmsg_data in ancdata:
                if cmsg_level == socket.SOL_SOCKET and cmsg_type == socket.SO_TIMESTAMPING:
                    # Extract hardware timestamp
                    if len(cmsg_data) >= 16:
                        recv_time = struct.unpack('!Q', cmsg_data[:8])[0]
            
            if recv_time is None:
                recv_time = self._get_timestamp()
            
            # Update counters
            self.packets_received += 1
            self.bytes_received += len(packet)
            
            # Extract payload (skip Ethernet, IP, UDP headers)
            if len(packet) >= 42:  # Minimum packet size
                payload = packet[42:]  # Skip Ethernet(14) + IP(20) + UDP(8)
                return payload, recv_time
            
            return packet, recv_time
            
        except socket.timeout:
            return None, None
        except Exception as e:
            print(f"Receive failed: {e}")
            return None, None
    
    def get_statistics(self) -> Dict:
        """Get performance statistics"""
        return {
            'packets_sent': self.packets_sent,
            'packets_received': self.packets_received,
            'bytes_sent': self.bytes_sent,
            'bytes_received': self.bytes_received,
            'supports_hardware_timestamps': self.supports_hardware_timestamps,
            'supports_checksum_offload': self.supports_checksum_offload,
            'supports_tso': self.supports_tso,
            'timestamp_errors': self.timestamp_errors
        }
    
    def close(self):
        """Close NIC interface"""
        if self.raw_socket:
            self.raw_socket.close()

class KernelBypassManager:
    """Manages kernel bypass operations for maximum performance"""
    
    def __init__(self):
        self.nics = {}  # Multiple NICs for parallelism
        self.ring_buffers = {}
        self.worker_threads = []
        self.running = False
        
        # Performance configuration
        self.num_workers = 4
        self.ring_size = 65536  # 64K entries
        self.packet_size = 1514  # Ethernet MTU
    
    def setup_interface(self, interface: str, dst_ip: str, dst_port: int) -> bool:
        """Setup interface for kernel bypass"""
        nic = UltraFastNIC(interface)
        if nic.setup(dst_ip, dst_port):
            self.nics[interface] = nic
            
            # Create ring buffer for this interface
            ring = MemoryMappedRingBuffer(self.ring_size, self.packet_size)
            self.ring_buffers[interface] = ring
            
            return True
        return False
    
    def start_workers(self):
        """Start worker threads for packet processing"""
        self.running = True
        
        # TX worker threads
        for i, (interface, nic) in enumerate(self.nics.items()):
            ring = self.ring_buffers[interface]
            thread = threading.Thread(target=self._tx_worker, args=(nic, ring, i))
            thread.daemon = True
            thread.start()
            self.worker_threads.append(thread)
        
        # RX worker thread
        for interface, nic in self.nics.items():
            thread = threading.Thread(target=self._rx_worker, args=(nic, interface))
            thread.daemon = True
            thread.start()
            self.worker_threads.append(thread)
    
    def _tx_worker(self, nic: UltraFastNIC, ring: MemoryMappedRingBuffer, worker_id: int):
        """TX worker thread"""
        while self.running:
            # Get packet from ring buffer
            packet_data = ring.pop()
            if packet_data:
                # Send packet
                success, latency = nic.send_packet_ultra_fast(packet_data)
                if not success:
                    print(f"TX worker {worker_id}: Send failed")
            else:
                # No packets, sleep briefly
                time.sleep(0.001)  # 1ms
    
    def _rx_worker(self, nic: UltraFastNIC, interface: str):
        """RX worker thread"""
        ring = self.ring_buffers[interface]
        
        while self.running:
            # Receive packet
            packet_data, timestamp = nic.receive_packet_ultra_fast()
            if packet_data:
                # Push to ring buffer
                ring.push(packet_data)
            else:
                # No packet, sleep briefly
                time.sleep(0.001)  # 1ms
    
    def send_packet(self, interface: str, data: bytes) -> bool:
        """Send packet via ring buffer"""
        if interface in self.ring_buffers:
            return self.ring_buffers[interface].push(data)
        return False
    
    def receive_packet(self, interface: str) -> Optional[bytes]:
        """Receive packet from ring buffer"""
        if interface in self.ring_buffers:
            return self.ring_buffers[interface].pop()
        return None
    
    def stop(self):
        """Stop all workers"""
        self.running = False
        
        # Wait for workers to finish
        for thread in self.worker_threads:
            thread.join(timeout=1.0)
        
        # Cleanup
        for nic in self.nics.values():
            nic.close()
        
        for ring in self.ring_buffers.values():
            ring.close()
    
    def get_total_statistics(self) -> Dict:
        """Get statistics from all NICs"""
        total_stats = {
            'total_packets_sent': 0,
            'total_packets_received': 0,
            'total_bytes_sent': 0,
            'total_bytes_received': 0,
            'interfaces': {}
        }
        
        for interface, nic in self.nics.items():
            stats = nic.get_statistics()
            total_stats['interfaces'][interface] = stats
            total_stats['total_packets_sent'] += stats['packets_sent']
            total_stats['total_packets_received'] += stats['packets_received']
            total_stats['total_bytes_sent'] += stats['bytes_sent']
            total_stats['total_bytes_received'] += stats['bytes_received']
        
        return total_stats

def demo_kernel_bypass():
    """Demonstration of kernel bypass networking"""
    print("Kernel Bypass Networking Demo")
    print("=" * 40)
    
    manager = KernelBypassManager()
    
    try:
        # Setup interface
        if manager.setup_interface("eth0", "192.168.1.100", 9999):
            print("Kernel bypass interface setup successful")
            
            # Start workers
            manager.start_workers()
            print("Worker threads started")
            
            # Test packet sending
            test_data = b"Kernel bypass test packet!" * 100
            
            start_time = time.time()
            for i in range(1000):
                manager.send_packet("eth0", test_data + str(i).encode())
            end_time = time.time()
            
            print(f"Sent 1000 packets in {(end_time - start_time) * 1000:.2f} ms")
            print(f"Average send time: {(end_time - start_time) * 1000000 / 1000:.2f} μs")
            
            # Get statistics
            stats = manager.get_total_statistics()
            print(f"\nKernel Bypass Statistics:")
            for key, value in stats.items():
                if key != 'interfaces':
                    print(f"  {key}: {value}")
            
            # Wait for some packets to be received
            time.sleep(2)
            
            # Get final statistics
            final_stats = manager.get_total_statistics()
            print(f"\nFinal Statistics:")
            print(f"  Packets sent: {final_stats['total_packets_sent']}")
            print(f"  Packets received: {final_stats['total_packets_received']}")
            print(f"  Bytes sent: {final_stats['total_bytes_sent']}")
            print(f"  Bytes received: {final_stats['total_bytes_received']}")
            
        else:
            print("Failed to setup kernel bypass interface")
            print("Make sure you have root privileges and the interface exists")
    
    finally:
        manager.stop()

if __name__ == "__main__":
    demo_kernel_bypass()
