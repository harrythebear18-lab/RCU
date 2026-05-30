#!/usr/bin/env python3
"""
Tool Organization - Scan and organize all 273 tools into proper launcher groups
"""

import os
import json
from pathlib import Path
from datetime import datetime

class ToolOrganizer:
    """Organize all tools into proper launcher groups"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.all_tools = []
        self.categories = {}
        
    def scan_all_tools(self):
        """Scan all executable files"""
        print("🔍 Scanning all tools...")
        
        for root, dirs, files in os.walk(self.base_path):
            # Skip hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', '.git', '.vscode']]
            
            for file in files:
                if file.startswith('.'):
                    continue
                    
                file_path = Path(root) / file
                
                # Check if it's an executable file
                if file_path.suffix.lower() in ['.py', '.bat', '.cmd', '.cpp', '.c', '.h']:
                    relative_path = file_path.relative_to(self.base_path)
                    
                    tool = {
                        'name': file,
                        'path': str(relative_path),
                        'type': file_path.suffix.lower(),
                        'size': file_path.stat().st_size,
                        'category': self.get_category(relative_path)
                    }
                    
                    self.all_tools.append(tool)
        
        print(f"Found {len(self.all_tools)} tools")
        return self.all_tools
    
    def get_category(self, relative_path):
        """Determine category from path"""
        parts = relative_path.parts
        if len(parts) > 1:
            return parts[0]
        return 'root'
    
    def organize_by_category(self):
        """Organize tools by category"""
        for tool in self.all_tools:
            cat = tool['category']
            if cat not in self.categories:
                self.categories[cat] = []
            self.categories[cat].append(tool)
        
        print(f"Organized into {len(self.categories)} categories")
        return self.categories
    
    def generate_launcher_config(self):
        """Generate launcher configuration with all tools"""
        print("📋 Generating launcher configuration...")
        
        # Map categories to launcher groups
        category_mapping = {
            'CPU Monitor': 'System Monitoring',
            'GPU Monitor': 'System Monitoring', 
            'Network Monitor': 'System Monitoring',
            'Storage Monitor': 'System Monitoring',
            'Memory Monitor': 'System Monitoring',
            'RDMA Desktop App': 'Distributed Computing',
            'Memory Portal': 'Distributed Computing',
            'Hybrid Compute': 'Distributed Computing',
            'Container Manager': 'Infrastructure & Management',
            'Core Services': 'Infrastructure & Management',
            'VPN Gateway': 'Infrastructure & Management',
            'Media Server': 'Infrastructure & Management',
            'CI': 'Infrastructure & Management',
            'Power Manager': 'Infrastructure & Management',
            'IoT Platform': 'Infrastructure & Management',
            'Subnet Portal': 'Infrastructure & Management',
            'Network Management': 'Network & Security',
            'setup': 'Setup & Installation',
            'config': 'Configuration',
            'logs': 'System Logs',
            'data': 'Data & Storage',
            'docs': 'Documentation',
            'Integration_Examples': 'Examples & Demos',
            'Mobile_Interface': 'Mobile & Remote',
            'Compute Sharing': 'Distributed Computing',
            'Backup System': 'Infrastructure & Management',
            'Web Dashboard': 'Infrastructure & Management',
            'Power Management': 'Infrastructure & Management',
            'Storage Management': 'System Monitoring',
            'Ram clean up': 'System Monitoring',
            'RDMA': 'Distributed Computing',
            'common': 'Utilities',
            'CI/CD Pipeline': 'Infrastructure & Management'
        }
        
        launcher_groups = {}
        
        for category, tools in self.categories.items():
            # Map category to launcher group
            group_name = category_mapping.get(category, category)
            
            if group_name not in launcher_groups:
                launcher_groups[group_name] = {}
            
            # Add tools to group
            for tool in tools:
                # Clean up tool name
                display_name = tool['name']
                if display_name.endswith('.py'):
                    display_name = display_name[:-3].replace('_', ' ').title()
                elif display_name.endswith('.bat'):
                    display_name = display_name[:-4].replace('_', ' ').title()
                elif display_name.endswith('.cmd'):
                    display_name = display_name[:-4].replace('_', ' ').title()
                
                # Determine icon based on type and name
                icon = self.get_tool_icon(tool)
                
                # Determine description
                description = self.get_tool_description(tool)
                
                launcher_groups[group_name][display_name] = {
                    'path': tool['path'],
                    'icon': icon,
                    'description': description,
                    'category': 'tool'
                }
        
        return launcher_groups
    
    def get_tool_icon(self, tool):
        """Get appropriate icon for tool"""
        name = tool['name'].lower()
        path = tool['path'].lower()
        
        if 'monitor' in name or 'monitor' in path:
            return '📊'
        elif 'rdma' in name or 'rdma' in path:
            return '⚡'
        elif 'network' in name or 'network' in path:
            return '🌐'
        elif 'backup' in name or 'backup' in path:
            return '💾'
        elif 'power' in name or 'power' in path:
            return '⚡'
        elif 'media' in name or 'media' in path:
            return '🎬'
        elif 'iot' in name or 'iot' in path:
            return '🏠'
        elif 'container' in name or 'container' in path:
            return '🐳'
        elif 'vpn' in name or 'vpn' in path:
            return '🔐'
        elif 'setup' in name or 'setup' in path or 'install' in name:
            return '🚀'
        elif 'test' in name or 'test' in path:
            return '🧪'
        elif 'config' in name or 'config' in path:
            return '⚙️'
        elif 'audit' in name or 'audit' in path:
            return '🔍'
        elif 'launch' in name or 'launch' in path:
            return '🚀'
        elif 'share' in name or 'share' in path:
            return '🔗'
        elif tool['type'] == '.py':
            return '🐍'
        elif tool['type'] in ['.bat', '.cmd']:
            return '🦾'
        elif tool['type'] in ['.cpp', '.c', '.h']:
            return '⚙️'
        else:
            return '📄'
    
    def get_tool_description(self, tool):
        """Get description for tool"""
        name = tool['name'].lower()
        path = tool['path'].lower()
        
        if 'monitor' in name or 'monitor' in path:
            return f"Monitoring tool for {name.replace('.py', '').replace('.bat', '').replace('_', ' ')}"
        elif 'rdma' in name or 'rdma' in path:
            return "RDMA networking and memory sharing"
        elif 'network' in name or 'network' in path:
            return "Network management and monitoring"
        elif 'backup' in name or 'backup' in path:
            return "Backup and recovery system"
        elif 'power' in name or 'power' in path:
            return "Power management and optimization"
        elif 'media' in name or 'media' in path:
            return "Media server and entertainment"
        elif 'iot' in name or 'iot' in path:
            return "IoT device management"
        elif 'container' in name or 'container' in path:
            return "Container management system"
        elif 'vpn' in name or 'vpn' in path:
            return "VPN and secure connectivity"
        elif 'setup' in name or 'setup' in path or 'install' in name:
            return "Installation and setup utility"
        elif 'test' in name or 'test' in path:
            return "Testing and verification tool"
        elif 'config' in name or 'config' in path:
            return "Configuration management"
        elif 'audit' in name or 'audit' in path:
            return "System audit and analysis"
        elif 'launch' in name or 'launch' in path:
            return "Application launcher"
        elif 'share' in name or 'share' in path:
            return "Resource sharing utility"
        else:
            return f"System tool - {tool['type'].upper()}"
    
    def update_launcher_file(self, launcher_groups):
        """Update the launcher file with all tools"""
        print("🔄 Updating launcher configuration...")
        
        launcher_file = self.base_path / 'homelab_launcher.py'
        
        # Read current launcher
        with open(launcher_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the tools dictionary section
        start_marker = "self.tools = {"
        end_marker = "}"
        
        start_idx = content.find(start_marker)
        if start_idx == -1:
            print("Could not find tools dictionary in launcher")
            return False
        
        # Find the end of the tools dictionary (need to find matching brace)
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
        
        if brace_count != 0:
            print("Could not find end of tools dictionary")
            return False
        
        # Generate new tools dictionary
        new_tools_dict = self.generate_tools_dict_code(launcher_groups)
        
        # Replace the tools dictionary
        new_content = content[:start_idx] + new_tools_dict + content[end_idx:]
        
        # Write updated launcher
        with open(launcher_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"Updated launcher with {len(launcher_groups)} groups")
        return True
    
    def generate_tools_dict_code(self, launcher_groups):
        """Generate Python code for tools dictionary"""
        lines = ["self.tools = {"]
        
        for group_name, tools in launcher_groups.items():
            lines.append(f'            "{group_name}": {{')
            
            for tool_name, tool_info in tools.items():
                lines.append(f'                "{tool_name}": {{')
                lines.append(f'                    "path": "{tool_info["path"]}",')
                lines.append(f'                    "icon": "{tool_info["icon"]}",')
                lines.append(f'                    "description": "{tool_info["description"]}",')
                lines.append(f'                    "category": "{tool_info["category"]}"')
                lines.append('                },')
            
            lines.append('            },')
        
        lines.append('        }')
        
        return '\n'.join(lines)
    
    def generate_report(self):
        """Generate organization report"""
        print("\n📊 TOOL ORGANIZATION REPORT")
        print("=" * 50)
        
        print(f"Total Tools: {len(self.all_tools)}")
        print(f"Categories: {len(self.categories)}")
        
        # Tool type breakdown
        python_count = sum(1 for t in self.all_tools if t['type'] == '.py')
        batch_count = sum(1 for t in self.all_tools if t['type'] in ['.bat', '.cmd'])
        cpp_count = sum(1 for t in self.all_tools if t['type'] in ['.cpp', '.c', '.h'])
        
        print(f"Python Files: {python_count}")
        print(f"Batch Files: {batch_count}")
        print(f"C/C++ Files: {cpp_count}")
        
        print("\n📋 Categories:")
        for category, tools in sorted(self.categories.items(), key=lambda x: len(x[1]), reverse=True):
            print(f"  {category}: {len(tools)} tools")
        
        # Save report
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_tools': len(self.all_tools),
            'categories': len(self.categories),
            'tool_types': {
                'python': python_count,
                'batch': batch_count,
                'cpp': cpp_count
            },
            'categories_detail': {
                cat: len(tools) for cat, tools in self.categories.items()
            },
            'all_tools': self.all_tools
        }
        
        report_file = self.base_path / 'tool_organization_report.json'
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n💾 Report saved to: {report_file}")
    
    def run_organization(self):
        """Run complete tool organization"""
        print("🚀 Starting Tool Organization")
        print("=" * 50)
        
        # Scan all tools
        self.scan_all_tools()
        
        # Organize by category
        self.organize_by_category()
        
        # Generate launcher configuration
        launcher_groups = self.generate_launcher_config()
        
        # Update launcher file
        success = self.update_launcher_file(launcher_groups)
        
        # Generate report
        self.generate_report()
        
        if success:
            print("\n🎉 Tool organization completed successfully!")
        else:
            print("\n⚠️ Tool organization completed with issues")
        
        return success

def main():
    """Main entry point"""
    organizer = ToolOrganizer()
    success = organizer.run_organization()
    
    return success

if __name__ == "__main__":
    main()
