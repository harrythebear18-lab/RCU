#!/usr/bin/env python3
"""
Homelab Monitoring Tools Setup Script
Automated setup and dependency installation for all monitoring tools
"""

import subprocess
import sys
import os
from pathlib import Path
import platform

def check_python_version():
    """Check Python version compatibility"""
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required")
        return False
    print(f"✅ Python version: {sys.version}")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    
    try:
        # Install from unified requirements.txt
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def check_tool_availability():
    """Check availability of all monitoring tools"""
    print("\n🔍 Checking tool availability...")
    
    tools = {
        "CPU Monitor": "Cpu Monitor/cpu_monitor.py",
        "GPU Monitor": "Gpu Monitor/gpu_monitor.py", 
        "Network Monitor": "Network Monitor/network_monitor.py",
        "RAM Monitor": "Ram clean up/ram_monitor_gui.py",
        "RDMA Tools": "RDMA/rdma_desktop_app.py"
    }
    
    available_count = 0
    for tool_name, tool_path in tools.items():
        if Path(tool_path).exists():
            print(f"✅ {tool_name}: Available")
            available_count += 1
        else:
            print(f"❌ {tool_name}: Missing ({tool_path})")
    
    print(f"\n📊 Summary: {available_count}/{len(tools)} tools available")
    return available_count == len(tools)

def setup_gpu_support():
    """Setup GPU monitoring support"""
    print("\n🎮 Setting up GPU monitoring...")
    
    try:
        # Check for NVIDIA GPU
        try:
            subprocess.run(["nvidia-smi"], check=True, capture_output=True, timeout=5)
            print("✅ NVIDIA GPU detected")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠️  NVIDIA GPU not detected or nvidia-smi not available")
        
        # Install GPU monitoring library
        subprocess.check_call([sys.executable, "-m", "pip", "install", "GPUtil"], 
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("✅ GPU monitoring libraries installed")
        
    except subprocess.CalledProcessError:
        print("⚠️  GPU monitoring setup incomplete (optional)")

def setup_network_tools():
    """Setup network monitoring tools"""
    print("\n🌐 Setting up network monitoring...")
    
    # Check for ping3
    try:
        import ping3
        print("✅ Network ping tools available")
    except ImportError:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "ping3"],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("✅ Network ping tools installed")
        except:
            print("⚠️  Network ping tools setup incomplete")

def create_desktop_shortcuts():
    """Create desktop shortcuts for easy access"""
    print("\n🖥️  Creating desktop shortcuts...")
    
    desktop = Path.home() / "Desktop"
    if not desktop.exists():
        desktop = Path.home() / "Desktop"  # Try alternative path
    
    if desktop.exists():
        try:
            # Create dashboard shortcut
            if platform.system() == "Windows":
                # Windows shortcut creation
                import winshell
                from win32com.client import Dispatch
                
                desktop_path = str(desktop)
                path = os.path.join(desktop_path, "Homelab Dashboard.lnk")
                target = os.path.join(os.getcwd(), "homelab_dashboard.py")
                wDir = os.getcwd()
                icon = target
                
                shell = Dispatch('WScript.Shell')
                shortcut = shell.CreateShortCut(path)
                shortcut.Targetpath = sys.executable
                shortcut.Arguments = f'"{target}"'
                shortcut.WorkingDirectory = wDir
                shortcut.IconLocation = icon
                shortcut.save()
                
            print("✅ Desktop shortcuts created")
        except ImportError:
            print("⚠️  Cannot create desktop shortcuts (additional libraries required)")
        except Exception as e:
            print(f"⚠️  Desktop shortcut creation failed: {e}")
    else:
        print("⚠️  Desktop folder not found")

def verify_installation():
    """Verify installation by testing imports"""
    print("\n🧪 Verifying installation...")
    
    test_imports = [
        ("psutil", "System monitoring"),
        ("matplotlib", "Data visualization"),
        ("numpy", "Numerical computing"),
        ("tkinter", "GUI framework"),
        ("ping3", "Network tools"),
        ("requests", "HTTP client")
    ]
    
    failed_imports = []
    
    for module, description in test_imports:
        try:
            __import__(module)
            print(f"✅ {module}: {description}")
        except ImportError:
            print(f"❌ {module}: {description} - FAILED")
            failed_imports.append(module)
    
    # Optional imports
    optional_imports = [
        ("PyQt5", "Advanced GUI (RDMA tools)"),
        ("GPUtil", "GPU monitoring"),
        ("wmi", "Windows temperature monitoring")
    ]
    
    print("\n📋 Optional components:")
    for module, description in optional_imports:
        try:
            __import__(module)
            print(f"✅ {module}: {description}")
        except ImportError:
            print(f"⚠️  {module}: {description} - Not installed (optional)")
    
    return len(failed_imports) == 0

def main():
    """Main setup function"""
    print("🚀 Homelab Monitoring Tools Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Setup failed during dependency installation")
        return False
    
    # Setup additional components
    setup_gpu_support()
    setup_network_tools()
    
    # Check tool availability
    all_tools_available = check_tool_availability()
    
    # Create desktop shortcuts
    create_desktop_shortcuts()
    
    # Verify installation
    installation_ok = verify_installation()
    
    # Final summary
    print("\n" + "=" * 50)
    print("📊 SETUP SUMMARY")
    print("=" * 50)
    
    if installation_ok and all_tools_available:
        print("🎉 Setup completed successfully!")
        print("\n🚀 You can now run the dashboard:")
        print("   python homelab_dashboard.py")
        print("\n📚 Or run individual tools:")
        print("   python 'Cpu Monitor/cpu_monitor.py'")
        print("   python 'Gpu Monitor/gpu_monitor.py'")
        print("   python 'Network Monitor/network_monitor.py'")
        print("   python 'Ram clean up/ram_monitor_gui.py'")
        print("   python 'RDMA/rdma_desktop_app.py'")
        return True
    else:
        print("⚠️  Setup completed with some issues:")
        if not installation_ok:
            print("   - Some required dependencies failed to install")
        if not all_tools_available:
            print("   - Some monitoring tools are missing")
        
        print("\n💡 You can still use the available tools:")
        print("   python homelab_dashboard.py")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
