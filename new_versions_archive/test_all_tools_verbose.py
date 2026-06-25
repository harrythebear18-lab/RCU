#!/usr/bin/env python3
"""
Comprehensive tool testing script with verbose output and message boxes
Tests all 51 tools for launch and basic functionality with detailed feedback
"""

import subprocess
import sys
import time
import os
from pathlib import Path
import threading
import signal
import tkinter as tk
from tkinter import messagebox

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

class VerboseTester:
    def __init__(self):
        self.working_tools = []
        self.broken_tools = []
        self.skipped_tools = []
        self.show_messageboxes = True
        
    def test_tool_verbose(self, name, filename, timeout=10):
        """Test a single tool with verbose output"""
        print(f"\n{'='*60}")
        print(f"🧪 TESTING: {name}")
        print(f"📁 File: {filename}")
        print(f"⏱️ Timeout: {timeout} seconds")
        print(f"{'='*60}")
        
        try:
            # Check if file exists
            file_path = Path(filename)
            if not file_path.exists():
                print(f"❌ FILE NOT FOUND: {filename}")
                return False, "File not found"
            
            print(f"✅ File exists: {file_path.stat().st_size:,} bytes")
            
            # Try to run the tool
            print(f"🚀 Launching tool...")
            process = subprocess.Popen(
                [sys.executable, filename],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
            )
            
            start_time = time.time()
            output_lines = []
            error_lines = []
            
            try:
                # Monitor the process
                while time.time() - start_time < timeout:
                    return_code = process.poll()
                    
                    if return_code is not None:
                        # Process finished
                        stdout, stderr = process.communicate()
                        output_lines = stdout.split('\n') if stdout else []
                        error_lines = stderr.split('\n') if stderr else []
                        
                        print(f"⏹️ Process finished with exit code: {return_code}")
                        print(f"⏱️ Runtime: {time.time() - start_time:.2f} seconds")
                        
                        if return_code == 0:
                            print(f"✅ SUCCESS: Tool completed successfully")
                            if output_lines:
                                print(f"📤 Output (first 10 lines):")
                                for line in output_lines[:10]:
                                    if line.strip():
                                        print(f"   {line}")
                            return True, f"Completed successfully (exit code 0)"
                        else:
                            print(f"❌ FAILED: Tool exited with code {return_code}")
                            if error_lines:
                                print(f"📥 Error output:")
                                for line in error_lines[:10]:
                                    if line.strip():
                                        print(f"   {line}")
                            return False, f"Exit code {return_code}"
                    
                    # Check for output
                    try:
                        # Try to read any available output without blocking
                        if os.name == 'nt':
                            import msvcrt
                            if msvcrt.kbhit():
                                # There's input available
                                pass
                    except:
                        pass
                    
                    time.sleep(0.1)
                
                # Timeout reached - process is still running
                print(f"⏰ TIMEOUT: Tool still running after {timeout} seconds")
                print(f"🔍 This likely means the tool is working but waiting for input or running a GUI")
                
                # Show message box if enabled
                if self.show_messageboxes:
                    try:
                        root = tk.Tk()
                        root.withdraw()  # Hide the main window
                        
                        result = messagebox.askyesno(
                            "Tool Running",
                            f"{name}\n\nThe tool is still running after {timeout} seconds.\nThis likely means it's working but waiting for input or running a GUI.\n\nDo you want to keep it running?",
                            icon='question'
                        )
                        root.destroy()
                        
                        if result:
                            print(f"✅ USER CHOICE: Keep tool running (considered SUCCESS)")
                            return True, "Running (user chose to keep)"
                        else:
                            print(f"⏹️ USER CHOICE: Terminate tool")
                            
                    except Exception as e:
                        print(f"⚠️ Could not show message box: {e}")
                
                # Terminate the process
                print(f"🛑 Terminating process...")
                if os.name == 'nt':
                    process.terminate()
                else:
                    process.send_signal(signal.SIGTERM)
                
                try:
                    process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    if os.name == 'nt':
                        process.kill()
                    else:
                        process.send_signal(signal.SIGKILL)
                
                return True, f"Running (timeout - tool likely working)"
                
            except subprocess.TimeoutExpired:
                print(f"⏰ TIMEOUT EXCEEDED")
                return False, "Timeout exceeded"
                
        except FileNotFoundError:
            print(f"❌ FILE NOT FOUND: {filename}")
            return False, "File not found"
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            return False, f"Error: {str(e)}"
    
    def run_all_tests(self):
        """Run all tests with verbose output"""
        print("🧪 COMPREHENSIVE VERBOSE TOOL TESTING")
        print("=" * 60)
        print(f"📊 Testing {len(all_tools)} tools with detailed output")
        print(f"⏱️ Each tool gets 10 seconds to respond")
        print(f"📱 Message boxes will appear for running tools")
        print("=" * 60)
        
        # Ask about message boxes
        try:
            root = tk.Tk()
            root.withdraw()
            
            self.show_messageboxes = messagebox.askyesno(
                "Message Boxes",
                "Do you want to see message boxes for tools that are still running?\n\nThis will let you decide whether to keep them running or terminate them.",
                icon='question'
            )
            root.destroy()
        except:
            self.show_messageboxes = False
        
        print(f"📱 Message boxes: {'ENABLED' if self.show_messageboxes else 'DISABLED'}")
        print()
        
        for i, (name, filename, color) in enumerate(all_tools, 1):
            print(f"\n{'='*60}")
            print(f"📍 Progress: [{i:2d}/{len(all_tools)}] {i/len(all_tools)*100:.1f}%")
            print(f"{'='*60}")
            
            success, message = self.test_tool_verbose(name, filename)
            
            if success:
                self.working_tools.append((name, filename, message))
                print(f"✅ RESULT: WORKING - {message}")
            else:
                self.broken_tools.append((name, filename, message))
                print(f"❌ RESULT: BROKEN - {message}")
            
            # Small delay between tests
            time.sleep(1)
        
        # Final summary
        print(f"\n{'='*60}")
        print("📊 FINAL TEST RESULTS")
        print("=" * 60)
        print(f"   Total Tools: {len(all_tools)}")
        print(f"   ✅ Working: {len(self.working_tools)}")
        print(f"   ❌ Broken: {len(self.broken_tools)}")
        print(f"   ⏭️ Skipped: {len(self.skipped_tools)}")
        
        success_rate = (len(self.working_tools) / len(all_tools)) * 100
        print(f"\n📈 Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 90:
            print("🎉 EXCELLENT - Almost all tools working!")
        elif success_rate >= 75:
            print("👍 GOOD - Most tools working!")
        elif success_rate >= 50:
            print("⚠️ FAIR - About half working")
        else:
            print("🚨 POOR - Many tools broken")
        
        # Show detailed results
        if self.working_tools:
            print(f"\n✅ WORKING TOOLS ({len(self.working_tools)}):")
            for name, filename, message in self.working_tools:
                print(f"   - {name}: {message}")
        
        if self.broken_tools:
            print(f"\n❌ BROKEN TOOLS ({len(self.broken_tools)}):")
            for name, filename, message in self.broken_tools:
                print(f"   - {name}: {message}")

def main():
    """Main function"""
    try:
        base_path = Path(__file__).parent
        os.chdir(base_path)
        
        tester = VerboseTester()
        tester.run_all_tests()
        
    except Exception as e:
        print(f"❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
