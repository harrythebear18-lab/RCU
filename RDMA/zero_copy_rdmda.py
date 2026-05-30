#!/usr/bin/env python3
"""
Software-Defined RDMA: Zero-Copy Memory Sharing
Safe alternative to physical DMA cards using ZeroMQ
"""

import zmq
import numpy as np
import mmap
import os
import time
import threading
from typing import Optional, Callable
import logging

class ZeroCopyRDMAServer:
    """Server side - exposes memory regions over network"""
    
    def __init__(self, port: int = 5555, buffer_size: int = 1024*1024):
        self.port = port
        self.buffer_size = buffer_size
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.memory_regions = {}
        self.running = False
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def create_shared_memory_region(self, name: str, size: int) -> np.ndarray:
        """Create a shared memory region that can be accessed remotely"""
        # Create shared memory using numpy memmap
        filename = f"/tmp/rdma_{name}_{os.getpid()}"
        
        try:
            # Create file-backed memory map
            with open(filename, 'wb') as f:
                f.truncate(size)
            
            # Memory map the file
            mem_map = mmap.mmap(f.fileno(), 0)
            array = np.frombuffer(mem_map, dtype=np.uint8)
            
            self.memory_regions[name] = {
                'array': array,
                'mmap': mem_map,
                'filename': filename,
                'size': size
            }
            
            self.logger.info(f"Created memory region '{name}' of size {size} bytes")
            return array
            
        except Exception as e:
            self.logger.error(f"Failed to create memory region: {e}")
            raise
    
    def start_server(self):
        """Start the RDMA server"""
        self.socket.bind(f"tcp://*:{self.port}")
        self.running = True
        self.logger.info(f"RDMA Server started on port {self.port}")
        
        while self.running:
            try:
                # Wait for requests
                request = self.socket.recv_json()
                response = self.handle_request(request)
                self.socket.send_json(response)
                
            except zmq.ZMQError as e:
                if self.running:
                    self.logger.error(f"ZMQ Error: {e}")
                break
    
    def handle_request(self, request: dict) -> dict:
        """Handle incoming RDMA requests"""
        cmd = request.get('cmd')
        region = request.get('region')
        
        if cmd == 'read':
            return self.handle_read_request(region, request.get('offset', 0), request.get('size', 1024))
        elif cmd == 'write':
            return self.handle_write_request(region, request.get('offset', 0), request.get('data'))
        elif cmd == 'list_regions':
            return {'status': 'ok', 'regions': list(self.memory_regions.keys())}
        else:
            return {'status': 'error', 'message': f'Unknown command: {cmd}'}
    
    def handle_read_request(self, region: str, offset: int, size: int) -> dict:
        """Handle read requests from remote clients"""
        if region not in self.memory_regions:
            return {'status': 'error', 'message': f'Region {region} not found'}
        
        mem_region = self.memory_regions[region]
        if offset + size > mem_region['size']:
            return {'status': 'error', 'message': 'Read beyond region bounds'}
        
        data = mem_region['array'][offset:offset+size].tobytes()
        return {
            'status': 'ok',
            'data': data.hex(),  # Send as hex for JSON compatibility
            'size': len(data)
        }
    
    def handle_write_request(self, region: str, offset: int, data_hex: str) -> dict:
        """Handle write requests from remote clients"""
        if region not in self.memory_regions:
            return {'status': 'error', 'message': f'Region {region} not found'}
        
        mem_region = self.memory_regions[region]
        data = bytes.fromhex(data_hex)
        
        if offset + len(data) > mem_region['size']:
            return {'status': 'error', 'message': 'Write beyond region bounds'}
        
        mem_region['array'][offset:offset+len(data)] = np.frombuffer(data, dtype=np.uint8)
        return {'status': 'ok', 'bytes_written': len(data)}
    
    def stop(self):
        """Stop the server and cleanup"""
        self.running = False
        
        # Close socket
        self.socket.close()
        self.context.term()
        
        # Cleanup memory regions
        for region in self.memory_regions.values():
            region['mmap'].close()
            try:
                os.unlink(region['filename'])
            except:
                pass
        
        self.logger.info("RDMA Server stopped")


