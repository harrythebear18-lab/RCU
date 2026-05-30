#!/usr/bin/env python3
"""
Console Homelab Launcher
Simple console launcher that stays open until manually closed.
"""

import sys
import os
import subprocess
from pathlib import Path

class ConsoleLauncher:
    def __init__(self):
        self.current_dir = Path(__file__).parent
        self.available_tools = self.scan_available_tools()
    
    def scan_available_tools(self):
        """Scan for available tools"""
        tools = {}
        
        # Unified homelab systems
        tools['1'] = {
            'name': '[HOME] Simple Unified GUI',
            'file': 'simple_unified_gui.PY',
            'description': 'Error-free unified homelab interface'
        }
        
        tools['2'] = {
            'name': '[ROCKET] Unified Launcher GUI',
            'file': 'launcher_gui.py',
            'description': 'Tool management interface'
        }
        
        tools['3'] = {
            'name': '[LOCK] PC Authentication GUI',
            'file': 'pc_auth_gui.py',
            'description': 'PC authentication management'
        }
        
        tools['4'] = {
            'name': '[CHART] Streamlined Dashboard',
            'file': 'streamlined_dashboard.py',
            'description': 'Core streamlined system dashboard'
        }
        
        # Legacy tools
        tools['5'] = {
            'name': '[ROCKET] System Dashboard',
            'file': 'system_dashboard.py',
            'description': 'Original system dashboard'
        }
        
        tools['6'] = {
            'name': '[CHART] Enhanced Dashboard',
            'file': 'system_dashboard_enhanced.py',
            'description': 'Enhanced system dashboard'
        }
        
        tools['7'] = {
            'name': '[CLEAN] RAM Monitor',
            'file': 'ram_monitor_gui.py',
            'description': 'RAM monitoring tool'
        }
        
        tools['8'] = {
            'name': '[GAME] GPU Monitor',
            'file': 'gpu_monitor_gui.py',
            'description': 'GPU monitoring tool'
        }
        
        tools['9'] = {
            'name': '[POWER] CPU Monitor',
            'file': 'cpu_monitor_gui.py',
            'description': 'CPU monitoring tool'
        }
        
        tools['0'] = {
            'name': '📦 Install Dependencies',
            'file': 'install_deps',
            'description': 'Install required Python packages'
        }
        
        return tools
    
    def display_header(self):
        """Display header"""
        print("=" * 60)
        print("[HOME] UNIFIED HOMELAB CONSOLE LAUNCHER")
        print("=" * 60)
        print("Choose a tool to launch:")
        print()
    
    def display_menu(self):
        """Display menu options"""
        for key, tool in self.available_tools.items():
            if key == '0':
                print(f"{key}. {tool['name']} - {tool['description']}")
                print("-" * 50)
            else:
                status = "[OK] Available" if self.check_file_exists(tool['file']) else "[ERROR] Missing"
                print(f"{key}. {tool['name']} [{status}]")
                print(f"   → {tool['description']}")
                print()
    
    def check_file_exists(self, filename):
        """Check if file exists"""
        if filename == 'install_deps':
            return True
        return (self.current_dir / filename).exists()
    
    def launch_tool(self, choice):
        """Launch selected tool"""
        if choice not in self.available_tools:
            print("[ERROR] Invalid choice!")
            return
        
        tool = self.available_tools[choice]
        
        if choice == '0':
            self.install_dependencies()
        else:
            if not self.check_file_exists(tool['file']):
                print(f"[ERROR] File not found: {tool['file']}")
                return
            
            print(f"[ROCKET] Launching {tool['name']}...")
            self.run_script(tool['file'])
    
    def run_script(self, script_name):
        """Run a Python script"""
        try:
            # Use the same Python interpreter
            subprocess.Popen([sys.executable, str(self.current_dir / script_name)])
            print(f"[OK] {script_name} launched successfully!")
            print("[CLIPBOARD] Note: The tool is now running in a separate window")
            print("[REFRESH] Console remains open - you can launch more tools!")
        except Exception as e:
            print(f"[ERROR] Failed to launch {script_name}: {e}")
    
    def install_dependencies(self):
        """Install dependencies"""
        print("📦 Installing dependencies...")
        
        deps = [
            "tkinter",
            "matplotlib", 
            "numpy",
            "psutil"
        ]
        
        for dep in deps:
            print(f"Installing {dep}...")
            try:
                if dep == "tkinter":
                    print("[OK] tkinter is usually included with Python")
                else:
                    result = subprocess.run([sys.executable, '-m', 'pip', 'install', dep], 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        print(f"[OK] {dep} installed successfully")
                    else:
                        print(f"[ERROR] Failed to install {dep}: {result.stderr}")
            except Exception as e:
                print(f"[ERROR] Error installing {dep}: {e}")
        
        print("📦 Dependency installation completed!")
    
    def run(self):
        """Main launcher loop - stays open until manually closed"""
        print("[REFRESH] Console launcher started - will stay open until you close it!")
        print("💡 You can launch multiple tools without closing the console")
        print("[TOOL] Type 'q' and press Enter to quit, or close the window manually")
        print()
        
        while True:
            try:
                # Clear screen (works on Windows)
                os.system('cls' if os.name == 'nt' else 'clear')
                
                self.display_header()
                self.display_menu()
                
                print("[CLIPBOARD] Enter your choice (0-9) to launch a tool:")
                print("👋 Type 'q' to quit, or close this window to exit")
                choice = input("👉 ").strip().lower()
                
                if choice == 'q':
                    print("👋 Exiting console launcher...")
                    print("💡 Note: Any launched tools will continue running")
                    break
                
                if choice in self.available_tools:
                    self.launch_tool(choice)
                    print()
                    print("[REFRESH] Console remains open - you can launch more tools!")
                    print("💡 Press Enter to return to menu, or 'q' to quit")
                    next_action = input("👉 ").strip().lower()
                    if next_action == 'q':
                        print("👋 Exiting console launcher...")
                        break
                else:
                    print("[ERROR] Invalid choice! Please try again.")
                    print("💡 Press Enter to continue, or 'q' to quit")
                    next_action = input("👉 ").strip().lower()
                    if next_action == 'q':
                        print("👋 Exiting console launcher...")
                        break
                    
            except KeyboardInterrupt:
                print("\n👋 Exiting console launcher...")
                print("💡 Note: Any launched tools will continue running")
                break
            except Exception as e:
                print(f"[ERROR] Error: {e}")
                print("💡 Press Enter to continue, or 'q' to quit")
                try:
                    next_action = input("👉 ").strip().lower()
                    if next_action == 'q':
                        print("👋 Exiting console launcher...")
                        break
                except:
                    print("👋 Exiting console launcher...")
                    break

def main():
    """Main function"""
    print("[HOME] Starting Unified Homelab Console Launcher...")
    
    # Check Python version
    if sys.version_info < (3, 6):
        print("[ERROR] This launcher requires Python 3.6 or higher")
        input("Press Enter to exit...")
        return
    
    launcher = ConsoleLauncher()
    launcher.run()

if __name__ == "__main__":
    main()
