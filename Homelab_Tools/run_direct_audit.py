#!/usr/bin/env python3
"""
Direct Audit Runner - Bypasses batch file issues
Runs comprehensive audit directly with Python
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Run comprehensive audit directly"""
    print("🔍 DIRECT COMPREHENSIVE AUDIT")
    print("=" * 50)
    print("Running audit directly with Python...")
    print("=" * 50)
    
    try:
        # Run the comprehensive audit
        audit_script = Path("comprehensive_chunked_audit.py")
        
        if not audit_script.exists():
            print(f"❌ Audit script not found: {audit_script}")
            return 1
        
        print(f"📁 Running: {audit_script}")
        print()
        
        # Use the same Python that's running this script
        result = subprocess.run([sys.executable, str(audit_script)], 
                              cwd=Path.cwd(),
                              capture_output=False,
                              text=True)
        
        print()
        print("=" * 50)
        print("✅ Direct audit completed!")
        print("=" * 50)
        
        return result.returncode
        
    except Exception as e:
        print(f"❌ Direct audit failed: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    input("Press Enter to exit...")
    sys.exit(exit_code)
