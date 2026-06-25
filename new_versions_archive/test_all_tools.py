#!/usr/bin/env python3
"""
Comprehensive tool testing script
Tests all 51 tools for launch and basic functionality
"""

import subprocess
import sys
import time
import os
from pathlib import Path
import threading
import signal

# All tools from the launcher
all_tools = [
    # Working Systems - Only Best Versions
    ("⭐ Simple Unified GUI", "simple_unified_gui.PY", "#2ecc71"),
    ("🚀 Unified Launcher GUI", "launcher_gui.py", "#3498db"),
    ("🔐 PC Authentication GUI", "pc_auth_gui.py", "#9b59b6"),
    ("📊 Streamlined Dashboard", "streamlined_dashboard.py", "#e67e22"),
    ("📈 Enhanced Dashboard (Fixed)", "enhanced_dashboard_fixed.py", "#d35400"),
    ("🌟 Fully Unified GUI", "fully_unified_gui.py", "#27ae60"),
    
    # Windows Server & Client
    ("🏢 Windows 10 Homelab Server", "win10_homelab_server.py", "#27ae60"),
    ("🚀 Windows 10 Server Launcher", "win10_server_launcher.py", "#3498db"),
    ("💻 Windows 11 Homelab Client", "win11_homelab_client.py", "#e67e22"),
    ("🔌 Windows 11 RDMA Client", "win11_rdma_client.py", "#f39c12"),
    
    # Overclocking & Performance - Only Fixed Versions
    ("🔧 Overclocking Dashboard", "overclocking_dashboard.py", "#e67e22"),
    ("⚡ Performance Optimizer (Fixed)", "performance_optimizer_fixed.py", "#27ae60"),
    ("🔧 Resource Optimizer Fixed", "resource_optimizer_fixed.py", "#d35400"),
    ("📊 Performance Reports", "performance_reports.py", "#f39c12"),
    ("💚 System Health Scorer", "system_health_scorer.py", "#2ecc71"),
    
    # RDMA & Networking - Only Fixed Version
    ("🔌 RDMA Integration (Fixed)", "rdma_integration_fixed.py", "#3498db"),
    ("🏢 Homelab Server", "homelab_server.py", "#27ae60"),
    ("💻 Homelab Client", "homelab_client.py", "#e67e22"),
    ("📊 Homelab Dashboard", "homelab_dashboard.py", "#f39c12"),
    ("🌐 Unified Homelab Dashboard", "unified_homelab_dashboard.py", "#3498db"),
    
    # System Cleanup & Optimization - Verified Working
    ("🧹 Aggressive RAM Cleaner", "aggressive_ram_cleaner.py", "#c0392b"),
    ("🧽 Soft RAM Cleaner", "soft_ram_cleaner.py", "#3498db"),
    ("🔄 RAM Cleanup Script", "ram_cleanup_script.py", "#f39c12"),
    ("⚡ CPU Cleanup Script", "cpu_cleanup_script.py", "#27ae60"),
    ("🎮 GPU Cleanup Script", "gpu_cleanup_script.py", "#e67e22"),
    ("👑 System Cleanup Master", "system_cleanup_master.py", "#9b59b6"),
    ("⚡ Memory Jolt", "memory_jolt.py", "#c0392b"),
    
    # Security & Authentication - Verified Working
    ("🔐 PC Authentication System", "pc_auth_system.py", "#9b59b6"),
    ("🛡️ Advanced Security", "advanced_security.py", "#c0392b"),
    ("🤖 Automated Interventions", "automated_interventions.py", "#3498db"),
    ("📡 Automated Responses", "automated_responses.py", "#f39c12"),
    
    # Backup & Management - Only Fixed Versions
    ("💾 Backup Manager (Fixed)", "backup_manager_fixed.py", "#27ae60"),
    ("⚙️ Settings Manager (Fixed)", "settings_manager_fixed.py", "#3498db"),
    ("🗄️ Database Schema (Fixed)", "database_schema_fixed.py", "#e67e22"),
    ("📅 Task Scheduler (Fixed)", "task_scheduler_fixed.py", "#f39c12"),
    
    # Testing & Diagnostics
    ("🎮 Test GPU Monitoring", "test_gpu_monitoring.py", "#e67e22"),
    ("🖥️ Test GUI", "test_gui.py", "#3498db"),
    ("🐛 Debug GPU GUI", "debug_gpu_gui.py", "#c0392b"),
    ("🎯 Test NVIDIA SMI", "test_nvidia_smi.py", "#27ae60"),
    
    # Utilities & Tools - Only Fixed Versions
    ("🖥️ Console Launcher", "console_launcher.PY", "#3498db"),
    ("🔄 Stay Open Launcher", "stay_open_launcher.PY", "#27ae60"),
    ("🔌 System API", "system_api.py", "#e67e22"),
    ("❓ Help System", "help_system.py", "#f39c12"),
    ("📧 Email Notifications", "email_notifications.py", "#9b59b6"),
    ("🌍 Internationalization (Fixed)", "internationalization_fixed.py", "#2ecc71"),
    ("♿ Accessibility", "accessibility.py", "#3498db"),
    ("🤖 Machine Learning", "machine_learning.py", "#e67e22"),
    
    # Legacy Tools - Verified Working
    ("🚀 System Dashboard", "system_dashboard.py", "#16a085"),
    ("🧹 RAM Monitor", "ram_monitor_gui.py", "#f39c12"),
    ("🎮 GPU Monitor", "gpu_monitor_gui.py", "#c0392b"),
    ("⚡ CPU Monitor", "cpu_monitor_gui.py", "#5dade2")
]

