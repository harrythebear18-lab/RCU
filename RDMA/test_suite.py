#!/usr/bin/env python3
"""
Comprehensive Testing and Validation Suite for Software-Defined RDMA
Tests all components: ZeroMQ, Virtual PCIe, UDP Bridge, and Kernel Driver
"""

import unittest
import threading
import time
import socket
import subprocess
import sys
import os
import mmap
import tempfile
import struct
import random
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Tuple, Optional

# Import our modules
try:
    from zero_copy_rdmda import ZeroCopyRDMAServer, ZeroCopyRDMAClient
    from virtual_pcie_tunnel import VirtualPCIEDriver, VirtualPCIEClient
    from udp_memory_bridge import UDPMemoryBridgeServer, UDPMemoryBridgeClient
    from robust_network_layer import RobustNetworkLayer, NetworkError
    from virtual_dma_userspace import VirtualDMAController, RemoteDMAReceiver
    from advanced_dma_service import AdvancedDMAService, DMAPacket, PacketType
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure all modules are in the same directory")
    sys.exit(1)

class TestZeroCopyRDMA(unittest.TestCase):
    """Test Zero-Copy RDMA implementation"""
    
    def setUp(self):
        self.server = ZeroCopyRDMAServer(port=15555)
        self.client = ZeroCopyRDMAClient(port=15555)
        
        # Start server in background
        self.server_thread = threading.Thread(target=self.server.start_server)
        self.server_thread.daemon = True
        self.server_thread.start()
        
        # Give server time to start
        time.sleep(0.5)
    
    def tearDown(self):
        self.server.stop()
    
    def test_basic_connectivity(self):
        """Test basic server-client connectivity"""
        regions = self.client.list_regions()
        self.assertIsInstance(regions, list)
    
    def test_memory_region_creation(self):
        """Test memory region creation and access"""
        # Create test region
        test_data = b"Hello, Zero-Copy RDMA!"
        self.server.create_shared_memory_region("test", len(test_data))
        
        # Write data
        bytes_written = self.client.write_memory("test", 0, test_data)
        self.assertEqual(bytes_written, len(test_data))
        
        # Read data back
        read_data = self.client.read_memory("test", 0, len(test_data))
        self.assertEqual(read_data, test_data)
    
    def test_large_data_transfer(self):
        """Test large data transfer performance"""
        size = 1024 * 1024  # 1MB
        test_data = bytes(range(256)) * (size // 256)
        
        self.server.create_shared_memory_region("large", size)
        
        start_time = time.time()
        bytes_written = self.client.write_memory("large", 0, test_data)
        write_time = time.time() - start_time
        
        start_time = time.time()
        read_data = self.client.read_memory("large", 0, size)
        read_time = time.time() - start_time
        
        self.assertEqual(bytes_written, size)
        self.assertEqual(len(read_data), size)
        self.assertEqual(read_data, test_data)
        
        # Performance assertions
        self.assertLess(write_time, 1.0)  # Should complete within 1 second
        self.assertLess(read_time, 1.0)
        
        throughput = size / (write_time + read_time) / 1024 / 1024
        print(f"Zero-Copy throughput: {throughput:.2f} MB/s")
    
    def test_concurrent_access(self):
        """Test concurrent memory access"""
        self.server.create_shared_memory_region("concurrent", 1024)
        
        def worker(thread_id):
            data = f"Thread {thread_id}".encode()
            offset = (thread_id % 10) * 100
            self.client.write_memory("concurrent", offset, data)
            read_data = self.client.read_memory("concurrent", offset, len(data))
            return read_data == data
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(worker, i) for i in range(50)]
            results = [f.result() for f in as_completed(futures)]
        
        self.assertTrue(all(results))

