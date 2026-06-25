#!/usr/bin/env python3
"""
Mesh Application Integration Kit
Easy integration for existing Homelab Tools applications with mesh communication
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Callable
import logging
from mesh_app_communication import MeshAppCommunication

class MeshAppIntegration:
    """Integration kit for existing applications"""
    
    def __init__(self):
        self.comm_layer = None
        self.integrated_apps = {}
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging"""
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger('MeshAppIntegration')
    
    def start_integration_layer(self):
        """Start the mesh communication layer"""
        try:
            self.comm_layer = MeshAppCommunication()
            self.comm_layer.start()
            self.logger.info("Mesh integration layer started")
            return True
        except Exception as e:
            self.logger.error(f"Failed to start integration layer: {e}")
            return False
    
    def integrate_vpn_gateway(self) -> str:
        """Integrate VPN Gateway with mesh communication"""
        try:
            if not self.comm_layer:
                raise Exception("Communication layer not started")
            
            app_id = self.comm_layer.register_application(
                app_name="vpn-gateway",
                app_type="vpn",
                port=51820,
                endpoints=[
                    "/api/status",
                    "/api/clients", 
                    "/api/config",
                    "/api/mesh/nodes"
                ],
                capabilities=[
                    "wireguard_management",
                    "client_management",
                    "mesh_coordination",
                    "traffic_monitoring"
                ]
            )
            
            # Register message handlers
            self.comm_layer.register_message_handler("vpn_status", self.handle_vpn_status)
            self.comm_layer.register_message_handler("client_connect", self.handle_client_connect)
            self.comm_layer.register_message_handler("mesh_sync", self.handle_mesh_sync)
            
            self.integrated_apps["vpn_gateway"] = app_id
            self.logger.info(f"VPN Gateway integrated (ID: {app_id})")
            
            return app_id
            
        except Exception as e:
            self.logger.error(f"Failed to integrate VPN Gateway: {e}")
            raise
    
    def integrate_network_monitor(self) -> str:
        """Integrate Network Monitor with mesh communication"""
        try:
            if not self.comm_layer:
                raise Exception("Communication layer not started")
            
            app_id = self.comm_layer.register_application(
                app_name="network-monitor",
                app_type="monitoring",
                port=9090,
                endpoints=[
                    "/api/stats",
                    "/api/traffic",
                    "/api/connections",
                    "/api/alerts"
                ],
                capabilities=[
                    "network_monitoring",
                    "traffic_analysis",
                    "connection_tracking",
                    "performance_metrics"
                ]
            )
            
            # Register message handlers
            self.comm_layer.register_message_handler("network_stats", self.handle_network_stats)
            self.comm_layer.register_message_handler("traffic_alert", self.handle_traffic_alert)
            self.comm_layer.register_message_handler("connection_query", self.handle_connection_query)
            
            self.integrated_apps["network_monitor"] = app_id
            self.logger.info(f"Network Monitor integrated (ID: {app_id})")
            
            return app_id
            
        except Exception as e:
            self.logger.error(f"Failed to integrate Network Monitor: {e}")
            raise
    
    def integrate_gpu_monitor(self) -> str:
        """Integrate GPU Monitor with mesh communication"""
        try:
            if not self.comm_layer:
                raise Exception("Communication layer not started")
            
            app_id = self.comm_layer.register_application(
                app_name="gpu-monitor",
                app_type="gpu",
                port=8083,
                endpoints=[
                    "/api/gpu/status",
                    "/api/gpu/metrics",
                    "/api/gpu/share",
                    "/api/gpu/processes"
                ],
                capabilities=[
                    "gpu_monitoring",
                    "gpu_sharing",
                    "performance_tracking",
                    "process_monitoring"
                ]
            )
            
            # Register message handlers
            self.comm_layer.register_message_handler("gpu_status", self.handle_gpu_status)
            self.comm_layer.register_message_handler("gpu_share_request", self.handle_gpu_share_request)
            self.comm_layer.register_message_handler("gpu_metrics", self.handle_gpu_metrics)
            
            self.integrated_apps["gpu_monitor"] = app_id
            self.logger.info(f"GPU Monitor integrated (ID: {app_id})")
            
            return app_id
            
        except Exception as e:
            self.logger.error(f"Failed to integrate GPU Monitor: {e}")
            raise
    
    def integrate_ram_sharing(self) -> str:
        """Integrate RAM Sharing with mesh communication"""
        try:
            if not self.comm_layer:
                raise Exception("Communication layer not started")
            
            app_id = self.comm_layer.register_application(
                app_name="ram-sharing",
                app_type="memory",
                port=8084,
                endpoints=[
                    "/api/memory/status",
                    "/api/memory/share",
                    "/api/memory/alloc",
                    "/api/memory/free"
                ],
                capabilities=[
                    "memory_sharing",
                    "memory_allocation",
                    "performance_monitoring",
                    "resource_management"
                ]
            )
            
            # Register message handlers
            self.comm_layer.register_message_handler("memory_status", self.handle_memory_status)
            self.comm_layer.register_message_handler("memory_share_request", self.handle_memory_share_request)
            self.comm_layer.register_message_handler("memory_alloc", self.handle_memory_alloc)
            
            self.integrated_apps["ram_sharing"] = app_id
            self.logger.info(f"RAM Sharing integrated (ID: {app_id})")
            
            return app_id
            
        except Exception as e:
            self.logger.error(f"Failed to integrate RAM Sharing: {e}")
            raise
    
    def integrate_web_dashboard(self) -> str:
        """Integrate Web Dashboard with mesh communication"""
        try:
            if not self.comm_layer:
                raise Exception("Communication layer not started")
            
            app_id = self.comm_layer.register_application(
                app_name="web-dashboard",
                app_type="web",
                port=8080,
                endpoints=[
                    "/api/dashboard/status",
                    "/api/dashboard/apps",
                    "/api/dashboard/metrics",
                    "/api/dashboard/alerts"
                ],
                capabilities=[
                    "dashboard_display",
                    "app_management",
                    "metrics_visualization",
                    "alert_management"
                ]
            )
            
            # Register message handlers
            self.comm_layer.register_message_handler("dashboard_update", self.handle_dashboard_update)
            self.comm_layer.register_message_handler("app_status_update", self.handle_app_status_update)
            self.comm_layer.register_message_handler("metrics_update", self.handle_metrics_update)
            
            self.integrated_apps["web_dashboard"] = app_id
            self.logger.info(f"Web Dashboard integrated (ID: {app_id})")
            
            return app_id
            
        except Exception as e:
            self.logger.error(f"Failed to integrate Web Dashboard: {e}")
            raise
    
    def integrate_all_homelab_apps(self) -> Dict[str, str]:
        """Integrate all major Homelab Tools applications"""
        try:
            integrated = {}
            
            # Core applications
            integrated["vpn_gateway"] = self.integrate_vpn_gateway()
            integrated["network_monitor"] = self.integrate_network_monitor()
            integrated["web_dashboard"] = self.integrate_web_dashboard()
            
            # Resource sharing applications
            integrated["gpu_monitor"] = self.integrate_gpu_monitor()
            integrated["ram_sharing"] = self.integrate_ram_sharing()
            
            self.logger.info(f"Integrated {len(integrated)} Homelab applications")
            return integrated
            
        except Exception as e:
            self.logger.error(f"Failed to integrate all apps: {e}")
            raise
    
    def create_app_routes(self):
        """Create application routes for seamless communication"""
        try:
            if not self.comm_layer:
                raise Exception("Communication layer not started")
            
            # VPN Gateway routes
            self.comm_layer.create_app_route("network-monitor", "vpn-gateway", "status_sync", "/api/status")
            self.comm_layer.create_app_route("gpu-monitor", "vpn-gateway", "resource_sync", "/api/mesh/nodes")
            self.comm_layer.create_app_route("ram-sharing", "vpn-gateway", "resource_sync", "/api/mesh/nodes")
            
            # Web Dashboard routes
            self.comm_layer.create_app_route("web-dashboard", "vpn-gateway", "status_update", "/api/status")
            self.comm_layer.create_app_route("web-dashboard", "network-monitor", "metrics_update", "/api/stats")
            self.comm_layer.create_app_route("web-dashboard", "gpu-monitor", "metrics_update", "/api/gpu/metrics")
            self.comm_layer.create_app_route("web-dashboard", "ram-sharing", "metrics_update", "/api/memory/status")
            
            # Resource sharing routes
            self.comm_layer.create_app_route("gpu-monitor", "ram-sharing", "resource_coordination", "/api/memory/status")
            self.comm_layer.create_app_route("ram-sharing", "gpu-monitor", "resource_coordination", "/api/gpu/status")
            
            self.logger.info("Application routes created for seamless communication")
            
        except Exception as e:
            self.logger.error(f"Failed to create app routes: {e}")
    
    def enable_cross_system_communication(self):
        """Enable communication between HAZACER and HAZINTEL2 systems"""
        try:
            if not self.comm_layer:
                raise Exception("Communication layer not started")
            
            # Create cross-system routes
            cross_system_routes = [
                ("hazer-vpn-gateway", "hazintel2-vpn-gateway", "mesh_sync", "/api/mesh/sync"),
                ("hazer-network-monitor", "hazintel2-network-monitor", "stats_sync", "/api/stats"),
                ("hazer-gpu-monitor", "hazintel2-gpu-monitor", "resource_share", "/api/gpu/share"),
                ("hazer-ram-sharing", "hazintel2-ram-sharing", "resource_share", "/api/memory/share"),
                ("hazer-web-dashboard", "hazintel2-web-dashboard", "dashboard_sync", "/api/dashboard/sync")
            ]
            
            for source, target, route_type, endpoint in cross_system_routes:
                self.comm_layer.create_app_route(source, target, route_type, endpoint, priority=10)
            
            self.logger.info("Cross-system communication enabled")
            
        except Exception as e:
            self.logger.error(f"Failed to enable cross-system communication: {e}")
    
    # Message handlers
    def handle_vpn_status(self, message_data: Dict):
        """Handle VPN status messages"""
        try:
            source_app = message_data.get('source_app')
            data = message_data.get('data', {})
            
            self.logger.info(f"VPN status update from {source_app}: {data}")
            
            # Forward to web dashboard
            if "web_dashboard" in self.integrated_apps:
                self.comm_layer.send_message(
                    "web-dashboard", 
                    "vpn_status_update", 
                    data
                )
                
        except Exception as e:
            self.logger.error(f"Failed to handle VPN status: {e}")
    
    def handle_network_stats(self, message_data: Dict):
        """Handle network statistics messages"""
        try:
            source_app = message_data.get('source_app')
            data = message_data.get('data', {})
            
            self.logger.info(f"Network stats from {source_app}")
            
            # Forward to web dashboard
            if "web_dashboard" in self.integrated_apps:
                self.comm_layer.send_message(
                    "web-dashboard",
                    "network_metrics_update",
                    data
                )
                
        except Exception as e:
            self.logger.error(f"Failed to handle network stats: {e}")
    
    def handle_gpu_status(self, message_data: Dict):
        """Handle GPU status messages"""
        try:
            source_app = message_data.get('source_app')
            data = message_data.get('data', {})
            
            self.logger.info(f"GPU status from {source_app}")
            
            # Forward to web dashboard and RAM sharing for coordination
            if "web_dashboard" in self.integrated_apps:
                self.comm_layer.send_message(
                    "web-dashboard",
                    "gpu_metrics_update",
                    data
                )
            
            if "ram-sharing" in self.integrated_apps:
                self.comm_layer.send_message(
                    "ram-sharing",
                    "gpu_coordination",
                    data
                )
                
        except Exception as e:
            self.logger.error(f"Failed to handle GPU status: {e}")
    
    def handle_memory_status(self, message_data: Dict):
        """Handle memory status messages"""
        try:
            source_app = message_data.get('source_app')
            data = message_data.get('data', {})
            
            self.logger.info(f"Memory status from {source_app}")
            
            # Forward to web dashboard and GPU monitor for coordination
            if "web_dashboard" in self.integrated_apps:
                self.comm_layer.send_message(
                    "web-dashboard",
                    "memory_metrics_update",
                    data
                )
            
            if "gpu-monitor" in self.integrated_apps:
                self.comm_layer.send_message(
                    "gpu-monitor",
                    "memory_coordination",
                    data
                )
                
        except Exception as e:
            self.logger.error(f"Failed to handle memory status: {e}")
    
    def handle_dashboard_update(self, message_data: Dict):
        """Handle dashboard update messages"""
        try:
            source_app = message_data.get('source_app')
            data = message_data.get('data', {})
            
            self.logger.info(f"Dashboard update from {source_app}")
            
        except Exception as e:
            self.logger.error(f"Failed to handle dashboard update: {e}")
    
    def handle_client_connect(self, message_data: Dict):
        """Handle client connection messages"""
        try:
            source_app = message_data.get('source_app')
            data = message_data.get('data', {})
            
            self.logger.info(f"Client connection from {source_app}")
            
            # Notify all monitoring apps
            for app_name in ["network-monitor", "gpu-monitor", "ram-sharing"]:
                if app_name in self.integrated_apps:
                    self.comm_layer.send_message(
                        app_name,
                        "client_connected",
                        data
                    )
                    
        except Exception as e:
            self.logger.error(f"Failed to handle client connect: {e}")
    
    def handle_mesh_sync(self, message_data: Dict):
        """Handle mesh synchronization messages"""
        try:
            source_app = message_data.get('source_app')
            data = message_data.get('data', {})
            
            self.logger.info(f"Mesh sync from {source_app}")
            
            # Forward to all mesh-aware apps
            mesh_apps = ["vpn-gateway", "network-monitor", "gpu-monitor", "ram-sharing"]
            for app_name in mesh_apps:
                if app_name in self.integrated_apps:
                    self.comm_layer.send_message(
                        app_name,
                        "mesh_sync_update",
                        data
                    )
                    
        except Exception as e:
            self.logger.error(f"Failed to handle mesh sync: {e}")
    
    # Additional handlers for other message types
    def handle_traffic_alert(self, message_data: Dict):
        """Handle traffic alerts"""
        try:
            self.logger.info(f"Traffic alert: {message_data.get('data', {})}")
        except Exception as e:
            self.logger.error(f"Failed to handle traffic alert: {e}")
    
    def handle_connection_query(self, message_data: Dict):
        """Handle connection queries"""
        try:
            self.logger.info(f"Connection query: {message_data.get('data', {})}")
        except Exception as e:
            self.logger.error(f"Failed to handle connection query: {e}")
    
    def handle_gpu_share_request(self, message_data: Dict):
        """Handle GPU share requests"""
        try:
            self.logger.info(f"GPU share request: {message_data.get('data', {})}")
        except Exception as e:
            self.logger.error(f"Failed to handle GPU share request: {e}")
    
    def handle_gpu_metrics(self, message_data: Dict):
        """Handle GPU metrics"""
        try:
            self.logger.info(f"GPU metrics: {message_data.get('data', {})}")
        except Exception as e:
            self.logger.error(f"Failed to handle GPU metrics: {e}")
    
    def handle_memory_share_request(self, message_data: Dict):
        """Handle memory share requests"""
        try:
            self.logger.info(f"Memory share request: {message_data.get('data', {})}")
        except Exception as e:
            self.logger.error(f"Failed to handle memory share request: {e}")
    
    def handle_memory_alloc(self, message_data: Dict):
        """Handle memory allocation"""
        try:
            self.logger.info(f"Memory allocation: {message_data.get('data', {})}")
        except Exception as e:
            self.logger.error(f"Failed to handle memory allocation: {e}")
    
    def handle_app_status_update(self, message_data: Dict):
        """Handle application status updates"""
        try:
            self.logger.info(f"App status update: {message_data.get('data', {})}")
        except Exception as e:
            self.logger.error(f"Failed to handle app status update: {e}")
    
    def handle_metrics_update(self, message_data: Dict):
        """Handle metrics updates"""
        try:
            self.logger.info(f"Metrics update: {message_data.get('data', {})}")
        except Exception as e:
            self.logger.error(f"Failed to handle metrics update: {e}")
    
    def get_integration_status(self) -> Dict:
        """Get integration status"""
        try:
            if not self.comm_layer:
                return {"status": "not_started", "integrated_apps": []}
            
            apps = self.comm_layer.discover_applications()
            stats = self.comm_layer.get_communication_stats()
            routes = self.comm_layer.get_app_routes()
            
            return {
                "status": "running",
                "integrated_apps": list(self.integrated_apps.keys()),
                "discovered_apps": len(apps),
                "communication_stats": stats,
                "active_routes": len(routes)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get integration status: {e}")
            return {"status": "error", "error": str(e)}

# Main integration function
def setup_homelab_mesh_integration():
    """Setup complete Homelab Tools mesh integration"""
    try:
        integration = MeshAppIntegration()
        
        # Start communication layer
        if not integration.start_integration_layer():
            raise Exception("Failed to start communication layer")
        
        # Integrate all applications
        integrated_apps = integration.integrate_all_homelab_apps()
        
        # Create application routes
        integration.create_app_routes()
        
        # Enable cross-system communication
        integration.enable_cross_system_communication()
        
        print("✅ Homelab Tools mesh integration completed successfully!")
        print(f"📱 Integrated applications: {list(integrated_apps.keys())}")
        print("🔗 Application routes created")
        print("🌐 Cross-system communication enabled")
        
        return integration
        
    except Exception as e:
        print(f"❌ Failed to setup mesh integration: {e}")
        return None

if __name__ == "__main__":
    # Test the mesh integration
    print("🔧 Setting up Homelab Tools mesh integration...")
    print("=" * 50)
    
    integration = setup_homelab_mesh_integration()
    
    if integration:
        try:
            # Show integration status
            status = integration.get_integration_status()
            print(f"\n📊 Integration Status: {json.dumps(status, indent=2)}")
            
            # Keep running for testing
            print("\n🚀 Mesh integration running... Press Ctrl+C to stop")
            while True:
                time.sleep(30)
                status = integration.get_integration_status()
                print(f"📱 Active apps: {status.get('discovered_apps', 0)}")
                
        except KeyboardInterrupt:
            print("\n🛑 Stopping mesh integration...")
            if integration.comm_layer:
                integration.comm_layer.stop()
    else:
        print("❌ Integration setup failed")
