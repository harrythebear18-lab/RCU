#!/usr/bin/env python3
"""
Fix VPN Gateway syntax error - Final Version
"""

def fix_vpn_syntax():
    vpn_file = r"c:\Users\htsou\Desktop\Homelab Tools\VPN Gateway\vpn_gateway.py"
    
    # Read the file
    with open(vpn_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Remove the problematic duplicate line 385
    fixed_lines = []
    for i, line in enumerate(lines):
        line_num = i + 1
        
        # Skip the duplicate line 385
        if line_num == 385 and "bg=self.colors['primary'], fg='white', font=('Segoe UI', 9)," in line:
            continue
        
        fixed_lines.append(line)
    
    # Write back the fixed file
    with open(vpn_file, 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)
    
    print(f"Fixed VPN Gateway syntax error - removed duplicate line 385")

if __name__ == "__main__":
    fix_vpn_syntax()
