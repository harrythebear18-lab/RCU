#!/usr/bin/env python3
"""
Software-Defined RDMA REST API
HTTP API for external integrations and remote management
"""

from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from flask_httpauth import HTTPBasicAuth
from functools import wraps
import json
import time
import threading
from typing import Dict, List, Optional, Any
from dataclasses import asdict
import logging
from datetime import datetime, timedelta

# Import our DMA components
try:
    from ultra_low_latency_userspace import UltraLowLatencyDMA
    from monitoring_system import MonitoringSystem
    from fault_tolerance_manager import FailoverManager, ClusterNode
    from security_manager import SecurityManager
    from performance_profiler import RealTimeProfiler
    from realtime_cpu_optimizer import RealTimeOptimizer
except ImportError as e:
    print(f"Warning: Some DMA components not available: {e}")

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests
auth = HTTPBasicAuth()

# Global DMA components
dma_controller = None
monitoring_system = None
failover_manager = None
security_manager = None
performance_profiler = None
cpu_optimizer = None

# API Configuration
API_VERSION = "v2.0"
API_PREFIX = f"/api/{API_VERSION}"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In-memory session storage (in production, use Redis or database)
sessions = {}

# Rate limiting
rate_limits = {}

def require_auth(f):
    """Authentication decorator"""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({'error': 'Missing authorization header'}), 401
        
        # Extract token
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
        else:
            return jsonify({'error': 'Invalid authorization format'}), 401
        
        # Validate session
        if token not in sessions:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Check session expiry
        if time.time() > sessions[token]['expires_at']:
            del sessions[token]
            return jsonify({'error': 'Token expired'}), 401
        
        # Update session activity
        sessions[token]['last_activity'] = time.time()
        
        return f(*args, **kwargs)
    
    return decorated

def rate_limit(max_requests=100, window_seconds=60):
    """Rate limiting decorator"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            client_ip = request.remote_addr
            current_time = time.time()
            
            # Clean old entries
            cutoff_time = current_time - window_seconds
            if client_ip in rate_limits:
                rate_limits[client_ip] = [t for t in rate_limits[client_ip] if t > cutoff_time]
            else:
                rate_limits[client_ip] = []
            
            # Check rate limit
            if len(rate_limits[client_ip]) >= max_requests:
                return jsonify({'error': 'Rate limit exceeded'}), 429
            
            # Add current request
            rate_limits[client_ip].append(current_time)
            
            return f(*args, **kwargs)
        
        return decorated
    return decorator

def initialize_dma_components():
    """Initialize DMA components"""
    global dma_controller, monitoring_system, failover_manager, security_manager, performance_profiler, cpu_optimizer
    
    try:
        # Initialize DMA controller
        dma_controller = UltraLowLatencyDMA()
        if dma_controller.open():
            logger.info("DMA controller initialized successfully")
        else:
            logger.error("Failed to initialize DMA controller")
        
        # Initialize monitoring system
        monitoring_system = MonitoringSystem()
        logger.info("Monitoring system initialized")
        
        # Initialize failover manager
        failover_manager = FailoverManager()
        failover_manager.start_health_monitoring()
        logger.info("Failover manager initialized")
        
        # Initialize security manager
        security_manager = SecurityManager()
        logger.info("Security manager initialized")
        
        # Initialize performance profiler
        performance_profiler = RealTimeProfiler()
        logger.info("Performance profiler initialized")
        
        # Initialize CPU optimizer
        cpu_optimizer = RealTimeOptimizer()
        cpu_optimizer.optimize_process()
        logger.info("CPU optimizer initialized")
        
    except Exception as e:
        logger.error(f"Failed to initialize DMA components: {e}")

# Authentication endpoints
@app.route(f'{API_PREFIX}/auth/login', methods=['POST'])
@rate_limit(max_requests=10, window_seconds=300)
def login():
    """User authentication"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400
        
        # Authenticate user
        session_token = security_manager.authenticate_user(username, password, request.remote_addr)
        
        if session_token:
            # Create session
            sessions[session_token] = {
                'username': username,
                'created_at': time.time(),
                'last_activity': time.time(),
                'expires_at': time.time() + 3600  # 1 hour
            }
            
            return jsonify({
                'session_token': session_token,
                'expires_in': 3600,
                'user': username
            })
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
    
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'error': 'Authentication failed'}), 500

@app.route(f'{API_PREFIX}/auth/logout', methods=['POST'])
@require_auth
def logout():
    """User logout"""
    try:
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header[7:]
            if token in sessions:
                del sessions[token]
        
        return jsonify({'message': 'Logged out successfully'})
    
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return jsonify({'error': 'Logout failed'}), 500

