#!/usr/bin/env python3
"""
Fix emoji characters in all broken tools
"""

import os
import re
from pathlib import Path

# List of broken tools with emoji issues
broken_tools = [
    "simple_unified_gui.PY",
    "win10_homelab_server.py", 
    "win11_homelab_client.py",
    "win11_rdma_client.py",
    "resource_optimizer_fixed.py",
    "unified_homelab_dashboard.py",
    "aggressive_ram_cleaner.py",
    "soft_ram_cleaner.py",
    "ram_cleanup_script.py",
    "cpu_cleanup_script.py",
    "gpu_cleanup_script.py",
    "system_cleanup_master.py",
    "memory_jolt.py",
    "pc_auth_system.py",
    "test_gpu_monitoring.py",
    "test_gui.py",
    "test_nvidia_smi.py",
    "console_launcher.PY",
    "stay_open_launcher.PY"
]

# Emoji to ASCII replacements
emoji_replacements = {
    '✅': '[OK]',
    '⚠️': '[WARNING]',
    '❌': '[ERROR]',
    '🔧': '[TOOL]',
    '⚡': '[POWER]',
    '📊': '[CHART]',
    '💚': '[GREEN]',
    '🔌': '[PLUGIN]',
    '🏢': '[BUILDING]',
    '💻': '[COMPUTER]',
    '🌐': '[WEB]',
    '🧹': '[CLEAN]',
    '🧽': '[SPONGE]',
    '🔄': '[REFRESH]',
    '🎮': '[GAME]',
    '👑': '[KING]',
    '🔐': '[LOCK]',
    '🖥️': '[MONITOR]',
    '🎯': '[TARGET]',
    '❓': '[QUESTION]',
    '📧': '[EMAIL]',
    '🌍': '[WORLD]',
    '♿': '[ACCESS]',
    '🤖': '[ROBOT]',
    '🚀': '[ROCKET]',
    '📈': '[UP]',
    '📉': '[DOWN]',
    '📁': '[FOLDER]',
    '📄': '[FILE]',
    '🔍': '[SEARCH]',
    '⭐': '[STAR]',
    '🏠': '[HOME]',
    '🔥': '[FIRE]',
    '💾': '[SAVE]',
    '⚙️': '[SETTINGS]',
    '🗄️': '[DATABASE]',
    '📅': '[CALENDAR]',
    '🧪': '[TEST]',
    '🛠️': '[TOOLS]',
    '📜': '[SCROLL]',
    '🔗': '[LINK]',
    '📡': '[SIGNAL]',
    '🛡️': '[SHIELD]',
    '🤖': '[BOT]',
    '📋': '[CLIPBOARD]',
    '🎨': '[ART]',
    '🌟': '[STAR]'
}

def fix_emoji_in_file(filename):
    """Fix emoji characters in a file"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Replace all emoji characters
        for emoji, replacement in emoji_replacements.items():
            content = content.replace(emoji, replacement)
        
        # Also fix any remaining Unicode characters that might cause issues
        # Remove or replace problematic Unicode characters
        content = re.sub(r'[\u2600-\u27FF]', '', content)  # Remove misc symbols
        content = re.sub(r'[\uE000-\uF8FF]', '', content)  # Remove private use area
        
        # Write back the fixed content
        if content != original_content:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ Fixed: {filename}")
            return True
        else:
            print(f"- No changes needed: {filename}")
            return False
            
    except Exception as e:
        print(f"✗ Error fixing {filename}: {e}")
        return False

def main():
    """Main function"""
    print("🔧 Fixing Emoji Characters in Broken Tools")
    print("=" * 50)
    
    fixed_count = 0
    total_count = len(broken_tools)
    
    for tool in broken_tools:
        if os.path.exists(tool):
            if fix_emoji_in_file(tool):
                fixed_count += 1
        else:
            print(f"✗ File not found: {tool}")
    
    print(f"\n{'='*50}")
    print(f"📊 Results:")
    print(f"   Total files: {total_count}")
    print(f"   Fixed: {fixed_count}")
    print(f"   Skipped: {total_count - fixed_count}")
    
    if fixed_count > 0:
        print(f"\n✅ Successfully fixed {fixed_count} files!")
        print("🎉 These tools should now work without Unicode errors!")
    else:
        print(f"\n⚠️ No files needed fixing.")

if __name__ == "__main__":
    main()
