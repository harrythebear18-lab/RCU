#!/usr/bin/env python3
"""
Comprehensive Dashboard Update
Updates the dashboard to include representative tools from each launcher category
"""

def update_dashboard_comprehensive():
    """Update dashboard with comprehensive tool organization"""
    print("🔄 Updating Dashboard with Comprehensive Tool Organization")
    print("=" * 60)
    
    dashboard_file = Path('homelab_dashboard.py')
    
    if not dashboard_file.exists():
        print("❌ Dashboard file not found")
        return False
    
    # Read current dashboard
    with open(dashboard_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Define comprehensive tools based on launcher organization
    comprehensive_tools = {
        # System Monitoring
        'CPU Monitor': {
            'path': 'CPU Monitor/cpu_monitor.py',
            'icon': '🖥️',
            'color': '#00ff88',
            'description': 'Real-time CPU monitoring and optimization',
            'status': 'ready'
        },
        'GPU Monitor': {
            'path': 'GPU Monitor/gpu_monitor.py',
            'icon': '🎮',
            'color': '#ff6b6b',
            'description': 'GPU temperature, usage, and performance tracking',
            'status': 'ready'
        },
        'Network Monitor': {
            'path': 'Network Monitor/network_monitor.py',
            'icon': '🌐',
            'color': '#00d4ff',
            'description': 'Bandwidth, latency, and connection monitoring',
            'status': 'ready'
        },
        'Storage Monitor': {
            'path': 'Storage Monitor/storage_monitor.py',
            'icon': '💾',
            'color': '#ffaa00',
            'description': 'Disk usage and storage management',
            'status': 'ready'
        },
        'RAM Monitor': {
            'path': 'Memory Monitor/ram_monitor_gui.py',
            'icon': '🧠',
            'color': '#ff6b6b',
            'description': 'Memory monitoring and optimization',
            'status': 'ready'
        },
        
        # Infrastructure & Management
        'Web Dashboard': {
            'path': 'Core Services/web_dashboard.py',
            'icon': '🌐',
            'color': '#0078ff',
            'description': 'Web-based system dashboard',
            'status': 'ready'
        },
        'VPN Gateway': {
            'path': 'VPN Gateway/vpn_gateway.py',
            'icon': '🔐',
            'color': '#ff6b6b',
            'description': 'VPN management and secure connectivity',
            'status': 'ready'
        },
        'Backup Manager': {
            'path': 'Core Services/backup_manager.py',
            'icon': '💾',
            'color': '#00ff88',
            'description': 'Automated backup and disaster recovery',
            'status': 'ready'
        },
        'Power Manager': {
            'path': 'Power Manager/power_manager.py',
            'icon': '⚡',
            'color': '#ffaa00',
            'description': 'Power management and optimization',
            'status': 'ready'
        },
        'Container Manager': {
            'path': 'Container Manager/container_manager.py',
            'icon': '🐳',
            'color': '#0078ff',
            'description': 'Docker/Podman container management',
            'status': 'ready'
        },
        
        # Distributed Computing
        'RDMA Desktop App': {
            'path': 'RDMA Desktop App/rdma_desktop_app.py',
            'icon': '⚡',
            'color': '#0078ff',
            'description': 'Ultra-low latency DMA system',
            'status': 'advanced'
        },
        'RDMA Modern App': {
            'path': 'RDMA Desktop App/rdma_modern_tkinter.py',
            'icon': '🚀',
            'color': '#00d4ff',
            'description': 'Modern RDMA with advanced UI',
            'status': 'advanced'
        },
        'Memory Portal': {
            'path': 'Memory Portal/memory_portal_gui.py',
            'icon': '🔄',
            'color': '#ffaa00',
            'description': 'Computer-to-computer RAM sharing',
            'status': 'advanced'
        },
        'Hybrid Compute': {
            'path': 'Hybrid Compute/hybrid_client.py',
            'icon': '⚛️',
            'color': '#00ff88',
            'description': 'Remote CPU + local GPU computing',
            'status': 'advanced'
        },
        
        # Network & Security
        'Mesh VPN Server': {
            'path': 'Network Management/mesh_vpn_server.py',
            'icon': '🔐',
            'color': '#ff6b6b',
            'description': 'Mesh VPN server management',
            'status': 'ready'
        },
        'Mesh VPN Client': {
            'path': 'Network Management/mesh_vpn_client.py',
            'icon': '🌐',
            'color': '#0078ff',
            'description': 'Mesh VPN client connectivity',
            'status': 'ready'
        },
        
        # Setup & Installation
        'Install WireGuard': {
            'path': 'install_wireguard.bat',
            'icon': '🚀',
            'color': '#ffaa00',
            'description': 'WireGuard VPN installation',
            'status': 'ready'
        },
        'WireGuard Installer': {
            'path': 'setup/wireguard_installer.py',
            'icon': '⚙️',
            'color': '#00ff88',
            'description': 'Advanced WireGuard installer',
            'status': 'ready'
        },
        
        # RAM Sharing
        'RAM Sharing Manager': {
            'path': 'RAM_Sharing_GUI.py',
            'icon': '🖥️',
            'color': '#00ff88',
            'description': 'Cross-PC RAM sharing with GUI',
            'status': 'ready'
        },
        'Simple RAM Sharing': {
            'path': 'RAM_Sharing_Simple_GUI.py',
            'icon': '🔗',
            'color': '#ffaa00',
            'description': 'Console-based RAM sharing',
            'status': 'ready'
        },
        
        # System Tools
        'System Integration Test': {
            'path': 'system_integration_test.py',
            'icon': '🧪',
            'color': '#ff6b6b',
            'description': 'Comprehensive system testing',
            'status': 'ready'
        },
        'Homelab Launcher': {
            'path': 'homelab_launcher.py',
            'icon': '🚀',
            'color': '#0078ff',
            'description': 'Main Homelab launcher application',
            'status': 'ready'
        },
        'Comprehensive Audit': {
            'path': 'comprehensive_chunked_audit.py',
            'icon': '🔍',
            'color': '#00d4ff',
            'description': 'Complete system audit and analysis',
            'status': 'ready'
        }
    }
    
    # Generate new tools dictionary
    new_tools_dict = generate_tools_dict_code(comprehensive_tools)
    
    # Find and replace the tools dictionary in dashboard
    start_marker = "self.tools = {"
    start_idx = content.find(start_marker)
    
    if start_idx == -1:
        print("❌ Could not find tools dictionary in dashboard")
        return False
    
    # Find the end of the tools dictionary
    brace_count = 0
    end_idx = start_idx + len(start_marker)
    
    for i, char in enumerate(content[start_idx:], start_idx):
        if char == '{':
            brace_count += 1
        elif char == '}':
            brace_count -= 1
            if brace_count == 0:
                end_idx = i + 1
                break
    
    # Replace the tools dictionary
    new_content = content[:start_idx] + new_tools_dict + content[end_idx:]
    
    # Write updated dashboard
    with open(dashboard_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ Dashboard updated with {len(comprehensive_tools)} comprehensive tools")
    return True

def generate_tools_dict_code(tools):
    """Generate Python code for tools dictionary"""
    lines = ["self.tools = {"]
    
    for tool_name, tool_info in tools.items():
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
    from pathlib import Path
    
    success = update_dashboard_comprehensive()
    
    if success:
        print("\n🎉 Dashboard updated successfully!")
        print("📊 Dashboard now includes representative tools from all launcher categories")
    else:
        print("\n❌ Dashboard update failed")
    
    return success

if __name__ == "__main__":
    main()