# DMA Management endpoints
@app.route(f'{API_PREFIX}/dma/status', methods=['GET'])
@require_auth
def get_dma_status():
    """Get DMA system status"""
    try:
        status = {
            'dma_controller': {
                'active': dma_controller is not None,
                'device_open': dma_controller.device_fd is not None if dma_controller else False,
                'active_regions': len(dma_controller.regions) if dma_controller else 0
            },
            'monitoring': {
                'active': monitoring_system is not None,
                'metrics_collected': len(monitoring_system.metrics_collector.metrics) if monitoring_system else 0
            },
            'failover': {
                'active': failover_manager is not None,
                'cluster_status': failover_manager.get_cluster_status() if failover_manager else {}
            },
            'security': {
                'active': security_manager is not None,
                'active_sessions': len(sessions),
                'security_stats': security_manager.get_security_stats() if security_manager else {}
            },
            'performance': {
                'profiling_active': performance_profiler.running if performance_profiler else False,
                'metrics_samples': len(performance_profiler.metrics_history) if performance_profiler else 0
            },
            'timestamp': time.time()
        }
        
        return jsonify(status)
    
    except Exception as e:
        logger.error(f"Status error: {e}")
        return jsonify({'error': 'Failed to get status'}), 500

@app.route(f'{API_PREFIX}/dma/regions', methods=['GET'])
@require_auth
def get_dma_regions():
    """List DMA memory regions"""
    try:
        if not dma_controller:
            return jsonify({'error': 'DMA controller not available'}), 503
        
        regions = []
        for region_id, region_info in dma_controller.regions.items():
            regions.append({
                'id': region_id,
                'start_addr': hex(region_info['start_addr']),
                'size': region_info['size'],
                'remote_host': region_info['remote_host'],
                'remote_port': region_info['remote_port'],
                'active': region_info['active']
            })
        
        return jsonify({'regions': regions})
    
    except Exception as e:
        logger.error(f"Regions error: {e}")
        return jsonify({'error': 'Failed to get regions'}), 500

