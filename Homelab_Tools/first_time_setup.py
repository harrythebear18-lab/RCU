#!/usr/bin/env python3
"""
Homelab Tools - First Time Setup
Simple setup script for initial configuration
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def print_header():
    """Print setup header"""
    print("=" * 60)
    print("  Homelab Tools - First Time Setup")
    print("=" * 60)
    print()

def run_command(cmd, description):
    """Run a command and show result"""
    print(f"[+] {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"    ✓ Success")
            return True
        else:
            print(f"    ✗ Failed: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"    ✗ Error: {e}")
        return False

def check_python():
    """Check Python installation"""
    print("[+] Checking Python installation...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"    ✓ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"    ✗ Python {version.major}.{version.minor} (need 3.8+)")
        return False

def check_git():
    """Check Git installation"""
    return run_command("git --version", "Checking Git")

def setup_git_lfs():
    """Setup Git LFS"""
    # Try bundled git-lfs first
    if os.path.exists("git-lfs.exe"):
        print("[+] Using bundled Git LFS...")
        if run_command(".\\git-lfs.exe install", "Installing Git LFS"):
            return True
    
    # Try system git-lfs
    return run_command("git lfs install", "Installing Git LFS")

def install_dependencies():
    """Install essential dependencies"""
    print("[+] Installing essential dependencies...")
    
    # Essential packages only
    essential_packages = [
        "psutil>=5.9.8",
        "matplotlib>=3.8.2", 
        "numpy>=1.26.4",
        "requests>=2.31.0",
        "wmi>=1.5.1"
    ]
    
    for package in essential_packages:
        if not run_command(f"pip install {package}", f"Installing {package}"):
            print(f"    ⚠ {package} failed (optional)")
    
    return True

def create_directories():
    """Create necessary directories"""
    print("[+] Creating directories...")
    
    directories = ["logs", "cache", "temp"]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"    ✓ Created {directory}")
    
    return True

def download_lfs_files():
    """Download LFS files"""
    return run_command("git lfs pull", "Downloading large files")

def create_config():
    """Create basic configuration"""
    print("[+] Creating configuration...")
    
    config_content = """# Homelab Tools - Basic Configuration
# Edit these settings as needed

# Performance settings
update_interval = 1000  # milliseconds
cache_size = 100       # MB

# Network settings  
timeout = 30           # seconds
max_connections = 10

# Logging
log_level = "INFO"
log_file = "logs/homelab.log"

# GPU support (if available)
gpu_enabled = True

# Display settings
theme = "dark"
window_size = "1200x800"
"""
    
    try:
        with open("homelab_config.ini", "w") as f:
            f.write(config_content)
        print("    ✓ Created homelab_config.ini")
        return True
    except Exception as e:
        print(f"    ✗ Failed to create config: {e}")
        return False

def test_setup():
    """Test basic setup"""
    print("[+] Testing setup...")
    
    try:
        import psutil
        import matplotlib
        import numpy
        import requests
        print("    ✓ Essential packages working")
        return True
    except ImportError as e:
        print(f"    ✗ Setup test failed: {e}")
        return False

def main():
    """Main setup function"""
    print_header()
    
    # Check if we're in the right directory
    if not os.path.exists("homelab_launcher.py"):
        print("Error: homelab_launcher.py not found!")
        print("Please run this script from the Homelab Tools directory.")
        return False
    
    # Run setup steps
    steps = [
        ("Python Installation", check_python),
        ("Git Installation", check_git), 
        ("Git LFS Setup", setup_git_lfs),
        ("Dependencies", install_dependencies),
        ("Directories", create_directories),
        ("LFS Files", download_lfs_files),
        ("Configuration", create_config),
        ("Setup Test", test_setup)
    ]
    
    print("Running first-time setup...")
    print()
    
    failed_steps = []
    
    for step_name, step_func in steps:
        try:
            if not step_func():
                failed_steps.append(step_name)
        except Exception as e:
            print(f"    ✗ {step_name} failed: {e}")
            failed_steps.append(step_name)
    
    print()
    print("=" * 60)
    print("  Setup Complete!")
    print("=" * 60)
    
    if failed_steps:
        print(f"⚠ {len(failed_steps)} steps had issues:")
        for step in failed_steps:
            print(f"   - {step}")
        print()
    
    print("Next steps:")
    print("1. Run: python homelab_launcher.py")
    print("2. Edit homelab_config.ini for custom settings")
    print("3. Check README.md for detailed usage")
    print()
    
    if len(failed_steps) == 0:
        print("✓ Setup completed successfully!")
        return True
    else:
        print("⚠ Setup completed with some issues")
        return False

if __name__ == "__main__":
    try:
        success = main()
        input("Press Enter to exit...")
    except KeyboardInterrupt:
        print("\nSetup cancelled.")
    except Exception as e:
        print(f"Setup failed: {e}")
        input("Press Enter to exit...")
