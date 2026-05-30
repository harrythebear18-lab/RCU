#!/usr/bin/env python3
"""
Homelab Tools Deployment Script
Automated setup and deployment for Homelab Tools system
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path
import json
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class HomelabDeployer:
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.system = platform.system()
        self.python_version = sys.version_info
        
    def check_requirements(self):
        """Check system requirements"""
        logger.info("🔍 Checking system requirements...")
        
        # Check Python version
        if self.python_version < (3, 7):
            logger.error("❌ Python 3.7+ required")
            return False
        
        logger.info(f"✅ Python {self.python_version.major}.{self.python_version.minor}")
        
        # Check platform
        if self.system in ["Windows", "Linux", "Darwin"]:
            logger.info(f"✅ Platform: {self.system}")
        else:
            logger.warning(f"⚠️  Platform {self.system} may have limited support")
        
        return True
    
    def install_dependencies(self):
        """Install required dependencies"""
        logger.info("📦 Installing dependencies...")
        
        requirements_file = self.root_dir / "requirements.txt"
        if requirements_file.exists():
            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
                ])
                logger.info("✅ Dependencies installed successfully")
            except subprocess.CalledProcessError as e:
                logger.error(f"❌ Failed to install dependencies: {e}")
                return False
        else:
            logger.warning("⚠️  requirements.txt not found")
        
        return True
    
    def install_gpu_packages(self):
        """Install optional GPU packages"""
        logger.info("🎮 Checking GPU packages...")
        
        gpu_packages = [
            "GPUtil",
            "cupy-cuda11x"  # NVIDIA CUDA support
        ]
        
        for package in gpu_packages:
            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", package
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                logger.info(f"✅ {package} installed")
            except subprocess.CalledProcessError:
                logger.warning(f"⚠️  {package} installation failed (optional)")
    
    def setup_environment(self):
        """Setup environment variables and configuration"""
        logger.info("⚙️  Setting up environment...")
        
        # Create .env file
        env_file = self.root_dir / ".env"
        env_config = {
            "HOMELAB_ROOT": str(self.root_dir),
            "HOMELAB_HOST_IP": "192.168.1.100",
            "HOMELAB_SERVER_HOST": "0.0.0.0",
            "HOMELAB_SERVER_PORT": "25565",
            "RDMA_DEVICE_PATH": r"\.\UltraDMA" if self.system == "Windows" else "/dev/ultra_dma",
            "CUDA_VISIBLE_DEVICES": "0",
            "GPU_MEMORY_FRACTION": "0.8",
            "OMP_NUM_THREADS": "4",
            "NUMBA_NUM_THREADS": "4"
        }
        
        with open(env_file, 'w') as f:
            for key, value in env_config.items():
                f.write(f"{key}={value}\n")
        
        logger.info("✅ Environment configuration created")
    
    def create_shortcuts(self):
        """Create desktop shortcuts and launch scripts"""
        logger.info("🚀 Creating launch shortcuts...")
        
        # Windows batch file
        if self.system == "Windows":
            batch_file = self.root_dir / "start_homelab.bat"
            with open(batch_file, 'w') as f:
                f.write(f"""@echo off
cd /d "{self.root_dir}"
echo Starting Homelab Tools Launcher...
python homelab_launcher.py
pause
""")
            logger.info("✅ Windows batch file created")
        
        # Linux/Mac shell script
        else:
            shell_file = self.root_dir / "start_homelab.sh"
            with open(shell_file, 'w') as f:
                f.write(f"""#!/bin/bash