@app.route(f'{API_PREFIX}/dma/regions', methods=['POST'])
@require_auth
def add_dma_region():
    """Add DMA memory region"""
    try:
        if not dma_controller:
            return jsonify({'error': 'DMA controller not available'}), 503
        
        data = request.get_json()
        start_addr = int(data.get('start_addr'), 16) if isinstance(data.get('start_addr'), str) else data.get('start_addr')
        size = data.get('size')
        remote_host = data.get('remote_host')
        remote_port = data.get('remote_port')
        
        if not all([start_addr, size, remote_host, remote_port]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Check permissions
        username = sessions[request.headers.get('Authorization')[7:]]['username']
        if not security_manager.check_permission(username, 'region_management', 'create'):
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        region_id = dma_controller.add_region(start_addr, size, remote_host, remote_port)
        
        return jsonify({
            'message': 'Region added successfully',
            'region_id': region_id,
            'start_addr': hex(start_addr),
            'size': size,
            'remote_host': remote_host,
            'remote_port': remote_port
        }), 201
    
    except Exception as e:
        logger.error(f"Add region error: {e}")
        return jsonify({'error': 'Failed to add region'}), 500

@app.route(f'{API_PREFIX}/dma/regions/<int:region_id>/write', methods=['POST'])
@require_auth
def write_dma_memory(region_id):
    """Write to DMA memory region"""
    try:
        if not dma_controller:
            return jsonify({'error': 'DMA controller not available'}), 503
        
        data = request.get_json()
        offset = data.get('offset', 0)
        data_hex = data.get('data')
        
        if not data_hex:
            return jsonify({'error': 'Data required'}), 400
        
        # Convert hex to bytes
        try:
            data_bytes = bytes.fromhex(data_hex)
        except ValueError:
            return jsonify({'error': 'Invalid hex data'}), 400
        
        # Check permissions
        username = sessions[request.headers.get('Authorization')[7:]]['username']
        if not security_manager.check_permission(username, f'region_{region_id}', 'write'):
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        success = dma_controller.write_memory_ultra_fast(region_id, offset, data_bytes)
        
        if success:
            return jsonify({
                'message': 'Memory write successful',
                'region_id': region_id,
                'offset': offset,
                'bytes_written': len(data_bytes)
            })
        else:
            return jsonify({'error': 'Memory write failed'}), 500
    
    except Exception as e:
        logger.error(f"Write memory error: {e}")
        return jsonify({'error': 'Failed to write memory'}), 500

# Monitoring endpoints
@app.route(f'{API_PREFIX}/monitoring/metrics', methods=['GET'])
@require_auth
def get_metrics():
    """Get monitoring metrics"""
    try:
        if not monitoring_system:
            return jsonify({'error': 'Monitoring system not available'}), 503
        
        # Get recent metrics
        recent_metrics = monitoring_system.metrics_collector.get_recent_metrics(300)  # Last 5 minutes
        
        # Format for API response
        formatted_metrics = {}
        for metric_name, metric_data in recent_metrics.items():
            formatted_metrics[metric_name] = [
                {
                    'timestamp': point.timestamp,
                    'value': point.value,
                    'unit': point.unit
                }
                for point in metric_data[-100:]  # Last 100 points
            ]
        
        return jsonify({
            'metrics': formatted_metrics,
            'timestamp': time.time(),
            'sample_count': len(formatted_metrics)
        })
    
    except Exception as e:
        logger.error(f"Metrics error: {e}")
        return jsonify({'error': 'Failed to get metrics'}), 500

@app.route(f'{API_PREFIX}/monitoring/alerts', methods=['GET'])
@require_auth
def get_alerts():
    """Get active alerts"""
    try:
        if not monitoring_system:
            return jsonify({'error': 'Monitoring system not available'}), 503
        
        active_alerts = monitoring_system.alert_manager.get_active_alerts()
        
        formatted_alerts = []
        for alert in active_alerts:
            formatted_alerts.append({
                'id': alert.id,
                'name': alert.name,
                'description': alert.description,
                'severity': alert.severity,
                'last_triggered': alert.last_triggered,
                'trigger_count': alert.trigger_count
            })
        
        return jsonify({
            'alerts': formatted_alerts,
            'count': len(formatted_alerts),
            'timestamp': time.time()
        })
    
    except Exception as e:
        logger.error(f"Alerts error: {e}")
        return jsonify({'error': 'Failed to get alerts'}), 500

@app.route(f'{API_PREFIX}/monitoring/health', methods=['GET'])
@require_auth
def get_health_status():
    """Get system health status"""
    try:
        if not monitoring_system:
            return jsonify({'error': 'Monitoring system not available'}), 503
        
        health_status = monitoring_system.health_checker.get_health_status()
        
        return jsonify({
            'health': health_status,
            'overall_healthy': monitoring_system.health_checker.is_healthy(),
            'timestamp': time.time()
        })
    
    except Exception as e:
        logger.error(f"Health status error: {e}")
        return jsonify({'error': 'Failed to get health status'}), 500

# Performance endpoints
@app.route(f'{API_PREFIX}/performance/benchmark', methods=['POST'])
@require_auth
def run_benchmark():
    """Run performance benchmark"""
    try:
        if not performance_profiler:
            return jsonify({'error': 'Performance profiler not available'}), 503
        
        # Check permissions
        username = sessions[request.headers.get('Authorization')[7:]]['username']
        if not security_manager.check_permission(username, 'benchmark', 'run'):
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        # Start profiling
        performance_profiler.start_profiling()
        
        # Simulate benchmark workload
        time.sleep(5)  # In real implementation, would run actual benchmark
        
        # Stop profiling
        performance_profiler.stop_profiling()
        
        # Get results
        metrics_summary = performance_profiler.get_metrics_summary()
        bottleneck_report = performance_profiler.get_bottleneck_report()
        
        return jsonify({
            'message': 'Benchmark completed',
            'metrics_summary': metrics_summary,
            'bottleneck_report': bottleneck_report,
            'timestamp': time.time()
        })
    
    except Exception as e:
        logger.error(f"Benchmark error: {e}")
        return jsonify({'error': 'Failed to run benchmark'}), 500

@app.route(f'{API_PREFIX}/performance/profile', methods=['GET'])
@require_auth
def get_performance_profile():
    """Get current performance profile"""
    try:
        if not performance_profiler:
            return jsonify({'error': 'Performance profiler not available'}), 503
        
        metrics_summary = performance_profiler.get_metrics_summary()
        bottleneck_report = performance_profiler.get_bottleneck_report()
        
        return jsonify({
            'metrics_summary': metrics_summary,
            'bottleneck_report': bottleneck_report,
            'profiling_active': performance_profiler.running,
            'timestamp': time.time()
        })
    
    except Exception as e:
        logger.error(f"Profile error: {e}")
        return jsonify({'error': 'Failed to get performance profile'}), 500

# Failover endpoints
@app.route(f'{API_PREFIX}/failover/cluster', methods=['GET'])
@require_auth
def get_cluster_status():
    """Get cluster failover status"""
    try:
        if not failover_manager:
            return jsonify({'error': 'Failover manager not available'}), 503
        
        cluster_status = failover_manager.get_cluster_status()
        
        return jsonify({
            'cluster': cluster_status,
            'timestamp': time.time()
        })
    
    except Exception as e:
        logger.error(f"Cluster status error: {e}")
        return jsonify({'error': 'Failed to get cluster status'}), 500

@app.route(f'{API_PREFIX}/failover/nodes', methods=['GET'])
@require_auth
def get_cluster_nodes():
    """Get cluster nodes"""
    try:
        if not failover_manager:
            return jsonify({'error': 'Failover manager not available'}), 503
        
        nodes = []
        for node_id, node in failover_manager.nodes.items():
            nodes.append({
                'id': node.node_id,
                'host': node.host,
                'port': node.port,
                'role': node.role,
                'region': node.region,
                'status': node.status.value,
                'active_connections': node.active_connections,
                'max_connections': node.max_connections,
                'response_time': node.response_time,
                'failure_count': node.failure_count
            })
        
        return jsonify({
            'nodes': nodes,
            'count': len(nodes),
            'timestamp': time.time()
        })
    
    except Exception as e:
        logger.error(f"Nodes error: {e}")
        return jsonify({'error': 'Failed to get cluster nodes'}), 500

# Utility endpoints
@app.route(f'{API_PREFIX}/system/info', methods=['GET'])
@require_auth
def get_system_info():
    """Get system information"""
    try:
        import psutil
        import platform
        
        system_info = {
            'platform': {
                'system': platform.system(),
                'release': platform.release(),
                'version': platform.version(),
                'machine': platform.machine(),
                'processor': platform.processor()
            },
            'cpu': {
                'count_logical': psutil.cpu_count(logical=True),
                'count_physical': psutil.cpu_count(logical=False),
                'frequency': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None,
                'percent': psutil.cpu_percent(interval=1)
            },
            'memory': {
                'total': psutil.virtual_memory().total,
                'available': psutil.virtual_memory().available,
                'percent': psutil.virtual_memory().percent,
                'used': psutil.virtual_memory().used,
                'free': psutil.virtual_memory().free
            },
            'disk': {
                'total': psutil.disk_usage('/').total,
                'used': psutil.disk_usage('/').used,
                'free': psutil.disk_usage('/').free,
                'percent': psutil.disk_usage('/').percent
            },
            'network': {
                'bytes_sent': psutil.net_io_counters().bytes_sent,
                'bytes_recv': psutil.net_io_counters().bytes_recv,
                'packets_sent': psutil.net_io_counters().packets_sent,
                'packets_recv': psutil.net_io_counters().packets_recv
            },
            'timestamp': time.time()
        }
        
        return jsonify(system_info)
    
    except Exception as e:
        logger.error(f"System info error: {e}")
        return jsonify({'error': 'Failed to get system info'}), 500

@app.route(f'{API_PREFIX}/version', methods=['GET'])
def get_api_version():
    """Get API version information"""
    return jsonify({
        'api_version': API_VERSION,
        'software_version': '2.0.0',
        'build_date': '2024-01-01',
        'features': [
            'Ultra-low-latency DMA',
            'Real-time monitoring',
            'Fault tolerance',
            'Security management',
            'Performance profiling',
            'Windows compatibility'
        ],
        'endpoints': [
            '/auth/login',
            '/auth/logout',
            '/dma/status',
            '/dma/regions',
            '/monitoring/metrics',
            '/monitoring/alerts',
            '/performance/benchmark',
            '/failover/cluster',
            '/system/info'
        ]
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({'error': 'Method not allowed'}), 405

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

# Cleanup expired sessions
def cleanup_sessions():
    """Clean up expired sessions"""
    current_time = time.time()
    expired_tokens = [token for token, session in sessions.items() 
                     if current_time > session['expires_at']]
    
    for token in expired_tokens:
        del sessions[token]
    
    if expired_tokens:
        logger.info(f"Cleaned up {len(expired_tokens)} expired sessions")

# Background tasks
def background_tasks():
    """Run background maintenance tasks"""
    while True:
        try:
            cleanup_sessions()
            time.sleep(300)  # Run every 5 minutes
        except Exception as e:
            logger.error(f"Background task error: {e}")
            time.sleep(60)

def create_app():
    """Create and configure Flask app"""
    # Initialize DMA components
    initialize_dma_components()
    
    # Start background tasks
    background_thread = threading.Thread(target=background_tasks, daemon=True)
    background_thread.start()
    
    logger.info("RDMA REST API initialized")
    return app

if __name__ == '__main__':
    app = create_app()
    
    # Run the API server
    app.run(
        host='0.0.0.0',
        port=8080,
        debug=False,
        threaded=True
    )
