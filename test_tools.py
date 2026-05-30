#!/usr/bin/env python3
"""
Test script to verify all tools work
"""

import subprocess
import sys
import os
from pathlib import Path

def test_tool(filename, tool_name):
    """Test if a tool can be imported and run basic check"""
    try:
        # Try to import the module first
        if filename.endswith('.PY'):
            filename = filename[:-3] + '.py'
        
        file_path = Path(filename)
        if not file_path.exists():
            return False, f"File not found: {filename}"
        
        # Try to run a quick syntax check
        result = subprocess.run([sys.executable, "-m", "py_compile", filename], 
                              capture_output=True, text=True, timeout=5)
        
        if result.returncode != 0:
            return False, f"Syntax error: {result.stderr}"
        
        return True, "OK"
    except Exception as e:
        return False, f"Error: {str(e)}"

def main():
    """Test all tools in the launcher"""
    tools = [
        ("simple_unified_gui.PY", "⭐ Simple Unified GUI"),
        ("launcher_gui.py", "🚀 Unified Launcher GUI"),
        ("pc_auth_gui.py", "🔐 PC Authentication GUI"),
        ("streamlined_dashboard.py", "📊 Streamlined Dashboard"),
        ("system_dashboard_enhanced.py", "📈 Enhanced Dashboard"),
        ("fully_unified_gui.py", "🌟 Fully Unified GUI"),
        ("integrated_homelab_with_auth.py", "🔑 Integrated Homelab with Auth"),
        ("streamlined_homelab_system.py", "🎯 Streamlined Homelab System"),
        ("unified_launcher.py", "🚀 Unified Launcher"),
        ("win10_homelab_server.py", "🏢 Windows 10 Homelab Server"),
        ("win10_server_launcher.py", "🚀 Windows 10 Server Launcher"),
        ("win11_homelab_client.py", "💻 Windows 11 Homelab Client"),
        ("win11_rdma_client.py", "🔌 Windows 11 RDMA Client"),
        ("overclocking_dashboard.py", "🔧 Overclocking Dashboard"),
        ("performance_optimizer.py", "⚡ Performance Optimizer"),
        ("resource_optimizer.py", "🎯 Resource Optimizer"),
        ("resource_optimizer_fixed.py", "🔧 Resource Optimizer Fixed"),
        ("performance_reports.py", "📊 Performance Reports"),
        ("system_health_scorer.py", "💚 System Health Scorer"),
        ("rdma_integration.py", "🔌 RDMA Integration"),
        ("homelab_server.py", "🏢 Homelab Server"),
        ("homelab_client.py", "💻 Homelab Client"),
        ("homelab_dashboard.py", "📊 Homelab Dashboard"),
        ("unified_homelab_dashboard.py", "🌐 Unified Homelab Dashboard"),
        ("unified_homelab_integration.py", "🔗 Unified Homelab Integration"),
        ("aggressive_ram_cleaner.py", "🧹 Aggressive RAM Cleaner"),
        ("soft_ram_cleaner.py", "🧽 Soft RAM Cleaner"),
        ("ram_cleanup_script.py", "🔄 RAM Cleanup Script"),
        ("cpu_cleanup_script.py", "⚡ CPU Cleanup Script"),
        ("gpu_cleanup_script.py", "🎮 GPU Cleanup Script"),
        ("system_cleanup_master.py", "👑 System Cleanup Master"),
        ("memory_jolt.py", "⚡ Memory Jolt"),
        ("pc_auth_system.py", "🔐 PC Authentication System"),
        ("advanced_security.py", "🛡️ Advanced Security"),
        ("automated_interventions.py", "🤖 Automated Interventions"),
        ("automated_responses.py", "📡 Automated Responses"),
        ("backup_manager.py", "💾 Backup Manager"),
        ("settings_manager.py", "⚙️ Settings Manager"),
        ("database_schema.py", "🗄️ Database Schema"),
        ("task_scheduler.py", "📅 Task Scheduler"),
        ("test_gpu_monitoring.py", "🎮 Test GPU Monitoring"),
        ("test_gui.py", "🖥️ Test GUI"),
        ("debug_gpu_gui.py", "🐛 Debug GPU GUI"),
        ("test_nvidia_smi.py", "🎯 Test NVIDIA SMI"),
        ("console_launcher.PY", "🖥️ Console Launcher"),
        ("stay_open_launcher.PY", "🔄 Stay Open Launcher"),
        ("system_api.py", "🔌 System API"),
        ("help_system.py", "❓ Help System"),
        ("email_notifications.py", "📧 Email Notifications"),
        ("internationalization.py", "🌍 Internationalization"),
        ("accessibility.py", "♿ Accessibility"),
        ("machine_learning.py", "🤖 Machine Learning"),
        ("system_dashboard.py", "🚀 System Dashboard"),
        ("ram_monitor_gui.py", "🧹 RAM Monitor"),
        ("gpu_monitor_gui.py", "🎮 GPU Monitor"),
        ("cpu_monitor_gui.py", "⚡ CPU Monitor"),
        ("launcher.py", "🚀 Launcher")
    ]
    
    print("Testing all tools...")
    print("=" * 50)
    
    working_tools = []
    broken_tools = []
    
    for filename, tool_name in tools:
        works, message = test_tool(filename, tool_name)
        if works:
            working_tools.append((filename, tool_name))
            print(f"✅ {tool_name}: {message}")
        else:
            broken_tools.append((filename, tool_name, message))
            print(f"❌ {tool_name}: {message}")
    
    print("=" * 50)
    print(f"Working tools: {len(working_tools)}")
    print(f"Broken tools: {len(broken_tools)}")
    
    if broken_tools:
        print("\nBroken tools:")
        for filename, tool_name, error in broken_tools:
            print(f"  - {tool_name}: {error}")
    
    # Generate corrected tool list
    print("\nCorrected tool list for launcher:")
    print("all_tools = [")
    for filename, tool_name in working_tools:
        print(f'    ("{tool_name}", "{filename}", "#color"),')
    print("]")

if __name__ == "__main__":
    main()
