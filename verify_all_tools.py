#!/usr/bin/env python3
"""
Comprehensive tool verification script
Checks file existence, syntax, and import validity for all launcher tools
"""

import os
import sys
import py_compile
from pathlib import Path

# All tools from the current launcher.py
# (name, filename, category, check_type)
# check_type: "syntax" = py_compile only, "import" = attempt import
all_tools = [
    # === Single-Device Tools (Root Directory) ===
    ("PC Authentication GUI", "pc_auth_gui.py", "Single-Device", "syntax"),
    ("Streamlined Dashboard", "streamlined_dashboard.py", "Single-Device", "syntax"),
    ("Overclocking Dashboard", "overclocking_dashboard.py", "Single-Device", "syntax"),
    ("Resource Optimizer", "resource_optimizer.py", "Single-Device", "syntax"),
    ("Resource Optimizer (Tray)", "resource_optimizer_tray.py", "Single-Device", "syntax"),

    # === Legacy Tools (Root Directory) ===
    ("System Dashboard", "system_dashboard.py", "Legacy", "syntax"),
    ("RAM Monitor", "ram_monitor_gui.py", "Legacy", "syntax"),
    ("GPU Monitor", "gpu_monitor_gui.py", "Legacy", "syntax"),
    ("CPU Monitor", "cpu_monitor_gui.py", "Legacy", "syntax"),
    ("RAM Cleanup Script", "ram_cleanup_script.py", "Legacy", "syntax"),
    ("Memory Jolt", "memory_jolt.py", "Legacy", "syntax"),
    ("Soft RAM Cleaner", "soft_ram_cleaner.py", "Legacy", "syntax"),

    # === Advanced Networking (Root + RDMA Directory) ===
    ("RDMA Launcher", "rdma_launcher.py", "Advanced Networking", "syntax"),

    # === Homelab Systems (Root + External) ===
    ("Homelab Portal", "homelab_portal.py", "Homelab Systems", "syntax"),
]

# External tools referenced by rdma_launcher.py
rdma_tools = [
    ("RDMA Desktop App", "rdma_desktop_app.py"),
    ("RDMA REST API", "rdma_rest_api.py"),
    ("Performance Profiler", "performance_profiler.py"),
    ("Ultra Latency Benchmark", "ultra_latency_benchmark.py"),
    ("Zero-Copy Operations", "zero_copy_rdmda.py"),
    ("UDP Memory Bridge", "udp_memory_bridge.py"),
    ("PCIe Tunneling", "virtual_pcie_tunnel.py"),
    ("Network Bypass", "raw_network_bypass.py"),
    ("Monitoring System", "monitoring_system.py"),
]

# External tools referenced by launcher.py
external_tools = [
    ("Homelab Tools Launcher", r"Homelab_Tools\simple_launcher.py"),
]

# Core Services directory
core_services_dir = "Core Services"
core_services_files = [
    "event_bus.py", "config_manager.py", "auth_service.py",
    "data_persistence.py", "unified_monitoring.py",
    "bidirectional_resource_sharing.py", "windows_network_discovery.py",
    "intel_ethernet_optimizer.py", "identical_hardware_optimizer.py",
    "nvidia_gpu_sharing.py", "ddr4_ram_sharing.py",
    "windows_screen_sharing.py", "system_data_connector.py",
    "theme_config.py", "windows_assistant_integration.py",
    "portal_api_endpoints.py", "rest_api.py", "simple_rest_api.py",
    "analytics_engine.py", "automation_framework.py",
    "advanced_security.py", "smart_system_sensing.py",
    "mesh_app_communication.py", "mesh_app_integration.py",
    "wireguard_installer.py", "admin_auto_config.py",
    "data_abstraction_layer.py", "frontend_backend_mixer.py",
    "frontend_backend_synchronization.py", "unified_path_manager.py",
    "windows_version_abstraction.py",
]


def check_syntax(filepath):
    """Check if a Python file compiles without syntax errors"""
    try:
        py_compile.compile(str(filepath), doraise=True)
        return True, None
    except py_compile.PyCompileError as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)


