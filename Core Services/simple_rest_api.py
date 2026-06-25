#!/usr/bin/env python3
"""
Simple REST API for Homelab Portal
Basic API server for testing
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import logging

app = Flask(__name__)
CORS(app)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'message': 'Homelab Portal API is running'
    })

@app.route('/api/portal/status', methods=['GET'])
def portal_status():
    """Portal status endpoint"""
    return jsonify({
        'status': 'active',
        'node_id': 'test-node-123',
        'hostname': 'Homelab-PC',
        'ip_address': '192.168.1.100',
        'port': 30000,
        'active_nodes_count': 1,
        'active_sessions_count': 0,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/nodes', methods=['GET'])
def get_nodes():
    """Get nodes endpoint"""
    return jsonify({
        'nodes': [
            {
                'node_id': 'test-node-123',
                'hostname': 'Homelab-PC',
                'ip_address': '192.168.1.100',
                'port': 30000,
                'status': 'active',
                'capabilities': ['screen', 'sound', 'file', 'resource']
            }
        ],
        'count': 1,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/hardware/info', methods=['GET'])
def get_hardware_info():
    """Get hardware info endpoint"""
    return jsonify({
        'hardware_info': {
            'cpu': {
                'name': 'Intel(R) Core(TM) i7-10700K',
                'is_intel': True
            },
            'gpu': {
                'name': 'NVIDIA GeForce RTX 3080',
                'is_nvidia': True
            },
            'windows_version': 'Windows 11',
            'memory_info': {
                'total_gb': 32.0,
                'available_gb': 24.5
            }
        },
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/test', methods=['GET', 'POST'])
def test_endpoint():
    """Test endpoint"""
    if request.method == 'GET':
        return jsonify({
            'message': 'GET request received',
            'method': 'GET',
            'timestamp': datetime.now().isoformat()
        })
    else:
        data = request.get_json()
        return jsonify({
            'message': 'POST request received',
            'method': 'POST',
            'data': data,
            'timestamp': datetime.now().isoformat()
        })

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    logger.info("Starting Simple Homelab Portal REST API")
    logger.info("API will be available at: http://localhost:8080")
    logger.info("Available endpoints:")
    logger.info("  GET  /api/health")
    logger.info("  GET  /api/portal/status")
    logger.info("  GET  /api/nodes")
    logger.info("  GET  /api/hardware/info")
    logger.info("  GET/POST /api/test")
    
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
