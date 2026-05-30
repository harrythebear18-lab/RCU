#!/usr/bin/env python3
"""
Test Bidirectional Resource Sharing
Verifies peer-to-peer communication and bidirectional data flow
"""

import asyncio
import sys
import os
from pathlib import Path

# Add Core Services to path
sys.path.insert(0, str(Path(__file__).parent / "Core Services"))

from bidirectional_resource_sharing import (
    BidirectionalResourceSharing, 
    ResourceType, 
    MessageType,
    get_resource_sharing
)

class ResourceSharingTester:
    """Test suite for bidirectional resource sharing"""
    
    def __init__(self):
        self.test_results = []
        self.system1 = None
        self.system2 = None
        
    def log_test(self, test_name: str, passed: bool, message: str = ""):
        """Log test result"""
        status = "PASS" if passed else "FAIL"
        self.test_results.append((test_name, passed, message))
        print(f"[{status}] {test_name}: {message}")
    
    async def test_system_initialization(self):
        """Test system initialization"""
        try:
            # Create two test systems
            self.system1 = BidirectionalResourceSharing("system1")
            self.system2 = BidirectionalResourceSharing("system2")
            
            # Verify different system IDs
            assert self.system1.system_id != self.system2.system_id
            assert self.system1.system_id == "system1"
            assert self.system2.system_id == "system2"
            
            # Verify resource initialization
            assert len(self.system1.resources) > 0
            assert len(self.system2.resources) > 0
            
            # Verify CPU and RAM resources exist
            cpu_resources = [r for r in self.system1.resources.values() if r.type == ResourceType.CPU]
            ram_resources = [r for r in self.system1.resources.values() if r.type == ResourceType.RAM]
            
            assert len(cpu_resources) > 0
            assert len(ram_resources) > 0
            
            self.log_test("System Initialization", True, f"Systems initialized with {len(self.system1.resources)} resources")
            
        except Exception as e:
            self.log_test("System Initialization", False, str(e))
    
    async def test_server_startup(self):
        """Test server startup and port allocation"""
        try:
            # Start both servers
            port1 = await self.system1.start_server()
            port2 = await self.system2.start_server()
            
            # Verify ports are in range
            assert 30000 <= port1 <= 31000
            assert 30000 <= port2 <= 31000
            assert port1 != port2  # Should be different ports
            
            # Verify server is running
            assert self.system1.running
            assert self.system2.running
            
            self.log_test("Server Startup", True, f"System1: {port1}, System2: {port2}")
            
        except Exception as e:
            self.log_test("Server Startup", False, str(e))
    
    async def test_peer_discovery(self):
        """Test peer discovery"""
        try:
            # Import PeerInfo from the module
            from bidirectional_resource_sharing import PeerInfo
            
            # Manually add peer connection (simulating network discovery)
            from datetime import datetime
            self.system1.peers[self.system2.system_id] = PeerInfo(
                system_id=self.system2.system_id,
                hostname='test-host',
                ip_address='127.0.0.1',
                port=self.system2.server_port,
                last_seen=datetime.now().isoformat(),
                capabilities=[],
                status='active'
            )
            
            # Test discovery message
            discovery_handled = False
            
            async def handle_discovery(message):
                nonlocal discovery_handled
                discovery_handled = True
                assert message.type == MessageType.DISCOVERY.value
                assert message.sender_id == self.system1.system_id
            
            self.system2.add_message_handler(MessageType.DISCOVERY, handle_discovery)
            
            # Send discovery message
            from bidirectional_resource_sharing import Message
            discovery_msg = Message(
                type=MessageType.DISCOVERY,
                sender_id=self.system1.system_id,
                receiver_id=self.system2.system_id,
                timestamp=None,
                data={'test': True},
                message_id='test-discovery'
            )
            
            await self.system1._send_to_peer(
                self.system1.peers[self.system2.system_id], 
                discovery_msg
            )
            
            # Wait for message processing
            await asyncio.sleep(0.1)
            
            assert discovery_handled
            self.log_test("Peer Discovery", True, "Discovery message handled successfully")
            
        except Exception as e:
            self.log_test("Peer Discovery", False, str(e))
    
    async def test_resource_offering(self):
        """Test resource offering between systems"""
        try:
            offer_received = False
            received_resources = {}
            
            async def handle_resource_offer(message):
                nonlocal offer_received, received_resources
                offer_received = True
                assert message.type == MessageType.RESOURCE_OFFER
                received_resources = message.data.get('resources', {})
            
            self.system2.add_message_handler(MessageType.RESOURCE_OFFER, handle_resource_offer)
            
            # Send resource offer
            await self.system1.offer_resources(self.system2.system_id)
            
            # Wait for message processing
            await asyncio.sleep(0.1)
            
            assert offer_received
            assert len(received_resources) > 0
            
            self.log_test("Resource Offering", True, f"Offered {len(received_resources)} resources")
            
        except Exception as e:
            self.log_test("Resource Offering", False, str(e))
    
    async def test_resource_request_response(self):
        """Test resource request and response cycle"""
        try:
            request_received = False
            response_received = False
            
            async def handle_resource_request(message):
                nonlocal request_received
                request_received = True
                assert message.type == MessageType.RESOURCE_REQUEST
                assert message.data['type'] == ResourceType.CPU.value
                assert message.data['amount'] == 2.0
            
            async def handle_resource_response(message):
                nonlocal response_received
                response_received = True
                assert message.type == MessageType.RESOURCE_RESPONSE
                assert 'granted' in message.data
            
            self.system2.add_message_handler(MessageType.RESOURCE_REQUEST, handle_resource_request)
            self.system1.add_message_handler(MessageType.RESOURCE_RESPONSE, handle_resource_response)
            
            # Send resource request
            await self.system1.request_resource(ResourceType.CPU, 2.0, self.system2.system_id)
            
            # Wait for message processing
            await asyncio.sleep(0.1)
            
            assert request_received
            assert response_received
            
            self.log_test("Resource Request/Response", True, "Request-response cycle completed")
            
        except Exception as e:
            self.log_test("Resource Request/Response", False, str(e))
    
    async def test_bidirectional_communication(self):
        """Test bidirectional data flow"""
        try:
            messages_system1 = []
            messages_system2 = []
            
            async def capture_system1_messages(message):
                messages_system1.append(message)
            
            async def capture_system2_messages(message):
                messages_system2.append(message)
            
            # Add message capture handlers
            for msg_type in [MessageType.HEARTBEAT, MessageType.DATA_TRANSFER]:
                self.system1.add_message_handler(msg_type, capture_system1_messages)
                self.system2.add_message_handler(msg_type, capture_system2_messages)
            
            # Send bidirectional messages
            from bidirectional_resource_sharing import Message
            
            # System1 to System2
            msg1 = Message(
                type=MessageType.DATA_TRANSFER,
                sender_id=self.system1.system_id,
                receiver_id=self.system2.system_id,
                timestamp=None,
                data={'direction': '1->2', 'payload': 'test_data_1'},
                message_id='bidirectional-test-1'
            )
            
            # System2 to System1
            msg2 = Message(
                type=MessageType.DATA_TRANSFER,
                sender_id=self.system2.system_id,
                receiver_id=self.system1.system_id,
                timestamp=None,
                data={'direction': '2->1', 'payload': 'test_data_2'},
                message_id='bidirectional-test-2'
            )
            
            await self.system1._send_to_peer(self.system1.peers[self.system2.system_id], msg1)
            await self.system2._send_to_peer(self.system2.peers[self.system1.system_id], msg2)
            
            # Wait for message processing
            await asyncio.sleep(0.1)
            
            # Verify bidirectional communication
            system2_received = [m for m in messages_system2 if m.message_id == 'bidirectional-test-1']
            system1_received = [m for m in messages_system1 if m.message_id == 'bidirectional-test-2']
            
            assert len(system2_received) > 0
            assert len(system1_received) > 0
            assert system2_received[0].data['direction'] == '1->2'
            assert system1_received[0].data['direction'] == '2->1'
            
            self.log_test("Bidirectional Communication", True, "Both directions working correctly")
            
        except Exception as e:
            self.log_test("Bidirectional Communication", False, str(e))
    
    async def test_dynamic_port_allocation(self):
        """Test dynamic port allocation"""
        try:
            # Create additional systems to test port allocation
            system3 = BidirectionalResourceSharing("system3")
            system4 = BidirectionalResourceSharing("system4")
            
            port3 = await system3.start_server()
            port4 = await system4.start_server()
            
            # Verify all ports are unique and in range
            ports = [self.system1.server_port, self.system2.server_port, port3, port4]
            assert len(set(ports)) == 4  # All unique
            assert all(30000 <= p <= 31000 for p in ports)  # All in range
            
            # Cleanup
            await system3.stop()
            await system4.stop()
            
            self.log_test("Dynamic Port Allocation", True, f"Allocated unique ports: {ports}")
            
        except Exception as e:
            self.log_test("Dynamic Port Allocation", False, str(e))
    
    async def test_peer_status_monitoring(self):
        """Test peer status and monitoring"""
        try:
            # Get status from both systems
            status1 = self.system1.get_peer_status()
            status2 = self.system2.get_peer_status()
            
            # Verify status structure
            required_fields = ['system_id', 'hostname', 'ip_address', 'port', 'peers', 'resources']
            for field in required_fields:
                assert field in status1
                assert field in status2
            
            # Verify system IDs
            assert status1['system_id'] == self.system1.system_id
            assert status2['system_id'] == self.system2.system_id
            
            # Verify port information
            assert status1['port'] == self.system1.server_port
            assert status2['port'] == self.system2.server_port
            
            self.log_test("Peer Status Monitoring", True, f"System1: {status1['total_peers']} peers, {status1['total_resources']} resources")
            
        except Exception as e:
            self.log_test("Peer Status Monitoring", False, str(e))
    
    async def run_all_tests(self):
        """Run all tests"""
        print("Starting Bidirectional Resource Sharing Tests")
        print("=" * 50)
        
        tests = [
            self.test_system_initialization,
            self.test_server_startup,
            self.test_peer_discovery,
            self.test_resource_offering,
            self.test_resource_request_response,
            self.test_bidirectional_communication,
            self.test_dynamic_port_allocation,
            self.test_peer_status_monitoring
        ]
        
        for test in tests:
            try:
                await test()
            except Exception as e:
                self.log_test(test.__name__, False, f"Test crashed: {e}")
        
        # Cleanup
        if self.system1:
            await self.system1.stop()
        if self.system2:
            await self.system2.stop()
        
        # Print results
        print("\n" + "=" * 50)
        print("TEST RESULTS")
        print("=" * 50)
        
        passed = sum(1 for _, p, _ in self.test_results if p)
        total = len(self.test_results)
        
        for test_name, passed, message in self.test_results:
            status = "PASS" if passed else "FAIL"
            print(f"[{status}] {test_name}: {message}")
        
        print(f"\nSummary: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Bidirectional resource sharing is working correctly.")
        else:
            print("❌ Some tests failed. Check the implementation.")
        
        return passed == total

async def main():
    """Main test runner"""
    tester = ResourceSharingTester()
    success = await tester.run_all_tests()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
