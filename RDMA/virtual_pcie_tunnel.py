#!/usr/bin/env python3
"""
Virtual PCIe Tunnel: Network-based Memory Access
Safe alternative to physical DMA cards for cross-system debugging
"""

import socket
import struct
import json
import threading
import time
import logging
from typing import Dict, Optional, Tuple
import psutil
import os

class VirtualPCIEDriver:
    """Target side: Exposes memory access over network socket"""
    
    def __init__(self, port: int = 7777):
        self.port = port
        self.server_socket = None
        self.client_connections = []
        self.running = False
        self.allowed_pids = set()  # Whitelist of accessible PIDs
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def add_allowed_pid(self, pid: int):
        """Add a PID to the whitelist of accessible processes"""
        self.allowed_pids.add(pid)
        self.logger.info(f"Added PID {pid} to whitelist")
    
    def remove_allowed_pid(self, pid: int):
        """Remove a PID from the whitelist"""
        self.allowed_pids.discard(pid)
        self.logger.info(f"Removed PID {pid} from whitelist")
    
    def start_server(self):
        """Start the virtual PCIe server"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(('0.0.0.0', self.port))
        self.server_socket.listen(5)
        
        self.running = True
        self.logger.info(f"Virtual PCIe Driver started on port {self.port}")
        
        try:
            while self.running:
                client_socket, addr = self.server_socket.accept()
                self.logger.info(f"New connection from {addr}")
                
                # Handle client in separate thread
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, addr)
                )
                client_thread.daemon = True
                client_thread.start()
                
        except Exception as e:
            if self.running:
                self.logger.error(f"Server error: {e}")
        finally:
            self.stop()
    
    def handle_client(self, client_socket: socket.socket, addr: Tuple[str, int]):
        """Handle individual client connections"""
        self.client_connections.append(client_socket)
        
        try:
            while self.running:
                # Receive request header (4 bytes for length)
                header_data = client_socket.recv(4)
                if not header_data:
                    break
                
                msg_length = struct.unpack('!I', header_data)[0]
                request_data = client_socket.recv(msg_length)
                
                if not request_data:
                    break
                
                # Parse and handle request
                try:
                    request = json.loads(request_data.decode('utf-8'))
                    response = self.process_request(request)
                except json.JSONDecodeError:
                    response = {
                        'status': 'error',
                        'message': 'Invalid JSON format'
                    }
                except Exception as e:
                    response = {
                        'status': 'error', 
                        'message': str(e)
                    }
                
                # Send response
                response_data = json.dumps(response).encode('utf-8')
                response_header = struct.pack('!I', len(response_data))
                client_socket.send(response_header + response_data)
                
        except Exception as e:
            self.logger.error(f"Client handler error: {e}")
        finally:
            client_socket.close()
            self.client_connections.remove(client_socket)
            self.logger.info(f"Client {addr} disconnected")
    
    def process_request(self, request: dict) -> dict:
        """Process memory access requests"""
        cmd = request.get('cmd')
        pid = request.get('pid')
        
        if not pid or pid not in self.allowed_pids:
            return {
                'status': 'error',
                'message': f'PID {pid} not authorized for memory access'
            }
        
        try:
            if cmd == 'read_memory':
                return self.handle_read_memory(pid, request.get('address'), request.get('size'))
            elif cmd == 'write_memory':
                return self.handle_write_memory(pid, request.get('address'), request.get('data'))
            elif cmd == 'get_process_info':
                return self.handle_get_process_info(pid)
            elif cmd == 'list_processes':
                return self.handle_list_processes()
            else:
                return {'status': 'error', 'message': f'Unknown command: {cmd}'}
                
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def handle_read_memory(self, pid: int, address: int, size: int) -> dict:
        """Read memory from target process"""
        try:
            # On Windows, we'd use ReadProcessMemory via ctypes
            # On Linux, we can read from /proc/[pid]/mem
            if os.name == 'nt':  # Windows
                return self._read_memory_windows(pid, address, size)
            else:  # Linux/Unix
                return self._read_memory_linux(pid, address, size)
                
        except Exception as e:
            return {'status': 'error', 'message': f'Memory read failed: {e}'}
    
    def _read_memory_windows(self, pid: int, address: int, size: int) -> dict:
        """Windows memory reading using ReadProcessMemory"""
        try:
            import ctypes
            from ctypes import wintypes
            
            # Windows API setup
            kernel32 = ctypes.windll.kernel32
            PROCESS_VM_READ = 0x0010
            
            # Open process handle
            process_handle = kernel32.OpenProcess(PROCESS_VM_READ, False, pid)
            if not process_handle:
                return {'status': 'error', 'message': 'Failed to open process'}
            
            # Allocate buffer
            buffer = ctypes.create_string_buffer(size)
            bytes_read = ctypes.c_size_t()
            
            # Read memory
            success = kernel32.ReadProcessMemory(
                process_handle,
                ctypes.c_void_p(address),
                buffer,
                size,
                ctypes.byref(bytes_read)
            )
            
            kernel32.CloseHandle(process_handle)
            
            if success:
                return {
                    'status': 'ok',
                    'data': buffer.raw.hex(),
                    'bytes_read': bytes_read.value
                }
            else:
                return {'status': 'error', 'message': 'ReadProcessMemory failed'}
                
        except ImportError:
            return {'status': 'error', 'message': 'Windows API not available'}
    
    def _read_memory_linux(self, pid: int, address: int, size: int) -> dict:
        """Linux memory reading via /proc/[pid]/mem"""
        try:
            mem_file = f"/proc/{pid}/mem"
            with open(mem_file, 'rb') as f:
                f.seek(address)
                data = f.read(size)
                return {
                    'status': 'ok',
                    'data': data.hex(),
                    'bytes_read': len(data)
                }
        except Exception as e:
            return {'status': 'error', 'message': f'Linux memory read failed: {e}'}
    
    def handle_write_memory(self, pid: int, address: int, data_hex: str) -> dict:
        """Write memory to target process (dangerous, requires explicit approval)"""
        # Memory writing is inherently dangerous - implement with caution
        return {
            'status': 'error',
            'message': 'Memory writing disabled for safety'
        }
    
    def handle_get_process_info(self, pid: int) -> dict:
        """Get information about a process"""
        try:
            process = psutil.Process(pid)
            return {
                'status': 'ok',
                'info': {
                    'pid': pid,
                    'name': process.name(),
                    'memory_info': process.memory_info()._asdict(),
                    'cpu_percent': process.cpu_percent(),
                    'status': process.status()
                }
            }
        except psutil.NoSuchProcess:
            return {'status': 'error', 'message': f'Process {pid} not found'}
    
    def handle_list_processes(self) -> dict:
        """List all accessible processes"""
        processes = []
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                processes.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name']
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return {
            'status': 'ok',
            'processes': processes
        }
    
    def stop(self):
        """Stop the server and cleanup"""
        self.running = False
        
        # Close all client connections
        for client_socket in self.client_connections:
            try:
                client_socket.close()
            except:
                pass
        
        # Close server socket
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        
        self.logger.info("Virtual PCIe Driver stopped")


class VirtualPCIEClient:
    """Controller side: Accesses remote memory over network"""
    
    def __init__(self, target_host: str, port: int = 7777):
        self.target_host = target_host
        self.port = port
        self.socket = None
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def connect(self):
        """Connect to target system"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.target_host, self.port))
            self.logger.info(f"Connected to {self.target_host}:{self.port}")
            return True
        except Exception as e:
            self.logger.error(f"Connection failed: {e}")
            return False
    
    def send_request(self, request: dict) -> dict:
        """Send request to target and get response"""
        if not self.socket:
            raise Exception("Not connected to target")
        
        try:
            # Send request
            request_data = json.dumps(request).encode('utf-8')
            header = struct.pack('!I', len(request_data))
            self.socket.send(header + request_data)
            
            # Receive response
            response_header = self.socket.recv(4)
            response_length = struct.unpack('!I', response_header)[0]
            response_data = self.socket.recv(response_length)
            
            return json.loads(response_data.decode('utf-8'))
            
        except Exception as e:
            self.logger.error(f"Request failed: {e}")
            raise
    
    def read_memory(self, pid: int, address: int, size: int) -> bytes:
        """Read memory from remote process"""
        request = {
            'cmd': 'read_memory',
            'pid': pid,
            'address': address,
            'size': size
        }
        
        response = self.send_request(request)
        
        if response['status'] == 'ok':
            return bytes.fromhex(response['data'])
        else:
            raise Exception(f"Memory read failed: {response['message']}")
    
    def get_process_info(self, pid: int) -> dict:
        """Get information about remote process"""
        request = {
            'cmd': 'get_process_info',
            'pid': pid
        }
        
        response = self.send_request(request)
        
        if response['status'] == 'ok':
            return response['info']
        else:
            raise Exception(f"Get process info failed: {response['message']}")
    
    def list_processes(self) -> list:
        """List processes on target system"""
        request = {'cmd': 'list_processes'}
        response = self.send_request(request)
        
        if response['status'] == 'ok':
            return response['processes']
        else:
            raise Exception(f"List processes failed: {response['message']}")
    
    def disconnect(self):
        """Disconnect from target"""
        if self.socket:
            self.socket.close()
            self.socket = None
            self.logger.info("Disconnected from target")


