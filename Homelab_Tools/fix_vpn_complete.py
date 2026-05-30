#!/usr/bin/env python3
"""
Complete fix for VPN Gateway syntax error
"""

def fix_vpn_syntax():
    vpn_file = r"c:\Users\htsou\Desktop\Homelab Tools\VPN Gateway\vpn_gateway.py"
    
    # Read the file
    with open(vpn_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find the problematic section and replace it completely
    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        line_num = i + 1
        
        # When we reach the Export Config button, replace the entire section
        if 'tk.Button(toolbar, text="Export Config", command=self.export_mesh_config,' in line:
            # Add the corrected Export Config button
            new_lines.append('        tk.Button(toolbar, text="Export Config", command=self.export_mesh_config,\n')
            new_lines.append('                 bg=self.colors[\'primary\'], fg=\'white\', font=(\'Segoe UI\', 9),\n')
            new_lines.append('                 relief=\'flat\').pack(side=tk.LEFT, padx=2)\n')
            
            # Add the corrected Refresh button (without duplicate parameters)
            new_lines.append('        tk.Button(toolbar, text="Refresh", command=self.refresh_mesh_nodes,\n')
            new_lines.append('                 bg=self.colors[\'warning\'], fg=\'white\', font=(\'Segoe UI\', 9),\n')
            new_lines.append('                 relief=\'flat\').pack(side=tk.LEFT, padx=2)\n')
            
            # Skip the original problematic lines (next few lines)
            i += 1  # Skip the original Export Config line
            while i < len(lines) and 'tk.Button(toolbar, text="Refresh"' not in lines[i]:
                i += 1
            if i < len(lines):
                i += 1  # Skip the Refresh line
            while i < len(lines) and 'relief=\'flat\').pack(side=tk.LEFT, padx=2)' not in lines[i]:
                i += 1
            if i < len(lines):
                i += 1  # Skip the problematic duplicate line
            continue
        
        new_lines.append(line)
        i += 1
    
    # Write back the fixed file
    with open(vpn_file, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print(f"Fixed VPN Gateway syntax error - complete section replacement")

if __name__ == "__main__":
    fix_vpn_syntax()
