#!/usr/bin/env python3
"""
Fix VPN Gateway syntax error - Version 3
"""

def fix_vpn_syntax():
    vpn_file = r"c:\Users\htsou\Desktop\Homelab Tools\VPN Gateway\vpn_gateway.py"
    
    # Read the file
    with open(vpn_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Fix the specific lines
    fixed_lines = []
    for i, line in enumerate(lines):
        line_num = i + 1
        
        # Fix line 381 - add missing parameters
        if line_num == 381 and "relief='flat').pack(side=tk.LEFT, padx=2)" in line:
            fixed_line = line.replace(
                "relief='flat').pack(side=tk.LEFT, padx=2)",
                "bg=self.colors['primary'], fg='white', font=('Segoe UI', 9),\n                 relief='flat').pack(side=tk.LEFT, padx=2)"
            )
            fixed_lines.append(fixed_line)
        
        # Remove duplicate line 384
        elif line_num == 384 and "bg=self.colors['primary'], fg='white', font=('Segoe UI', 9)," in line:
            # Skip this line - it's the duplicate
            continue
        
        else:
            fixed_lines.append(line)
    
    # Write back the fixed file
    with open(vpn_file, 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)
    
    print(f"Fixed VPN Gateway syntax error - corrected lines 381 and 384")

if __name__ == "__main__":
    fix_vpn_syntax()
