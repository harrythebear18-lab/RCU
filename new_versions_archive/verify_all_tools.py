#!/usr/bin/env python3
"""
Comprehensive tool verification script
"""

import os
from pathlib import Path

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

def main():
    """Verify all tool files exist"""
    base_path = Path(__file__).parent
    missing_files = []
    existing_files = []
    
    print("🔍 COMPREHENSIVE TOOL VERIFICATION")
    print("=" * 50)
    
    for name, filename, color in all_tools:
        file_path = base_path / filename
        
        if file_path.exists():
            size = file_path.stat().st_size
            existing_files.append((name, filename, size))
            print(f"✅ {name}: {filename} ({size:,} bytes)")
        else:
            missing_files.append((name, filename))
            print(f"❌ {name}: {filename} - MISSING")
    
    print("\n" + "=" * 50)
    print(f"📊 SUMMARY:")
    print(f"   Total Tools: {len(all_tools)}")
    print(f"   ✅ Existing: {len(existing_files)}")
    print(f"   ❌ Missing: {len(missing_files)}")
    
    if missing_files:
        print(f"\n🚨 MISSING FILES:")
        for name, filename in missing_files:
            print(f"   - {name}: {filename}")
    else:
        print(f"\n✅ ALL FILES VERIFIED - NO MISSING FILES!")
    
    # Check launcher file
    launcher_file = base_path / "working_gui_launcher_no_duplicates.py"
    if launcher_file.exists():
        print(f"\n✅ Launcher file exists: {launcher_file.name}")
        print(f"   Size: {launcher_file.stat().st_size:,} bytes")
    else:
        print(f"\n❌ Launcher file MISSING: {launcher_file.name}")
    
    # Check syntax of launcher
    try:
        import py_compile
        py_compile.compile(launcher_file, doraise=True)
        print(f"✅ Launcher syntax check PASSED")
    except Exception as e:
        print(f"❌ Launcher syntax check FAILED: {e}")

if __name__ == "__main__":
    main()
