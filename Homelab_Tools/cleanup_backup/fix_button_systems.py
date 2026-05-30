#!/usr/bin/env python3
"""
Fix Button Systems
Complete redo of launcher and dashboard button systems to connect to actual working tools
"""

import os
import json
from pathlib import Path

def scan_working_tools():
    """Scan for actual working tools that can be launched"""
    base_path = Path(__file__).parent
    working_tools = {}
    
    # Known working tools with their actual paths
    known_tools = {
        # Core monitoring tools
        "CPU Monitor": {
            "path": "CPU Monitor/cpu_monitor.py",
            "icon": "💻",
            "description": "CPU usage monitoring",
            "category": "monitoring"
        },
        "GPU Monitor": {
            "path": "GPU Monitor/gpu_monitor.py", 
            "icon": "🎮",
            "description": "GPU usage monitoring",
            "category": "monitoring"
        },
        "Network Monitor": {
            "path": "Network Monitor/network_monitor.py",
            "icon": "🌐",
            "description": "Network activity monitoring",
            "category": "monitoring"
        },
        "Storage Monitor": {
            "path": "Storage Monitor/storage_monitor.py",
            "icon": "💾",
            "description": "Disk space monitoring",
            "category": "monitoring"
        },
        "Memory Monitor": {
            "path": "Memory Monitor/ram_monitor_gui.py",
            "icon": "🧠",
            "description": "RAM usage monitoring",
            "category": "monitoring"
        },
        
        # Core services
        "Web Dashboard": {
            "path": "Core Services/web_dashboard.py",
            "icon": "📊",
            "description": "Web-based monitoring dashboard",
            "category": "services"
        },
        "Backup Manager": {
            "path": "Core Services/backup_manager.py",
            "icon": "💿",
            "description": "System backup management",
            "category": "services"
        },
        "Power Manager": {
            "path": "Power Manager/power_manager.py",
            "icon": "⚡",
            "description": "Power management utilities",
            "category": "services"
        },
        
        # VPN and networking
        "VPN Gateway": {
            "path": "VPN Gateway/vpn_gateway.py",
            "icon": "🔐",
            "description": "VPN connection management",
            "category": "network"
        },
        
        # RDMA tools
        "RDMA Desktop App": {
            "path": "RDMA Desktop App/rdma_desktop_app.py",
            "icon": "🔌",
            "description": "RDMA desktop application",
            "category": "rdma"
        },
        
        # System tools
        "System Dashboard": {
            "path": "homelab_dashboard.py",
            "icon": "🏠",
            "description": "Main system dashboard",
            "category": "system"
        },
        "System Launcher": {
            "path": "homelab_launcher.py",
            "icon": "🚀",
            "description": "Main system launcher",
            "category": "system"
        },
        
        # Batch files
        "Auto Connect": {
            "path": "Auto_Connect_Launcher.bat",
            "icon": "🔗",
            "description": "Auto connection launcher",
            "category": "utilities"
        },
        "Windows Compatibility Fix": {
            "path": "Fix_Windows_Compatibility.bat",
            "icon": "🔧",
            "description": "Windows compatibility fixes",
            "category": "utilities"
        },
        
        # Python utilities
        "RAM Sharing GUI": {
            "path": "RAM_Sharing_GUI.py",
            "icon": "🔄",
            "description": "RAM sharing interface",
            "category": "utilities"
        },
        "System Audit": {
            "path": "comprehensive_chunked_audit.py",
            "icon": "🔍",
            "description": "Comprehensive system audit",
            "category": "utilities"
        }
    }
    
    # Verify which tools actually exist
    for tool_name, tool_info in known_tools.items():
        tool_path = base_path / tool_info['path']
        if tool_path.exists():
            working_tools[tool_name] = tool_info
            print(f"✅ Found: {tool_name} -> {tool_info['path']}")
        else:
            print(f"❌ Missing: {tool_name} -> {tool_info['path']}")
    
    return working_tools

def fix_dashboard_buttons():
    """Fix dashboard with working button system"""
    dashboard_file = Path(__file__).parent / "homelab_dashboard.py"
    
    if not dashboard_file.exists():
        print(f"Dashboard file not found: {dashboard_file}")
        return False
    
    # Read the dashboard file
    with open(dashboard_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Get working tools
    working_tools = scan_working_tools()
    
    # Create new tools dictionary for dashboard
    new_tools = {}
    for tool_name, tool_info in working_tools.items():
        new_tools[tool_name] = {
            'path': tool_info['path'],
            'icon': tool_info['icon'],
            'description': tool_info['description'],
            'status': 'ready',
            'color': '#00ff88' if tool_info['category'] == 'monitoring' else '#00aaff'
        }
    
    # Update the tools dictionary in dashboard
    tools_start = content.find('self.tools = {')
    if tools_start == -1:
        print("Could not find tools dictionary in dashboard")
        return False
    
    # Find the end of the tools dictionary
    brace_count = 0
    tools_end = tools_start
    for i, char in enumerate(content[tools_start:], tools_start):
        if char == '{':
            brace_count += 1
        elif char == '}':
            brace_count -= 1
            if brace_count == 0:
                tools_end = i + 1
                break
    
    # Replace the tools dictionary
    new_tools_str = 'self.tools = ' + json.dumps(new_tools, indent=4) + '\n'
    content = content[:tools_start] + new_tools_str + content[tools_end:]
    
    # Write back to dashboard
    with open(dashboard_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Updated dashboard with {len(new_tools)} working tools")
    return True

def fix_launcher_buttons():
    """Fix launcher with working button system"""
    launcher_file = Path(__file__).parent / "homelab_launcher.py"
    
    if not launcher_file.exists():
        print(f"Launcher file not found: {launcher_file}")
        return False
    
    # Read the launcher file
    with open(launcher_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Get working tools
    working_tools = scan_working_tools()
    
    # Create new tools dictionary for launcher
    new_tools = {"root": {}}
    for tool_name, tool_info in working_tools.items():
        new_tools["root"][tool_name] = {
            'path': tool_info['path'],
            'icon': tool_info['icon'],
            'description': tool_info['description'],
            'category': tool_info['category']
        }
    
    # Update the tools dictionary in launcher
    tools_start = content.find('self.tools = {')
    if tools_start == -1:
        print("Could not find tools dictionary in launcher")
        return False
    
    # Find the end of the tools dictionary
    brace_count = 0
    tools_end = tools_start
    for i, char in enumerate(content[tools_start:], tools_start):
        if char == '{':
            brace_count += 1
        elif char == '}':
            brace_count -= 1
            if brace_count == 0:
                tools_end = i + 1
                break
    
    # Replace the tools dictionary
    new_tools_str = 'self.tools = ' + json.dumps(new_tools, indent=4) + '\n'
    content = content[:tools_start] + new_tools_str + content[tools_end:]
    
    # Write back to launcher
    with open(launcher_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Updated launcher with {len(new_tools['root'])} working tools")
    return True

def main():
    """Main function"""
    print("🔧 Fixing Button Systems")
    print("=" * 50)
    
    try:
        # Scan for working tools
        print("📁 Scanning for working tools...")
        working_tools = scan_working_tools()
        print(f"Found {len(working_tools)} working tools")
        
        # Fix dashboard
        print("\n📊 Fixing dashboard buttons...")
        dashboard_success = fix_dashboard_buttons()
        
        # Fix launcher
        print("\n🚀 Fixing launcher buttons...")
        launcher_success = fix_launcher_buttons()
        
        if dashboard_success and launcher_success:
            print("\n✅ Both dashboard and launcher buttons fixed successfully!")
        else:
            print("\n❌ Some fixes failed")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