def demo_usage():
    """Demonstration of Virtual PCIe Tunnel usage"""
    print("Virtual PCIe Tunnel Demo")
    print("=" * 40)
    
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python virtual_pcie_tunnel.py [target|controller] [host]")
        sys.exit(1)
    
    mode = sys.argv[1]
    
    if mode == "target":
        # Target system - run the driver
        driver = VirtualPCIEDriver()
        
        # Add some example PIDs (in real usage, you'd add the actual game/research process)
        print("Starting Virtual PCIe Driver...")
        print("Add PIDs with: driver.add_allowed_pid(pid)")
        print("Available processes:")
        
        # List current processes
        try:
            for proc in psutil.process_iter(['pid', 'name'])[:10]:
                print(f"  PID {proc.info['pid']}: {proc.info['name']}")
        except:
            pass
        
        try:
            driver.start_server()
        except KeyboardInterrupt:
            print("\nShutting down driver...")
            driver.stop()
    
    elif mode == "controller":
        if len(sys.argv) < 3:
            print("Usage: python virtual_pcie_tunnel.py controller <target_host>")
            sys.exit(1)
        
        target_host = sys.argv[2]
        client = VirtualPCIEClient(target_host)
        
        if client.connect():
            try:
                # List processes
                print("Available processes on target:")
                processes = client.list_processes()
                for proc in processes[:10]:  # Show first 10
                    print(f"  PID {proc['pid']}: {proc['name']}")
                
                # Example: Try to read from first process (if authorized)
                if processes:
                    pid = processes[0]['pid']
                    print(f"\nTrying to read from PID {pid}...")
                    
                    try:
                        data = client.read_memory(pid, 0x1000, 1024)  # Read 1KB from address 0x1000
                        print(f"Successfully read {len(data)} bytes")
                        print(f"First 32 bytes: {data[:32].hex()}")
                    except Exception as e:
                        print(f"Read failed (expected if PID not authorized): {e}")
                
            finally:
                client.disconnect()
    
    else:
        print("Unknown mode. Use 'target' or 'controller'")


if __name__ == "__main__":
    demo_usage()
