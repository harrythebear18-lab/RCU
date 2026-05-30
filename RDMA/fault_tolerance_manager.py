#!/usr/bin/env python3
"""
Fault Tolerance and Failover Manager
Provides high availability, automatic failover, and disaster recovery
"""

import time
import threading
import json
import hashlib
import socket
import requests
from typing import Dict, List, Optional, Tuple, Callable, Any
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor, as_completed
import random

class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    FAILED = "failed"

class FailoverMode(Enum):
    ACTIVE_PASSIVE = "active_passive"
    ACTIVE_ACTIVE = "active_active"
    GEOGRAPHIC = "geographic"

@dataclass
class ClusterNode:
    """Represents a cluster node in the DMA system"""
    node_id: str
    host: str
    port: int
    role: str  # primary, secondary, backup
    region: str
    weight: int = 1
    status: HealthStatus = HealthStatus.HEALTHY
    last_check: float = 0
    failure_count: int = 0
    response_time: float = 0
    active_connections: int = 0
    max_connections: int = 1000

@dataclass
class FailoverPolicy:
    """Failover policy configuration"""
    health_check_interval: int = 5  # seconds
    failure_threshold: int = 3  # consecutive failures
    recovery_threshold: int = 2  # consecutive successes
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: int = 30  # seconds
    failover_timeout: int = 10  # seconds
    max_failover_attempts: int = 3
    data_consistency_check: bool = True

class CircuitBreaker:
    """Circuit breaker pattern for fault tolerance"""
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 30):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = "closed"  # closed, open, half_open
        self.lock = threading.RLock()
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        with self.lock:
            if self.state == "open":
                if time.time() - self.last_failure_time > self.timeout:
                    self.state = "half_open"
                else:
                    raise Exception("Circuit breaker is open")
        
        try:
            result = func(*args, **kwargs)
            self.on_success()
            return result
        except Exception as e:
            self.on_failure()
            raise
    
    def on_success(self):
        """Handle successful call"""
        with self.lock:
            self.failure_count = 0
            if self.state == "half_open":
                self.state = "closed"
    
    def on_failure(self):
        """Handle failed call"""
        with self.lock:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = "open"

