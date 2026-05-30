#!/usr/bin/env python3
"""
Windows 10 Dependency Installer for Homelab Tools
Checks and installs all required dependencies for Windows 10 compatibility
"""

import subprocess
import sys
import os
import platform
from pathlib import Path

def run_command(command, capture_output=True):
    """Run a command and return result"""
    try:
        result = subprocess.run(command, shell=True, capture_output=capture_output, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_python_version():
    """Check Python version compatibility"""
    print("🔍 Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.8+")
        return False

def check_pip():
    """Check if pip is available"""
    print("🔍 Checking pip...")
    success, _, _ = run_command("python -m pip --version")
    if success:
        print("✅ pip is available")
        return True
    else:
        print("❌ pip not found")
        return False

def install_package(package):
    """Install a Python package"""
    print(f"📦 Installing {package}...")
    success, output, error = run_command(f"python -m pip install {package}")
    if success:
        print(f"✅ {package} installed successfully")
        return True
    else:
        print(f"❌ Failed to install {package}: {error}")
        return False

def check_and_install_package(package_name, import_name=None):
    """Check if a package is installed and install if needed"""
    if import_name is None:
        import_name = package_name
    
    print(f"🔍 Checking {package_name}...")
    try:
        __import__(import_name)
        print(f"✅ {package_name} is already installed")
        return True
    except ImportError:
        print(f"⚠️ {package_name} not found, installing...")
        return install_package(package_name)

def check_windows_features():
    """Check Windows-specific features"""
    print("🔍 Checking Windows features...")
    
    # Check Windows version
    windows_version = platform.version()
    print(f"📋 Windows version: {windows_version}")
    
    # Check if we're on Windows 10
    if "10" in windows_version:
        print("✅ Running on Windows 10")
        return True
    else:
        print(f"⚠️ Not running on Windows 10 (version: {windows_version})")
        return False

def check_visual_cpp():
    """Check for Visual C++ Redistributable"""
    print("🔍 Checking Visual C++ Redistributable...")
    
    # Check if Visual C++ is installed
    success, output, _ = run_command('where cl', capture_output=True)
    if success:
        print("✅ Visual C++ compiler found")
        return True
    else:
        print("⚠️ Visual C++ compiler not found")
        print("💡 Some packages may require Visual C++ Redistributable")
        print("📥 Download from: https://aka.ms/vs/17/release/vc_redist.x64.exe")
        return False

def main():
    """Main installation function"""
    print("🚀 Homelab Tools - Windows 10 Dependency Installer")
    print("=" * 60)
    
    # System checks
    print("\n📋 SYSTEM CHECKS")
    print("-" * 20)
    
    python_ok = check_python_version()
    if not python_ok:
        print("\n❌ Please install Python 3.8 or higher from https://python.org")
        return False
    
    pip_ok = check_pip()
    if not pip_ok:
        print("\n❌ Please install pip first")
        return False
    
    windows_ok = check_windows_features()
    check_visual_cpp()
    
    # Required packages
    print("\n📦 REQUIRED PACKAGES")
    print("-" * 20)
    
    required_packages = [
        ("psutil", "psutil"),           # System monitoring
        ("tkinter", "tkinter"),         # GUI (built-in)
        ("requests", "requests"),       # HTTP requests
        ("numpy", "numpy"),             # Numerical computing
        ("matplotlib", "matplotlib"),   # Plotting
        ("pillow", "PIL"),             # Image processing
        ("scapy", "scapy"),            # Network packet manipulation
        ("netifaces", "netifaces"),    # Network interface discovery
        ("pywin32", "win32api"),       # Windows API
        ("wmi", "wmi"),                # Windows Management Instrumentation
        ("colorama", "colorama"),       # Colored terminal output
        ("pyyaml", "yaml"),            # YAML parsing
        ("jinja2", "jinja2"),          # Template engine
    ]
    
    failed_packages = []
    
    for package_name, import_name in required_packages:
        if not check_and_install_package(package_name, import_name):
            failed_packages.append(package_name)
    
    # Optional packages
    print("\n🎯 OPTIONAL PACKAGES")
    print("-" * 20)
    
    optional_packages = [
        ("opencv-python", "cv2"),      # Computer vision
        ("pandas", "pandas"),          # Data analysis
        ("scipy", "scipy"),            # Scientific computing
        ("plotly", "plotly"),          # Interactive plots
        ("dash", "dash"),              # Web apps
        ("flask", "flask"),            # Web framework
        ("fastapi", "fastapi"),        # Modern web API
        ("uvicorn", "uvicorn"),        # ASGI server
        ("websockets", "websockets"), # WebSocket support
        ("aiohttp", "aiohttp"),        # Async HTTP
        ("asyncio", "asyncio"),        # Async programming (built-in)
    ]
    
    for package_name, import_name in optional_packages:
        check_and_install_package(package_name, import_name)
    
    # Check common directory dependencies
    print("\n📁 COMMON DIRECTORY DEPENDENCIES")
    print("-" * 35)
    
    common_dir = Path("common")
    if common_dir.exists():
        print("✅ Common directory found")
        
        # Check if common modules can be imported
        sys.path.insert(0, str(common_dir))
        
        common_modules = [
            "subnet_discovery",
            "subnet_manager", 
            "windows_abstraction",
            "windows_compat",
            "error_handling"
        ]
        
        for module in common_modules:
            try:
                __import__(module)
                print(f"✅ {module} module available")
            except ImportError as e:
                print(f"❌ {module} module error: {e}")
                failed_packages.append(f"common.{module}")
    else:
        print("❌ Common directory not found")
    
    # Summary
    print("\n📊 INSTALLATION SUMMARY")
    print("=" * 60)
    
    if failed_packages:
        print(f"❌ {len(failed_packages)} packages failed to install:")
        for package in failed_packages:
            print(f"   - {package}")
        
        print("\n🔧 TROUBLESHOOTING:")
        print("1. Run this script as Administrator")
        print("2. Check your internet connection")
        print("3. Try installing packages individually:")
        for package in failed_packages:
            print(f"   python -m pip install {package}")
        
        print("\n4. If pywin32 fails, install from:")
        print("   https://github.com/mhammond/pywin32/releases")
        
        print("\n5. If WMI fails, install from:")
        print("   python -m pip install WMI")
        
        return False
    else:
        print("✅ All dependencies installed successfully!")
        print("\n🎉 Homelab Tools should now work on Windows 10!")
        print("\n📝 NEXT STEPS:")
        print("1. Restart your terminal/command prompt")
        print("2. Run: python homelab_launcher.py")
        print("3. Or double-click: launch_homelab.bat")
        
        return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Installation completed with errors")
        sys.exit(1)
    else:
        print("\n✅ Installation completed successfully")
        sys.exit(0)
