#!/usr/bin/env python3
"""
Portal API Endpoints for Homelab REST API
Additional endpoints for portal-specific functionality
"""

from flask import request, jsonify
from datetime import datetime
import logging
from functools import wraps

class PortalAPIEndpoints:
    """Portal-specific API endpoints"""
    
    def __init__(self, api_instance):
        self.api = api_instance
        self.logger = logging.getLogger("PortalAPI")
        
    def register_endpoints(self):
        """Register portal-specific endpoints"""
        app = self.api.app
        
        # Portal endpoints
        @app.route('/api/portal/status', methods=['GET'])
        def get_portal_status():
            """Get portal status and information"""
            try:
                portal_info = self.api.portal.hardware_info
                active_nodes = self.api.portal.get_active_nodes()
                active_sessions = self.api.portal.get_active_sessions()
                
                return jsonify({
                    'status': 'active',
                    'node_id': self.api.portal.node_id,
                    'hostname': self.api.portal.hostname,
                    'ip_address': self.api.portal.ip_address,
                    'port': self.api.portal.port,
                    'hardware_info': portal_info,
                    'active_nodes_count': len(active_nodes),
                    'active_sessions_count': len(active_sessions),
                    'capabilities': [cap.value for cap in self.api.portal.capabilities],
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @app.route('/api/portal/nodes', methods=['GET'])
        def get_portal_nodes():
            """Get list of active portal nodes"""
            try:
                nodes = self.api.portal.get_active_nodes()
                nodes_list = []
                
                for node in nodes:
                    nodes_list.append({
                        'node_id': node.node_id,
                        'hostname': node.hostname,
                        'ip_address': node.ip_address,
                        'port': node.port,
                        'capabilities': [cap.value for cap in node.capabilities],
                        'status': node.status,
                        'last_seen': node.last_seen,
                        'metadata': node.metadata
                    })
                
                return jsonify({
                    'nodes': nodes_list,
                    'count': len(nodes_list),
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @app.route('/api/portal/sessions', methods=['GET'])
        def get_portal_sessions():
            """Get list of active portal sessions"""
            try:
                sessions = self.api.portal.get_active_sessions()
                sessions_list = []
                
                for session in sessions:
                    sessions_list.append({
                        'session_id': session.session_id,
                        'source_node': session.source_node,
                        'target_node': session.target_node,
                        'share_type': session.share_type.value,
                        'status': session.status,
                        'created_at': session.created_at,
                        'metadata': session.metadata
                    })
                
                return jsonify({
                    'sessions': sessions_list,
                    'count': len(sessions_list),
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @app.route('/api/portal/connect', methods=['POST'])
        def connect_to_node():
            """Connect to a portal node"""
            try:
                data = request.get_json()
                target_ip = data.get('target_ip')
                target_port = data.get('target_port', 30000)
                
                if not target_ip:
                    return jsonify({'error': 'target_ip is required'}), 400
                
                success = self.api.portal.connect_to_node(target_ip, target_port)
                
                if success:
                    return jsonify({
                        'success': True,
                        'message': f'Connected to {target_ip}:{target_port}',
                        'timestamp': datetime.now().isoformat()
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': 'Failed to connect to node'
                    }), 400
                    
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @app.route('/api/portal/share/file', methods=['POST'])
        def share_file():
            """Share file with target node"""
            try:
                data = request.get_json()
                file_path = data.get('file_path')
                target_node = data.get('target_node')
                
                if not file_path or not target_node:
                    return jsonify({'error': 'file_path and target_node are required'}), 400
                
                success = self.api.portal.share_file(file_path, target_node)
                
                if success:
                    return jsonify({
                        'success': True,
                        'message': f'File shared with {target_node}',
                        'file_path': file_path,
                        'timestamp': datetime.now().isoformat()
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': 'Failed to share file'
                    }), 400
                    
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @app.route('/api/portal/share/screen', methods=['POST'])
        def start_screen_share():
            """Start screen sharing session"""
            try:
                data = request.get_json()
                target_node = data.get('target_node')
                
                if not target_node:
                    return jsonify({'error': 'target_node is required'}), 400
                
                session_id = self.api.portal.start_screen_share(target_node)
                
                if session_id:
                    return jsonify({
                        'success': True,
                        'session_id': session_id,
                        'message': f'Screen sharing started with {target_node}',
                        'timestamp': datetime.now().isoformat()
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': 'Failed to start screen sharing'
                    }), 400
                    
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @app.route('/api/portal/share/sound', methods=['POST'])
        def start_sound_share():
            """Start sound sharing session"""
            try:
                data = request.get_json()
                target_node = data.get('target_node')
                
                if not target_node:
                    return jsonify({'error': 'target_node is required'}), 400
                
                session_id = self.api.portal.start_sound_share(target_node)
                
                if session_id:
                    return jsonify({
                        'success': True,
                        'session_id': session_id,
                        'message': f'Sound sharing started with {target_node}',
                        'timestamp': datetime.now().isoformat()
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': 'Failed to start sound sharing'
                    }), 400
                    
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        # GPU Sharing endpoints
        @app.route('/api/gpu/status', methods=['GET'])
        def get_gpu_status():
            """Get GPU sharing status"""
            try:
                status = self.api.gpu_sharing.get_gpu_sharing_status()
                return jsonify({
                    'gpu_status': status,
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @app.route('/api/gpu/share', methods=['POST'])
        def share_gpu_compute():
            """Share GPU compute with target node"""
            try:
                data = request.get_json()
                target_node = data.get('target_node')
                compute_task = data.get('compute_task', {})
                
                if not target_node:
                    return jsonify({'error': 'target_node is required'}), 400
                
                session_id = self.api.gpu_sharing.share_gpu_compute(target_node, compute_task)
                
                if session_id:
                    return jsonify({
                        'success': True,
                        'session_id': session_id,
                        'message': f'GPU compute shared with {target_node}',
                        'timestamp': datetime.now().isoformat()
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': 'Failed to share GPU compute'
                    }), 400
                    
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @app.route('/api/gpu/monitor', methods=['GET'])
        def monitor_gpu_performance():
            """Monitor GPU performance"""
            try:
                performance = self.api.gpu_sharing.monitor_gpu_performance()
                return jsonify({
                    'gpu_performance': performance,
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        # RAM Sharing endpoints
        @app.route('/api/ram/status', methods=['GET'])
        def get_ram_status():
            """Get RAM sharing status"""
            try:
                status = self.api.ram_sharing.get_ram_sharing_status()
                return jsonify({
                    'ram_status': status,
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @app.route('/api/ram/share', methods=['POST'])
        def share_ram_region():
            """Share RAM region with target node"""
            try:
                data = request.get_json()
                target_node = data.get('target_node')
                size_mb = data.get('size_mb', 512)
                region_name = data.get('region_name', 'shared_region')
                
                if not target_node:
                    return jsonify({'error': 'target_node is required'}), 400
                
                region_id = self.api.ram_sharing.share_ram_region(target_node, size_mb, region_name)
                
                if region_id:
                    return jsonify({
                        'success': True,
                        'region_id': region_id,
                        'message': f'RAM region shared with {target_node}',
                        'size_mb': size_mb,
                        'timestamp': datetime.now().isoformat()
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': 'Failed to share RAM region'
                    }), 400
                    
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @app.route('/api/ram/access', methods=['POST'])
        def access_shared_ram():
            """Access shared RAM from source node"""
            try:
                data = request.get_json()
                source_node = data.get('source_node')
                region_id = data.get('region_id')
                operation = data.get('operation', 'read')
                access_data = data.get('data')
                
                if not source_node or not region_id:
                    return jsonify({'error': 'source_node and region_id are required'}), 400
                
                result = self.api.ram_sharing.access_shared_ram(source_node, region_id, operation, access_data)
                
                return jsonify({
                    'success': True,
                    'result': result,
                    'timestamp': datetime.now().isoformat()
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        # Screen Sharing endpoints
        @app.route('/api/screen/status', methods=['GET'])
        def get_screen_status():
            """Get screen sharing status"""
            try:
                status = self.api.screen_sharing.get_screen_sharing_status()
                return jsonify({
                    'screen_status': status,
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @app.route('/api/screen/benchmark', methods=['GET'])
        def benchmark_screen_capture():
            """Benchmark screen capture performance"""
            try:
                benchmarks = self.api.screen_sharing.benchmark_screen_capture()
                return jsonify({
                    'screen_benchmarks': benchmarks,
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        # Hardware Optimization endpoints
        @app.route('/api/hardware/info', methods=['GET'])
        def get_hardware_info():
            """Get hardware information"""
            try:
                hardware_info = self.api.hardware_optimizer.get_system_info()
                return jsonify({
                    'hardware_info': hardware_info,
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @app.route('/api/hardware/benchmarks', methods=['GET'])
        def get_hardware_benchmarks():
            """Get hardware performance benchmarks"""
            try:
                benchmarks = self.api.hardware_optimizer.get_performance_benchmarks()
                return jsonify({
                    'hardware_benchmarks': benchmarks,
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @app.route('/api/hardware/optimize', methods=['POST'])
        def optimize_hardware():
            """Optimize hardware for portal"""
            try:
                success = self.api.hardware_optimizer.optimize_for_identical_hardware()
                
                if success:
                    return jsonify({
                        'success': True,
                        'message': 'Hardware optimization completed',
                        'timestamp': datetime.now().isoformat()
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': 'Hardware optimization failed'
                    }), 400
                    
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        # Compatibility endpoints
        @app.route('/api/hardware/compatibility', methods=['POST'])
        def check_hardware_compatibility():
            """Check hardware compatibility with remote system"""
            try:
                data = request.get_json()
                remote_system_info = data.get('remote_system_info')
                
                if not remote_system_info:
                    return jsonify({'error': 'remote_system_info is required'}), 400
                
                compatibility = self.api.hardware_optimizer.check_hardware_compatibility(remote_system_info)
                
                return jsonify({
                    'compatibility': compatibility,
                    'timestamp': datetime.now().isoformat()
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        self.logger.info("Portal API endpoints registered")
