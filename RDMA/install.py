#!/usr/bin/env python3
"""
Software-Defined RDMA Installation Script
Automated setup and dependency management
"""

import os
import sys
import subprocess
import platform
import urllib.request
import zipfile
import shutil
from pathlib import Path

class RDMAInstaller:
    """Automated installer for Software-Defined RDMA components"""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.python_version = sys.version_info
        self.install_dir = Path.cwd()
        
        # Required packages
        self.packages = [
            'pyzmq>=25.0.0',
            'numpy>=1.24.0',
            'psutil>=5.9.0',
            'asyncio-mqtt>=0.13.0'
        ]
        
        # Optional packages for enhanced functionality
        self.optional_packages = [
            'pytest>=7.0.0',  # For testing
            'matplotlib>=3.5.0',  # For performance graphs
            'scipy>=1.9.0'  # For advanced analytics
        ]
        
        print("Software-Defined RDMA Installer")
        print("=" * 40)
        print(f"System: {platform.system()} {platform.release()}")
        print(f"Python: {self.python_version.major}.{self.python_version.minor}.{self.python_version.micro}")
        print(f"Install Directory: {self.install_dir}")
        print()
    
    def check_python_version(self):
        """Check if Python version is compatible"""
        if self.python_version < (3, 8):
            print("❌ Python 3.8+ is required")
            return False
        
        print(f"✅ Python {self.python_version.major}.{self.python_version.minor} is compatible")
        return True
    
    def check_pip(self):
        """Check if pip is available and up to date"""
        try:
            import pip
            print("✅ pip is available")
            
            # Check if pip is up to date
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                             check=True, capture_output=True)
                print("✅ pip is up to date")
            except subprocess.CalledProcessError:
                print("⚠️  Failed to upgrade pip, continuing...")
            
            return True
        except ImportError:
            print("❌ pip is not available")
            return False
    
    def install_packages(self, packages, optional=False):
        """Install Python packages"""
        package_type = "Optional" if optional else "Required"
        print(f"\nInstalling {package_type} Packages:")
        print("-" * 30)
        
        for package in packages:
            try:
                print(f"Installing {package}...")
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", package],
                    check=True,
                    capture_output=True,
                    text=True
                )
                print(f"✅ {package}")
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to install {package}: {e}")
                if not optional:
                    return False
                else:
                    print(f"⚠️  Skipping optional package {package}")
        
        return True
    
    def check_system_dependencies(self):
        """Check system-specific dependencies"""
        print(f"\nChecking {self.system} dependencies:")
        print("-" * 30)
        
        if self.system == "windows":
            return self.check_windows_deps()
        elif self.system == "linux":
            return self.check_linux_deps()
        elif self.system == "darwin":
            return self.check_macos_deps()
        else:
            print(f"⚠️  Unknown system: {self.system}")
            return True
    
    def check_windows_deps(self):
        """Check Windows-specific dependencies"""
        try:
            import ctypes
            print("✅ Windows API (ctypes) available")
        except ImportError:
            print("❌ Windows API not available")
            return False
        
        # Check for Visual C++ redistributable
        try:
            # Test if we can load Windows APIs
            kernel32 = ctypes.windll.kernel32
            print("✅ Windows kernel32 accessible")
        except:
            print("⚠️  Windows API access may be limited")
        
        return True
    
    def check_linux_deps(self):
        """Check Linux-specific dependencies"""
        # Check for /proc filesystem access
        if os.path.exists("/proc"):
            print("✅ /proc filesystem accessible")
        else:
            print("⚠️  /proc filesystem not available (memory access limited)")
        
        # Check for ptrace capabilities
        try:
            with open("/proc/sys/kernel/yama/ptrace_scope", 'r') as f:
                ptrace_scope = f.read().strip()
                if ptrace_scope == "0":
                    print("✅ ptrace access available")
                else:
                    print("⚠️  ptrace access restricted (may need sudo)")
        except:
            print("⚠️  Could not check ptrace scope")
        
        return True
    
    def check_macos_deps(self):
        """Check macOS-specific dependencies"""
        try:
            import ctypes
            print("✅ macOS APIs (ctypes) available")
        except ImportError:
            print("❌ macOS APIs not available")
            return False
        
        return True
    
    def create_config_files(self):
        """Create configuration files"""
        print("\nCreating configuration files:")
        print("-" * 30)
        
        # Create config directory
        config_dir = self.install_dir / "config"
        config_dir.mkdir(exist_ok=True)
        print("✅ Created config directory")
        
        # Create default configuration
        config_content = """# Software-Defined RDMA Configuration
# Edit these values to customize your setup

[zeromq]
port = 5555
buffer_size = 1048576  # 1MB

[virtual_pcie]
port = 7777
max_connections = 10
allowed_pids = []

[udp_bridge]
port = 9999
max_packet_size = 1400
timeout = 1.0
max_retries = 5

[logging]
level = INFO
file = rdma.log
max_size = 10485760  # 10MB
backup_count = 5

[security]
enable_encryption = false
require_authentication = false
allowed_hosts = []
"""
        
        config_file = config_dir / "default.conf"
        with open(config_file, 'w') as f:
            f.write(config_content)
        print("✅ Created default configuration")
        
        # Create example scripts directory
        examples_dir = self.install_dir / "examples"
        examples_dir.mkdir(exist_ok=True)
        print("✅ Created examples directory")
        
        return True
    
    def create_startup_scripts(self):
        """Create startup scripts for different platforms"""
        print("\nCreating startup scripts:")
        print("-" * 30)
        
        if self.system == "windows":
            self.create_windows_scripts()
        else:
            self.create_unix_scripts()
        
        return True
    
    def create_windows_scripts(self):
        """Create Windows batch scripts"""
        # Start ZeroMQ server
        zmq_server = f"""@echo off
echo Starting ZeroMQ RDMA Server...
cd /d "{self.install_dir}"
python zero_copy_rdmda.py server
pause
"""
        
        # Start Virtual PCIe driver
        pcie_driver = f"""@echo off
echo Starting Virtual PCIe Driver...
cd /d "{self.install_dir}"
python virtual_pcie_tunnel.py target
pause
"""
        
        # Start UDP bridge server
        udp_server = f"""@echo off
echo Starting UDP Memory Bridge Server...
cd /d "{self.install_dir}"
python udp_memory_bridge.py server
pause
"""
        
        scripts = {
            "start_zmq_server.bat": zmq_server,
            "start_pcie_driver.bat": pcie_driver,
            "start_udp_server.bat": udp_server
        }
        
        for filename, content in scripts.items():
            filepath = self.install_dir / filename
            with open(filepath, 'w') as f:
                f.write(content)
            print(f"✅ Created {filename}")
    
    def create_unix_scripts(self):
        """Create Unix/Linux shell scripts"""
        # Start ZeroMQ server
        zmq_server = f"""#!/bin/bash
echo "Starting ZeroMQ RDMA Server..."
cd "{self.install_dir}"
python3 zero_copy_rdmda.py server
"""
        
        # Start Virtual PCIe driver
        pcie_driver = f"""#!/bin/bash
echo "Starting Virtual PCIe Driver..."
cd "{self.install_dir}"
python3 virtual_pcie_tunnel.py target
"""
        
        # Start UDP bridge server
        udp_server = f"""#!/bin/bash
echo "Starting UDP Memory Bridge Server..."
cd "{self.install_dir}"
python3 udp_memory_bridge.py server
"""
        
        scripts = {
            "start_zmq_server.sh": zmq_server,
            "start_pcie_driver.sh": pcie_driver,
            "start_udp_server.sh": udp_server
        }
        
        for filename, content in scripts.items():
            filepath = self.install_dir / filename
            with open(filepath, 'w') as f:
                f.write(content)
            os.chmod(filepath, 0o755)  # Make executable
            print(f"✅ Created {filename}")
    
    def run_tests(self):
        """Run basic functionality tests"""
        print("\nRunning basic tests:")
        print("-" * 30)
        
        try:
            # Test imports
            print("Testing imports...")
            import zmq
            import numpy
            import psutil
            print("✅ All required packages imported successfully")
            
            # Test basic functionality
            print("Testing ZeroMQ...")
            context = zmq.Context()
            socket = context.socket(zmq.REQ)
            context.term()
            print("✅ ZeroMQ basic functionality OK")
            
            print("Testing NumPy...")
            test_array = numpy.array([1, 2, 3, 4, 5])
            print("✅ NumPy basic functionality OK")
            
            print("Testing psutil...")
            cpu_percent = psutil.cpu_percent()
            print("✅ psutil basic functionality OK")
            
            return True
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            return False
    
    def create_uninstall_info(self):
        """Create uninstall information"""
        uninstall_info = f"""# Software-Defined RDMA Uninstall Information
# Installed on: {platform.system()} {platform.release()}
# Python version: {self.python_version.major}.{self.python_version.minor}.{self.python_version.micro}
# Install directory: {self.install_dir}
# Packages: {', '.join(self.packages)}

# To uninstall, run:
# pip uninstall {' '.join(p.split('>=')[0] for p in self.packages)}

# To remove files:
# rm -rf {self.install_dir}
"""
        
        with open(self.install_dir / "uninstall.txt", 'w') as f:
            f.write(uninstall_info)
        print("✅ Created uninstall information")
    
    def install(self):
        """Run complete installation"""
        print("Starting installation...")
        print()
        
        # Check prerequisites
        if not self.check_python_version():
            return False
        
        if not self.check_pip():
            return False
        
        # Check system dependencies
        if not self.check_system_dependencies():
            print("⚠️  System dependency check failed, but continuing...")
        
        # Install required packages
        if not self.install_packages(self.packages):
            print("❌ Required package installation failed")
            return False
        
        # Install optional packages
        self.install_packages(self.optional_packages, optional=True)
        
        # Create configuration files
        self.create_config_files()
        
        # Create startup scripts
        self.create_startup_scripts()
        
        # Run tests
        if not self.run_tests():
            print("⚠️  Some tests failed, but installation may still work")
        
        # Create uninstall info
        self.create_uninstall_info()
        
        print("\n" + "=" * 40)
        print("🎉 Installation completed successfully!")
        print()
        print("Next steps:")
        print("1. Review configuration in config/default.conf")
        print("2. Start a server component:")
        if self.system == "windows":
            print("   - Run start_zmq_server.bat")
            print("   - Run start_pcie_driver.bat")
            print("   - Run start_udp_server.bat")
        else:
            print("   - ./start_zmq_server.sh")
            print("   - ./start_pcie_driver.sh")
            print("   - ./start_udp_server.sh")
        print("3. Test with client components")
        print("4. Read README.md for detailed usage")
        print()
        print("🔥 Safe DMA without the fire hazard!")
        
        return True


def main():
    """Main installation function"""
    installer = RDMAInstaller()
    
    try:
        success = installer.install()
        if not success:
            print("\n❌ Installation failed")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Installation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Installation error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