def test_tool(name, filename, timeout=3):
    """Test a single tool"""
    try:
        # Try to run the tool with timeout
        process = subprocess.Popen(
            [sys.executable, filename],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
        )
        
        try:
            stdout, stderr = process.communicate(timeout=timeout)
            
            if process.returncode == 0:
                return True, "Launched successfully"
            else:
                return False, f"Exit code: {process.returncode}"
                
        except subprocess.TimeoutExpired:
            # Tool is running (good sign) - kill it
            if os.name == 'nt':
                process.terminate()
            else:
                process.send_signal(signal.SIGTERM)
            
            try:
                process.wait(timeout=1)
            except subprocess.TimeoutExpired:
                if os.name == 'nt':
                    process.kill()
                else:
                    process.send_signal(signal.SIGKILL)
            
            return True, "Launched and running (timeout)"
            
    except FileNotFoundError:
        return False, "File not found"
    except Exception as e:
        return False, f"Error: {str(e)}"

def main():
    """Test all tools"""
    base_path = Path(__file__).parent
    os.chdir(base_path)
    
    print("🧪 COMPREHENSIVE TOOL TESTING")
    print("=" * 50)
    
    working_tools = []
    broken_tools = []
    skipped_tools = []
    
    for i, (name, filename, color) in enumerate(all_tools, 1):
        print(f"\n[{i:2d}/51] Testing: {name}")
        print(f"      File: {filename}")
        
        try:
            success, message = test_tool(name, filename)
            
            if success:
                working_tools.append((name, filename, message))
                print(f"      ✅ {message}")
            else:
                broken_tools.append((name, filename, message))
                print(f"      ❌ {message}")
                
        except Exception as e:
            broken_tools.append((name, filename, f"Test error: {e}"))
            print(f"      ❌ Test error: {e}")
        
        # Small delay between tests
        time.sleep(0.5)
    
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    print(f"   Total Tools: {len(all_tools)}")
    print(f"   ✅ Working: {len(working_tools)}")
    print(f"   ❌ Broken: {len(broken_tools)}")
    print(f"   ⏭️ Skipped: {len(skipped_tools)}")
    
    if working_tools:
        print(f"\n✅ WORKING TOOLS ({len(working_tools)}):")
        for name, filename, message in working_tools:
            print(f"   - {name}: {message}")
    
    if broken_tools:
        print(f"\n❌ BROKEN TOOLS ({len(broken_tools)}):")
        for name, filename, message in broken_tools:
            print(f"   - {name}: {message}")
    
    # Success rate
    success_rate = (len(working_tools) / len(all_tools)) * 100
    print(f"\n📈 Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print("🎉 EXCELLENT - Almost all tools working!")
    elif success_rate >= 75:
        print("👍 GOOD - Most tools working!")
    elif success_rate >= 50:
        print("⚠️ FAIR - About half working")
    else:
        print("🚨 POOR - Many tools broken")

if __name__ == "__main__":
    main()
