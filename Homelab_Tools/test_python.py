#!/usr/bin/env python3
"""
Python Installation Test Script
Tests if Python and required packages are available
"""

import sys
import subprocess
import os

def test_python_installation():
    """Test Python installation and version"""
    print("=== Python Installation Test ===")
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print(f"Python path: {sys.path[0]}")
    print()

def test_required_packages():
    """Test if required packages are available"""
    print("=== Required Packages Test ===")
    
    packages = [
        ("requests", "HTTP requests"),
        ("psutil", "System monitoring"),
        ("PIL", "Image processing (Pillow)"),
        ("flask", "Web framework"),
        ("flask_cors", "CORS support for Flask"),
        ("tkinter", "GUI framework"),
        ("matplotlib", "Plotting and graphs")
    ]
    
    missing_packages = []
    
    for package, description in packages:
        try:
            if package == "PIL":
                import PIL
                print(f"✅ {package} ({description}) - Available")
            elif package == "flask_cors":
                import flask_cors
                print(f"✅ {package} ({description}) - Available")
            else:
                __import__(package)
                print(f"✅ {package} ({description}) - Available")
        except ImportError:
            print(f"❌ {package} ({description}) - Missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\nMissing packages: {', '.join(missing_packages)}")
        print("Install with: pip install " + " ".join(missing_packages))
    else:
        print("\n✅ All required packages are available!")
    
    return len(missing_packages) == 0

def test_file_paths():
    """Test if required files exist"""
    print("\n=== File Path Test ===")
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Current directory: {current_dir}")
    
    required_files = [
        "Homelab_Bidirectional_Launcher.py",
        "Core Services\\homelab_portal.py",
        "Core Services\\windows_assistant_integration.py",
        "Windows Assistant\\main.py",
        "Windows Assistant\\homelab_integration.py"
    ]
    
    for file_path in required_files:
        full_path = os.path.join(current_dir, file_path)
        if os.path.exists(full_path):
            print(f"✅ {file_path} - Found")
        else:
            print(f"❌ {file_path} - Missing")

def main():
    """Main test function"""
    try:
        test_python_installation()
        packages_ok = test_required_packages()
        test_file_paths()
        
        print("\n=== Test Summary ===")
        if packages_ok:
            print("✅ All tests passed! You can run the Homelab Bidirectional Launcher.")
            print("\nTo start the launcher, run:")
            print("python Homelab_Bidirectional_Launcher.py")
        else:
            print("❌ Some tests failed. Please install missing packages.")
        
        input("\nPress Enter to exit...")
        
    except Exception as e:
        print(f"Test error: {e}")
        input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
