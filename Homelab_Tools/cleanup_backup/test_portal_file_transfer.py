#!/usr/bin/env python3
"""
Test File Transfer for Homelab Portal
Test file transfer performance between Intel+NVIDIA+DDR4 systems
"""

import time
import os
import hashlib
import socket
import threading
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
import psutil

class PortalFileTransferTest:
    """Test file transfer between identical hardware systems"""
    
    def __init__(self):
        self.logger = logging.getLogger("PortalFileTransferTest")
        self.test_results = {}
        self.test_files = {}
        
    def create_test_files(self) -> Dict[str, str]:
        """Create test files of various sizes"""
        test_files = {}
        
        try:
            # Create test directory
            test_dir = Path("test_files")
            test_dir.mkdir(exist_ok=True)
            
            # File sizes to test (in MB)
            test_sizes = [1, 10, 50, 100, 500]  # 1MB, 10MB, 50MB, 100MB, 500MB
            
            for size_mb in test_sizes:
                filename = f"test_file_{size_mb}mb.dat"
                filepath = test_dir / filename
                
                # Create file with random data
                if not filepath.exists():
                    self.logger.info(f"Creating test file: {filename} ({size_mb}MB)")
                    
                    # Generate test data pattern
                    data = bytearray(size_mb * 1024 * 1024)
                    
                    # Fill with pattern that's good for testing
                    for i in range(0, len(data), 1024):
                        pattern = i % 256
                        data[i:i+1024] = bytes([pattern] * min(1024, len(data) - i))
                    
                    # Write file
                    with open(filepath, 'wb') as f:
                        f.write(data)
                
                # Calculate checksum
                with open(filepath, 'rb') as f:
                    file_hash = hashlib.sha256(f.read()).hexdigest()
                
                test_files[filename] = {
                    'path': str(filepath),
                    'size_mb': size_mb,
                    'size_bytes': size_mb * 1024 * 1024,
                    'hash': file_hash
                }
            
            self.test_files = test_files
            return test_files
            
        except Exception as e:
            self.logger.error(f"Failed to create test files: {e}")
            return {}
    
    def test_local_file_transfer(self) -> Dict[str, Any]:
        """Test local file transfer performance"""
        try:
            results = {
                'test_type': 'local_file_transfer',
                'files_tested': len(self.test_files),
                'results': {}
            }
            
            for filename, file_info in self.test_files.items():
                self.logger.info(f"Testing local transfer: {filename}")
                
                # Test copy performance
                copy_result = self._test_file_copy(file_info)
                
                # Test read performance
                read_result = self._test_file_read(file_info)
                
                # Test write performance
                write_result = self._test_file_write(file_info)
                
                results['results'][filename] = {
                    'size_mb': file_info['size_mb'],
                    'copy': copy_result,
                    'read': read_result,
                    'write': write_result
                }
            
            return results
            
        except Exception as e:
            self.logger.error(f"Local file transfer test failed: {e}")
            return {'error': str(e)}
    
    def _test_file_copy(self, file_info: Dict[str, Any]) -> Dict[str, Any]:
        """Test file copy performance"""
        try:
            source_path = file_info['path']
            dest_path = source_path + ".copy"
            
            start_time = time.time()
            
            # Copy file
            with open(source_path, 'rb') as src:
                with open(dest_path, 'wb') as dst:
                    while True:
                        chunk = src.read(1024 * 1024)  # 1MB chunks
                        if not chunk:
                            break
                        dst.write(chunk)
            
            end_time = time.time()
            
            # Verify checksum
            with open(dest_path, 'rb') as f:
                dest_hash = hashlib.sha256(f.read()).hexdigest()
            
            # Calculate performance
            transfer_time = end_time - start_time
            file_size = file_info['size_bytes']
            throughput_mbps = (file_size / (1024 * 1024)) / transfer_time
            
            # Clean up
            os.remove(dest_path)
            
            return {
                'transfer_time_seconds': transfer_time,
                'throughput_mbps': throughput_mbps,
                'integrity_check': dest_hash == file_info['hash'],
                'chunk_size_mb': 1
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _test_file_read(self, file_info: Dict[str, Any]) -> Dict[str, Any]:
        """Test file read performance"""
        try:
            source_path = file_info['path']
            
            start_time = time.time()
            
            # Read file
            total_read = 0
            with open(source_path, 'rb') as f:
                while True:
                    chunk = f.read(1024 * 1024)  # 1MB chunks
                    if not chunk:
                        break
                    total_read += len(chunk)
            
            end_time = time.time()
            
            # Calculate performance
            read_time = end_time - start_time
            file_size = file_info['size_bytes']
            read_mbps = (file_size / (1024 * 1024)) / read_time
            
            return {
                'read_time_seconds': read_time,
                'read_mbps': read_mbps,
                'bytes_read': total_read,
                'chunk_size_mb': 1
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _test_file_write(self, file_info: Dict[str, Any]) -> Dict[str, Any]:
        """Test file write performance"""
        try:
            test_path = file_info['path'] + ".write"
            file_size = file_info['size_bytes']
            
            start_time = time.time()
            
            # Write file
            with open(test_path, 'wb') as f:
                remaining = file_size
                while remaining > 0:
                    chunk_size = min(1024 * 1024, remaining)  # 1MB chunks
                    chunk = b'\x00' * chunk_size
                    f.write(chunk)
                    remaining -= chunk_size
            
            end_time = time.time()
            
            # Calculate performance
            write_time = end_time - start_time
            write_mbps = (file_size / (1024 * 1024)) / write_time
            
            # Clean up
            os.remove(test_path)
            
            return {
                'write_time_seconds': write_time,
                'write_mbps': write_mbps,
                'bytes_written': file_size,
                'chunk_size_mb': 1
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def test_network_file_transfer(self, target_ip: str, target_port: int = 30000) -> Dict[str, Any]:
        """Test network file transfer to target system"""
        try:
            results = {
                'test_type': 'network_file_transfer',
                'target_ip': target_ip,
                'target_port': target_port,
                'files_tested': len(self.test_files),
                'results': {}
            }
            
            # Test connection
            if not self._test_connection(target_ip, target_port):
                return {'error': f'Cannot connect to {target_ip}:{target_port}'}
            
            for filename, file_info in self.test_files.items():
                self.logger.info(f"Testing network transfer: {filename} to {target_ip}")
                
                # Test network transfer
                transfer_result = self._test_network_transfer(file_info, target_ip, target_port)
                
                results['results'][filename] = {
                    'size_mb': file_info['size_mb'],
                    'network_transfer': transfer_result
                }
            
            return results
            
        except Exception as e:
            self.logger.error(f"Network file transfer test failed: {e}")
            return {'error': str(e)}
    
    def _test_connection(self, target_ip: str, target_port: int) -> bool:
        """Test connection to target system"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5.0)
            
            result = sock.connect_ex((target_ip, target_port))
            sock.close()
            
            return result == 0
            
        except Exception:
            return False
    
    def _test_network_transfer(self, file_info: Dict[str, Any], target_ip: str, target_port: int) -> Dict[str, Any]:
        """Test network file transfer"""
        try:
            source_path = file_info['path']
            file_size = file_info['size_bytes']
            
            # Connect to target
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(30.0)
            sock.connect((target_ip, target_port))
            
            # Send file transfer request
            request = {
                'type': 'file_transfer',
                'filename': os.path.basename(source_path),
                'file_size': file_size,
                'file_hash': file_info['hash']
            }
            
            sock.send(json.dumps(request).encode('utf-8') + b'\n')
            
            # Wait for acknowledgment
            ack = sock.recv(1024)
            if not ack.startswith(b'OK'):
                sock.close()
                return {'error': 'Target rejected file transfer'}
            
            # Send file data
            start_time = time.time()
            
            with open(source_path, 'rb') as f:
                while True:
                    chunk = f.read(1024 * 1024)  # 1MB chunks
                    if not chunk:
                        break
                    sock.sendall(chunk)
            
            # Wait for completion confirmation
            response = sock.recv(1024)
            end_time = time.time()
            
            sock.close()
            
            # Calculate performance
            transfer_time = end_time - start_time
            throughput_mbps = (file_size / (1024 * 1024)) / transfer_time
            
            return {
                'transfer_time_seconds': transfer_time,
                'throughput_mbps': throughput_mbps,
                'bytes_transferred': file_size,
                'chunk_size_mb': 1,
                'response': response.decode('utf-8', errors='ignore')
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def test_concurrent_transfers(self, target_ip: str, target_port: int = 30000) -> Dict[str, Any]:
        """Test concurrent file transfers"""
        try:
            results = {
                'test_type': 'concurrent_file_transfer',
                'target_ip': target_ip,
                'target_port': target_port,
                'concurrent_files': 3,
                'results': {}
            }
            
            # Select 3 files for concurrent test
            test_files = list(self.test_files.values())[:3]
            
            # Create threads for concurrent transfers
            threads = []
            thread_results = {}
            
            def transfer_file(file_info, index):
                try:
                    result = self._test_network_transfer(file_info, target_ip, target_port)
                    thread_results[index] = result
                except Exception as e:
                    thread_results[index] = {'error': str(e)}
            
            # Start transfers
            start_time = time.time()
            
            for i, file_info in enumerate(test_files):
                thread = threading.Thread(target=transfer_file, args=(file_info, i))
                threads.append(thread)
                thread.start()
            
            # Wait for completion
            for thread in threads:
                thread.join()
            
            end_time = time.time()
            
            # Calculate overall performance
            total_size = sum(f['size_bytes'] for f in test_files)
            total_time = end_time - start_time
            overall_throughput = (total_size / (1024 * 1024)) / total_time
            
            results['overall'] = {
                'total_time_seconds': total_time,
                'total_size_mb': total_size / (1024 * 1024),
                'overall_throughput_mbps': overall_throughput,
                'concurrent_transfers': len(test_files)
            }
            
            results['individual'] = thread_results
            
            return results
            
        except Exception as e:
            self.logger.error(f"Concurrent transfer test failed: {e}")
            return {'error': str(e)}
    
    def test_ethernet_optimization(self) -> Dict[str, Any]:
        """Test Ethernet optimization effects"""
        try:
            results = {
                'test_type': 'ethernet_optimization',
                'before_optimization': {},
                'after_optimization': {},
                'improvement': {}
            }
            
            # Test before optimization
            self.logger.info("Testing before Ethernet optimization...")
            before_results = self.test_local_file_transfer()
            results['before_optimization'] = before_results
            
            # Apply Ethernet optimizations
            self.logger.info("Applying Ethernet optimizations...")
            optimization_success = self._apply_ethernet_optimizations()
            
            if optimization_success:
                # Wait for optimizations to take effect
                time.sleep(2)
                
                # Test after optimization
                self.logger.info("Testing after Ethernet optimization...")
                after_results = self.test_local_file_transfer()
                results['after_optimization'] = after_results
                
                # Calculate improvement
                improvement = self._calculate_improvement(before_results, after_results)
                results['improvement'] = improvement
            else:
                results['error'] = 'Failed to apply Ethernet optimizations'
            
            return results
            
        except Exception as e:
            self.logger.error(f"Ethernet optimization test failed: {e}")
            return {'error': str(e)}
    
    def _apply_ethernet_optimizations(self) -> bool:
        """Apply Ethernet optimizations"""
        try:
            optimizations = [
                ('netsh int tcp set global autotuninglevel=restricted', 'TCP AutoTuning'),
                ('netsh int tcp set global chimney=enabled', 'TCP Chimney'),
                ('netsh int tcp set global rss=enabled', 'TCP RSS'),
                ('netsh int tcp set global netdma=enabled', 'TCP NetDMA')
            ]
            
            for command, description in optimizations:
                try:
                    subprocess.run(command.split(), capture_output=True, timeout=10)
                    self.logger.info(f"Applied optimization: {description}")
                except Exception as e:
                    self.logger.warning(f"Failed to apply {description}: {e}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to apply Ethernet optimizations: {e}")
            return False
    
    def _calculate_improvement(self, before: Dict[str, Any], after: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate performance improvement"""
        try:
            improvement = {}
            
            if 'results' in before and 'results' in after:
                for filename in before['results']:
                    if filename in after['results']:
                        before_file = before['results'][filename]
                        after_file = after['results'][filename]
                        
                        # Calculate copy improvement
                        if 'copy' in before_file and 'copy' in after_file:
                            before_throughput = before_file['copy'].get('throughput_mbps', 0)
                            after_throughput = after_file['copy'].get('throughput_mbps', 0)
                            
                            if before_throughput > 0:
                                copy_improvement = ((after_throughput - before_throughput) / before_throughput) * 100
                            else:
                                copy_improvement = 0
                            
                            improvement[filename] = {
                                'copy_improvement_percent': copy_improvement,
                                'before_mbps': before_throughput,
                                'after_mbps': after_throughput
                            }
            
            return improvement
            
        except Exception as e:
            self.logger.error(f"Failed to calculate improvement: {e}")
            return {}
    
    def run_comprehensive_test(self, target_ip: str = None) -> Dict[str, Any]:
        """Run comprehensive file transfer test"""
        try:
            self.logger.info("Starting comprehensive file transfer test...")
            
            # Create test files
            self.create_test_files()
            
            # Run all tests
            test_results = {
                'test_timestamp': time.time(),
                'test_files_created': len(self.test_files),
                'tests': {}
            }
            
            # Local file transfer test
            self.logger.info("Running local file transfer test...")
            local_results = self.test_local_file_transfer()
            test_results['tests']['local_transfer'] = local_results
            
            # Network file transfer test (if target provided)
            if target_ip:
                self.logger.info(f"Running network file transfer test to {target_ip}...")
                network_results = self.test_network_file_transfer(target_ip)
                test_results['tests']['network_transfer'] = network_results
                
                # Concurrent transfer test
                self.logger.info(f"Running concurrent transfer test to {target_ip}...")
                concurrent_results = self.test_concurrent_transfers(target_ip)
                test_results['tests']['concurrent_transfer'] = concurrent_results
            
            # Ethernet optimization test
            self.logger.info("Running Ethernet optimization test...")
            optimization_results = self.test_ethernet_optimization()
            test_results['tests']['ethernet_optimization'] = optimization_results
            
            # Generate summary
            summary = self._generate_test_summary(test_results)
            test_results['summary'] = summary
            
            return test_results
            
        except Exception as e:
            self.logger.error(f"Comprehensive test failed: {e}")
            return {'error': str(e)}
    
    def _generate_test_summary(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate test summary"""
        try:
            summary = {
                'overall_status': 'completed',
                'local_performance': {},
                'network_performance': {},
                'optimization_effects': {},
                'recommendations': []
            }
            
            # Local performance summary
            if 'local_transfer' in test_results['tests']:
                local_test = test_results['tests']['local_transfer']
                if 'results' in local_test:
                    throughputs = []
                    for filename, result in local_test['results'].items():
                        if 'copy' in result and 'throughput_mbps' in result['copy']:
                            throughputs.append(result['copy']['throughput_mbps'])
                    
                    if throughputs:
                        summary['local_performance'] = {
                            'avg_throughput_mbps': sum(throughputs) / len(throughputs),
                            'max_throughput_mbps': max(throughputs),
                            'min_throughput_mbps': min(throughputs),
                            'files_tested': len(throughputs)
                        }
            
            # Network performance summary
            if 'network_transfer' in test_results['tests']:
                network_test = test_results['tests']['network_transfer']
                if 'results' in network_test:
                    throughputs = []
                    for filename, result in network_test['results'].items():
                        if 'network_transfer' in result and 'throughput_mbps' in result['network_transfer']:
                            throughputs.append(result['network_transfer']['throughput_mbps'])
                    
                    if throughputs:
                        summary['network_performance'] = {
                            'avg_throughput_mbps': sum(throughputs) / len(throughputs),
                            'max_throughput_mbps': max(throughputs),
                            'min_throughput_mbps': min(throughputs),
                            'files_tested': len(throughputs)
                        }
            
            # Optimization effects
            if 'ethernet_optimization' in test_results['tests']:
                opt_test = test_results['tests']['ethernet_optimization']
                if 'improvement' in opt_test:
                    improvements = []
                    for filename, result in opt_test['improvement'].items():
                        if 'copy_improvement_percent' in result:
                            improvements.append(result['copy_improvement_percent'])
                    
                    if improvements:
                        summary['optimization_effects'] = {
                            'avg_improvement_percent': sum(improvements) / len(improvements),
                            'max_improvement_percent': max(improvements),
                            'files_improved': len(improvements)
                        }
            
            # Recommendations
            if 'local_performance' in summary and 'network_performance' in summary:
                local_avg = summary['local_performance'].get('avg_throughput_mbps', 0)
                network_avg = summary['network_performance'].get('avg_throughput_mbps', 0)
                
                if network_avg < local_avg * 0.5:
                    summary['recommendations'].append("Network performance significantly lower than local - check network configuration")
                
                if local_avg < 100:
                    summary['recommendations'].append("Local file transfer performance below 100 MB/s - consider SSD upgrade")
                
                if network_avg < 50:
                    summary['recommendations'].append("Network transfer performance below 50 MB/s - check Ethernet cable and switch")
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Failed to generate summary: {e}")
            return {}
    
    def cleanup_test_files(self):
        """Clean up test files"""
        try:
            test_dir = Path("test_files")
            if test_dir.exists():
                for file_path in test_dir.glob("*.dat"):
                    file_path.unlink()
                test_dir.rmdir()
                self.logger.info("Test files cleaned up")
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup test files: {e}")

def main():
    """Main test function"""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    tester = PortalFileTransferTest()
    
    try:
        # Run comprehensive test
        results = tester.run_comprehensive_test()
        
        # Print results
        print("\n" + "=" * 60)
        print("FILE TRANSFER TEST RESULTS")
        print("=" * 60)
        
        if 'summary' in results:
            summary = results['summary']
            
            print(f"Overall Status: {summary.get('overall_status', 'Unknown')}")
            print(f"Test Files Created: {results.get('test_files_created', 0)}")
            
            if 'local_performance' in summary:
                local = summary['local_performance']
                print(f"\nLocal Performance:")
                print(f"  Average: {local.get('avg_throughput_mbps', 0):.2f} MB/s")
                print(f"  Maximum: {local.get('max_throughput_mbps', 0):.2f} MB/s")
                print(f"  Minimum: {local.get('min_throughput_mbps', 0):.2f} MB/s")
            
            if 'network_performance' in summary:
                network = summary['network_performance']
                print(f"\nNetwork Performance:")
                print(f"  Average: {network.get('avg_throughput_mbps', 0):.2f} MB/s")
                print(f"  Maximum: {network.get('max_throughput_mbps', 0):.2f} MB/s")
                print(f"  Minimum: {network.get('min_throughput_mbps', 0):.2f} MB/s")
            
            if 'optimization_effects' in summary:
                opt = summary['optimization_effects']
                print(f"\nOptimization Effects:")
                print(f"  Average Improvement: {opt.get('avg_improvement_percent', 0):.2f}%")
                print(f"  Maximum Improvement: {opt.get('max_improvement_percent', 0):.2f}%")
            
            if 'recommendations' in summary and summary['recommendations']:
                print(f"\nRecommendations:")
                for rec in summary['recommendations']:
                    print(f"  - {rec}")
        
        # Save detailed results
        with open('file_transfer_test_results.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\nDetailed results saved to: file_transfer_test_results.json")
        
    except Exception as e:
        print(f"Test failed: {e}")
    
    finally:
        # Cleanup
        tester.cleanup_test_files()

if __name__ == "__main__":
    main()
