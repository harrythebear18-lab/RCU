#!/usr/bin/env python3
"""
Fix All Launcher Tool Paths
Comprehensive fix for all 205 tool paths in the launcher
"""

import os
import json
from pathlib import Path

def scan_directory_structure():
    """Scan the actual directory structure and create a file mapping"""
    base_path = Path(__file__).parent
    file_mapping = {}
    
    # Scan all subdirectories
    for root, dirs, files in os.walk(base_path):
        # Skip hidden directories and git
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        
        for file in files:
            if file.endswith(('.py', '.bat', '.cmd', '.ps1')):
                file_path = Path(root) / file
                relative_path = file_path.relative_to(base_path)
                file_mapping[file] = str(relative_path)
    
    return file_mapping

def create_correct_tool_mapping():
    """Create the correct tool mapping based on actual files"""
    base_path = Path(__file__).parent
    file_mapping = scan_directory_structure()
    
    # Known tool mappings based on actual directory structure
    correct_paths = {
        # Core monitoring tools
        "cpu_monitor.py": "CPU Monitor/cpu_monitor.py",
        "gpu_monitor.py": "GPU Monitor/gpu_monitor.py", 
        "network_monitor.py": "Network Monitor/network_monitor.py",
        "storage_monitor.py": "Storage Monitor/storage_monitor.py",
        "ram_monitor_gui.py": "Memory Monitor/ram_monitor_gui.py",
        
        # Core services
        "web_dashboard.py": "Core Services/web_dashboard.py",
        "backup_manager.py": "Core Services/backup_manager.py",
        "power_manager.py": "Power Manager/power_manager.py",
        "container_manager.py": "Container Manager/container_manager.py",
        
        # VPN and networking
        "vpn_gateway.py": "VPN Gateway/vpn_gateway.py",
        
        # RDMA tools
        "rdma_desktop_app.py": "RDMA Desktop App/rdma_desktop_app.py",
        "rdma_modern_tkinter.py": "RDMA Desktop App/rdma_modern_tkinter.py",
        
        # Memory and compute
        "memory_portal_gui.py": "Memory Portal/memory_portal_gui.py",
        "hybrid_client.py": "Hybrid Compute/hybrid_client.py",
        
        # RAM sharing
        "RAM_Sharing_GUI.py": "RAM_Sharing_GUI.py",
        "RAM_Sharing_Simple_GUI.py": "RAM_Sharing_Simple_GUI.py",
        
        # System tools
        "system_integration_test.py": "system_integration_test.py",
        "homelab_dashboard.py": "homelab_dashboard.py",
        "homelab_launcher.py": "homelab_launcher.py",
        "comprehensive_chunked_audit.py": "comprehensive_chunked_audit.py",
        
        # Batch files
        "Auto_Connect_Launcher.bat": "Auto_Connect_Launcher.bat",
        "Fix_Windows_Compatibility.bat": "Fix_Windows_Compatibility.bat",
        "GUI_Troubleshooting.bat": "GUI_Troubleshooting.bat",
        "install_wireguard.bat": "install_wireguard.bat",
        
        # Other Python files
        "Auto_RAM_Connect.py": "Auto_RAM_Connect.py",
        "abstraction_layer_integration_test.py": "abstraction_layer_integration_test.py",
        "auto_setup.py": "auto_setup.py",
        "batch_file_fixer.py": "batch_file_fixer.py",
        "check_failures.py": "check_failures.py",
        "check_failures_simple.py": "check_failures_simple.py",
        "comprehensive_system_audit.py": "comprehensive_system_audit.py",
        "comprehensive_system_verification.py": "comprehensive_system_verification.py",
        "enhanced_system_verification.py": "enhanced_system_verification.py",
        "final_verification_suite.py": "final_verification_suite.py",
        "find_failed_python.py": "find_failed_python.py",
        "first_time_setup.py": "first_time_setup.py",
        "fully_comprehensive_system_audit.py": "fully_comprehensive_system_audit.py",
        "fully_comprehensive_system_audit_optimized.py": "fully_comprehensive_system_audit_optimized.py",
        "organize_tools.py": "organize_tools.py",
        "test_cpu_monitor.py": "test_cpu_monitor.py",
        "test_integration.py": "test_integration.py",
        "test_portal_file_transfer.py": "test_portal_file_transfer.py",
        "test_rdma_windows.py": "test_rdma_windows.py",
        "test_rest_api.py": "test_rest_api.py",
        "tool_connection_verification.py": "tool_connection_verification.py",
        "tool_launch_verification.py": "tool_launch_verification.py",
        "visentrix_launcher.py": "Visentrix_Launcher.py",
    }
    
    # Add any additional files found in scanning
    for filename, path in file_mapping.items():
        if filename not in correct_paths:
            correct_paths[filename] = path
    
    return correct_paths