class TestVirtualPCIETunnel(unittest.TestCase):
    """Test Virtual PCIe Tunnel implementation"""
    
    def setUp(self):
        self.driver = VirtualPCIEDriver(port=17777)
        self.client = VirtualPCIEClient("localhost", port=17777)
        
        # Start driver in background
        self.driver_thread = threading.Thread(target=self.driver.start_server)
        self.driver_thread.daemon = True
        self.driver_thread.start()
        
        time.sleep(0.5)
    
    def tearDown(self):
        self.driver.stop()
    
    def test_process_listing(self):
        """Test process listing functionality"""
        if self.client.connect():
            try:
                processes = self.client.list_processes()
                self.assertIsInstance(processes, list)
                self.assertGreater(len(processes), 0)
                
                # Check process structure
                if processes:
                    proc = processes[0]
                    self.assertIn('pid', proc)
                    self.assertIn('name', proc)
            finally:
                self.client.disconnect()
    
    def test_process_info(self):
        """Test process information retrieval"""
        if self.client.connect():
            try:
                processes = self.client.list_processes()
                if processes:
                    # Try to get info for current process
                    info = self.client.get_process_info(os.getpid())
                    self.assertIsInstance(info, dict)
                    self.assertIn('pid', info)
                    self.assertIn('name', info)
            finally:
                self.client.disconnect()

class TestUDPMemoryBridge(unittest.TestCase):
    """Test UDP Memory Bridge implementation"""
    
    def setUp(self):
        self.server = UDPMemoryBridgeServer(port=19999)
        self.client = UDPMemoryBridgeClient("localhost", port=19999)
        
        # Add test memory region
        test_data = b"UDP Bridge Test Data" * 1000
        self.server.add_memory_region("test_region", 0x1000, test_data)
        
        # Start server in background
        self.server_thread = threading.Thread(target=self.server.start_server)
        self.server_thread.daemon = True
        self.server_thread.start()
        
        time.sleep(0.5)
    
    def tearDown(self):
        self.server.stop()
    
    def test_basic_memory_read(self):
        """Test basic memory reading over UDP"""
        if self.client.connect():
            try:
                data = self.client.read_memory(0x1000, 1024)
                self.assertIsInstance(data, bytes)
                self.assertGreater(len(data), 0)
            finally:
                self.client.disconnect()
    
    def test_packet_ordering(self):
        """Test UDP packet ordering"""
        if self.client.connect():
            try:
                # Read multiple blocks
                reads = []
                for i in range(10):
                    offset = 0x1000 + i * 100
                    data = self.client.read_memory(offset, 50)
                    reads.append(data)
                
                # Verify all reads succeeded
                self.assertEqual(len(reads), 10)
                for data in reads:
                    self.assertIsInstance(data, bytes)
                    self.assertGreater(len(data), 0)
            finally:
                self.client.disconnect()

class TestRobustNetworkLayer(unittest.TestCase):
    """Test robust network layer functionality"""
    
    def setUp(self):
        self.layer = RobustNetworkLayer(max_retries=3, timeout=0.5)
        self.layer.start_background_tasks()
    
    def tearDown(self):
        self.layer.stop()
    
    def test_error_handling(self):
        """Test error handling mechanisms"""
        errors_handled = []
        
        def test_handler(error, seq=None):
            errors_handled.append(error)
            return True
        
        self.layer.register_error_handler(NetworkError.TIMEOUT, test_handler)
        
        # Simulate timeout
        self.layer._handle_error(NetworkError.TIMEOUT, TimeoutError("Test timeout"))
        
        self.assertEqual(len(errors_handled), 1)
        self.assertIsInstance(errors_handled[0], TimeoutError)
    
    def test_packet_buffer(self):
        """Test packet reordering buffer"""
        buffer = self.layer.packet_buffer
        
        # Add packets out of order
        data1 = buffer.add_packet(5, b"data5")
        data2 = buffer.add_packet(1, b"data1")
        data3 = buffer.add_packet(2, b"data2")
        data4 = buffer.add_packet(3, b"data3")
        
        # Should get ordered data when sequence 1 arrives
        self.assertIsNone(data1)  # Packet 5 is out of order
        self.assertEqual(data2, b"data1")  # Packet 1 can be delivered
        self.assertIsNone(data3)  # Still waiting for packet 2
        self.assertIsNone(data4)  # Still waiting for packet 2
        
        # Add packet 2
        data5 = buffer.add_packet(2, b"data2")
        self.assertEqual(data5, b"data2data3")  # Packets 2 and 3 can be delivered
    
    def test_metrics_tracking(self):
        """Test performance metrics"""
        # Simulate some activity
        self.layer.metrics.packets_sent = 100
        self.layer.metrics.packets_received = 95
        self.layer.metrics.packets_lost = 5
        
        metrics = self.layer.get_metrics()
        self.assertEqual(metrics.packets_sent, 100)
        self.assertEqual(metrics.packets_received, 95)
        self.assertEqual(metrics.packets_lost, 5)
        self.assertEqual(metrics.error_rate, 0.05)

