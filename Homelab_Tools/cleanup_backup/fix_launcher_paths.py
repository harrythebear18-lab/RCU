#!/usr/bin/env python3
"""
Fix Launcher Path Escape Sequences
Fixes invalid escape sequences in homelab_launcher.py tool paths
"""

import re
from pathlib import Path

def fix_launcher_paths():
    """Fix path escape sequences in launcher file"""
    launcher_file = Path('homelab_launcher.py')
    
    if not launcher_file.exists():
        print("Launcher file not found")
        return False
    
    # Read the launcher file
    with open(launcher_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix path escape sequences
    # Pattern to find "path": "path\with\backslashes"
    pattern = r'("path":\s*")([^"]*\\[^"]*")'
    
    def fix_path(match):
        prefix = match.group(1)
        path = match.group(2)
        # Convert single backslashes to double backslashes or forward slashes
        fixed_path = path.replace('\\', '/')
        return prefix + fixed_path
    
    # Apply the fix
    fixed_content = re.sub(pattern, fix_path, content)
    
    # Write the fixed content back
    with open(launcher_file, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print("Fixed launcher path escape sequences")
    return True

if __name__ == "__main__":
    fix_launcher_paths()
