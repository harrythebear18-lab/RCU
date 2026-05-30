#!/usr/bin/env python3
"""
Homelab Tools - Dependency Packaging Script
This script downloads and packages all dependencies for offline installation
"""

import os
import sys
import subprocess
import shutil
import zipfile
import tarfile
from pathlib import Path

def run_command(cmd, check=True):
    """Run a command and return the result"""
    try:
        result = subprocess.run(cmd, shell=True, check=check, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return False, e.stdout, e.stderr

def create_package_directory():
    """Create the package directory structure"""
    package_dir = Path("homelab_dependencies_package")
    
    # Create directory structure
    dirs = [
        "wheels",
        "scripts", 
        "docs",
        "config",
        "binaries"
    ]
    
    for dir_name in dirs:
        (package_dir / dir_name).mkdir(parents=True, exist_ok=True)
    
    return package_dir

def download_wheels(package_dir):
    """Download all dependencies as wheels"""
    print("Downloading dependencies as wheels...")
    
    # Download all dependencies
    success, stdout, stderr = run_command(f"pip download -r requirements.txt -d {package_dir / 'wheels'}")
    
    if success:
        print(f"✓ Downloaded wheels to {package_dir / 'wheels'}")
    else:
        print(f"✗ Failed to download wheels: {stderr}")
        return False
    
    # Download optional GPU packages
    print("Downloading optional GPU packages...")
    gpu_packages = [
        "cupy-cuda11x",
        "pyopencl", 
        "nvidia-ml-py3",
        "torch",
        "torchvision",
        "tensorflow"
    ]
    
    for package in gpu_packages:
        success, stdout, stderr = run_command(f"pip download {package} -d {package_dir / 'wheels'} --no-deps")
        if not success:
            print(f"  ⚠ Failed to download {package}: {stderr}")
    
    return True

def create_install_scripts(package_dir):
    """Create installation scripts for the package"""
    print("Creating installation scripts...")
    
    # Create offline install script
    install_script = f"""@echo off
title Homelab Tools - Offline Dependency Installation
color 0A
echo.
echo ========================================
echo  Homelab Tools - Offline Setup
echo ========================================
echo.
echo Installing dependencies from local package...
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

echo [✓] Python found

REM Install dependencies from wheels
echo Installing dependencies...
pip install --no-index --find-links wheels -r requirements.txt

if errorlevel 1 (
    echo [WARNING] Some dependencies failed to install
    echo Trying to install core dependencies...
    pip install --no-index --find-links wheels psutil matplotlib numpy
)

echo [✓] Dependencies installed

REM Install optional GPU packages
echo Installing optional GPU packages...
pip install --no-index --find-links wheels cupy-cuda11x pyopencl nvidia-ml-py3 >nul 2>&1

echo.
echo ========================================
echo    Installation Complete!
echo ========================================
echo.
echo You can now run: python homelab_launcher.py
echo.
pause
"""
    
    with open(package_dir / "scripts" / "install_offline.bat", "w") as f:
        f.write(install_script)
    
    # Create PowerShell install script
    ps_script = f"""# Homelab Tools - Offline PowerShell Installation
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Homelab Tools - Offline Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Check Python
try {{
    python --version | Out-Null
    Write-Host "[✓] Python found" -ForegroundColor Green
}} catch {{
    Write-Host "[ERROR] Python not found. Please install Python 3.8+" -ForegroundColor Red
    exit 1
}}

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
try {{
    pip install --no-index --find-links wheels -r requirements.txt
    Write-Host "[✓] Dependencies installed" -ForegroundColor Green
}} catch {{
    Write-Host "[!] Some dependencies failed to install" -ForegroundColor Yellow
    try {{
        pip install --no-index --find-links wheels psutil matplotlib numpy
        Write-Host "[✓] Core dependencies installed" -ForegroundColor Green
    }} catch {{
        Write-Host "[ERROR] Core dependencies installation failed" -ForegroundColor Red
    }}
}}

# Install optional GPU packages
Write-Host "Installing optional GPU packages..." -ForegroundColor Yellow
try {{
    pip install --no-index --find-links wheels cupy-cuda11x pyopencl nvidia-ml-py3
    Write-Host "[✓] GPU packages installed" -ForegroundColor Green
}} catch {{
    Write-Host "[!] GPU packages installation failed (optional)" -ForegroundColor Yellow
}}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Installation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "You can now run: python homelab_launcher.py" -ForegroundColor White
"""
    
    with open(package_dir / "scripts" / "install_offline.ps1", "w") as f:
        f.write(ps_script)
    
    print("✓ Installation scripts created")

def create_documentation(package_dir):
    """Create documentation for the package"""
    print("Creating documentation...")
    
    readme_content = """# Homelab Tools - Offline Dependencies Package

This package contains all dependencies needed to run Homelab Tools without internet access.

## Installation

### Windows (Batch File)
```cmd
scripts\\install_offline.bat
```

### Windows (PowerShell)
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\\scripts\\install_offline.ps1
```

### Manual Installation
```cmd
pip install --no-index --find-links wheels -r requirements.txt
```

## Package Contents

- `wheels/` - All Python package wheels
- `scripts/` - Installation scripts
- `docs/` - Documentation
- `config/` - Configuration files
- `binaries/` - Binary dependencies

## Requirements

- Python 3.8 or higher
- Windows 10/11 (recommended)
- Administrator privileges (optional, for some features)

## Optional GPU Support

After installation, you can install GPU packages:
```cmd
pip install --no-index --find-links wheels cupy-cuda11x pyopencl nvidia-ml-py3
```

## Troubleshooting

1. **Python not found**: Install Python from https://python.org
2. **Permission denied**: Run as administrator
3. **Dependencies fail**: Check Python version and try manual installation

## Support

For issues with Homelab Tools, check the main repository documentation.
"""
    
    with open(package_dir / "docs" / "README.md", "w") as f:
        f.write(readme_content)
    
    print("✓ Documentation created")

def create_configuration_files(package_dir):
    """Create configuration files"""
    print("Creating configuration files...")
    
    # Create environment configuration
    env_config = """# Homelab Tools Environment Configuration
# Copy this to .env file and modify as needed

# Performance settings
HOMELAB_PERFORMANCE_MODE=balanced
HOMELAB_UPDATE_INTERVAL=1000
HOMELAB_CACHE_SIZE=100

# Network settings
HOMELAB_NETWORK_TIMEOUT=30
HOMELAB_MAX_CONNECTIONS=10

# GPU settings
HOMELAB_GPU_ENABLED=true
HOMELAB_CUDA_DEVICE=0

# Logging settings
HOMELAB_LOG_LEVEL=INFO
HOMELAB_LOG_FILE=logs/homelab.log

# Security settings
HOMELAB_ENCRYPTION_ENABLED=false
HOMELAB_AUTH_REQUIRED=false
"""
    
    with open(package_dir / "config" / ".env.example", "w") as f:
        f.write(env_config)
    
    print("✓ Configuration files created")

def create_final_package(package_dir):
    """Create the final package archive"""
    print("Creating final package archive...")
    
    # Create ZIP archive
    archive_name = "homelab_dependencies_package.zip"
    
    with zipfile.ZipFile(archive_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in package_dir.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(package_dir.parent)
                zipf.write(file_path, arcname)
    
    print(f"✓ Package created: {archive_name}")
    
    # Calculate package size
    size_mb = os.path.getsize(archive_name) / (1024 * 1024)
    print(f"Package size: {size_mb:.1f} MB")
    
    return archive_name

def main():
    """Main packaging function"""
    print("========================================")
    print("  Homelab Tools - Dependency Packaging")
    print("========================================")
    print()
    
    # Check if pip is available
    success, stdout, stderr = run_command("pip --version")
    if not success:
        print("Error: pip not found. Please install Python and pip.")
        return False
    
    print(f"Using pip: {stdout.strip()}")
    print()
    
    # Create package directory
    package_dir = create_package_directory()
    print(f"✓ Created package directory: {package_dir}")
    
    # Download wheels
    if not download_wheels(package_dir):
        print("Failed to download dependencies")
        return False
    
    # Create installation scripts
    create_install_scripts(package_dir)
    
    # Create documentation
    create_documentation(package_dir)
    
    # Create configuration files
    create_configuration_files(package_dir)
    
    # Create final package
    archive_name = create_final_package(package_dir)
    
    print()
    print("========================================")
    print("  Packaging Complete!")
    print("========================================")
    print()
    print(f"Package created: {archive_name}")
    print()
    print("To use this package:")
    print("1. Extract the ZIP file on the target system")
    print("2. Run scripts/install_offline.bat")
    print("3. Launch Homelab Tools with: python homelab_launcher.py")
    print()
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nPackaging cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error during packaging: {e}")
        sys.exit(1)
