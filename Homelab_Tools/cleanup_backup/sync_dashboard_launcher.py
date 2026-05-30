#!/usr/bin/env python3
"""
Sync Dashboard with Launcher Tool Organization
Updates the dashboard to use the same tool organization as the launcher
"""

import json
from pathlib import Path
from datetime import datetime

def sync_dashboard_with_launcher():
    """Synchronize dashboard tools with launcher organization"""
    print("🔄 Syncing Dashboard with Launcher Tool Organization")
    print("=" * 60)
    
    # Read launcher tools
    launcher_file = Path('homelab_launcher.py')
    dashboard_file = Path('homelab_dashboard.py')
    
    if not launcher_file.exists():
        print("❌ Launcher file not found")
        return False
    
    if not dashboard_file.exists():
        print("❌ Dashboard file not found")
        return False
    
    # Read launcher content to extract tools
    with open(launcher_file, 'r', encoding='utf-8') as f:
        launcher_content = f.read()
    
    # Read dashboard content
    with open(dashboard_file, 'r', encoding='utf-8') as f:
        dashboard_content = f.read()
    
    # Extract tools from launcher
    # Find the tools dictionary in launcher
    start_marker = "self.tools = {"
    start_idx = launcher_content.find(start_marker)
    
    if start_idx == -1:
        print("❌ Could not find tools dictionary in launcher")
        return False
    
    # Find the end of the tools dictionary
    brace_count = 0
    end_idx = start_idx + len(start_marker)
    
    for i, char in enumerate(launcher_content[start_idx:], start_idx):
        if char == '{':
            brace_count += 1
        elif char == '}':
            brace_count -= 1
            if brace_count == 0:
                end_idx = i + 1
                break
    
    launcher_tools_dict = launcher_content[start_idx:end_idx]
    
    # Convert launcher tools to dashboard format
    dashboard_tools = convert_launcher_to_dashboard_format(launcher_tools_dict)
    
    # Generate new dashboard tools dictionary
    new_dashboard_tools = generate_dashboard_tools_dict(dashboard_tools)
    
    # Find and replace dashboard tools dictionary
    dashboard_start_marker = "self.tools = {"
    dashboard_start_idx = dashboard_content.find(dashboard_start_marker)
    
    if dashboard_start_idx == -1:
        print("❌ Could not find tools dictionary in dashboard")
        return False
    
    # Find the end of dashboard tools dictionary
    brace_count = 0
    dashboard_end_idx = dashboard_start_idx + len(dashboard_start_marker)
    
    for i, char in enumerate(dashboard_content[dashboard_start_idx:], dashboard_start_idx):
        if char == '{':
            brace_count += 1
        elif char == '}':
            brace_count -= 1
            if brace_count == 0:
                dashboard_end_idx = i + 1
                break
    
    # Replace dashboard tools
    new_dashboard_content = (dashboard_content[:dashboard_start_idx] + 
                           new_dashboard_tools + 
                           dashboard_content[dashboard_end_idx:])
    
    # Write updated dashboard
    with open(dashboard_file, 'w', encoding='utf-8') as f:
        f.write(new_dashboard_content)
    
    print(f"✅ Dashboard updated with {len(dashboard_tools)} tools")
    return True

def convert_launcher_to_dashboard_format(launcher_tools_dict):
    """Convert launcher tools format to dashboard format"""
    dashboard_tools = {}
    
    # Simple parsing - this is a basic approach
    # In a real implementation, you'd want to use ast.parse for safety
    lines = launcher_tools_dict.split('\n')
    
    current_category = None
    current_tool_name = None
    current_tool_info = {}
    
    for line in lines:
        line = line.strip()
        
        # Skip empty lines and braces
        if not line or line in ['{', '}', '},', 'self.tools = {']:
            continue
        
        # Check for category
        if line.startswith('"') and line.endswith(': {'):
            current_category = line.split('"')[1]
            continue
        
        # Check for tool name
        if line.startswith('"') and line.endswith('": {'):
            current_tool_name = line.split('"')[1]
            current_tool_info = {}
            continue
        
        # Check for tool properties
        if '":' in line and current_tool_name:
            if '"path":' in line:
                path = line.split('"')[3]
                current_tool_info['path'] = path
            elif '"icon":' in line:
                icon = line.split('"')[3]
                current_tool_info['icon'] = icon
            elif '"description":' in line:
                desc = line.split('"')[3]
                current_tool_info['description'] = desc
            continue
        
        # Check for end of tool
        if line == '},' and current_tool_name and current_tool_info:
            # Add to dashboard tools
            dashboard_tools[current_tool_name] = {
                'path': current_tool_info.get('path', ''),
                'icon': current_tool_info.get('icon', '📄'),
                'color': get_tool_color(current_tool_info.get('path', '')),
                'description': current_tool_info.get('description', 'System tool'),
                'status': 'ready'
            }
            
            current_tool_name = None
            current_tool_info = {}
    
    return dashboard_tools

def get_tool_color(tool_path):
    """Get color for tool based on type and path"""
    path = tool_path.lower()
    
    if 'monitor' in path:
        return '#00ff88'  # Green
    elif 'rdma' in path:
        return '#0078ff'  # Blue
    elif 'network' in path:
        return '#00d4ff'  # Cyan
    elif 'backup' in path:
        return '#ff6b6b'  # Red
    elif 'power' in path:
        return '#ffaa00'  # Orange
    elif 'media' in path:
        return '#ff6b6b'  # Red
    elif 'iot' in path:
        return '#00ff88'  # Green
    elif 'container' in path:
        return '#0078ff'  # Blue
    elif 'vpn' in path:
        return '#ff6b6b'  # Red
    elif 'setup' in path or 'install' in path:
        return '#ffaa00'  # Orange
    elif 'test' in path:
        return '#ff6b6b'  # Red
    elif 'config' in path:
        return '#ffaa00'  # Orange
    elif 'audit' in path:
        return '#00d4ff'  # Cyan
    elif 'launch' in path:
        return '#ffaa00'  # Orange
    elif 'share' in path:
        return '#0078ff'  # Blue
    else:
        return '#00ff88'  # Default green

def generate_dashboard_tools_dict(dashboard_tools):
    """Generate dashboard tools dictionary code"""
    lines = ["self.tools = {"]
    
    for tool_name, tool_info in dashboard_tools.items():
        lines.append(f'            \'{tool_name}\': {{')
        lines.append(f'                \'path\': \'{tool_info["path"]}\',')
        lines.append(f'                \'icon\': \'{tool_info["icon"]}\',')
        lines.append(f'                \'color\': \'{tool_info["color"]}\',')
        lines.append(f'                \'description\': \'{tool_info["description"]}\',')
        lines.append(f'                \'status\': \'{tool_info["status"]}\'')
        lines.append('            },')
    
    lines.append('        }')
    
    return '\n'.join(lines)

def main():
    """Main entry point"""
    success = sync_dashboard_with_launcher()
    
    if success:
        print("\n🎉 Dashboard synchronized with launcher successfully!")
    else:
        print("\n❌ Dashboard synchronization failed")
    
    return success

if __name__ == "__main__":
    main()