cd "{self.root_dir}"
echo "Starting Homelab Tools Launcher..."
python3 homelab_launcher.py
""")
            shell_file.chmod(0o755)
            logger.info("✅ Shell script created")
    
    def run_system_test(self):
        """Run system integration test"""
        logger.info("🧪 Running system integration test...")
        
        test_file = self.root_dir / "system_integration_test.py"
        if test_file.exists():
            try:
                result = subprocess.run([
                    sys.executable, str(test_file)
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    logger.info("✅ System integration test passed")
                    return True
                else:
                    logger.error(f"❌ System test failed: {result.stderr}")
                    return False
            except subprocess.TimeoutExpired:
                logger.error("❌ System test timed out")
                return False
            except Exception as e:
                logger.error(f"❌ System test error: {e}")
                return False
        else:
            logger.warning("⚠️  System integration test not found")
            return True
    
    def create_desktop_shortcut(self):
        """Create desktop shortcut (Windows only)"""
        if self.system != "Windows":
            return
        
        try:
            import winshell
            from win32com.client import Dispatch
            
            desktop = winshell.desktop()
            path = os.path.join(desktop, "Homelab Tools.lnk")
            target = str(self.root_dir / "homelab_launcher.py")
            wDir = str(self.root_dir)
            icon = str(self.root_dir / "icons" / "launcher.ico")
            
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(path)
            shortcut.Targetpath = sys.executable
            shortcut.Arguments = f'"{target}"'
            shortcut.WorkingDirectory = wDir
            shortcut.IconLocation = icon if os.path.exists(icon) else sys.executable
            shortcut.save()
            
            logger.info("✅ Desktop shortcut created")
        except ImportError:
            logger.warning("⚠️  Could not create desktop shortcut (missing winshell)")
        except Exception as e:
            logger.warning(f"⚠️  Desktop shortcut creation failed: {e}")
    
    def generate_deployment_report(self):
        """Generate deployment report"""
        logger.info("📋 Generating deployment report...")
        
        report = {
            "deployment_time": str(Path(__file__).stat().st_mtime),
            "system": self.system,
            "python_version": f"{self.python_version.major}.{self.python_version.minor}.{self.python_version.micro}",
            "root_directory": str(self.root_dir),
            "components": {
                "monitoring": ["CPU Monitor", "GPU Monitor", "Network Monitor", "RAM Monitor", "Storage Monitor"],
                "rdma": ["Memory Portal", "Memory Server", "Memory Client"],
                "compute": ["Compute Server", "Compute Client", "Hybrid Compute"],
                "management": ["Homelab Launcher", "System Integration Test"]
            },
            "ports": {
                "memory_sharing": 25565,
                "compute_sharing": 25565,
                "rdma_portal": 25565
            },
            "gpu_support": True,
            "windows_compatible": self.system == "Windows"
        }
        
        report_file = self.root_dir / "deployment_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info("✅ Deployment report generated")
    
    def deploy(self):
        """Main deployment function"""
        logger.info("🚀 Starting Homelab Tools deployment...")
        
        steps = [
            ("Checking requirements", self.check_requirements),
            ("Installing dependencies", self.install_dependencies),
            ("Installing GPU packages", self.install_gpu_packages),
            ("Setting up environment", self.setup_environment),
            ("Creating shortcuts", self.create_shortcuts),
            ("Running system test", self.run_system_test),
            ("Generating report", self.generate_deployment_report)
        ]
        
        for step_name, step_func in steps:
            logger.info(f"\n📋 {step_name}...")
            if not step_func():
                logger.error(f"❌ Deployment failed at {step_name}")
                return False
        
        logger.info("\n🎉 Homelab Tools deployment completed successfully!")
        logger.info(f"📁 Installation directory: {self.root_dir}")
        logger.info("🚀 Run 'python homelab_launcher.py' to start the system")
        
        return True

def main():
    """Main entry point"""
    deployer = HomelabDeployer()
    
    try:
        if deployer.deploy():
            print("\n" + "="*60)
            print("🎉 DEPLOYMENT SUCCESSFUL!")
            print("="*60)
            print("📁 Homelab Tools has been installed and configured")
            print("🚀 To start: python homelab_launcher.py")
            print("📊 All monitoring tools are ready to use")
            print("🌐 Distributed computing features enabled")
            print("="*60)
        else:
            print("\n❌ Deployment failed. Check the logs above.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️  Deployment cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
