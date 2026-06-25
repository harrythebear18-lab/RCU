#!/usr/bin/env python3
"""
Admin Auto-Configuration System
Automatically configures ports, auth levels, and permissions for admin systems
"""

import os
import sys
import json
import socket
import subprocess
import platform
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
import time

class AdminAutoConfig:
    """Automatic configuration system for admin-level homelab setup"""
    
    def __init__(self):
        self.system_info = self.get_system_info()
        self.is_admin = self.check_admin_privileges()
        self.config = self.load_default_config()
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging for auto-configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('admin_auto_config.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information"""
        try:
            import psutil
            return {
                'platform': platform.system(),
                'platform_release': platform.release(),
                'platform_version': platform.version(),
                'architecture': platform.machine(),
                'hostname': socket.gethostname(),
                'processor': platform.processor(),
                'cpu_count': psutil.cpu_count(),
                'memory_total': psutil.virtual_memory().total,
                'disk_total': psutil.disk_usage('/').total,
                'network_interfaces': list(psutil.net_if_addrs().keys()),
                'python_version': sys.version
            }
        except Exception as e:
            print(f"Error getting system info: {e}")
            return {}
    
    def check_admin_privileges(self) -> bool:
        """Check if running with admin privileges"""
        try:
            if platform.system() == "Windows":
                import ctypes
                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            else:
                # Unix/Linux/Mac
                return os.geteuid() == 0
        except Exception as e:
            print(f"Error checking admin privileges: {e}")
            return False
    
    def load_default_config(self) -> Dict[str, Any]:
        """Load default configuration for admin setup"""
        return {
            'ports': {
                'homelab_portal': 8080,
                'rest_api': 8081,
                'unified_dashboard': 8082,
                'network_monitor': 8083,
                'cpu_monitor': 8084,
                'gpu_monitor': 8085,
                'subnet_portal': 8090,
                'rdma_portal': 8091,
                'backup_system': 8092,
                'media_server': 8093,
                'vpn_gateway': 8094,
                'web_dashboard': 8095
            },
            'auth_levels': {
                'default_level': 'admin',
                'require_auth': False,  # Admin systems don't require auth
                'allow_anonymous': True,
                'session_timeout': 86400,  # 24 hours
                'max_sessions': 100
            },
            'security': {
                'firewall_rules': 'allow_all',
                'ssl_required': False,
                'encryption': 'optional',
                'api_key_required': False
            },
            'network': {
                'bind_all_interfaces': True,
                'auto_discovery': True,
                'p2p_enabled': True,
                'lan_broadcast': True
            },
            'performance': {
                'max_workers': None,  # Auto-detect
                'thread_pool_size': None,  # Auto-detect
                'cache_size': '1GB',
                'log_level': 'INFO'
            }
        }
    
    def check_port_available(self, port: int) -> bool:
        """Check if a port is available"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex(('localhost', port))
                return result != 0
        except Exception:
            return False
    
    def find_available_port(self, preferred_port: int) -> int:
        """Find an available port starting from preferred"""
        if self.check_port_available(preferred_port):
            return preferred_port
        
        # Find next available port
        for port in range(preferred_port + 1, preferred_port + 100):
            if self.check_port_available(port):
                return port
        
        raise Exception(f"No available ports found starting from {preferred_port}")
    
    def configure_firewall_windows(self, ports: List[int]):
        """Configure Windows firewall for admin access"""
        try:
            if platform.system() == "Windows":
                for port in ports:
                    cmd = f'netsh advfirewall firewall add rule name="Homelab Port {port}" dir=in action=allow protocol=TCP localport={port}'
                    subprocess.run(cmd, shell=True, check=True, capture_output=True)
                    self.logger.info(f"Added firewall rule for port {port}")
        except Exception as e:
            self.logger.warning(f"Failed to configure firewall: {e}")
    
    def auto_configure_ports(self) -> Dict[str, int]:
        """Auto-configure all ports for admin access"""
        configured_ports = {}
        
        for service_name, preferred_port in self.config['ports'].items():
            try:
                available_port = self.find_available_port(preferred_port)
                configured_ports[service_name] = available_port
                self.logger.info(f"Configured {service_name} on port {available_port}")
            except Exception as e:
                self.logger.error(f"Failed to configure port for {service_name}: {e}")
                configured_ports[service_name] = preferred_port
        
        # Configure firewall if admin
        if self.is_admin:
            self.configure_firewall_windows(list(configured_ports.values()))
        
        return configured_ports
    
    def generate_admin_config(self) -> Dict[str, Any]:
        """Generate complete admin configuration"""
        # Auto-configure ports
        configured_ports = self.auto_configure_ports()
        
        # Update config with actual ports
        admin_config = self.config.copy()
        admin_config['ports'] = configured_ports
        
        # Set admin-specific settings
        admin_config['system_info'] = self.system_info
        admin_config['is_admin'] = self.is_admin
        admin_config['configured_at'] = time.time()
        
        # Auto-detect performance settings
        if admin_config['performance']['max_workers'] is None:
            admin_config['performance']['max_workers'] = self.system_info.get('cpu_count', 4) * 2
        
        if admin_config['performance']['thread_pool_size'] is None:
            admin_config['performance']['thread_pool_size'] = self.system_info.get('cpu_count', 4)
        
        return admin_config
    
    def save_config(self, config: Dict[str, Any], config_path: str = None):
        """Save configuration to file"""
        if config_path is None:
            config_path = Path(__file__).parent / 'admin_config.json'
        
        try:
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2, default=str)
            self.logger.info(f"Configuration saved to {config_path}")
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")
    
    def apply_config_to_services(self, config: Dict[str, Any]):
        """Apply configuration to all homelab services"""
        try:
            # Update homelab_portal.py with new ports
            portal_path = Path(__file__).parent / 'homelab_portal.py'
            if portal_path.exists():
                self.update_service_config(portal_path, config['ports']['homelab_portal'])
            
            # Update rest_api.py with new ports
            api_path = Path(__file__).parent / 'rest_api.py'
            if api_path.exists():
                self.update_service_config(api_path, config['ports']['rest_api'])
            
            # Create unified_config.json for all services
            unified_config_path = Path(__file__).parent / 'unified_config.json'
            self.save_config(config, unified_config_path)
            
            self.logger.info("Configuration applied to all services")
            
        except Exception as e:
            self.logger.error(f"Failed to apply configuration to services: {e}")
    
    def update_service_config(self, service_path: Path, port: int):
        """Update individual service configuration"""
        try:
            with open(service_path, 'r') as f:
                content = f.read()
            
            # Update port in the file
            if 'port = ' in content:
                content = content.replace('port = 8080', f'port = {port}')
            elif 'port:' in content:
                content = content.replace('port: 8080', f'port: {port}')
            
            with open(service_path, 'w') as f:
                f.write(content)
                
            self.logger.info(f"Updated {service_path.name} with port {port}")
            
        except Exception as e:
            self.logger.error(f"Failed to update {service_path}: {e}")
    
    def run_auto_configuration(self):
        """Run complete auto-configuration process"""
        self.logger.info("Starting admin auto-configuration...")
        self.logger.info(f"Admin privileges: {self.is_admin}")
        self.logger.info(f"System: {self.system_info.get('platform')} {self.system_info.get('platform_release')}")
        
        # Generate admin configuration
        admin_config = self.generate_admin_config()
        
        # Save configuration
        self.save_config(admin_config)
        
        # Apply to services
        self.apply_config_to_services(admin_config)
        
        # Create startup script
        self.create_startup_script(admin_config)
        
        self.logger.info("Admin auto-configuration completed successfully!")
        return admin_config
    
    def create_startup_script(self, config: Dict[str, Any]):
        """Create startup script for admin homelab"""
        startup_script = f'''#!/usr/bin/env python3
"""
Admin Homelab Startup Script
Auto-generated configuration for admin-level access
"""

import sys
import os
import json
from pathlib import Path

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Configuration
CONFIG = {json.dumps(config, indent=4)}

def start_homelab_services():
    """Start all homelab services with admin configuration"""
    print("🚀 Starting Homelab Admin Services...")
    print(f"📊 System: {CONFIG['system_info']['platform']}")
    print(f"🔑 Admin Level: {CONFIG['auth_levels']['default_level']}")
    print(f"🌐 Portal Port: {CONFIG['ports']['homelab_portal']}")
    print(f"🔌 API Port: {CONFIG['ports']['rest_api']}")
    
    # Start homelab portal
    try:
        from homelab_portal import HomelabPortal
        portal = HomelabPortal(port=CONFIG['ports']['homelab_portal'])
        portal.start_portal_server()
        print("✅ Homelab Portal started")
    except Exception as e:
        print(f"❌ Failed to start portal: {e}")
    
    # Start REST API
    try:
        from rest_api import HomelabRESTAPI
        api = HomelabRESTAPI(port=CONFIG['ports']['rest_api'])
        api.start_monitoring()
        print("✅ REST API started")
    except Exception as e:
        print(f"❌ Failed to start API: {e}")
    
    print("🎯 Homelab Admin Services Ready!")
    print(f"🌐 Access Portal: http://localhost:{CONFIG['ports']['homelab_portal']}")
    print(f"🔌 Access API: http://localhost:{CONFIG['ports']['rest_api']}")

if __name__ == "__main__":
    start_homelab_services()
'''
        
        startup_path = Path(__file__).parent / 'admin_startup.py'
        with open(startup_path, 'w') as f:
            f.write(startup_script)
        
        self.logger.info(f"Created startup script: {startup_path}")

def main():
    """Main entry point for admin auto-configuration"""
    print("🔧 Homelab Admin Auto-Configuration")
    print("=" * 50)
    
    auto_config = AdminAutoConfig()
    
    if not auto_config.is_admin:
        print("⚠️  Warning: Not running with admin privileges")
        print("   Some features may be limited")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Configuration cancelled")
            return
    
    try:
        config = auto_config.run_auto_configuration()
        print("\n🎉 Auto-Configuration Complete!")
        print(f"📊 Portal: http://localhost:{config['ports']['homelab_portal']}")
        print(f"🔌 API: http://localhost:{config['ports']['rest_api']}")
        print(f"📁 Config saved to: admin_config.json")
        print(f"🚀 Run: python admin_startup.py")
        
    except Exception as e:
        print(f"❌ Auto-configuration failed: {e}")

if __name__ == "__main__":
    main()