def update_launcher_paths():
    """Update the launcher with correct paths"""
    launcher_file = Path(__file__).parent / "homelab_launcher.py"
    
    if not launcher_file.exists():
        print(f"Launcher file not found: {launcher_file}")
        return False
    
    # Read the launcher file
    with open(launcher_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Get correct path mappings
    correct_paths = create_correct_tool_mapping()
    
    # Update tool paths in the launcher
    updated_count = 0
    
    # Load the existing launcher tools structure
    import re
    
    # Find all path entries and update them
    path_pattern = r'"path":\s*"([^"]+)"'
    matches = re.findall(path_pattern, content)
    
    print(f"Found {len(matches)} path entries in launcher")
    
    # Force update specific files that need subdirectories
    subdirectory_files = [
        "cpu_monitor.py", "gpu_monitor.py", "network_monitor.py", "storage_monitor.py", "ram_monitor_gui.py",
        "web_dashboard.py", "backup_manager.py", "power_manager.py", "container_manager.py",
        "vpn_gateway.py", "rdma_desktop_app.py", "rdma_modern_tkinter.py", "memory_portal_gui.py", "hybrid_client.py"
    ]
    
    for current_path in matches:
        # Extract filename from current path
        filename = Path(current_path).name
        
        # Check if we have a correct path for this filename
        if filename in correct_paths:
            correct_path = correct_paths[filename]
            
            # Force update for files that should be in subdirectories
            if filename in subdirectory_files or current_path != correct_path:
                # Replace this specific occurrence
                old_entry = f'"path": "{current_path}"'
                # Use forward slashes to avoid escape sequence issues
                correct_path_fixed = correct_path.replace('\\', '/')
                new_entry = f'"path": "{correct_path_fixed}"'
                if old_entry in content:
                    content = content.replace(old_entry, new_entry)
                    updated_count += 1
                    print(f"Updated: {current_path} -> {correct_path_fixed}")
    
    # Write the updated content back
    with open(launcher_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Updated {updated_count} tool paths in launcher")
    return updated_count > 0

def main():
    """Main function"""
    try:
        print("🔧 Fixing All Launcher Tool Paths")
        print("=" * 50)
        
        # Scan directory structure
        print("📁 Scanning directory structure...")
        file_mapping = scan_directory_structure()
        print(f"Found {len(file_mapping)} executable files")
        
        # Show first few files for debugging
        print("First 10 files found:")
        for i, (filename, path) in enumerate(list(file_mapping.items())[:10]):
            print(f"  {i+1}. {filename} -> {path}")
        
        # Create correct mappings
        print("\n🗺️  Creating correct path mappings...")
        correct_paths = create_correct_tool_mapping()
        print(f"Created {len(correct_paths)} correct path mappings")
        
        # Update launcher
        print("\n🔄 Updating launcher paths...")
        success = update_launcher_paths()
        
        if success:
            print("✅ Launcher paths updated successfully!")
        else:
            print("❌ Failed to update launcher paths")
        
        # Save mapping for reference
        with open("launcher_path_mapping.json", 'w') as f:
            json.dump(correct_paths, f, indent=2)
        print("💾 Saved path mapping to launcher_path_mapping.json")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        print("\n✅ Script completed!")

if __name__ == "__main__":
    main()