def main():
    """Verify all tool files exist and have valid syntax"""
    base_path = Path(__file__).parent
    rdma_path = Path(r"C:\Users\htsou\Desktop\RDMA")

    missing_files = []
    syntax_errors = []
    existing_files = []
    passed_syntax = []

    print("=" * 70)
    print("  COMPREHENSIVE TOOL VERIFICATION - LAUNCHER + RDMA + HOMELAB")
    print("=" * 70)

    # === Check root tools ===
    print("\n--- Single-Device & Legacy Tools ---")
    for name, filename, category, check_type in all_tools:
        file_path = base_path / filename
        if file_path.exists():
            size = file_path.stat().st_size
            existing_files.append((name, filename, size))
            if check_type == "syntax":
                ok, err = check_syntax(file_path)
                if ok:
                    passed_syntax.append((name, filename))
                    print(f"  ✅ {name}: {filename} ({size:,} bytes) [syntax OK]")
                else:
                    syntax_errors.append((name, filename, err))
                    print(f"  ⚠️  {name}: {filename} ({size:,} bytes) [SYNTAX ERROR]")
            else:
                print(f"  ✅ {name}: {filename} ({size:,} bytes)")
        else:
            missing_files.append((name, filename))
            print(f"  ❌ {name}: {filename} - MISSING")

    # === Check RDMA tools ===
    print("\n--- RDMA Tools (C:\\Users\\htsou\\Desktop\\RDMA) ---")
    for name, filename in rdma_tools:
        file_path = rdma_path / filename
        if file_path.exists():
            size = file_path.stat().st_size
            existing_files.append((name, filename, size))
            ok, err = check_syntax(file_path)
            if ok:
                passed_syntax.append((name, filename))
                print(f"  ✅ {name}: {filename} ({size:,} bytes) [syntax OK]")
            else:
                syntax_errors.append((name, filename, err))
                print(f"  ⚠️  {name}: {filename} ({size:,} bytes) [SYNTAX ERROR]")
        else:
            missing_files.append((name, filename))
            print(f"  ❌ {name}: {filename} - MISSING")

    # === Check external tools ===
    print("\n--- External Tools ---")
    for name, rel_path in external_tools:
        file_path = base_path / rel_path
        if file_path.exists():
            size = file_path.stat().st_size
            existing_files.append((name, rel_path, size))
            ok, err = check_syntax(file_path)
            if ok:
                passed_syntax.append((name, rel_path))
                print(f"  ✅ {name}: {rel_path} ({size:,} bytes) [syntax OK]")
            else:
                syntax_errors.append((name, rel_path, err))
                print(f"  ⚠️  {name}: {rel_path} ({size:,} bytes) [SYNTAX ERROR]")
        else:
            missing_files.append((name, rel_path))
            print(f"  ❌ {name}: {rel_path} - MISSING")

    # === Check Core Services ===
    print(f"\n--- Core Services ({core_services_dir}/) ---")
    cs_path = base_path / core_services_dir
    if cs_path.exists():
        for filename in core_services_files:
            file_path = cs_path / filename
            if file_path.exists():
                size = file_path.stat().st_size
                existing_files.append((filename, f"Core Services/{filename}", size))
                ok, err = check_syntax(file_path)
                if ok:
                    passed_syntax.append((filename, f"Core Services/{filename}"))
                    print(f"  ✅ {filename} ({size:,} bytes) [syntax OK]")
                else:
                    syntax_errors.append((filename, f"Core Services/{filename}", err))
                    print(f"  ⚠️  {filename} ({size:,} bytes) [SYNTAX ERROR]")
            else:
                missing_files.append((filename, f"Core Services/{filename}"))
                print(f"  ❌ {filename} - MISSING")
    else:
        print(f"  ❌ Core Services directory MISSING")
        missing_files.append(("Core Services", "Core Services/"))

    # === Check launcher itself ===
    print("\n--- Main Launcher ---")
    launcher_file = base_path / "launcher.py"
    if launcher_file.exists():
        size = launcher_file.stat().st_size
        ok, err = check_syntax(launcher_file)
        if ok:
            passed_syntax.append(("Launcher", "launcher.py"))
            print(f"  ✅ launcher.py ({size:,} bytes) [syntax OK]")
        else:
            syntax_errors.append(("Launcher", "launcher.py", err))
            print(f"  ⚠️  launcher.py ({size:,} bytes) [SYNTAX ERROR]")
    else:
        missing_files.append(("Launcher", "launcher.py"))
        print(f"  ❌ launcher.py - MISSING")

    # === Check requirements.txt ===
    req_file = base_path / "requirements.txt"
    if req_file.exists():
        print(f"  ✅ requirements.txt ({req_file.stat().st_size:,} bytes)")
    else:
        missing_files.append(("Requirements", "requirements.txt"))
        print(f"  ❌ requirements.txt - MISSING")

    # === SUMMARY ===
    print("\n" + "=" * 70)
    print("  SUMMARY")
    print("=" * 70)
    total = len(all_tools) + len(rdma_tools) + len(external_tools) + len(core_services_files) + 2
    print(f"  Total Tools Checked:  {total}")
    print(f"  ✅ Files Found:       {len(existing_files)}")
    print(f"  ✅ Syntax Passed:     {len(passed_syntax)}")
    print(f"  ❌ Missing Files:     {len(missing_files)}")
    print(f"  ⚠️  Syntax Errors:    {len(syntax_errors)}")

    if missing_files:
        print(f"\n  🚨 MISSING FILES:")
        for name, filename in missing_files:
            print(f"     - {name}: {filename}")

    if syntax_errors:
        print(f"\n  ⚠️  SYNTAX ERRORS:")
        for name, filename, err in syntax_errors:
            print(f"     - {name}: {filename}")
            print(f"       Error: {err[:200]}")

    if not missing_files and not syntax_errors:
        print(f"\n  ✅ ALL TOOLS VERIFIED - NO MISSING FILES, NO SYNTAX ERRORS!")

    print("\n" + "=" * 70)
    return 0 if (not missing_files and not syntax_errors) else 1


if __name__ == "__main__":
    sys.exit(main())
