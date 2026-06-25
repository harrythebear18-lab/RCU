#!/usr/bin/env python3
"""
System API Server
REST API endpoints for system management, optimization, and data export.
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import json
import os
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any
import threading
import time
import psutil
import subprocess
from system_health_scorer import SystemHealthScorer
from performance_reports import PerformanceReports
from backup_manager import BackupManager
from email_notifications import EmailNotificationManager

app = Flask(__name__)
CORS(app)

# Initialize components
health_scorer = SystemHealthScorer()
performance_reports = PerformanceReports()
backup_manager = BackupManager()
email_notifications = EmailNotificationManager()

# API Configuration
API_VERSION = "v1"
BASE_URL = f"/api/{API_VERSION}"

class SystemAPI:
    """System API Server"""
    
    def __init__(self):
        self.app = app
        self.setup_routes()
        self.api_key = self.get_api_key()
        
    def get_api_key(self) -> str:
        """Get or generate API key"""
        api_key_file = os.path.join(os.path.dirname(__file__), "api_key.txt")
        if os.path.exists(api_key_file):
            with open(api_key_file, 'r') as f:
                return f.read().strip()
        else:
            import secrets
            api_key = secrets.token_urlsafe(32)
            with open(api_key_file, 'w') as f:
                f.write(api_key)
            return api_key
    
    def setup_routes(self):
        """Setup API routes"""
        
        @self.app.route(f'{BASE_URL}/system/status', methods=['GET'])
        def get_system_status():
            """Get current system status"""
            try:
                # Get current metrics
                metrics = self.get_current_metrics()
                
                # Calculate health score
                health_score = health_scorer.calculate_current_health_score(metrics)
                
                # Get system information
                system_info = {
                    "hostname": os.environ.get('COMPUTERNAME', 'Unknown'),
                    "os": os.name,
                    "cpu_count": psutil.cpu_count(),
                    "memory_total": psutil.virtual_memory().total,
                    "disk_total": psutil.disk_usage('/').total,
                    "uptime": time.time() - psutil.boot_time()
                }
                
                return jsonify({
                    "status": "healthy",
                    "timestamp": datetime.now().isoformat(),
                    "metrics": metrics,
                    "health_score": health_score,
                    "system_info": system_info,
                    "api_version": API_VERSION
                })
                
            except Exception as e:
                return jsonify({
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }), 500
        
        @self.app.route(f'{BASE_URL}/system/optimize', methods=['POST'])
        def optimize_system():
            """Trigger system optimization"""
            try:
                data = request.get_json() or {}
                optimization_type = data.get('type', 'balanced')
                intensity = data.get('intensity', 'medium')
                
                # Validate optimization type
                valid_types = ['balanced', 'gaming', 'productivity', 'multimedia', 'development']
                if optimization_type not in valid_types:
                    return jsonify({
                        "error": f"Invalid optimization type. Valid types: {valid_types}"
                    }), 400
                
                # Execute optimization
                result = self.execute_optimization(optimization_type, intensity)
                
                return jsonify({
                    "status": "success",
                    "optimization_type": optimization_type,
                    "intensity": intensity,
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                })
                
            except Exception as e:
                return jsonify({
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }), 500
        
        @self.app.route(f'{BASE_URL}/data/export', methods=['GET', 'POST'])
        def export_data():
            """Export system data"""
            try:
                if request.method == 'POST':
                    data = request.get_json() or {}
                    export_format = data.get('format', 'json')
                    date_range = data.get('date_range', 'daily')
                else:
                    export_format = request.args.get('format', 'json')
                    date_range = request.args.get('date_range', 'daily')
                
                # Validate format
                valid_formats = ['json', 'csv', 'html']
                if export_format not in valid_formats:
                    return jsonify({
                        "error": f"Invalid format. Valid formats: {valid_formats}"
                    }), 400
                
                # Generate export
                if date_range == 'daily':
                    report = performance_reports.generate_daily_report()
                elif date_range == 'weekly':
                    report = performance_reports.generate_weekly_report()
                else:
                    return jsonify({
                        "error": "Invalid date_range. Use 'daily' or 'weekly'"
                    }), 400
                
                if "error" in report:
                    return jsonify(report), 400
                
                # Export data
                if export_format == 'json':
                    return jsonify(report)
                elif export_format == 'csv':
                    return self.export_csv(report)
                elif export_format == 'html':
                    return self.export_html(report)
                
            except Exception as e:
                return jsonify({
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }), 500
        
        @self.app.route(f'{BASE_URL}/alerts/configure', methods=['GET', 'POST', 'PUT'])
        def configure_alerts():
            """Configure alert settings"""
            try:
                if request.method == 'GET':
                    # Get current alert configuration
                    return jsonify(self.get_alert_config())
                
                elif request.method in ['POST', 'PUT']:
                    # Update alert configuration
                    data = request.get_json()
                    result = self.update_alert_config(data)
                    
                    return jsonify({
                        "status": "success",
                        "message": "Alert configuration updated",
                        "config": result,
                        "timestamp": datetime.now().isoformat()
                    })
                    
            except Exception as e:
                return jsonify({
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }), 500
        
        @self.app.route(f'{BASE_URL}/profiles/manage', methods=['GET', 'POST', 'PUT', 'DELETE'])
        def manage_profiles():
            """Manage optimization profiles"""
            try:
                if request.method == 'GET':
                    # Get all profiles
                    return jsonify(self.get_profiles())
                
                elif request.method == 'POST':
                    # Create new profile
                    data = request.get_json()
                    result = self.create_profile(data)
                    
                    return jsonify({
                        "status": "success",
                        "message": "Profile created",
                        "profile": result,
                        "timestamp": datetime.now().isoformat()
                    })
                
                elif request.method == 'PUT':
                    # Update existing profile
                    data = request.get_json()
                    profile_id = data.get('id')
                    result = self.update_profile(profile_id, data)
                    
                    return jsonify({
                        "status": "success",
                        "message": "Profile updated",
                        "profile": result,
                        "timestamp": datetime.now().isoformat()
                    })
                
                elif request.method == 'DELETE':
                    # Delete profile
                    profile_id = request.args.get('id')
                    if not profile_id:
                        return jsonify({"error": "Profile ID required"}), 400
                    
                    result = self.delete_profile(profile_id)
                    
                    return jsonify({
                        "status": "success",
                        "message": "Profile deleted",
                        "timestamp": datetime.now().isoformat()
                    })
                    
            except Exception as e:
                return jsonify({
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }), 500
        
        @self.app.route(f'{BASE_URL}/health', methods=['GET'])
        def health_check():
            """API health check"""
            return jsonify({
                "status": "healthy",
                "api_version": API_VERSION,
                "timestamp": datetime.now().isoformat(),
                "uptime": time.time() - psutil.boot_time()
            })
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current system metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_freq = psutil.cpu_freq()
            cpu_temp = self.get_cpu_temperature()
            
            # Memory metrics
            memory = psutil.virtual_memory()
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_io = psutil.disk_io_counters()
            
            # Network metrics
            network = psutil.net_io_counters()
            
            # GPU metrics (if available)
            gpu_metrics = self.get_gpu_metrics()
            
            return {
                "cpu": {
                    "usage": cpu_percent,
                    "frequency": cpu_freq.current if cpu_freq else 0,
                    "temperature": cpu_temp
                },
                "memory": {
                    "usage": memory.percent,
                    "used": memory.used,
                    "total": memory.total,
                    "available": memory.available
                },
                "disk": {
                    "usage": disk.percent,
                    "used": disk.used,
                    "total": disk.total,
                    "free": disk.free,
                    "read_bytes": disk_io.read_bytes if disk_io else 0,
                    "write_bytes": disk_io.write_bytes if disk_io else 0
                },
                "network": {
                    "bytes_sent": network.bytes_sent,
                    "bytes_recv": network.bytes_recv,
                    "packets_sent": network.packets_sent,
                    "packets_recv": network.packets_recv
                },
                "gpu": gpu_metrics
            }
            
        except Exception as e:
            raise Exception(f"Failed to get metrics: {e}")
    
    def get_cpu_temperature(self) -> float:
        """Get CPU temperature"""
        try:
            import wmi
            c = wmi.WMI()
            for temp in c.Win32_TemperatureProbe():
                if temp.CurrentReading:
                    return temp.CurrentReading / 10.0  # Convert to Celsius
            return 0.0
        except:
            return 0.0
    
    def get_gpu_metrics(self) -> Dict[str, Any]:
        """Get GPU metrics"""
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu = gpus[0]
                return {
                    "usage": gpu.load * 100,
                    "memory_used": gpu.memoryUsed,
                    "memory_total": gpu.memoryTotal,
                    "temperature": gpu.temperature
                }
        except:
            pass
        
        return {"usage": 0, "memory_used": 0, "memory_total": 0, "temperature": 0}
    
    def execute_optimization(self, optimization_type: str, intensity: str) -> Dict[str, Any]:
        """Execute system optimization"""
        try:
            # Import resource optimizer
            import resource_optimizer_fixed
            
            # Create optimizer instance
            optimizer = resource_optimizer_fixed.ResourceOptimizer()
            
            # Start optimization with specified profile
            success = optimizer.start_optimization(optimization_type)
            
            if success:
                return {
                    "status": "success",
                    "profile": optimization_type,
                    "intensity": intensity,
                    "message": f"Optimization started with {optimization_type} profile"
                }
            else:
                return {
                    "status": "failed",
                    "message": "Failed to start optimization"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def export_csv(self, data: Dict[str, Any]):
        """Export data as CSV"""
        import io
        import csv
        
        output = io.StringIO()
        
        if 'summary' in data:
            writer = csv.writer(output)
            writer.writerow(['Metric', 'Value'])
            
            summary = data['summary']
            writer.writerow(['Average CPU', f"{summary.get('average_cpu', 0):.2f}%"])
            writer.writerow(['Max CPU', f"{summary.get('max_cpu', 0):.2f}%"])
            writer.writerow(['Average Memory', f"{summary.get('average_memory', 0):.2f}%"])
            writer.writerow(['Max Memory', f"{summary.get('max_memory', 0):.2f}%"])
            writer.writerow(['Total Network I/O', f"{summary.get('total_network_io', 0):.2f} MB"])
            writer.writerow(['Total Disk I/O', f"{summary.get('total_disk_io', 0):.2f} MB"])
        
        output.seek(0)
        return output.getvalue(), 200, {
            'Content-Type': 'text/csv',
            'Content-Disposition': 'attachment; filename=system_export.csv'
        }
    
    def export_html(self, data: Dict[str, Any]):
        """Export data as HTML"""
        html_content = performance_reports.export_report_to_html(data, "temp_report.html")
        
        return html_content, 200, {
            'Content-Type': 'text/html',
            'Content-Disposition': 'attachment; filename=system_report.html'
        }
    
    def get_alert_config(self) -> Dict[str, Any]:
        """Get current alert configuration"""
        try:
            from settings_manager import SettingsManager
            settings_manager = SettingsManager()
            
            return {
                "cpu_threshold": settings_manager.get_setting('alerts', 'cpu_warning', 80),
                "memory_threshold": settings_manager.get_setting('alerts', 'memory_warning', 85),
                "gpu_threshold": settings_manager.get_setting('alerts', 'gpu_warning', 85),
                "temperature_threshold": settings_manager.get_setting('alerts', 'temp_warning', 75),
                "enable_notifications": settings_manager.get_setting('alerts', 'enable_alerts', True),
                "email_notifications": settings_manager.get_setting('notifications', 'email_enabled', False)
            }
        except Exception as e:
            return {"error": str(e)}
    
    def update_alert_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Update alert configuration"""
        try:
            from settings_manager import SettingsManager
            settings_manager = SettingsManager()
            
            # Update alert settings
            settings_manager.set_setting('alerts', 'cpu_warning', config.get('cpu_threshold', 80))
            settings_manager.set_setting('alerts', 'memory_warning', config.get('memory_threshold', 85))
            settings_manager.set_setting('alerts', 'gpu_warning', config.get('gpu_threshold', 85))
            settings_manager.set_setting('alerts', 'temp_warning', config.get('temperature_threshold', 75))
            settings_manager.set_setting('alerts', 'enable_alerts', config.get('enable_notifications', True))
            settings_manager.set_setting('notifications', 'email_enabled', config.get('email_notifications', False))
            
            return config
            
        except Exception as e:
            raise Exception(f"Failed to update alert config: {e}")
    
    def get_profiles(self) -> List[Dict[str, Any]]:
        """Get all optimization profiles"""
        try:
            from settings_manager import SettingsManager
            settings_manager = SettingsManager()
            
            # Get default profiles
            default_profiles = settings_manager.get_setting('optimization', 'profiles', {})
            
            # Get custom profiles
            custom_profiles = settings_manager.get_setting('optimization', 'custom_profiles', {})
            
            # Combine profiles
            all_profiles = {**default_profiles, **custom_profiles}
            
            return [{"id": k, **v} for k, v in all_profiles.items()]
            
        except Exception as e:
            return [{"error": str(e)}]
    
    def create_profile(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new optimization profile"""
        try:
            from settings_manager import SettingsManager
            settings_manager = SettingsManager()
            
            # Generate profile ID
            import uuid
            profile_id = str(uuid.uuid4())[:8]
            
            # Validate profile data
            required_fields = ['name', 'cpu_priority', 'memory_priority', 'gpu_priority']
            for field in required_fields:
                if field not in profile_data:
                    raise Exception(f"Missing required field: {field}")
            
            # Add profile to custom profiles
            custom_profiles = settings_manager.get_setting('optimization', 'custom_profiles', {})
            custom_profiles[profile_id] = profile_data
            settings_manager.set_setting('optimization', 'custom_profiles', custom_profiles)
            
            return {"id": profile_id, **profile_data}
            
        except Exception as e:
            raise Exception(f"Failed to create profile: {e}")
    
    def update_profile(self, profile_id: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update existing profile"""
        try:
            from settings_manager import SettingsManager
            settings_manager = SettingsManager()
            
            custom_profiles = settings_manager.get_setting('optimization', 'custom_profiles', {})
            
            if profile_id not in custom_profiles:
                raise Exception(f"Profile {profile_id} not found")
            
            # Update profile
            custom_profiles[profile_id].update(profile_data)
            settings_manager.set_setting('optimization', 'custom_profiles', custom_profiles)
            
            return custom_profiles[profile_id]
            
        except Exception as e:
            raise Exception(f"Failed to update profile: {e}")
    
    def delete_profile(self, profile_id: str) -> bool:
        """Delete profile"""
        try:
            from settings_manager import SettingsManager
            settings_manager = SettingsManager()
            
            custom_profiles = settings_manager.get_setting('optimization', 'custom_profiles', {})
            
            if profile_id in custom_profiles:
                del custom_profiles[profile_id]
                settings_manager.set_setting('optimization', 'custom_profiles', custom_profiles)
                return True
            else:
                raise Exception(f"Profile {profile_id} not found")
                
        except Exception as e:
            raise Exception(f"Failed to delete profile: {e}")
    
    def run(self, host='127.0.0.1', port=5000, debug=False):
        """Run the API server"""
        print(f"Starting System API Server on http://{host}:{port}")
        print(f"API Version: {API_VERSION}")
        print(f"API Key: {self.api_key}")
        self.app.run(host=host, port=port, debug=debug)

# Initialize API server
if __name__ == '__main__':
    api_server = SystemAPI()
    api_server.run()