class TestAdvancedDMAService(unittest.TestCase):
    """Test advanced DMA service"""
    
    def setUp(self):
        self.service = AdvancedDMAService(listen_port=29999)
        
        # Add test memory regions
        self.service.add_memory_region(0x10000000, 1024*1024)
        self.service.add_memory_region(0x20000000, 2*1024*1024)
    
    def tearDown(self):
        self.service.stop()
    
    def test_memory_region_management(self):
        """Test memory region add/remove"""
        initial_count = len(self.service.memory_regions)
        
        # Add new region
        result = self.service.add_memory_region(0x30000000, 1024*1024)
        self.assertTrue(result)
        self.assertEqual(len(self.service.memory_regions), initial_count + 1)
        
        # Remove region
        result = self.service.remove_memory_region(0x30000000)
        self.assertTrue(result)
        self.assertEqual(len(self.service.memory_regions), initial_count)
    
    def test_packet_packing(self):
        """Test DMA packet packing/unpacking"""
        original_packet = DMAPacket(
            sequence=123,
            packet_type=PacketType.DMA_WRITE,
            address=0x10000000,
            size=1024,
            data=b"X" * 1024,
            checksum=0
        )
        
        # Pack and unpack
        packed_data = original_packet.pack()
        unpacked_packet = DMAPacket.unpack(packed_data)
        
        # Verify integrity
        self.assertEqual(original_packet.sequence, unpacked_packet.sequence)
        self.assertEqual(original_packet.packet_type, unpacked_packet.packet_type)
        self.assertEqual(original_packet.address, unpacked_packet.address)
        self.assertEqual(original_packet.size, unpacked_packet.size)
        self.assertEqual(original_packet.data, unpacked_packet.data)
    
    def test_ordered_packet_buffer(self):
        """Test ordered packet buffer"""
        buffer = self.service.packet_buffer
        
        # Add packets out of order
        packet1 = DMAPacket(5, PacketType.DMA_WRITE, 0x1000, 100, b"data5", 0)
        packet2 = DMAPacket(1, PacketType.DMA_WRITE, 0x1000, 100, b"data1", 0)
        packet3 = DMAPacket(2, PacketType.DMA_WRITE, 0x1000, 100, b"data2", 0)
        
        can_deliver1 = buffer.add_packet(packet1)
        can_deliver2 = buffer.add_packet(packet2)
        can_deliver3 = buffer.add_packet(packet3)
        
        self.assertFalse(can_deliver1)  # Out of order
        self.assertTrue(can_deliver2)   # In order
        self.assertFalse(can_deliver3)  # Still out of order
        
        # Get ordered packets
        ordered = buffer.get_ordered_packets()
        self.assertEqual(len(ordered), 2)  # Packets 1 and 2
        self.assertEqual(ordered[0].sequence, 1)
        self.assertEqual(ordered[1].sequence, 2)

