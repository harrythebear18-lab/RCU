#!/usr/bin/env python3
"""
Batch File Fixer for Windows 10/11 Compatibility
Automatically fixes common batch file issues
"""

import os
import re
import glob
from pathlib import Path

def fix_batch_file(file_path):
    """Fix a single batch file for Windows 10/11 compatibility"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Fix 1: Add setlocal enabledelayedexpansion if missing
        if '@echo off' in content and 'setlocal enabledelayedexpansion' not in content:
            content = content.replace('@echo off', '@echo off\nsetlocal enabledelayedexpansion', 1)
        
        # Fix 2: Replace %errorlevel% with !errorlevel! when delayed expansion is enabled
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            # Skip comments and labels
            if line.strip().startswith('REM') or line.strip().startswith(':') or line.strip().startswith('@echo'):
                fixed_lines.append(line)
                continue
            
            # Fix errorlevel references
            if '%errorlevel%' in line and 'setlocal enabledelayedexpansion' in content:
                line = line.replace('%errorlevel%', '!errorlevel!')
            
            # Fix variable assignments with spaces
            if '=' in line and not line.strip().startswith('REM') and not line.strip().startswith(':'):
                # Quote variable assignments
                parts = line.split('=', 1)
                if len(parts) == 2:
                    var_name = parts[0].strip()
                    var_value = parts[1].strip()
                    if not var_value.startswith('"') and not var_value.startswith("'"):
                        line = f'{var_name}="{var_value}"'
            
            fixed_lines.append(line)
        
        content = '\n'.join(fixed_lines)
        
        # Fix 3: Replace complex inline Python commands
        content = fix_inline_python_commands(content)
        
        # Fix 4: Fix hardcoded paths
        content = fix_hardcoded_paths(content)
        
        # Write back if changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
        
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False

def fix_inline_python_commands(content):
    """Replace complex inline Python commands with standalone scripts"""
    # Pattern to match inline Python commands
    python_pattern = r'python\s+-c\s+"([^"]+)"'
    
    def replace_python_match(match):
        python_code = match.group(1)
        script_name = f"temp_script_{hash(python_code) % 10000}.py"
        
        # Create temporary Python script
        with open(script_name, 'w') as f:
            f.write(python_code)
        
        return f'python "{script_name}"'
    
    return re.sub(python_pattern, replace_python_match, content)

def fix_hardcoded_paths(content):
    """Replace hardcoded paths with environment variables"""
    path_replacements = {
        r'C:\\Users\\%USERNAME%': '%USERPROFILE%',
        r'C:\\Users\\[^\\]+': '%USERPROFILE%',
        r'C:\\Program Files': '%PROGRAMFILES%',
        r'C:\\Program Files \(x86\)': '%PROGRAMFILES(X86%)',
        r'C:\\Windows': '%WINDIR%',
        r'C:\\ProgramData': '%ALLUSERSPROFILE%'
    }
    
    for pattern, replacement in path_replacements.items():
        content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
    
    return content

def fix_all_batch_files(directory):
    """Fix all batch files in directory"""
    batch_files = glob.glob(os.path.join(directory, '*.bat'))
    
    fixed_count = 0
    total_count = len(batch_files)
    
    print(f"Found {total_count} batch files to fix...")
    
    for batch_file in batch_files:
        print(f"Fixing: {os.path.basename(batch_file)}")
        if fix_batch_file(batch_file):
            fixed_count += 1
            print(f"  ✓ Fixed")
        else:
            print(f"  - No changes needed")
    
    print(f"\nFixed {fixed_count} out of {total_count} batch files")
    return fixed_count

if __name__ == "__main__":
    import sys
    
    directory = sys.argv[1] if len(sys.argv) > 1 else "."
    
    print("Batch File Fixer for Windows 10/11 Compatibility")
    print("=" * 50)
    
    fixed = fix_all_batch_files(directory)
    
    if fixed > 0:
        print(f"\n✅ Successfully fixed {fixed} batch files")
    else:
        print("\n✅ All batch files are already compatible")
    
    print("\nBatch file fixing completed!")
