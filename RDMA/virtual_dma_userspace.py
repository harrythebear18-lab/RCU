#!/usr/bin/env python3
"""
Virtual DMA User-Space Interface
Provides high-level interface to the kernel virtual DMA driver
"""

import os
import sys
import mmap
import struct
import fcntl
import ctypes
import time
import threading
import socket
import logging
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass

# IOCTL commands matching the kernel driver
VDMA_IOCTL_BASE = ord('D')
VDMA_ADD_REGION = 0x40044401  # _IOW('D', 1, struct dma_region)
VDMA_REMOVE_REGION = 0x40044402  # _IOW('D', 2, unsigned long)
VDMA_GET_STATS = 0x80044403  # _IOR('D', 3, struct vdma_stats)
VDMA_CONFIG = 0x40044404  # _IOW('D', 4, struct vdma_config)

@dataclass
class DMARegion:
    """DMA region configuration"""
    start_addr: int
    size: int
    remote_ip: str
    remote_port: int
    local_buffer: Optional[mmap.mmap] = None
    active: bool = False

@dataclass
class DMAStats:
    """DMA statistics"""
    bytes_transferred: int
    packets_sent: int
    packets_dropped: int
    active_regions: int
    pending_operations: int

@dataclass
class DMAConfig:
    """DMA configuration"""
    debug_mode: bool = False
    timeout_ms: int = 1000
    max_retries: int = 3

