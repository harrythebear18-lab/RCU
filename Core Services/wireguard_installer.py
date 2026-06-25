#!/usr/bin/env python3
"""
WireGuard Automatic Installer and Package Manager
Downloads, installs, and configures WireGuard for the Homelab Tools mesh VPN
"""

import os
import sys
import requests
import subprocess
import zipfile
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Optional
import logging
import json
from datetime import datetime

class WireGuardInstaller:
    """Automatic WireGuard installer for Homelab Tools"""
    
    def __init__(self):
        self.setup_logging()
        self.setup_directories()
        
        # WireGuard download URLs
        self.wireguard_urls = {
            "windows_x64": "https://download.wireguard.com/windows-client/wireguard-amd64-0.5.3.msi",
            "windows_arm64": "https://download.wireguard.com/windows-client/wireguard-arm64-0.5.3.msi",
            "linux_x64": "https://dl.wireguard.org/windows/wireguard-tools-1.0.20210914-x86_64.tar.xz",
            "documentation": "https://www.wireguard.com/quickstart/"
        }
        
        # Installation paths
        self.install_paths = {
            "windows": {
                "program_files": os.environ.get("ProgramFiles", "C:\\Program Files"),
                "wireguard": "C:\\Program Files\\WireGuard",
                "config_dir": "C:\\Program Files\\WireGuard\\configs",
                "executable": "C:\\Program Files\\WireGuard\\wg.exe",
                "service": "WireGuardService"
            },
            "linux": {
                "config_dir": "/etc/wireguard",
                "executable": "/usr/bin/wg",
                "service": "wg-quick"
            }
        }
        
    def setup_logging(self):
        """Setup logging"""
        log_file = Path("logs/wireguard_installer.log")
        log_file.parent.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('WireGuardInstaller')
    
    def setup_directories(self):
        """Setup required directories"""
        self.base_dir = Path("setup/wireguard")
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        self.download_dir = self.base_dir / "downloads"
        self.download_dir.mkdir(exist_ok=True)
        
        self.config_dir = self.base_dir / "configs"
        self.config_dir.mkdir(exist_ok=True)
        
        self.backup_dir = self.base_dir / "backups"
        self.backup_dir.mkdir(exist_ok=True)
    
    def detect_system(self) -> Dict:
        """Detect system information"""
        import platform
        
        system_info = {
            "os": platform.system().lower(),
            "arch": platform.machine().lower(),
            "version": platform.version(),
            "python_version": platform.python_version()
        }
        
        # Normalize architecture
        if system_info["arch"] in ["amd64", "x86_64"]:
            system_info["arch"] = "x64"
        elif system_info["arch"] in ["arm64", "aarch64"]:
            system_info["arch"] = "arm64"
        elif system_info["arch"] in ["i386", "i686"]:
            system_info["arch"] = "x86"
        
        self.logger.info(f"Detected system: {system_info['os']} {system_info['arch']}")
        return system_info
    
    def check_wireguard_installed(self) -> Dict:
        """Check if WireGuard is already installed"""
        system_info = self.detect_system()
        
        if system_info["os"] == "windows":
            return self.check_windows_wireguard()
        elif system_info["os"] == "linux":
            return self.check_linux_wireguard()
        else:
            return {"installed": False, "message": f"Unsupported OS: {system_info['os']}"}
    
    def check_windows_wireguard(self) -> Dict:
        """Check WireGuard installation on Windows"""
        try:
            # Check if WireGuard executable exists
            wg_path = self.install_paths["windows"]["executable"]
            if not Path(wg_path).exists():
                return {"installed": False, "message": "WireGuard executable not found"}
            
            # Check version
            result = subprocess.run([wg_path, "--version"], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                version = result.stdout.strip()
                
                # Check service
                try:
                    service_result = subprocess.run(
                        ["sc", "query", "WireGuardService"], 
                        capture_output=True, text=True, timeout=10
                    )
                    service_running = service_result.returncode == 0
                except:
                    service_running = False
                
                return {
                    "installed": True,
                    "version": version,
                    "service_running": service_running,
                    "executable": wg_path
                }
            else:
                return {"installed": False, "message": "WireGuard executable not working"}
                
        except Exception as e:
            return {"installed": False, "message": f"Error checking WireGuard: {e}"}
    
    def check_linux_wireguard(self) -> Dict:
        """Check WireGuard installation on Linux"""
        try:
            # Check if wg command exists
            result = subprocess.run(["which", "wg"], capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                return {"installed": False, "message": "WireGuard command not found"}
            
            wg_path = result.stdout.strip()
            
            # Check version
            version_result = subprocess.run(["wg", "--version"], capture_output=True, text=True, timeout=10)
            if version_result.returncode == 0:
                version = version_result.stdout.strip()
                
                # Check kernel module
                try:
                    module_result = subprocess.run(["lsmod", "|", "grep", "wireguard"], 
                                               shell=True, capture_output=True, text=True, timeout=10)
                    kernel_module = module_result.returncode == 0 and len(module_result.stdout.strip()) > 0
                except:
                    kernel_module = False
                
                return {
                    "installed": True,
                    "version": version,
                    "kernel_module": kernel_module,
                    "executable": wg_path
                }
            else:
                return {"installed": False, "message": "WireGuard command not working"}
                
        except Exception as e:
            return {"installed": False, "message": f"Error checking WireGuard: {e}"}
    
    def download_wireguard(self, system_info: Dict) -> bool:
        """Download WireGuard installer"""
        try:
            self.logger.info("Downloading WireGuard...")
            
            # Determine download URL
            if system_info["os"] == "windows":
                if system_info["arch"] == "arm64":
                    url = self.wireguard_urls["windows_arm64"]
                    filename = "wireguard-arm64-0.5.3.msi"
                else:
                    url = self.wireguard_urls["windows_x64"]
                    filename = "wireguard-amd64-0.5.3.msi"
            else:
                self.logger.error("Linux download not implemented yet")
                return False
            
            # Download file
            download_path = self.download_dir / filename
            
            if download_path.exists():
                self.logger.info(f"WireGuard installer already exists: {download_path}")
                return True
            
            response = requests.get(url, stream=True, timeout=300)
            response.raise_for_status()
            
            with open(download_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            self.logger.info(f"WireGuard downloaded to: {download_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to download WireGuard: {e}")
            return False
    
    def install_wireguard_windows(self) -> bool:
        """Install WireGuard on Windows"""
        try:
            self.logger.info("Installing WireGuard on Windows...")
            
            # Find installer
            installers = list(self.download_dir.glob("*.msi"))
            if not installers:
                self.logger.error("No WireGuard installer found")
                return False
            
            installer_path = installers[0]
            
            # Run installer silently
            cmd = [
                "msiexec", "/i", str(installer_path),
                "/quiet", "/norestart"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                self.logger.info("WireGuard installed successfully")
                
                # Wait for installation to complete
                import time
                time.sleep(5)
                
                return True
            else:
                self.logger.error(f"Installation failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to install WireGuard: {e}")
            return False
    
    def install_wireguard_linux(self) -> bool:
        """Install WireGuard on Linux"""
        try:
            self.logger.info("Installing WireGuard on Linux...")
            
            # Try package manager installation
            distro_commands = {
                "ubuntu": ["sudo", "apt-get", "update", "&&", "sudo", "apt-get", "install", "-y", "wireguard"],
                "debian": ["sudo", "apt-get", "update", "&&", "sudo", "apt-get", "install", "-y", "wireguard"],
                "fedora": ["sudo", "dnf", "install", "-y", "wireguard-tools"],
                "centos": ["sudo", "yum", "install", "-y", "epel-release", "&&", "sudo", "yum", "install", "-y", "wireguard-tools"],
                "arch": ["sudo", "pacman", "-S", "--noconfirm", "wireguard-tools"]
            }
            
            # Try to detect distribution
            try:
                with open("/etc/os-release", "r") as f:
                    os_release = f.read().lower()
                
                for distro, cmd in distro_commands.items():
                    if distro in os_release:
                        result = subprocess.run(" ".join(cmd), shell=True, capture_output=True, text=True, timeout=300)
                        return result.returncode == 0
                
                # Fallback to generic installation
                result = subprocess.run(["sudo", "pip", "install", "wireguard"], capture_output=True, text=True, timeout=300)
                return result.returncode == 0
                
            except Exception as e:
                self.logger.error(f"Failed to install WireGuard on Linux: {e}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to install WireGuard: {e}")
            return False
    
    def configure_firewall_windows(self) -> bool:
        """Configure Windows Firewall for WireGuard"""
        try:
            self.logger.info("Configuring Windows Firewall...")
            
            # Add firewall rule for WireGuard
            cmd = [
                "netsh", "advfirewall", "firewall", "add", "rule",
                "name=WireGuard",
                "dir=in",
                "action=allow",
                "protocol=UDP",
                "localport=51820"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                self.logger.info("Firewall rule added successfully")
                return True
            else:
                self.logger.warning(f"Failed to add firewall rule: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to configure firewall: {e}")
            return False
    
    def configure_firewall_linux(self) -> bool:
        """Configure Linux firewall for WireGuard"""
        try:
            self.logger.info("Configuring Linux firewall...")
            
            # Try ufw first
            try:
                result = subprocess.run(["sudo", "ufw", "allow", "51820/udp"], 
                                     capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    self.logger.info("UFW rule added successfully")
                    return True
            except:
                pass
            
            # Try iptables
            try:
                cmd = ["sudo", "iptables", "-A", "INPUT", "-p", "udp", "--dport", "51820", "-j", "ACCEPT"]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    self.logger.info("iptables rule added successfully")
                    return True
            except:
                pass
            
            self.logger.warning("Could not configure firewall automatically")
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to configure firewall: {e}")
            return False
    
    def create_service_config(self) -> bool:
        """Create WireGuard service configuration"""
        try:
            self.logger.info("Creating service configuration...")
            
            # Create a basic configuration
            config_content = '''# Homelab Tools Mesh VPN Configuration
# This file will be automatically updated by the mesh VPN system

[Interface]
# PrivateKey will be generated automatically
Address = 10.100.0.1/24
ListenPort = 51820
DNS = 1.1.1.1, 8.8.8.8

# Peers will be added automatically by the mesh VPN system
# [Peer]
# PublicKey = <peer_public_key>
# Endpoint = <peer_endpoint>:51820
# AllowedIPs = 10.100.0.2/32
# PersistentKeepalive = 25
'''
            
            system_info = self.detect_system()
            if system_info["os"] == "windows":
                config_path = Path(self.install_paths["windows"]["config_dir"]) / "wg0.conf"
            else:
                config_path = Path(self.install_paths["linux"]["config_dir"]) / "wg0.conf"
            
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(config_path, 'w') as f:
                f.write(config_content)
            
            self.logger.info(f"Service configuration created: {config_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create service configuration: {e}")
            return False
    
    def start_wireguard_service(self) -> bool:
        """Start WireGuard service"""
        try:
            system_info = self.detect_system()
            
            if system_info["os"] == "windows":
                return self.start_windows_service()
            else:
                return self.start_linux_service()
                
        except Exception as e:
            self.logger.error(f"Failed to start WireGuard service: {e}")
            return False
    
    def start_windows_service(self) -> bool:
        """Start Windows WireGuard service"""
        try:
            self.logger.info("Starting Windows WireGuard service...")
            
            # Start service
            result = subprocess.run(["sc", "start", "WireGuardService"], 
                                 capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                self.logger.info("WireGuard service started successfully")
                return True
            else:
                self.logger.error(f"Failed to start service: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to start Windows service: {e}")
            return False
    
    def start_linux_service(self) -> bool:
        """Start Linux WireGuard service"""
        try:
            self.logger.info("Starting Linux WireGuard service...")
            
            # Enable and start service
            commands = [
                ["sudo", "systemctl", "enable", "wg-quick@wg0"],
                ["sudo", "systemctl", "start", "wg-quick@wg0"]
            ]
            
            for cmd in commands:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                if result.returncode != 0:
                    self.logger.error(f"Failed command {' '.join(cmd)}: {result.stderr}")
                    return False
            
            self.logger.info("WireGuard service started successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start Linux service: {e}")
            return False
    
    def run_full_installation(self) -> Dict:
        """Run complete WireGuard installation"""
        installation_log = {
            "start_time": datetime.now().isoformat(),
            "steps": [],
            "success": False,
            "error": None
        }
        
        try:
            # Step 1: Detect system
            system_info = self.detect_system()
            installation_log["steps"].append({
                "step": "system_detection",
                "status": "completed",
                "details": system_info
            })
            
            # Step 2: Check if already installed
            check_result = self.check_wireguard_installed()
            if check_result.get("installed", False):
                installation_log["steps"].append({
                    "step": "installation_check",
                    "status": "already_installed",
                    "details": check_result
                })
                self.logger.info("WireGuard is already installed")
            else:
                # Step 3: Download WireGuard
                if not self.download_wireguard(system_info):
                    raise Exception("Failed to download WireGuard")
                
                installation_log["steps"].append({
                    "step": "download",
                    "status": "completed"
                })
                
                # Step 4: Install WireGuard
                if system_info["os"] == "windows":
                    if not self.install_wireguard_windows():
                        raise Exception("Failed to install WireGuard on Windows")
                else:
                    if not self.install_wireguard_linux():
                        raise Exception("Failed to install WireGuard on Linux")
                
                installation_log["steps"].append({
                    "step": "installation",
                    "status": "completed"
                })
            
            # Step 5: Configure firewall
            if system_info["os"] == "windows":
                self.configure_firewall_windows()
            else:
                self.configure_firewall_linux()
            
            installation_log["steps"].append({
                "step": "firewall_configuration",
                "status": "completed"
            })
            
            # Step 6: Create service configuration
            if not self.create_service_config():
                raise Exception("Failed to create service configuration")
            
            installation_log["steps"].append({
                "step": "service_configuration",
                "status": "completed"
            })
            
            # Step 7: Start service
            if not self.start_wireguard_service():
                raise Exception("Failed to start WireGuard service")
            
            installation_log["steps"].append({
                "step": "service_start",
                "status": "completed"
            })
            
            # Step 8: Verify installation
            verification = self.check_wireguard_installed()
            installation_log["steps"].append({
                "step": "verification",
                "status": "completed",
                "details": verification
            })
            
            installation_log["success"] = True
            installation_log["end_time"] = datetime.now().isoformat()
            
            self.logger.info("WireGuard installation completed successfully")
            return installation_log
            
        except Exception as e:
            installation_log["error"] = str(e)
            installation_log["end_time"] = datetime.now().isoformat()
            
            self.logger.error(f"WireGuard installation failed: {e}")
            return installation_log
    
    def create_installer_script(self) -> bool:
        """Create a standalone installer script"""
        try:
            script_content = '''@echo off
echo ========================================
echo Homelab Tools - WireGuard Installer
echo ========================================
echo.

echo Checking system requirements...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7 or higher
    pause
    exit /b 1
)

echo Starting WireGuard installation...
python setup\\wireguard_installer.py

if errorlevel 1 (
    echo.
    echo Installation failed. Check logs\\wireguard_installer.log for details.
    pause
    exit /b 1
)

echo.
echo WireGuard installation completed successfully!
echo.
echo Next steps:
echo 1. Run: python "Network Management\\bidirectional_mesh_setup.py"
echo 2. Follow the deployment instructions
echo 3. Start the mesh VPN using the provided scripts
echo.
pause
'''
            
            script_path = Path("setup/install_wireguard.bat")
            script_path.parent.mkdir(exist_ok=True)
            
            with open(script_path, 'w') as f:
                f.write(script_content)
            
            self.logger.info(f"Installer script created: {script_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create installer script: {e}")
            return False
    
    def create_package_info(self) -> bool:
        """Create package information file"""
        try:
            package_info = {
                "name": "Homelab Tools WireGuard Package",
                "version": "1.0.0",
                "description": "Automatic WireGuard installation for Homelab Tools mesh VPN",
                "supported_platforms": ["Windows 10", "Windows 11", "Linux"],
                "requirements": {
                    "python": ">=3.7",
                    "admin_privileges": True,
                    "internet_connection": True
                },
                "features": [
                    "Automatic WireGuard download and installation",
                    "Firewall configuration",
                    "Service setup and configuration",
                    "Installation verification",
                    "Cross-platform support"
                ],
                "installation_steps": [
                    "Run setup/install_wireguard.bat (Windows)",
                    "Follow on-screen instructions",
                    "Verify installation",
                    "Configure mesh VPN"
                ],
                "troubleshooting": {
                    "permission_denied": "Run as Administrator",
                    "download_failed": "Check internet connection",
                    "service_failed": "Check Windows Firewall settings"
                }
            }
            
            info_path = self.base_dir / "package_info.json"
            with open(info_path, 'w') as f:
                json.dump(package_info, f, indent=2)
            
            self.logger.info(f"Package info created: {info_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create package info: {e}")
            return False

def main():
    """Main installation function"""
    print("🔐 Homelab Tools - WireGuard Installer")
    print("=====================================")
    print()
    
    installer = WireGuardInstaller()
    
    # Create installer script and package info
    installer.create_installer_script()
    installer.create_package_info()
    
    print("📦 WireGuard package prepared")
    print("📜 Installer script created: setup/install_wireguard.bat")
    print("📋 Package info: setup/wireguard/package_info.json")
    print()
    
    # Run installation
    print("🚀 Starting WireGuard installation...")
    print()
    
    result = installer.run_full_installation()
    
    if result["success"]:
        print("✅ WireGuard installation completed successfully!")
        print()
        print("📊 Installation Summary:")
        for step in result["steps"]:
            status_icon = "✅" if step["status"] == "completed" else "ℹ️"
            print(f"   {status_icon} {step['step'].replace('_', ' ').title()}")
        
        print()
        print("🎯 Next Steps:")
        print("   1. Configure bidirectional mesh VPN")
        print("   2. Deploy to HAZINTEL2 system")
        print("   3. Start mesh VPN services")
        
    else:
        print("❌ WireGuard installation failed")
        print(f"📋 Error: {result.get('error', 'Unknown error')}")
        print()
        print("🔧 Troubleshooting:")
        print("   1. Run as Administrator")
        print("   2. Check internet connection")
        print("   3. Verify Windows Firewall settings")
        print("   4. Check logs/setup/wireguard_installer.log")
    
    print()
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()