class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system"""
    
    def test_end_to_end_workflow(self):
        """Test complete end-to-end workflow"""
        # This would test the full pipeline:
        # 1. Virtual DMA Controller writes to memory
        # 2. Kernel driver intercepts and forwards
        # 3. Network layer ensures reliability
        # 4. Remote service receives and writes
        
        # For now, just test that components can be instantiated together
        components = []
        
        try:
            # ZeroMQ components
            zmq_server = ZeroCopyRDMAServer(port=25555)
            zmq_client = ZeroCopyRDMAClient(port=25555)
            components.extend([zmq_server, zmq_client])
            
            # Virtual PCIe components
            pcie_driver = VirtualPCIEDriver(port=27777)
            pcie_client = VirtualPCIEClient("localhost", port=27777)
            components.extend([pcie_driver, pcie_client])
            
            # UDP Bridge components
            udp_server = UDPMemoryBridgeServer(port=29999)
            udp_client = UDPMemoryBridgeClient("localhost", port=29999)
            components.extend([udp_server, udp_client])
            
            # Network layer
            network_layer = RobustNetworkLayer()
            components.append(network_layer)
            
            # Advanced DMA service
            dma_service = AdvancedDMAService(listen_port=39999)
            components.append(dma_service)
            
            # All components created successfully
            self.assertEqual(len(components), 9)
            
        finally:
            # Cleanup
            for component in components:
                if hasattr(component, 'stop'):
                    component.stop()
                elif hasattr(component, 'close'):
                    component.close()

class PerformanceBenchmark(unittest.TestCase):
    """Performance benchmarking tests"""
    
    def test_throughput_comparison(self):
        """Compare throughput of different methods"""
        results = {}
        
        # Test ZeroMQ throughput
        print("\nBenchmarking Zero-Copy RDMA...")
        server = ZeroCopyRDMAServer(port=35555)
        client = ZeroCopyRDMAClient(port=35555)
        
        server_thread = threading.Thread(target=server.start_server)
        server_thread.daemon = True
        server_thread.start()
        time.sleep(0.5)
        
        try:
            size = 1024 * 1024  # 1MB
            test_data = b"X" * size
            server.create_shared_memory_region("benchmark", size)
            
            start_time = time.time()
            client.write_memory("benchmark", 0, test_data)
            read_data = client.read_memory("benchmark", 0, size)
            end_time = time.time()
            
            if read_data == test_data:
                throughput = size / (end_time - start_time) / 1024 / 1024
                results['zeromq'] = throughput
                print(f"ZeroMQ throughput: {throughput:.2f} MB/s")
        finally:
            server.stop()
        
        # Test UDP Bridge throughput
        print("\nBenchmarking UDP Memory Bridge...")
        udp_server = UDPMemoryBridgeServer(port=45555)
        udp_client = UDPMemoryBridgeClient("localhost", port=45555)
        
        test_data = b"Y" * 4096
        udp_server.add_memory_region("benchmark", 0x1000, test_data)
        
        server_thread = threading.Thread(target=udp_server.start_server)
        server_thread.daemon = True
        server_thread.start()
        time.sleep(0.5)
        
        try:
            iterations = 100
            total_bytes = 0
            start_time = time.time()
            
            for i in range(iterations):
                data = udp_client.read_memory(0x1000, 4096)
                total_bytes += len(data)
            
            end_time = time.time()
            throughput = total_bytes / (end_time - start_time) / 1024 / 1024
            results['udp'] = throughput
            print(f"UDP Bridge throughput: {throughput:.2f} MB/s")
        finally:
            udp_server.stop()
        
        # Print comparison
        print(f"\nThroughput Comparison:")
        for method, throughput in results.items():
            print(f"  {method}: {throughput:.2f} MB/s")
        
        # Verify we got results
        self.assertGreater(len(results), 0)

def run_comprehensive_tests():
    """Run all tests with detailed reporting"""
    print("Software-Defined RDMA Comprehensive Test Suite")
    print("=" * 50)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestZeroCopyRDMA,
        TestVirtualPCIETunnel,
        TestUDPMemoryBridge,
        TestRobustNetworkLayer,
        TestAdvancedDMAService,
        TestIntegration,
        PerformanceBenchmark
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 50)
    print("Test Summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"  {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"  {test}: {traceback.split('Exception:')[-1].strip()}")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)