class VirtualDMAController:
    """High-level interface to virtual DMA controller"""
    
    def __init__(self, device_path: str = "/dev/virtual_dma"):
        self.device_path = device_path
        self.device_fd = None
        self.regions: Dict[int, DMARegion] = {}
        self.next_region_id = 0
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Thread-safe operations
        self.lock = threading.RLock()
    
    def open(self) -> bool:
        """Open the virtual DMA device"""
        try:
            self.device_fd = os.open(self.device_path, os.O_RDWR | os.O_SYNC)
            self.logger.info(f"Opened virtual DMA device: {self.device_path}")
            return True
        except OSError as e:
            self.logger.error(f"Failed to open device {self.device_path}: {e}")
            return False
    
    def close(self):
        """Close the virtual DMA device and cleanup regions"""
        if self.device_fd:
            # Remove all regions
            region_ids = list(self.regions.keys())
            for region_id in region_ids:
                self.remove_region(region_id)
            
            os.close(self.device_fd)
            self.device_fd = None
            self.logger.info("Closed virtual DMA device")
    
    def add_region(self, start_addr: int, size: int, remote_ip: str, remote_port: int) -> int:
        """Add a new DMA region"""
        if not self.device_fd:
            raise RuntimeError("Device not opened")
        
        with self.lock:
            region_id = self.next_region_id
            self.next_region_id += 1
            
            # Prepare region structure for kernel
            region_struct = struct.pack(
                'Q I 16s H',  # start_addr(8), size(4), remote_ip(16), remote_port(2)
                start_addr,
                size,
                remote_ip.encode('ascii')[:16].ljust(16, b'\0'),
                remote_port
            )
            
            # Send IOCTL to kernel driver
            try:
                fcntl.ioctl(self.device_fd, VDMA_ADD_REGION, region_struct)
            except OSError as e:
                self.logger.error(f"Failed to add DMA region: {e}")
                raise
            
            # Create user-space region
            region = DMARegion(
                start_addr=start_addr,
                size=size,
                remote_ip=remote_ip,
                remote_port=remote_port,
                active=True
            )
            
            self.regions[region_id] = region
            
            self.logger.info(f"Added DMA region {region_id}: 0x{start_addr:x}-0x{start_addr+size:x} -> {remote_ip}:{remote_port}")
            
            return region_id
    
    def remove_region(self, region_id: int) -> bool:
        """Remove a DMA region"""
        if not self.device_fd:
            raise RuntimeError("Device not opened")
        
        with self.lock:
            if region_id not in self.regions:
                return False
            
            region = self.regions[region_id]
            
            # Unmap memory if mapped
            if region.local_buffer:
                region.local_buffer.close()
                region.local_buffer = None
            
            # Send IOCTL to kernel driver
            try:
                addr_struct = struct.pack('Q', region.start_addr)
                fcntl.ioctl(self.device_fd, VDMA_REMOVE_REGION, addr_struct)
            except OSError as e:
                self.logger.error(f"Failed to remove DMA region: {e}")
                return False
            
            del self.regions[region_id]
            
            self.logger.info(f"Removed DMA region {region_id}")
            return True
    
    def map_region(self, region_id: int) -> mmap.mmap:
        """Map a DMA region to user space memory"""
        if not self.device_fd:
            raise RuntimeError("Device not opened")
        
        with self.lock:
            if region_id not in self.regions:
                raise ValueError(f"Region {region_id} not found")
            
            region = self.regions[region_id]
            
            if region.local_buffer:
                return region.local_buffer
            
            # Map the region using mmap
            try:
                # Calculate offset for mmap (page-aligned)
                page_size = mmap.PAGESIZE
                offset = region.start_addr & ~(page_size - 1)
                mmap_offset = region.start_addr - offset
                
                region.local_buffer = mmap.mmap(
                    self.device_fd,
                    region.size,
                    offset=offset
                )
                
                # Seek to the correct offset within the mapped region
                if mmap_offset > 0:
                    region.local_buffer.seek(mmap_offset)
                
                self.logger.info(f"Mapped DMA region {region_id} to user space")
                return region.local_buffer
                
            except OSError as e:
                self.logger.error(f"Failed to map DMA region: {e}")
                raise
    
    def write_memory(self, region_id: int, offset: int, data: bytes) -> int:
        """Write data to DMA region (triggers network transfer)"""
        region = self.map_region(region_id)
        
        with self.lock:
            try:
                region.seek(offset)
                region.write(data)
                region.flush()  # Ensure write goes through to driver
                return len(data)
            except Exception as e:
                self.logger.error(f"Write failed: {e}")
                raise
    
    def read_memory(self, region_id: int, offset: int, size: int) -> bytes:
        """Read data from DMA region"""
        region = self.map_region(region_id)
        
        with self.lock:
            try:
                region.seek(offset)
                data = region.read(size)
                return data
            except Exception as e:
                self.logger.error(f"Read failed: {e}")
                raise
    
    def get_stats(self) -> DMAStats:
        """Get DMA statistics from kernel driver"""
        if not self.device_fd:
            raise RuntimeError("Device not opened")
        
        try:
            stats_buffer = bytearray(32)  # Size of vdma_stats struct
            fcntl.ioctl(self.device_fd, VDMA_GET_STATS, stats_buffer)
            
            # Unpack statistics
            stats = struct.unpack('Q Q Q I I', stats_buffer)
            
            return DMAStats(
                bytes_transferred=stats[0],
                packets_sent=stats[1],
                packets_dropped=stats[2],
                active_regions=stats[3],
                pending_operations=stats[4]
            )
            
        except OSError as e:
            self.logger.error(f"Failed to get stats: {e}")
            raise
    
    def configure(self, config: DMAConfig):
        """Configure the virtual DMA controller"""
        if not self.device_fd:
            raise RuntimeError("Device not opened")
        
        config_struct = struct.pack('B I I', config.debug_mode, config.timeout_ms, config.max_retries)
        
        try:
            fcntl.ioctl(self.device_fd, VDMA_CONFIG, config_struct)
            self.logger.info("Updated DMA configuration")
        except OSError as e:
            self.logger.error(f"Failed to configure DMA: {e}")
            raise
    
    def benchmark_throughput(self, region_id: int, iterations: int = 1000, block_size: int = 4096):
        """Benchmark DMA throughput"""
        self.logger.info(f"Starting DMA throughput benchmark: {iterations} iterations, {block_size} byte blocks")
        
        # Prepare test data
        test_data = b'A' * block_size
        
        start_time = time.time()
        total_bytes = 0
        
        for i in range(iterations):
            try:
                bytes_written = self.write_memory(region_id, i * block_size, test_data)
                total_bytes += bytes_written
                
                if (i + 1) % 100 == 0:
                    self.logger.info(f"Completed {i + 1}/{iterations} iterations")
                    
            except Exception as e:
                self.logger.error(f"Iteration {i} failed: {e}")
                break
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        if elapsed_time > 0:
            throughput_mbps = (total_bytes / elapsed_time) / (1024 * 1024)
            self.logger.info(f"Benchmark Results:")
            self.logger.info(f"  Total bytes: {total_bytes:,}")
            self.logger.info(f"  Elapsed time: {elapsed_time:.2f}s")
            self.logger.info(f"  Throughput: {throughput_mbps:.2f} MB/s")
            self.logger.info(f"  Average latency: {(elapsed_time / iterations) * 1000:.2f}ms")
        
        # Get final statistics
        stats = self.get_stats()
        self.logger.info(f"Driver Statistics:")
        self.logger.info(f"  Packets sent: {stats.packets_sent:,}")
        self.logger.info(f"  Packets dropped: {stats.packets_dropped:,}")
        self.logger.info(f"  Bytes transferred: {stats.bytes_transferred:,}")
        
        return throughput_mbps


