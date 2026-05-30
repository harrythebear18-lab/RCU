#!/usr/bin/env python3
"""
Fix All Escape Sequences in Launcher
Comprehensive fix for all escape sequence issues in the launcher
"""

import re
from pathlib import Path

def fix_all_escape_sequences():
    """Fix all escape sequences in the launcher file"""
    launcher_file = Path(__file__).parent / "homelab_launcher.py"
    
    if not launcher_file.exists():
        print(f"Launcher file not found: {launcher_file}")
        return False
    
    # Read the launcher file
    with open(launcher_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all path entries and fix escape sequences
    path_pattern = r'"path":\s*"([^"]+)"'
    matches = re.findall(path_pattern, content)
    
    print(f"Found {len(matches)} path entries to fix")
    
    updated_count = 0
    
    for current_path in matches:
        # Replace backslashes with forward slashes
        if '\\' in current_path:
            fixed_path = current_path.replace('\\', '/')
            old_entry = f'"path": "{current_path}"'
            new_entry = f'"path": "{fixed_path}"'
            
            if old_entry in content:
                content = content.replace(old_entry, new_entry)
                updated_count += 1
                print(f"Fixed: {current_path} -> {fixed_path}")
    
    # Write the updated content back
    with open(launcher_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Fixed {updated_count} escape sequences in launcher")
    return updated_count > 0

def main():
    """Main function"""
    print("🔧 Fixing All Escape Sequences in Launcher")
    print("=" * 50)
    
    try:
        success = fix_all_escape_sequences()
        
        if success:
            print("✅ Escape sequences fixed successfully!")
        else:
            print("❌ Failed to fix escape sequences")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
