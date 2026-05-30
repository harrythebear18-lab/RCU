#!/usr/bin/env python3
"""
Test Portal Startup Script
Diagnoses issues with Homelab Portal startup
"""

import sys
import os
import traceback
from pathlib import Path

def test_imports():
    """Test all required imports for portal"""
    print("=== Testing Portal Imports ===")
    
    required_imports = [
        ('tkinter', 'GUI framework'),
        ('tkinter.ttk', 'Themed widgets'),
        ('PIL', 'Image processing'),
        ('psutil', 'System monitoring'),
        ('socket', 'Network communication'),
        ('threading', 'Threading support'),
        ('json', 'JSON handling'),
        ('datetime', 'Date/time handling'),
        ('pathlib', 'Path handling'),
        ('logging', 'Logging system')
    ]
    
    failed_imports = []
    
    for module, description in required_imports:
        try:
            __import__(module)
            print(f"✅ {module} - {description}")
        except ImportError as e:
            print(f"❌ {module} - {description} - FAILED: {e}")
            failed_imports.append(module)
    
    return len(failed_imports) == 0

def test_portal_file():
    """Test if portal file exists and is accessible"""
    print("\n=== Testing Portal File ===")
    
    current_dir = Path(__file__).parent
    portal_path = current_dir / "Core Services" / "homelab_portal.py"
    
    if portal_path.exists():
        print(f"✅ Portal file found: {portal_path}")
        
        # Try to read the file
        try:
            with open(portal_path, 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"✅ Portal file readable ({len(content)} characters)")
            return True
        except Exception as e:
            print(f"❌ Portal file not readable: {e}")
            return False
    else:
        print(f"❌ Portal file not found: {portal_path}")
        return False

def test_portal_syntax():
    """Test portal file for syntax errors"""
    print("\n=== Testing Portal Syntax ===")
    
    current_dir = Path(__file__).parent
    portal_path = current_dir / "Core Services" / "homelab_portal.py"
    
    try:
        with open(portal_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        # Compile to check for syntax errors
        compile(code, str(portal_path), 'exec')
        print("✅ Portal syntax is valid")
        return True
        
    except SyntaxError as e:
        print(f"❌ Syntax error in portal: {e}")
        print(f"   Line {e.lineno}: {e.text}")
        return False
    except Exception as e:
        print(f"❌ Error reading portal file: {e}")
        return False

def test_portal_imports():
    """Test importing portal module"""
    print("\n=== Testing Portal Module Import ===")
    
    current_dir = Path(__file__).parent
    core_services_dir = current_dir / "Core Services"
    
    # Add to path
    if str(core_services_dir) not in sys.path:
        sys.path.insert(0, str(core_services_dir))
    
    try:
        import homelab_portal
        print("✅ Portal module imported successfully")
        
        # Check if main class exists
        if hasattr(homelab_portal, 'HomelabPortal'):
            print("✅ HomelabPortal class found")
        else:
            print("❌ HomelabPortal class not found")
            return False
            
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import portal: {e}")
        print("   This might be due to missing dependencies or circular imports")
        return False
    except Exception as e:
        print(f"❌ Error importing portal: {e}")
        traceback.print_exc()
        return False

def test_portal_instantiation():
    """Test creating portal instance (without GUI)"""
    print("\n=== Testing Portal Instantiation ===")
    
    current_dir = Path(__file__).parent
    core_services_dir = current_dir / "Core Services"
    
    # Add to path
    if str(core_services_dir) not in sys.path:
        sys.path.insert(0, str(core_services_dir))
    
    try:
        import homelab_portal
        
        # Try to create instance (this might fail due to GUI)
        print("Attempting to create portal instance...")
        portal = homelab_portal.HomelabPortal()
        print("✅ Portal instance created successfully")
        
        # Check key attributes
        if hasattr(portal, 'node_id'):
            print(f"✅ Portal node_id: {portal.node_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create portal instance: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("Homelab Portal Startup Diagnostic")
    print("=" * 40)
    
    tests = [
        ("Basic Imports", test_imports),
        ("Portal File", test_portal_file),
        ("Portal Syntax", test_portal_syntax),
        ("Portal Import", test_portal_imports),
        ("Portal Instantiation", test_portal_instantiation)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 40)
    print("DIAGNOSTIC SUMMARY:")
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    # Overall result
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n🎉 All tests passed! Portal should start properly.")
        print("\nTo start portal manually:")
        print("python Core Services\\homelab_portal.py")
    else:
        print("\n⚠️  Some tests failed. Portal may not start properly.")
        print("\nCommon fixes:")
        print("1. Install missing packages: pip install Pillow psutil")
        print("2. Check Core Services directory exists")
        print("3. Verify Python 3.9+ is installed")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