class RemoteDMAReceiver:
    """Remote service that receives and writes DMA packets"""
    
    def __init__(self, listen_port: int = 9999, buffer_size: int = 1024*1024*1024):
        self.listen_port = listen_port
        self.buffer_size = buffer_size
        self.memory_regions = {}
        self.running = False
        self.socket = None
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def add_memory_region(self, start_addr: int, size: int):
        """Add a memory region to receive data"""
        self.memory_regions[start_addr] = bytearray(size)
        self.logger.info(f"Added memory region: 0x{start_addr:x}-0x{start_addr+size:x}")
    
    def start(self):
        """Start the remote DMA receiver"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('0.0.0.0', self.listen_port))
        self.socket.settimeout(1.0)  # Non-blocking with timeout
        
        self.running = True
        self.logger.info(f"Remote DMA Receiver started on port {self.listen_port}")
        
        try:
            while self.running:
                try:
                    data, addr = self.socket.recvfrom(2048)  # Max packet size
                    
                    # Parse DMA packet
                    if len(data) >= 12:  # Minimum header size
                        self.handle_dma_packet(data, addr)
                    
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        self.logger.error(f"Receive error: {e}")
        finally:
            self.stop()
    
    def handle_dma_packet(self, data: bytes, addr: Tuple[str, int]):
        """Handle incoming DMA packet"""
        try:
            # Parse packet header
            sequence, address, size = struct.unpack('!III', data[:12])
            packet_data = data[12:12+size]
            
            # Find target memory region
            target_region = None
            for region_start, region_data in self.memory_regions.items():
                if region_start <= address < region_start + len(region_data):
                    target_region = region_data
                    offset = address - region_start
                    break
            
            if target_region:
                # Write data to memory region
                target_region[offset:offset+len(packet_data)] = packet_data
                self.logger.debug(f"Wrote {len(packet_data)} bytes to 0x{address:x} from {addr}")
            else:
                self.logger.warning(f"No memory region for address 0x{address:x}")
                
        except Exception as e:
            self.logger.error(f"Packet handling error: {e}")
    
    def stop(self):
        """Stop the remote DMA receiver"""
        self.running = False
        if self.socket:
            self.socket.close()
        self.logger.info("Remote DMA Receiver stopped")
    
    def get_memory_data(self, start_addr: int, size: int) -> bytes:
        """Get data from a memory region"""
        for region_start, region_data in self.memory_regions.items():
            if region_start <= start_addr < region_start + len(region_data):
                offset = start_addr - region_start
                return bytes(region_data[offset:offset+size])
        
        raise ValueError(f"No memory region for address 0x{start_addr:x}")


def demo_virtual_dma():
    """Demonstration of virtual DMA controller"""
    print("Virtual DMA Controller Demo")
    print("=" * 40)
    
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python virtual_dma_userspace.py [controller|receiver] [options]")
        sys.exit(1)
    
    mode = sys.argv[1]
    
    if mode == "controller":
        # Virtual DMA controller (client side)
        controller = VirtualDMAController()
        
        if not controller.open():
            print("Failed to open virtual DMA device")
            print("Make sure the kernel driver is loaded:")
            print("  sudo insmod virtual_dma_driver.ko")
            print("  sudo chmod 666 /dev/virtual_dma")
            sys.exit(1)
        
        try:
            # Configure controller
            config = DMAConfig(debug_mode=True, timeout_ms=1000)
            controller.configure(config)
            
            # Add DMA region
            region_id = controller.add_region(
                start_addr=0x10000000,  # 256MB base address
                size=1024*1024,         # 1MB region
                remote_ip="127.0.0.1",
                remote_port=9999
            )
            
            print(f"Added DMA region {region_id}")
            
            # Test write operations
            test_data = b"Virtual DMA Test Data!" * 100
            bytes_written = controller.write_memory(region_id, 0, test_data)
            print(f"Wrote {bytes_written} bytes to DMA region")
            
            # Test read operations
            read_data = controller.read_memory(region_id, 0, len(test_data))
            print(f"Read {len(read_data)} bytes from DMA region")
            
            if read_data == test_data:
                print("✓ Data integrity verified")
            else:
                print("✗ Data integrity check failed")
            
            # Benchmark
            print("\nRunning throughput benchmark...")
            controller.benchmark_throughput(region_id, iterations=500, block_size=4096)
            
            # Get statistics
            stats = controller.get_stats()
            print(f"\nFinal Statistics:")
            print(f"  Active regions: {stats.active_regions}")
            print(f"  Packets sent: {stats.packets_sent}")
            print(f"  Packets dropped: {stats.packets_dropped}")
            print(f"  Bytes transferred: {stats.bytes_transferred}")
            
        finally:
            controller.close()
    
    elif mode == "receiver":
        # Remote DMA receiver (server side)
        receiver = RemoteDMAReceiver(listen_port=9999)
        
        # Add memory region to receive data
        receiver.add_memory_region(0x10000000, 1024*1024)
        
        print("Starting remote DMA receiver...")
        print("Press Ctrl+C to stop")
        
        try:
            receiver.start()
        except KeyboardInterrupt:
            print("\nStopping receiver...")
            receiver.stop()
    
    else:
        print("Unknown mode. Use 'controller' or 'receiver'")


if __name__ == "__main__":
    demo_virtual_dma()