class HealthChecker:
    """Advanced health checking for cluster nodes"""
    
    def __init__(self, policy: FailoverPolicy):
        self.policy = policy
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.logger = logging.getLogger(__name__)
    
    def check_node_health(self, node: ClusterNode) -> Tuple[HealthStatus, Dict]:
        """Perform comprehensive health check"""
        health_data = {
            'timestamp': time.time(),
            'checks': {}
        }
        
        try:
            # Create circuit breaker for this node
            if node.node_id not in self.circuit_breakers:
                self.circuit_breakers[node.node_id] = CircuitBreaker(
                    self.policy.circuit_breaker_threshold,
                    self.policy.circuit_breaker_timeout
                )
            
            circuit_breaker = self.circuit_breakers[node.node_id]
            
            # Perform health checks
            health_data['checks']['connectivity'] = self._check_connectivity(node)
            health_data['checks']['response_time'] = self._check_response_time(node)
            health_data['checks']['resource_usage'] = self._check_resource_usage(node)
            health_data['checks']['service_availability'] = self._check_service_availability(node)
            
            if self.policy.data_consistency_check:
                health_data['checks']['data_consistency'] = self._check_data_consistency(node)
            
            # Evaluate overall health
            status = self._evaluate_health(health_data['checks'])
            
            return status, health_data
            
        except Exception as e:
            self.logger.error(f"Health check failed for node {node.node_id}: {e}")
            return HealthStatus.FAILED, health_data
    
    def _check_connectivity(self, node: ClusterNode) -> Dict:
        """Check network connectivity"""
        start_time = time.time()
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            
            result = sock.connect_ex((node.host, node.port))
            response_time = time.time() - start_time
            
            sock.close()
            
            return {
                'status': 'connected' if result == 0 else 'failed',
                'response_time': response_time,
                'error': None
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'response_time': time.time() - start_time,
                'error': str(e)
            }
    
    def _check_response_time(self, node: ClusterNode) -> Dict:
        """Check API response time"""
        try:
            start_time = time.time()
            
            # Simple health check endpoint
            response = requests.get(
                f"http://{node.host}:{node.port}/health",
                timeout=5
            )
            
            response_time = time.time() - start_time
            
            return {
                'status_code': response.status_code,
                'response_time': response_time,
                'healthy': response.status_code == 200
            }
            
        except Exception as e:
            return {
                'status_code': None,
                'response_time': time.time() - start_time,
                'healthy': False,
                'error': str(e)
            }
    
    def _check_resource_usage(self, node: ClusterNode) -> Dict:
        """Check resource usage on node"""
        try:
            response = requests.get(
                f"http://{node.host}:{node.port}/metrics",
                timeout=5
            )
            
            if response.status_code == 200:
                metrics = response.json()
                
                return {
                    'cpu_usage': metrics.get('cpu_percent', 0),
                    'memory_usage': metrics.get('memory_percent', 0),
                    'disk_usage': metrics.get('disk_percent', 0),
                    'network_usage': metrics.get('network_bytes', 0),
                    'healthy': True
                }
            else:
                return {'healthy': False, 'error': f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {'healthy': False, 'error': str(e)}
    
    def _check_service_availability(self, node: ClusterNode) -> Dict:
        """Check if DMA services are available"""
        services = ['zeromq', 'pcie', 'udp']
        service_status = {}
        
        for service in services:
            try:
                response = requests.get(
                    f"http://{node.host}:{node.port}/service/{service}/status",
                    timeout=3
                )
                
                service_status[service] = {
                    'available': response.status_code == 200,
                    'status_code': response.status_code
                }
                
            except Exception as e:
                service_status[service] = {
                    'available': False,
                    'error': str(e)
                }
        
        all_available = all(status['available'] for status in service_status.values())
        
        return {
            'services': service_status,
            'all_available': all_available,
            'healthy': all_available
        }
    
    def _check_data_consistency(self, node: ClusterNode) -> Dict:
        """Check data consistency across nodes"""
        try:
            # Get checksum of critical data
            response = requests.get(
                f"http://{node.host}:{node.port}/data/checksum",
                timeout=5
            )
            
            if response.status_code == 200:
                checksum_data = response.json()
                
                return {
                    'checksum': checksum_data.get('checksum'),
                    'timestamp': checksum_data.get('timestamp'),
                    'consistent': True,
                    'healthy': True
                }
            else:
                return {'consistent': False, 'error': f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {'consistent': False, 'error': str(e)}
    
    def _evaluate_health(self, checks: Dict) -> HealthStatus:
        """Evaluate overall health based on all checks"""
        if not checks:
            return HealthStatus.FAILED
        
        failed_checks = []
        warning_checks = []
        
        for check_name, check_data in checks.items():
            if isinstance(check_data, dict):
                if not check_data.get('healthy', True):
                    failed_checks.append(check_name)
                elif check_data.get('status') == 'degraded':
                    warning_checks.append(check_name)
        
        if failed_checks:
            if len(failed_checks) >= 3:
                return HealthStatus.FAILED
            elif len(failed_checks) >= 2:
                return HealthStatus.UNHEALTHY
            else:
                return HealthStatus.DEGRADED
        elif warning_checks:
            return HealthStatus.DEGRADED
        else:
            return HealthStatus.HEALTHY

class LoadBalancer:
    """Advanced load balancing with multiple algorithms"""
    
    def __init__(self, algorithm: str = "round_robin"):
        self.algorithm = algorithm
        self.current_index = 0
        self.logger = logging.getLogger(__name__)
    
    def select_node(self, healthy_nodes: List[ClusterNode], request_context: Dict = None) -> Optional[ClusterNode]:
        """Select best node based on algorithm"""
        if not healthy_nodes:
            return None
        
        if self.algorithm == "round_robin":
            return self._round_robin_select(healthy_nodes)
        elif self.algorithm == "weighted_round_robin":
            return self._weighted_round_robin_select(healthy_nodes)
        elif self.algorithm == "least_connections":
            return self._least_connections_select(healthy_nodes)
        elif self.algorithm == "response_time":
            return self._response_time_select(healthy_nodes)
        elif self.algorithm == "geographic":
            return self._geographic_select(healthy_nodes, request_context)
        else:
            return healthy_nodes[0]
    
    def _round_robin_select(self, nodes: List[ClusterNode]) -> ClusterNode:
        """Round-robin selection"""
        node = nodes[self.current_index % len(nodes)]
        self.current_index += 1
        return node
    
    def _weighted_round_robin_select(self, nodes: List[ClusterNode]) -> ClusterNode:
        """Weighted round-robin selection"""
        total_weight = sum(node.weight for node in nodes)
        if total_weight == 0:
            return nodes[0]
        
        random_weight = random.randint(0, total_weight - 1)
        current_weight = 0
        
        for node in nodes:
            current_weight += node.weight
            if random_weight < current_weight:
                return node
        
        return nodes[-1]
    
    def _least_connections_select(self, nodes: List[ClusterNode]) -> ClusterNode:
        """Select node with least connections"""
        return min(nodes, key=lambda n: n.active_connections)
    
    def _response_time_select(self, nodes: List[ClusterNode]) -> ClusterNode:
        """Select node with best response time"""
        return min(nodes, key=lambda n: n.response_time)
    
    def _geographic_select(self, nodes: List[ClusterNode], request_context: Dict) -> ClusterNode:
        """Select node based on geographic proximity"""
        if not request_context or 'client_region' not in request_context:
            return nodes[0]
        
        client_region = request_context['client_region']
        
        # Prefer nodes in same region
        same_region_nodes = [n for n in nodes if n.region == client_region]
        if same_region_nodes:
            return same_region_nodes[0]
        
        # Fallback to nearest region (simplified)
        return nodes[0]

class FailoverManager:
    """Main failover and fault tolerance manager"""
    
    def __init__(self, policy: FailoverPolicy = None):
        self.policy = policy or FailoverPolicy()
        self.nodes: Dict[str, ClusterNode] = {}
        self.health_checker = HealthChecker(self.policy)
        self.load_balancer = LoadBalancer()
        
        # Failover state
        self.primary_node_id: Optional[str] = None
        self.active_nodes: List[str] = []
        self.failed_nodes: List[str] = []
        
        # Statistics
        self.failover_count = 0
        self.last_failover_time = 0
        self.uptime_start = time.time()
        
        # Background tasks
        self.running = False
        self.health_check_thread = None
        self.recovery_thread = None
        
        # Callbacks
        self.failover_callbacks: List[Callable] = []
        self.recovery_callbacks: List[Callable] = []
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def add_node(self, node: ClusterNode):
        """Add a node to the cluster"""
        self.nodes[node.node_id] = node
        self.active_nodes.append(node.node_id)
        
        # Set primary node if none exists
        if self.primary_node_id is None:
            self.primary_node_id = node.node_id
        
        self.logger.info(f"Added node {node.node_id} ({node.host}:{node.port})")
    
    def remove_node(self, node_id: str):
        """Remove a node from the cluster"""
        if node_id in self.nodes:
            del self.nodes[node_id]
            
            if node_id in self.active_nodes:
                self.active_nodes.remove(node_id)
            
            if node_id in self.failed_nodes:
                self.failed_nodes.remove(node_id)
            
            if self.primary_node_id == node_id:
                self.primary_node_id = None
                # Select new primary
                if self.active_nodes:
                    self.primary_node_id = self.active_nodes[0]
            
            self.logger.info(f"Removed node {node_id}")
    
    def start_health_monitoring(self):
        """Start background health monitoring"""
        self.running = True
        
        # Health check thread
        self.health_check_thread = threading.Thread(target=self._health_monitoring_worker)
        self.health_check_thread.daemon = True
        self.health_check_thread.start()
        
        # Recovery thread
        self.recovery_thread = threading.Thread(target=self._recovery_worker)
        self.recovery_thread.daemon = True
        self.recovery_thread.start()
        
        self.logger.info("Health monitoring started")
    
    def stop_health_monitoring(self):
        """Stop background health monitoring"""
        self.running = False
        
        if self.health_check_thread:
            self.health_check_thread.join(timeout=5.0)
        
        if self.recovery_thread:
            self.recovery_thread.join(timeout=5.0)
        
        self.logger.info("Health monitoring stopped")
    
    def _health_monitoring_worker(self):
        """Background health monitoring worker"""
        while self.running:
            try:
                for node_id in list(self.active_nodes):
                    if node_id in self.nodes:
                        node = self.nodes[node_id]
                        
                        # Perform health check
                        status, health_data = self.health_checker.check_node_health(node)
                        
                        # Update node status
                        old_status = node.status
                        node.status = status
                        node.last_check = time.time()
                        node.response_time = health_data['checks'].get('response_time', {}).get('response_time', 0)
                        
                        # Handle status changes
                        if old_status != status:
                            self._handle_status_change(node, old_status, status)
                
                time.sleep(self.policy.health_check_interval)
                
            except Exception as e:
                self.logger.error(f"Health monitoring error: {e}")
                time.sleep(1)
    
    def _recovery_worker(self):
        """Background recovery worker"""
        while self.running:
            try:
                # Try to recover failed nodes
                for node_id in list(self.failed_nodes):
                    if node_id in self.nodes:
                        node = self.nodes[node_id]
                        
                        # Check if node should be recovered
                        if self._should_recover_node(node):
                            self._recover_node(node)
                
                time.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                self.logger.error(f"Recovery worker error: {e}")
                time.sleep(1)
    
    def _handle_status_change(self, node: ClusterNode, old_status: HealthStatus, new_status: HealthStatus):
        """Handle node status changes"""
        self.logger.info(f"Node {node.node_id} status changed: {old_status.value} -> {new_status.value}")
        
        if new_status in [HealthStatus.FAILED, HealthStatus.UNHEALTHY]:
            # Mark as failed
            if node.node_id in self.active_nodes:
                self.active_nodes.remove(node.node_id)
            
            if node.node_id not in self.failed_nodes:
                self.failed_nodes.append(node.node_id)
            
            # Trigger failover if this was primary
            if node.node_id == self.primary_node_id:
                self._trigger_failover(node)
        
        elif new_status == HealthStatus.HEALTHY:
            # Mark as recovered
            if node.node_id in self.failed_nodes:
                self.failed_nodes.remove(node.node_id)
            
            if node.node_id not in self.active_nodes:
                self.active_nodes.append(node.node_id)
            
            # Notify recovery callbacks
            for callback in self.recovery_callbacks:
                try:
                    callback(node)
                except Exception as e:
                    self.logger.error(f"Recovery callback error: {e}")
    
    def _should_recover_node(self, node: ClusterNode) -> bool:
        """Determine if a failed node should be recovered"""
        if node.status not in [HealthStatus.FAILED, HealthStatus.UNHEALTHY]:
            return False
        
        # Check if enough time has passed since last failure
        if time.time() - node.last_check < self.policy.failover_timeout:
            return False
        
        # Check if failure count is below threshold
        if node.failure_count < self.policy.failure_threshold:
            return True
        
        return False
    
    def _recover_node(self, node: ClusterNode):
        """Attempt to recover a failed node"""
        self.logger.info(f"Attempting to recover node {node.node_id}")
        
        try:
            # Reset failure count
            node.failure_count = 0
            
            # Perform health check
            status, health_data = self.health_checker.check_node_health(node)
            node.status = status
            
            if status == HealthStatus.HEALTHY:
                self.logger.info(f"Node {node.node_id} recovered successfully")
                
                # Notify recovery callbacks
                for callback in self.recovery_callbacks:
                    try:
                        callback(node)
                    except Exception as e:
                        self.logger.error(f"Recovery callback error: {e}")
            else:
                self.logger.warning(f"Node {node.node_id} recovery attempt failed")
                
        except Exception as e:
            self.logger.error(f"Node recovery error: {e}")
    
    def _trigger_failover(self, failed_node: ClusterNode):
        """Trigger failover to backup node"""
        self.logger.warning(f"Triggering failover from failed node {failed_node.node_id}")
        
        self.failover_count += 1
        self.last_failover_time = time.time()
        
        # Select new primary
        if self.active_nodes:
            new_primary_id = self.active_nodes[0]
            self.primary_node_id = new_primary_id
            
            self.logger.info(f"New primary node: {new_primary_id}")
            
            # Notify failover callbacks
            for callback in self.failover_callbacks:
                try:
                    callback(failed_node, self.nodes[new_primary_id])
                except Exception as e:
                    self.logger.error(f"Failover callback error: {e}")
        else:
            self.logger.error("No healthy nodes available for failover")
    
    def get_best_node(self, request_context: Dict = None) -> Optional[ClusterNode]:
        """Get best node for request"""
        healthy_nodes = [self.nodes[node_id] for node_id in self.active_nodes 
                        if self.nodes[node_id].status == HealthStatus.HEALTHY]
        
        if not healthy_nodes:
            # Try degraded nodes
            degraded_nodes = [self.nodes[node_id] for node_id in self.active_nodes 
                            if self.nodes[node_id].status == HealthStatus.DEGRADED]
            if degraded_nodes:
                healthy_nodes = degraded_nodes
        
        if not healthy_nodes:
            return None
        
        return self.load_balancer.select_node(healthy_nodes, request_context)
    
    def execute_with_failover(self, func: Callable, *args, max_retries: int = 3, **kwargs) -> Any:
        """Execute function with automatic failover"""
        last_exception = None
        
        for attempt in range(max_retries):
            node = self.get_best_node()
            
            if not node:
                raise Exception("No healthy nodes available")
            
            try:
                # Execute function on selected node
                if hasattr(func, '__self__'):
                    # Method call
                    result = func(node, *args, **kwargs)
                else:
                    # Function call
                    result = func(node, *args, **kwargs)
                
                return result
                
            except Exception as e:
                last_exception = e
                self.logger.warning(f"Request failed on node {node.node_id}: {e}")
                
                # Mark node as failed if this is a critical error
                if "connection" in str(e).lower() or "timeout" in str(e).lower():
                    node.status = HealthStatus.FAILED
                    node.failure_count += 1
        
        raise last_exception
    
    def add_failover_callback(self, callback: Callable):
        """Add callback for failover events"""
        self.failover_callbacks.append(callback)
    
    def add_recovery_callback(self, callback: Callable):
        """Add callback for recovery events"""
        self.recovery_callbacks.append(callback)
    
    def get_cluster_status(self) -> Dict:
        """Get comprehensive cluster status"""
        total_nodes = len(self.nodes)
        healthy_nodes = len([n for n in self.nodes.values() if n.status == HealthStatus.HEALTHY])
        degraded_nodes = len([n for n in self.nodes.values() if n.status == HealthStatus.DEGRADED])
        failed_nodes = len([n for n in self.nodes.values() if n.status in [HealthStatus.FAILED, HealthStatus.UNHEALTHY]])
        
        uptime = time.time() - self.uptime_start
        
        return {
            'total_nodes': total_nodes,
            'healthy_nodes': healthy_nodes,
            'degraded_nodes': degraded_nodes,
            'failed_nodes': failed_nodes,
            'active_nodes': len(self.active_nodes),
            'primary_node': self.primary_node_id,
            'uptime_seconds': uptime,
            'failover_count': self.failover_count,
            'last_failover_time': self.last_failover_time,
            'cluster_health': 'healthy' if healthy_nodes > 0 else 'failed',
            'nodes': {
                node_id: {
                    'host': node.host,
                    'port': node.port,
                    'role': node.role,
                    'status': node.status.value,
                    'active_connections': node.active_connections,
                    'response_time': node.response_time,
                    'failure_count': node.failure_count
                }
                for node_id, node in self.nodes.items()
            }
        }

def demo_fault_tolerance():
    """Demonstration of fault tolerance system"""
    print("Fault Tolerance Manager Demo")
    print("=" * 30)
    
    # Create failover policy
    policy = FailoverPolicy(
        health_check_interval=2,
        failure_threshold=2,
        circuit_breaker_threshold=3
    )
    
    # Create failover manager
    failover = FailoverManager(policy)
    
    # Add cluster nodes
    nodes = [
        ClusterNode("node1", "localhost", 5555, "primary", "us-east"),
        ClusterNode("node2", "localhost", 5556, "secondary", "us-east"),
        ClusterNode("node3", "localhost", 5557, "backup", "us-west")
    ]
    
    for node in nodes:
        failover.add_node(node)
    
    # Add callbacks
    def on_failover(failed_node, new_primary):
        print(f"FAILOVER: {failed_node.node_id} -> {new_primary.node_id}")
    
    def on_recovery(node):
        print(f"RECOVERY: {node.node_id} is back online")
    
    failover.add_failover_callback(on_failover)
    failover.add_recovery_callback(on_recovery)
    
    # Start health monitoring
    failover.start_health_monitoring()
    
    try:
        # Simulate some operations
        print("Simulating cluster operations...")
        
        for i in range(10):
            # Get best node
            node = failover.get_best_node()
            if node:
                print(f"Request {i+1} routed to {node.node_id} ({node.status.value})")
            else:
                print(f"Request {i+1}: No healthy nodes available")
            
            time.sleep(1)
        
        # Get cluster status
        status = failover.get_cluster_status()
        print(f"\nCluster Status:")
        print(f"  Total nodes: {status['total_nodes']}")
        print(f"  Healthy nodes: {status['healthy_nodes']}")
        print(f"  Failed nodes: {status['failed_nodes']}")
        print(f"  Primary node: {status['primary_node']}")
        print(f"  Failover count: {status['failover_count']}")
        
    finally:
        failover.stop_health_monitoring()

if __name__ == "__main__":
    demo_fault_tolerance()
