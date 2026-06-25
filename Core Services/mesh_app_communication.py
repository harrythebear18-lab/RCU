#!/usr/bin/env python3
"""
Mesh Application Communication Layer
Tailscale-like application discovery and communication for Homelab Tools
Enables seamless app-to-app communication across the mesh network
"""

import json
import socket
import threading
import time
import uuid
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any
import logging
import sqlite3
import asyncio
import websockets
from zeroconf import ServiceBrowser, Zeroconf, ServiceListener

class MeshAppCommunication:
    """Application communication layer for mesh network"""
    
    def __init__(self, node_id: str = None, mesh_ip: str = None):
        self.node_id = node_id or self.get_local_node_id()
        self.mesh_ip = mesh_ip or self.get_local_mesh_ip()
        
        self.setup_logging()
        self.setup_database()
        
        # Application registry
        self.registered_apps = {}
        self.app_endpoints = {}
        self.app_routes = {}
        
        # Communication state
        self.running = False
        self.discovery_services = {}
        self.zeroconf = None
        self.websocket_server = None
        
        # Message routing
        self.message_handlers = {}
        self.message_queue = asyncio.Queue()
        
    def setup_logging(self):
        """Setup logging"""
        log_file = Path("logs/mesh_app_communication.log")
        log_file.parent.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('MeshAppCommunication')
    
    def setup_database(self):
        """Setup database for app communication"""
        db_path = Path("data/mesh_app_communication.db")
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.conn = sqlite3.connect(str(db_path))
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS registered_apps (
                id TEXT PRIMARY KEY,
                app_name TEXT NOT NULL,
                app_type TEXT NOT NULL,
                node_id TEXT,
                mesh_ip TEXT,
                port INTEGER,
                protocol TEXT DEFAULT 'http',
                endpoints TEXT,
                capabilities TEXT,
                status TEXT DEFAULT 'active',
                last_seen TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (node_id) REFERENCES mesh_nodes (id)
            )
        ''')
        
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS app_routes (
                id TEXT PRIMARY KEY,
                source_app TEXT,
                target_app TEXT,
                route_type TEXT,
                endpoint TEXT,
                priority INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS message_log (
                id TEXT PRIMARY KEY,
                source_app TEXT,
                target_app TEXT,
                message_type TEXT,
                message_data TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'sent'
            )
        ''')
        
        self.conn.commit()
    
    def start(self):
        """Start the application communication layer"""
        try:
            self.logger.info("Starting mesh application communication layer...")
            
            # Start mDNS service discovery
            self.start_mdns_discovery()
            
            # Start WebSocket server for real-time communication
            self.start_websocket_server()
            
            # Start message processing
            self.start_message_processor()
            
            # Start heartbeat service
            self.start_heartbeat_service()
            
            self.running = True
            self.logger.info("Mesh application communication layer started")
            
        except Exception as e:
            self.logger.error(f"Failed to start app communication: {e}")
            raise
    
    def stop(self):
        """Stop the application communication layer"""
        try:
            self.running = False
            
            # Stop services
            if self.zeroconf:
                self.zeroconf.close()
            
            if self.websocket_server:
                # WebSocket server will be stopped by asyncio
                pass
            
            self.logger.info("Mesh application communication layer stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping app communication: {e}")
    
    def register_application(self, app_name: str, app_type: str, port: int, 
                           endpoints: List[str] = None, capabilities: List[str] = None,
                           protocol: str = 'http') -> str:
        """Register an application with the mesh communication layer"""
        try:
            app_id = str(uuid.uuid4())
            
            # Store in database
            self.conn.execute('''
                INSERT INTO registered_apps 
                (id, app_name, app_type, node_id, mesh_ip, port, protocol, endpoints, capabilities)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                app_id, app_name, app_type, self.node_id, self.mesh_ip, 
                port, protocol, json.dumps(endpoints or []), json.dumps(capabilities or [])
            ))
            self.conn.commit()
            
            # Store in memory
            self.registered_apps[app_id] = {
                'id': app_id,
                'name': app_name,
                'type': app_type,
                'node_id': self.node_id,
                'mesh_ip': self.mesh_ip,
                'port': port,
                'protocol': protocol,
                'endpoints': endpoints or [],
                'capabilities': capabilities or [],
                'status': 'active',
                'last_seen': datetime.now()
            }
            
            # Register with mDNS
            self.register_mdns_service(app_id, app_name, app_type, port)
            
            self.logger.info(f"Registered application: {app_name} ({app_type})")
            return app_id
            
        except Exception as e:
            self.logger.error(f"Failed to register application: {e}")
            raise
    
    def register_mdns_service(self, app_id: str, app_name: str, app_type: str, port: int):
        """Register application with mDNS"""
        try:
            from zeroconf import ServiceInfo
            
            service_type = f"_{app_type}._tcp.local."
            service_name = f"{app_name}.{service_type}"
            
            info = ServiceInfo(
                service_type=service_type,
                name=service_name,
                addresses=[socket.inet_aton(self.mesh_ip)],
                port=port,
                properties={
                    'app_id': app_id,
                    'node_id': self.node_id,
                    'app_type': app_type
                }
            )
            
            if self.zeroconf:
                self.zeroconf.register_service(info)
                self.logger.info(f"Registered mDNS service: {service_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to register mDNS service: {e}")
    
    def discover_applications(self, app_type: str = None) -> List[Dict]:
        """Discover applications on the mesh network"""
        try:
            query = "SELECT * FROM registered_apps WHERE status = 'active'"
            params = []
            
            if app_type:
                query += " AND app_type = ?"
                params.append(app_type)
            
            query += " ORDER BY app_name"
            
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            
            apps = []
            for row in cursor.fetchall():
                apps.append({
                    'id': row[0],
                    'name': row[1],
                    'type': row[2],
                    'node_id': row[3],
                    'mesh_ip': row[4],
                    'port': row[5],
                    'protocol': row[6],
                    'endpoints': json.loads(row[7]) if row[7] else [],
                    'capabilities': json.loads(row[8]) if row[8] else [],
                    'status': row[9],
                    'last_seen': row[10]
                })
            
            return apps
            
        except Exception as e:
            self.logger.error(f"Failed to discover applications: {e}")
            return []
    
    def get_app_endpoint(self, app_name: str, endpoint: str = None) -> Optional[str]:
        """Get application endpoint URL"""
        try:
            # Find the application
            apps = self.discover_applications()
            target_app = None
            
            for app in apps:
                if app['name'] == app_name:
                    target_app = app
                    break
            
            if not target_app:
                return None
            
            # Build endpoint URL
            base_url = f"{target_app['protocol']}://{target_app['mesh_ip']}:{target_app['port']}"
            
            if endpoint:
                return f"{base_url}/{endpoint.lstrip('/')}"
            else:
                return base_url
            
        except Exception as e:
            self.logger.error(f"Failed to get app endpoint: {e}")
            return None
    
    def send_message(self, target_app: str, message_type: str, data: Dict, 
                    endpoint: str = None) -> bool:
        """Send message to another application"""
        try:
            # Get target endpoint
            target_url = self.get_app_endpoint(target_app, endpoint)
            if not target_url:
                self.logger.error(f"Target application not found: {target_app}")
                return False
            
            # Send message
            message_data = {
                'source_app': self.get_local_app_name(),
                'target_app': target_app,
                'message_type': message_type,
                'data': data,
                'timestamp': datetime.now().isoformat(),
                'message_id': str(uuid.uuid4())
            }
            
            response = requests.post(
                f"{target_url}/mesh/message",
                json=message_data,
                timeout=30
            )
            
            if response.status_code == 200:
                # Log message
                self.log_message(message_data['message_id'], 
                              self.get_local_app_name(), target_app, 
                              message_type, json.dumps(data))
                
                self.logger.info(f"Message sent to {target_app}: {message_type}")
                return True
            else:
                self.logger.error(f"Failed to send message: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to send message: {e}")
            return False
    
    def register_message_handler(self, message_type: str, handler: Callable):
        """Register a message handler"""
        self.message_handlers[message_type] = handler
        self.logger.info(f"Registered message handler: {message_type}")
    
    def handle_incoming_message(self, message_data: Dict):
        """Handle incoming message"""
        try:
            message_type = message_data.get('message_type')
            
            if message_type in self.message_handlers:
                handler = self.message_handlers[message_type]
                # Run handler in thread to avoid blocking
                threading.Thread(target=handler, args=(message_data,), daemon=True).start()
            else:
                self.logger.warning(f"No handler for message type: {message_type}")
                
        except Exception as e:
            self.logger.error(f"Failed to handle incoming message: {e}")
    
    def log_message(self, message_id: str, source_app: str, target_app: str, 
                   message_type: str, message_data: str):
        """Log message to database"""
        try:
            self.conn.execute('''
                INSERT INTO message_log (id, source_app, target_app, message_type, message_data)
                VALUES (?, ?, ?, ?, ?)
            ''', (message_id, source_app, target_app, message_type, message_data))
            self.conn.commit()
        except Exception as e:
            self.logger.error(f"Failed to log message: {e}")
    
    def start_mdns_discovery(self):
        """Start mDNS discovery for applications"""
        try:
            self.zeroconf = Zeroconf()
            
            # Discover common application types
            app_types = ['web', 'api', 'database', 'storage', 'gpu', 'monitoring']
            
            for app_type in app_types:
                listener = MeshAppServiceListener(self, app_type)
                browser = ServiceBrowser(self.zeroconf, f"_{app_type}._tcp.local.", listener)
                self.discovery_services[app_type] = browser
            
            self.logger.info("mDNS discovery started for applications")
            
        except Exception as e:
            self.logger.error(f"Failed to start mDNS discovery: {e}")
    
    def start_websocket_server(self):
        """Start WebSocket server for real-time communication"""
        try:
            async def handle_websocket(websocket, path):
                try:
                    async for message in websocket:
                        data = json.loads(message)
                        self.handle_incoming_message(data)
                except Exception as e:
                    self.logger.error(f"WebSocket error: {e}")
            
            # Start WebSocket server in background
            def run_websocket_server():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                start_server = websockets.serve(handle_websocket, self.mesh_ip, 8081)
                loop.run_until_complete(start_server)
                loop.run_forever()
            
            threading.Thread(target=run_websocket_server, daemon=True).start()
            self.logger.info("WebSocket server started")
            
        except Exception as e:
            self.logger.error(f"Failed to start WebSocket server: {e}")
    
    def start_message_processor(self):
        """Start message processing loop"""
        def process_messages():
            while self.running:
                try:
                    if not self.message_queue.empty():
                        message = self.message_queue.get_nowait()
                        self.handle_incoming_message(message)
                    time.sleep(0.1)
                except Exception as e:
                    self.logger.error(f"Message processing error: {e}")
        
        threading.Thread(target=process_messages, daemon=True).start()
    
    def start_heartbeat_service(self):
        """Start heartbeat service for application health"""
        def heartbeat_loop():
            while self.running:
                try:
                    self.update_app_heartbeats()
                    self.cleanup_inactive_apps()
                    time.sleep(30)
                except Exception as e:
                    self.logger.error(f"Heartbeat error: {e}")
                    time.sleep(60)
        
        threading.Thread(target=heartbeat_loop, daemon=True).start()
    
    def update_app_heartbeats(self):
        """Update heartbeats for local applications"""
        try:
            current_time = datetime.now()
            
            for app_id, app_info in self.registered_apps.items():
                if app_info['node_id'] == self.node_id:
                    # Update local apps
                    self.conn.execute('''
                        UPDATE registered_apps SET last_seen = ? WHERE id = ?
                    ''', (current_time, app_id))
            
            self.conn.commit()
            
        except Exception as e:
            self.logger.error(f"Failed to update heartbeats: {e}")
    
    def cleanup_inactive_apps(self):
        """Clean up inactive applications"""
        try:
            timeout = datetime.now() - timedelta(minutes=5)
            
            cursor = self.conn.cursor()
            cursor.execute('''
                UPDATE registered_apps SET status = 'inactive' 
                WHERE last_seen < ? AND status = 'active'
            ''', (timeout,))
            
            inactive_count = cursor.rowcount
            if inactive_count > 0:
                self.logger.info(f"Cleaned up {inactive_count} inactive applications")
            
            self.conn.commit()
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup inactive apps: {e}")
    
    def get_local_node_id(self) -> str:
        """Get local node ID"""
        try:
            # Try to get from mesh VPN database
            mesh_db_path = Path("data/mesh_vpn.db")
            if mesh_db_path.exists():
                conn = sqlite3.connect(str(mesh_db_path))
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM mesh_nodes WHERE name LIKE '%local%' OR name LIKE '%this%' LIMIT 1")
                result = cursor.fetchone()
                conn.close()
                
                if result:
                    return result[0]
        except:
            pass
        
        # Generate a persistent node ID
        node_id_file = Path("data/local_node_id")
        if node_id_file.exists():
            with open(node_id_file, 'r') as f:
                return f.read().strip()
        else:
            node_id = str(uuid.uuid4())
            node_id_file.parent.mkdir(exist_ok=True)
            with open(node_id_file, 'w') as f:
                f.write(node_id)
            return node_id
    
    def get_local_mesh_ip(self) -> str:
        """Get local mesh IP"""
        try:
            # Try to get from mesh VPN database
            mesh_db_path = Path("data/mesh_vpn.db")
            if mesh_db_path.exists():
                conn = sqlite3.connect(str(mesh_db_path))
                cursor = conn.cursor()
                cursor.execute("SELECT mesh_ip FROM mesh_nodes LIMIT 1")
                result = cursor.fetchone()
                conn.close()
                
                if result:
                    return result[0]
        except:
            pass
        
        # Fallback to local IP
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except:
            return "127.0.0.1"
    
    def get_local_app_name(self) -> str:
        """Get local application name"""
        return f"mesh-comm-{self.node_id[:8]}"
    
    def create_app_route(self, source_app: str, target_app: str, route_type: str, 
                        endpoint: str, priority: int = 1):
        """Create application route"""
        try:
            route_id = str(uuid.uuid4())
            
            self.conn.execute('''
                INSERT INTO app_routes (id, source_app, target_app, route_type, endpoint, priority)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (route_id, source_app, target_app, route_type, endpoint, priority))
            
            self.conn.commit()
            self.logger.info(f"Created app route: {source_app} -> {target_app} ({route_type})")
            
        except Exception as e:
            self.logger.error(f"Failed to create app route: {e}")
    
    def get_app_routes(self, source_app: str = None) -> List[Dict]:
        """Get application routes"""
        try:
            query = "SELECT * FROM app_routes"
            params = []
            
            if source_app:
                query += " WHERE source_app = ?"
                params.append(source_app)
            
            query += " ORDER BY priority DESC"
            
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            
            routes = []
            for row in cursor.fetchall():
                routes.append({
                    'id': row[0],
                    'source_app': row[1],
                    'target_app': row[2],
                    'route_type': row[3],
                    'endpoint': row[4],
                    'priority': row[5]
                })
            
            return routes
            
        except Exception as e:
            self.logger.error(f"Failed to get app routes: {e}")
            return []
    
    def get_communication_stats(self) -> Dict:
        """Get communication statistics"""
        try:
            cursor = self.conn.cursor()
            
            # App statistics
            cursor.execute("SELECT app_type, COUNT(*) FROM registered_apps WHERE status = 'active' GROUP BY app_type")
            app_stats = dict(cursor.fetchall())
            
            # Message statistics
            cursor.execute("SELECT COUNT(*) FROM message_log WHERE timestamp > datetime('now', '-1 hour')")
            recent_messages = cursor.fetchone()[0]
            
            cursor.execute("SELECT message_type, COUNT(*) FROM message_log GROUP BY message_type")
            message_stats = dict(cursor.fetchall())
            
            return {
                'total_apps': sum(app_stats.values()),
                'apps_by_type': app_stats,
                'recent_messages': recent_messages,
                'message_types': message_stats,
                'active_routes': len(self.get_app_routes()),
                'discovery_services': len(self.discovery_services)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get communication stats: {e}")
            return {}

class MeshAppServiceListener(ServiceListener):
    """mDNS service listener for mesh applications"""
    
    def __init__(self, comm_layer: MeshAppCommunication, app_type: str):
        self.comm_layer = comm_layer
        self.app_type = app_type
        self.logger = logging.getLogger(f'MeshAppServiceListener-{app_type}')
    
    def add_service(self, zeroconf: Zeroconf, service_type: str, name: str):
        """Handle service discovery"""
        try:
            info = zeroconf.get_service_info(service_type, name)
            if info:
                self.process_service_info(info, 'discovered')
        except Exception as e:
            self.logger.error(f"Error adding service: {e}")
    
    def remove_service(self, zeroconf: Zeroconf, service_type: str, name: str):
        """Handle service removal"""
        try:
            self.logger.info(f"Service removed: {name}")
        except Exception as e:
            self.logger.error(f"Error removing service: {e}")
    
    def update_service(self, zeroconf: Zeroconf, service_type: str, name: str):
        """Handle service update"""
        try:
            info = zeroconf.get_service_info(service_type, name)
            if info:
                self.process_service_info(info, 'updated')
        except Exception as e:
            self.logger.error(f"Error updating service: {e}")
    
    def process_service_info(self, info, action: str):
        """Process discovered service information"""
        try:
            # Extract service details
            app_name = info.name.split('.')[0]
            host = socket.inet_ntoa(info.addresses[0]) if info.addresses else 'unknown'
            port = info.port
            properties = {k.decode(): v.decode() for k, v in info.properties.items()}
            
            app_id = properties.get('app_id')
            node_id = properties.get('node_id')
            
            if app_id and node_id != self.comm_layer.node_id:
                # Update database with discovered app
                self.comm_layer.conn.execute('''
                    INSERT OR REPLACE INTO registered_apps 
                    (id, app_name, app_type, node_id, mesh_ip, port, protocol, endpoints, capabilities, status, last_seen)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    app_id, app_name, self.app_type, node_id, host, port,
                    'http', '[]', '[]', 'active', datetime.now()
                ))
                
                self.comm_layer.conn.commit()
                self.logger.info(f"Discovered {self.app_type} app: {app_name} at {host}:{port}")
            
        except Exception as e:
            self.logger.error(f"Error processing service info: {e}")

# Integration helper for existing applications
def integrate_app_with_mesh(app_name: str, app_type: str, port: int, 
                          endpoints: List[str] = None, capabilities: List[str] = None):
    """Helper function to integrate an existing app with mesh communication"""
    try:
        comm = MeshAppCommunication()
        comm.start()
        
        app_id = comm.register_application(
            app_name=app_name,
            app_type=app_type,
            port=port,
            endpoints=endpoints,
            capabilities=capabilities
        )
        
        print(f"App {app_name} integrated with mesh communication (ID: {app_id})")
        return app_id, comm
        
    except Exception as e:
        print(f"Failed to integrate app: {e}")
        return None, None

if __name__ == "__main__":
    # Test the mesh application communication layer
    comm = MeshAppCommunication()
    
    try:
        comm.start()
        
        # Register a test application
        app_id = comm.register_application(
            app_name="test-web-app",
            app_type="web",
            port=8080,
            endpoints=["/api/status", "/api/data"],
            capabilities=["status", "data"]
        )
        
        print(f"Registered test app: {app_id}")
        
        # Discover applications
        apps = comm.discover_applications()
        print(f"Discovered {len(apps)} applications:")
        
        for app in apps:
            print(f"  - {app['name']} ({app['type']}) at {app['mesh_ip']}:{app['port']}")
        
        # Get communication stats
        stats = comm.get_communication_stats()
        print(f"\nCommunication stats: {json.dumps(stats, indent=2)}")
        
        # Keep running for testing
        print("\nMesh app communication running... Press Ctrl+C to stop")
        while True:
            time.sleep(10)
            apps = comm.discover_applications()
            print(f"Active applications: {len(apps)}")
            
    except KeyboardInterrupt:
        print("\nStopping mesh app communication...")
        comm.stop()