class ZeroCopyRDMAClient:
    """Client side - accesses remote memory regions"""
    
    def __init__(self, server_host: str = "localhost", port: int = 5555):
        self.server_host = server_host
        self.port = port
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect(f"tcp://{server_host}:{port}")
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def read_memory(self, region: str, offset: int, size: int) -> bytes:
        """Read memory from remote server"""
        request = {
            'cmd': 'read',
            'region': region,
            'offset': offset,
            'size': size
        }
        
        self.socket.send_json(request)
        response = self.socket.recv_json()
        
        if response['status'] == 'ok':
            return bytes.fromhex(response['data'])
        else:
            raise Exception(f"Read failed: {response['message']}")
    
    def write_memory(self, region: str, offset: int, data: bytes) -> int:
        """Write memory to remote server"""
        request = {
            'cmd': 'write',
            'region': region,
            'offset': offset,
            'data': data.hex()
        }
        
        self.socket.send_json(request)
        response = self.socket.recv_json()
        
        if response['status'] == 'ok':
            return response['bytes_written']
        else:
            raise Exception(f"Write failed: {response['message']}")
    
    def list_regions(self) -> list:
        """List available memory regions on server"""
        request = {'cmd': 'list_regions'}
        self.socket.send_json(request)
        response = self.socket.recv_json()
        
        if response['status'] == 'ok':
            return response['regions']
        else:
            raise Exception(f"List failed: {response['message']}")
    
    def close(self):
        """Close client connection"""
        self.socket.close()
        self.context.term()


def benchmark_performance(server: ZeroCopyRDMAServer, client: ZeroCopyRDMAClient):
    """Benchmark the performance of the RDMA system"""
    print("Starting performance benchmark...")
    
    # Create test region
    test_data = np.random.randint(0, 256, 1024*1024, dtype=np.uint8)
    server.create_shared_memory_region("benchmark", len(test_data))
    
    # Write test data
    start_time = time.time()
    client.write_memory("benchmark", 0, test_data.tobytes())
    write_time = time.time() - start_time
    
    # Read test data
    start_time = time.time()
    read_data = client.read_memory("benchmark", 0, len(test_data))
    read_time = time.time() - start_time
    
    # Verify data integrity
    if np.array_equal(test_data, np.frombuffer(read_data, dtype=np.uint8)):
        print(f"✓ Data integrity verified")
    else:
        print("✗ Data integrity check failed")
    
    print(f"Write throughput: {len(test_data) / write_time / 1024 / 1024:.2f} MB/s")
    print(f"Read throughput: {len(test_data) / read_time / 1024 / 1024:.2f} MB/s")


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python zero_copy_rdmda.py [server|client|benchmark]")
        sys.exit(1)
    
    mode = sys.argv[1]
    
    if mode == "server":
        server = ZeroCopyRDMAServer()
        
        # Create some test memory regions
        server.create_shared_memory_region("test_buffer", 1024*1024)
        server.create_shared_memory_region("game_memory", 16*1024*1024)
        
        try:
            server.start_server()
        except KeyboardInterrupt:
            print("\nShutting down server...")
            server.stop()
    
    elif mode == "client":
        client = ZeroCopyRDMAClient()
        
        try:
            regions = client.list_regions()
            print(f"Available regions: {regions}")
            
            if regions:
                # Test reading
                data = client.read_memory(regions[0], 0, 1024)
                print(f"Read {len(data)} bytes from {regions[0]}")
                
                # Test writing
                test_data = b"Hello, Software-Defined RDMA!"
                bytes_written = client.write_memory(regions[0], 0, test_data)
                print(f"Wrote {bytes_written} bytes to {regions[0]}")
        
        finally:
            client.close()
    
    elif mode == "benchmark":
        server = ZeroCopyRDMAServer()
        client = ZeroCopyRDMAClient()
        
        # Start server in background thread
        server_thread = threading.Thread(target=server.start_server)
        server_thread.daemon = True
        server_thread.start()
        
        # Give server time to start
        time.sleep(0.5)
        
        try:
            benchmark_performance(server, client)
        finally:
            server.stop()
    
    else:
        print("Unknown mode. Use 'server', 'client', or 'benchmark'")
