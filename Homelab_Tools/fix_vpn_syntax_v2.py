#!/usr/bin/env python3
"""
Fix VPN Gateway syntax error - Version 2
"""

def fix_vpn_syntax():
    vpn_file = r"c:\Users\htsou\Desktop\Homelab Tools\VPN Gateway\vpn_gateway.py"
    
    # Read the file
    with open(vpn_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix the specific issue around lines 380-385
    # The problem is that line 381 is missing parameters and line 384 has duplicates
    
    # Replace the problematic section
    old_section = """        tk.Button(toolbar, text="Export Config", command=self.export_mesh_config,
                 relief='flat').pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="Refresh", command=self.refresh_mesh_nodes,
                 bg=self.colors['warning'], fg='white', font=('Segoe UI', 9),
                 bg=self.colors['primary'], fg='white', font=('Segoe UI', 9),
                 relief='flat').pack(side=tk.LEFT, padx=2)"""
    
    new_section = """        tk.Button(toolbar, text="Export Config", command=self.export_mesh_config,
                 bg=self.colors['primary'], fg='white', font=('Segoe UI', 9),
                 relief='flat').pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="Refresh", command=self.refresh_mesh_nodes,
                 bg=self.colors['warning'], fg='white', font=('Segoe UI', 9),
                 relief='flat').pack(side=tk.LEFT, padx=2)"""
    
    # Replace the section
    content = content.replace(old_section, new_section)
    
    # Write back the fixed file
    with open(vpn_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Fixed VPN Gateway syntax error - corrected button parameters")

if __name__ == "__main__":
    fix_vpn_syntax()
