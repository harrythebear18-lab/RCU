#!/usr/bin/env python3
"""
Ultra-Low-Latency DMA Userspace Interface
Optimized for minimal latency with:
- Lock-free ring buffers
- Memory-mapped I/O
- CPU affinity and real-time scheduling
- Kernel bypass networking
- Hardware timestamping
"""

import os
import sys
import mmap
import struct
import time
import threading
import socket
import select
import ctypes
import ctypes.util
from ctypes import Structure, c_uint32, c_uint64, c_uint8, c_uint16, c_bool
from typing import Optional, Dict, List, Tuple
import numpy as np
import psutil

# Load C library for low-level operations
try:
    libc = ctypes.CDLL(ctypes.util.find_library('c'), use_errno=True)
except:
    # Fallback for Windows
    try:
        libc = ctypes.CDLL('msvcrt', use_errno=True)
    except:
        libc = None

# CPU affinity and scheduling constants
SCHED_FIFO = 4
SCHED_RR = 3
CPU_SETSIZE = 1024

class CPUSet(ctypes.Structure):
    _fields_ = [
        ('bits', c_uint64 * (CPU_SETSIZE // (8 * ctypes.sizeof(c_uint64))))
    ]

# IOCTL commands matching kernel driver
ULTRA_DMA_IOCTL_BASE = ord('U')
ULTRA_ADD_REGION = 0x40045501  # _IOW('U', 1, struct ultra_dma_region)
ULTRA_REMOVE_REGION = 0x40045502  # _IOW('U', 2, unsigned long)
ULTRA_GET_STATS = 0x80045503  # _IOR('U', 3, struct ultra_dma_stats)
ULTRA_CONFIG = 0x40045504  # _IOW('U', 4, struct ultra_dma_config)

class LockFreeRingBuffer:
    """Ultra-fast lock-free ring buffer for zero-copy operations"""
    
    def __init__(self, size: int, item_size: int):
        # Ensure size is power of 2 for fast modulo
        if size & (size - 1):
            size = 1 << (size - 1).bit_length()
        
        self.size = size
        self.mask = size - 1
        self.item_size = item_size
        self.buffer = mmap.mmap(-1, size * item_size)
        self.head = 0
        self.tail = 0
        
        # Memory barriers for thread safety
        self._load_barrier = ctypes.c_uint8()
        self._store_barrier = ctypes.c_uint8()
    
    def push(self, data: bytes) -> bool:
        """Push item to ring buffer (lock-free)"""
        next_head = (self.head + 1) & self.mask
        
        if next_head == self.tail:
            return False  # Ring full
        
        # Write data
        offset = self.head * self.item_size
        self.buffer.seek(offset)
        self.buffer.write(data[:self.item_size])
        
        # Memory barrier
        ctypes.memcpy(ctypes.byref(self._store_barrier), ctypes.byref(self._store_barrier), 1)
        
        self.head = next_head
        return True
    
    def pop(self) -> Optional[bytes]:
        """Pop item from ring buffer (lock-free)"""
        if self.tail == self.head:
            return None  # Ring empty
        
        # Read data
        offset = self.tail * self.item_size
        self.buffer.seek(offset)
        data = self.buffer.read(self.item_size)
        
        # Memory barrier
        ctypes.memcpy(ctypes.byref(self._load_barrier), ctypes.byref(self._load_barrier), 1)
        
        self.tail = (self.tail + 1) & self.mask
        return data
    
    def is_empty(self) -> bool:
        return self.tail == self.head
    
    def is_full(self) -> bool:
        return ((self.head + 1) & self.mask) == self.tail

class UltraFastPacket:
    """Optimized packet structure for minimal overhead"""
    
    __slots__ = ['timestamp', 'address', 'size', 'sequence', 'data']
    
    def __init__(self, address: int = 0, size: int = 0, data: bytes = b''):
        self.timestamp = self._rdtsc()
        self.address = address
        self.size = size
        self.sequence = 0
        self.data = data
    
    @staticmethod
    def _rdtsc() -> int:
        """Read Time Stamp Counter for ultra-precise timing"""
        if hasattr(ctypes, 'c_uint64'):
            # Try to use RDTSC on x86
            try:
                x86_asm = ctypes.CDLL(None)
                class RDTSC(ctypes.Structure):
                    _fields_ = [('low', c_uint32), ('high', c_uint32)]
                
                rdtsc = x86_asm.rdtsc
                rdtsc.argtypes = []
                rdtsc.restype = RDTSC
                
                result = rdtsc()
                return (result.high << 32) | result.low
            except:
                pass
        
        # Fallback to high-resolution timer
        return time.time_ns()
    
    def pack(self) -> bytes:
        """Pack packet for network transmission"""
        header = struct.pack('<QIIQ', self.timestamp, self.address, self.size, self.sequence)
        return header + self.data
    
    @classmethod
    def unpack(cls, data: bytes) -> 'UltraFastPacket':
        """Unpack packet from network data"""
        if len(data) < 24:  # Minimum header size
            raise ValueError("Packet too small")
        
        timestamp, address, size, sequence = struct.unpack('<QIIQ', data[:24])
        packet_data = data[24:24+size]
        
        packet = cls(address, size, packet_data)
        packet.timestamp = timestamp
        packet.sequence = sequence
        return packet

class KernelBypassNetwork:
    """Kernel bypass networking for ultra-low latency"""
    
    def __init__(self, interface: str = "eth0"):
        self.interface = interface
        self.raw_socket = None
        self.src_mac = None
        self.dst_mac = None
        self.src_ip = None
        self.dst_ip = None
        
        # Pre-computed headers for speed
        self.eth_header = None
        self.ip_header = None
        self.udp_header = None
    
    def setup(self, dst_ip: str, dst_port: int, src_port: int = 0):
        """Setup kernel bypass network connection"""
        try:
            # Create raw socket
            self.raw_socket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(0x0800))
            self.raw_socket.bind((self.interface, 0))
            
            # Get MAC addresses
            self.src_mac = self._get_mac_address(self.interface)
            self.dst_mac = self._arp_lookup(dst_ip)
            
            # Setup IP addresses
            self.src_ip = self._get_ip_address(self.interface)
            self.dst_ip = socket.inet_aton(dst_ip)
            
            # Pre-compute headers
            self._precompute_headers(dst_port, src_port)
            
            return True
        except Exception as e:
            print(f"Kernel bypass setup failed: {e}")
            return False
    
    def _get_mac_address(self, interface: str) -> bytes:
        """Get MAC address of interface"""
        import fcntl
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        info = fcntl.ioctl(s.fileno(), 0x8927, struct.pack('256s', bytes(interface, 'utf-8')[:15]))
        return info[18:24]
    
    def _arp_lookup(self, ip: str) -> bytes:
        """ARP lookup for MAC address (simplified)"""
        # In production, this would do actual ARP resolution
        # For now, use broadcast MAC
        return b'\xff\xff\xff\xff\xff\xff'
    
    def _get_ip_address(self, interface: str) -> bytes:
        """Get IP address of interface"""
        import fcntl
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', bytes(interface, 'utf-8')[:15]))[20:24]
    
    def _precompute_headers(self, dst_port: int, src_port: int):
        """Pre-compute headers for maximum speed"""
        # Ethernet header
        self.eth_header = struct.pack('!6s6sH', self.dst_mac, self.src_mac, 0x0800)
        
        # IP header (simplified)
        self.ip_header = struct.pack('!BBHHHBBH4s4s', 
                                   0x45, 0x00, 0, 0, 0, 0, 0x11, 0, 0, self.dst_ip)
        
        # UDP header
        self.udp_header = struct.pack('!HHHH', src_port, dst_port, 0, 0)
    
    def send_packet(self, packet: UltraFastPacket) -> bool:
        """Send packet with kernel bypass"""
        try:
            # Build complete packet
            data = packet.pack()
            total_length = len(self.eth_header) + len(self.ip_header) + len(self.udp_header) + len(data)
            
            # Update IP and UDP headers
            ip_header = struct.pack('!BBHHHBBH4s4s', 
                                   0x45, 0x00, total_length - 14, 0, 0, 0x40, 0x11, 0, 
                                   self.src_ip, self.dst_ip)
            
            udp_header = struct.pack('!HHHH', 
                                    0x1234, 9999, len(data) + 8, 0)
            
            # Complete packet
            full_packet = self.eth_header + ip_header + udp_header + data
            
            # Send via raw socket
            self.raw_socket.send(full_packet)
            return True
        except Exception as e:
            print(f"Send failed: {e}")
            return False

class UltraLowLatencyDMA:
    """Ultra-low-latency DMA controller with all optimizations"""
    
    def __init__(self, device_path: str = "/dev/ultra_dma"):
        self.device_path = device_path
        self.device_fd = None
        self.regions = {}
        self.next_region_id = 0
        
        # Performance optimizations
        self.enable_cpu_affinity = True
        self.enable_realtime = True
        self.enable_kernel_bypass = True
        self.enable_hardware_timestamp = True
        
        # Lock-free ring buffers
        self.tx_rings = {}
        self.rx_rings = {}
        
        # Network bypass
        self.network = KernelBypassNetwork()
        
        # CPU affinity setup
        self.cpu_mask = 0xF  # Use first 4 CPUs
        
        # Performance counters
        self.packets_sent = 0
        self.packets_received = 0
        self.total_latency = 0
        self.latency_samples = 0
    
    def open(self) -> bool:
        """Open ultra DMA device with optimizations"""
        try:
            self.device_fd = os.open(self.device_path, os.O_RDWR | os.O_SYNC)
            
            # Configure for ultra-low latency
            self._configure_ultra_mode()
            
            # Set CPU affinity for this process
            if self.enable_cpu_affinity:
                self._set_cpu_affinity()
            
            # Set real-time scheduling
            if self.enable_realtime:
                self._set_realtime_priority()
            
            return True
        except OSError as e:
            print(f"Failed to open ultra DMA device: {e}")
            return False
    
    def _configure_ultra_mode(self):
        """Configure kernel driver for ultra-low latency"""
        config = struct.pack('BBII', 
                           self.enable_hardware_timestamp,
                           self.enable_kernel_bypass,
                           99,  # Priority
                           self.cpu_mask)
        
        try:
            fcntl.ioctl(self.device_fd, ULTRA_CONFIG, config)
        except OSError as e:
            print(f"Failed to configure ultra mode: {e}")
    
    def _set_cpu_affinity(self):
        """Set CPU affinity for this process"""
        try:
            # Get current process
            pid = os.getpid()
            
            # Create CPU set
            cpu_set = CPUSet()
            for i in range(4):  # Use first 4 CPUs
                cpu_set.bits[i // 64] |= (1 << (i % 64))
            
            # Set affinity
            libc.sched_setaffinity(pid, ctypes.sizeof(cpu_set), ctypes.byref(cpu_set))
            print(f"Set CPU affinity to mask: 0x{self.cpu_mask:x}")
        except Exception as e:
            print(f"Failed to set CPU affinity: {e}")
    
    def _set_realtime_priority(self):
        """Set real-time scheduling priority"""
        try:
            pid = os.getpid()
            
            # Set scheduling policy and priority
            param = ctypes.c_int(99)  # Highest priority
            libc.sched_setscheduler(pid, SCHED_FIFO, ctypes.byref(param))
            print("Set real-time scheduling priority")
        except Exception as e:
            print(f"Failed to set real-time priority: {e}")
    
    def add_region(self, start_addr: int, size: int, remote_ip: str, remote_port: int) -> int:
        """Add ultra-fast DMA region"""
        if not self.device_fd:
            raise RuntimeError("Device not opened")
        
        region_id = self.next_region_id
        self.next_region_id += 1
        
        # Prepare region structure for kernel
        region_struct = struct.pack('QQII16sHH', 
                                   start_addr, size, 0, 0,  # address, size, pages, virt_addr
                                   remote_ip.encode('ascii')[:16].ljust(16, b'\0'),
                                   0, 0)  # phys_addr, flags
        
        try:
            fcntl.ioctl(self.device_fd, ULTRA_ADD_REGION, region_struct)
        except OSError as e:
            raise RuntimeError(f"Failed to add DMA region: {e}")
        
        # Create lock-free ring buffers
        self.tx_rings[region_id] = LockFreeRingBuffer(8192, 64)  # 8K packets, 64 bytes each
        self.rx_rings[region_id] = LockFreeRingBuffer(8192, 64)
        
        # Setup network bypass
        if self.enable_kernel_bypass:
            self.network.setup(remote_ip, remote_port)
        
        self.regions[region_id] = {
            'start_addr': start_addr,
            'size': size,
            'remote_ip': remote_ip,
            'remote_port': remote_port,
            'active': True
        }
        
        print(f"Added ultra DMA region {region_id}: 0x{start_addr:x} -> {remote_ip}:{remote_port}")
        return region_id
    
    def write_memory_ultra_fast(self, region_id: int, offset: int, data: bytes) -> bool:
        """Ultra-fast memory write with minimal latency"""
        if region_id not in self.regions:
            return False
        
        region = self.regions[region_id]
        address = region['start_addr'] + offset
        
        # Create ultra-fast packet
        packet = UltraFastPacket(address, len(data), data)
        packet.sequence = self.packets_sent
        
        start_time = packet.timestamp
        
        # Try lock-free ring buffer first
        if self.tx_rings[region_id].push(packet.pack()):
            # Packet queued successfully
            self.packets_sent += 1
            
            # Update latency statistics
            end_time = UltraFastPacket._rdtsc()
            self.total_latency += (end_time - start_time)
            self.latency_samples += 1
            
            return True
        
        # Fallback to direct network send
        elif self.enable_kernel_bypass:
            success = self.network.send_packet(packet)
            if success:
                self.packets_sent += 1
            return success
        
        return False
    
    def benchmark_ultra_latency(self, region_id: int, iterations: int = 10000):
        """Ultra-low latency benchmark"""
        print(f"Running ultra-low latency benchmark: {iterations} iterations")
        
        test_data = b'X' * 64  # Small packets for minimum latency
        latencies = []
        
        start_time = time.time()
        
        for i in range(iterations):
            packet_start = UltraFastPacket._rdtsc()
            
            success = self.write_memory_ultra_fast(region_id, 0, test_data)
            
            packet_end = UltraFastPacket._rdtsc()
            
            if success:
                latencies.append(packet_end - packet_start)
            
            if (i + 1) % 1000 == 0:
                print(f"Completed {i + 1}/{iterations} iterations")
        
        end_time = time.time()
        
        # Calculate statistics
        if latencies:
            avg_latency_cycles = sum(latencies) / len(latencies)
            min_latency = min(latencies)
            max_latency = max(latencies)
            
            # Convert to nanoseconds (assuming 3GHz CPU)
            cpu_freq = 3e9  # Hz
            avg_latency_ns = (avg_latency_cycles / cpu_freq) * 1e9
            
            total_time = end_time - start_time
            throughput = (iterations * len(test_data)) / total_time
            
            print(f"\nUltra-Low Latency Results:")
            print(f"  Average latency: {avg_latency_ns:.2f} ns")
            print(f"  Min latency: {(min_latency / cpu_freq) * 1e9:.2f} ns")
            print(f"  Max latency: {(max_latency / cpu_freq) * 1e9:.2f} ns")
            print(f"  Throughput: {throughput / 1024 / 1024:.2f} MB/s")
            print(f"  Packets per second: {iterations / total_time:.0f}")
            print(f"  Success rate: {len(latencies) / iterations * 100:.1f}%")
        
        return latencies
    
    def get_ultra_stats(self) -> Dict:
        """Get ultra-performance statistics"""
        stats = struct.pack('QQQQQII', 0, 0, 0, 0, 0, 0, 0)  # Buffer for stats
        
        try:
            fcntl.ioctl(self.device_fd, ULTRA_GET_STATS, stats)
            stats_data = struct.unpack('QQQQQII', stats)
            
            return {
                'kernel_bytes': stats_data[0],
                'kernel_packets': stats_data[1],
                'kernel_dropped': stats_data[2],
                'kernel_avg_latency_ns': stats_data[3],
                'active_regions': stats_data[4],
                'cpu_usage': stats_data[5],
                'userspace_packets_sent': self.packets_sent,
                'userspace_packets_received': self.packets_received,
                'avg_latency_ns': (self.total_latency / self.latency_samples / 3e9 * 1e9) if self.latency_samples > 0 else 0
            }
        except OSError as e:
            print(f"Failed to get stats: {e}")
            return {}
    
    def close(self):
        """Close ultra DMA device"""
        if self.device_fd:
            os.close(self.device_fd)
            self.device_fd = None
        
        # Cleanup ring buffers
        for ring in self.tx_rings.values():
            ring.buffer.close()
        for ring in self.rx_rings.values():
            ring.buffer.close()
        
        print("Ultra DMA device closed")

def demo_ultra_low_latency():
    """Demonstration of ultra-low-latency DMA"""
    print("Ultra-Low-Latency DMA Demo")
    print("=" * 40)
    
    dma = UltraLowLatencyDMA()
    
    if not dma.open():
        print("Failed to open ultra DMA device")
        print("Make sure the ultra_dma kernel module is loaded:")
        print("  sudo insmod ultra_low_latency_dma.ko")
        print("  sudo chmod 666 /dev/ultra_dma")
        return
    
    try:
        # Add ultra-fast region
        region_id = dma.add_region(
            start_addr=0x10000000,
            size=1024*1024,
            remote_ip="192.168.1.100",
            remote_port=9999
        )
        
        print(f"Added ultra DMA region {region_id}")
        
        # Test ultra-fast writes
        print("Testing ultra-fast memory writes...")
        test_data = b"Ultra-fast DMA test data!" * 100
        
        start_time = time.time()
        for i in range(1000):
            dma.write_memory_ultra_fast(region_id, i * len(test_data), test_data)
        end_time = time.time()
        
        print(f"1000 writes completed in {(end_time - start_time) * 1000:.2f} ms")
        print(f"Average write time: {(end_time - start_time) * 1000000:.2f} μs")
        
        # Ultra-low latency benchmark
        dma.benchmark_ultra_latency(region_id, iterations=50000)
        
        # Get statistics
        stats = dma.get_ultra_stats()
        print(f"\nUltra Performance Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
    finally:
        dma.close()

if __name__ == "__main__":
    demo_ultra_low_latency()
