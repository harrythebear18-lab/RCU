#!/usr/bin/env python3
"""
Stay Open Launcher - Guaranteed to stay open until manually closed
"""

import sys
import os
import subprocess
from pathlib import Path

def clear_screen():
    """Clear the screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def launch_tool(tool_name, script_file):
    """Launch a tool and keep console open"""
    try:
        print(f"[ROCKET] Launching {tool_name}...")
        
        # Launch in background so console doesn't wait
        subprocess.Popen([sys.executable, str(Path(__file__).parent / script_file)], 
                       creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
        
        print(f"[OK] {tool_name} launched!")
        print("[CLIPBOARD] Tool is running in separate window")
        
    except Exception as e:
        print(f"[ERROR] Error launching {tool_name}: {e}")

def show_menu():
    """Show the menu"""
    print("=" * 60)
    print("[HOME] UNIFIED HOMELAB LAUNCHER")
    print("=" * 60)
    print("[CLIPBOARD] Choose a tool to launch (console will stay open):")
    print()
    print("1. [HOME] Simple Unified GUI")
    print("2. [ROCKET] Unified Launcher GUI") 
    print("3. [LOCK] PC Authentication GUI")
    print("4. [CHART] Streamlined Dashboard")
    print("5. [ROCKET] System Dashboard")
    print("6. [CHART] Enhanced Dashboard")
    print("7. [CLEAN] RAM Monitor")
    print("8. [GAME] GPU Monitor")
    print("9. [POWER] CPU Monitor")
    print("0. 📦 Install Dependencies")
    print("q. 👋 Quit")
    print()

def main_loop():
    """Main loop that never exits unless told to"""
    current_dir = Path(__file__).parent
    
    while True:
        try:
            clear_screen()
            show_menu()
            
            choice = input("👉 Enter choice (1-9, 0, q): ").strip().lower()
            
            if choice == 'q':
                print("👋 Goodbye!")
                break
            
            elif choice == '1':
                if (current_dir / 'simple_unified_gui.PY').exists():
                    launch_tool("Simple Unified GUI", 'simple_unified_gui.PY')
                else:
                    print("[ERROR] simple_unified_gui.PY not found")
            
            elif choice == '2':
                if (current_dir / 'launcher_gui.py').exists():
                    launch_tool("Unified Launcher GUI", 'launcher_gui.py')
                else:
                    print("[ERROR] launcher_gui.py not found")
            
            elif choice == '3':
                if (current_dir / 'pc_auth_gui.py').exists():
                    launch_tool("PC Authentication GUI", 'pc_auth_gui.py')
                else:
                    print("[ERROR] pc_auth_gui.py not found")
            
            elif choice == '4':
                if (current_dir / 'streamlined_dashboard.py').exists():
                    launch_tool("Streamlined Dashboard", 'streamlined_dashboard.py')
                else:
                    print("[ERROR] streamlined_dashboard.py not found")
            
            elif choice == '5':
                if (current_dir / 'system_dashboard.py').exists():
                    launch_tool("System Dashboard", 'system_dashboard.py')
                else:
                    print("[ERROR] system_dashboard.py not found")
            
            elif choice == '6':
                if (current_dir / 'system_dashboard_enhanced.py').exists():
                    launch_tool("Enhanced Dashboard", 'system_dashboard_enhanced.py')
                else:
                    print("[ERROR] system_dashboard_enhanced.py not found")
            
            elif choice == '7':
                if (current_dir / 'ram_monitor_gui.py').exists():
                    launch_tool("RAM Monitor", 'ram_monitor_gui.py')
                else:
                    print("[ERROR] ram_monitor_gui.py not found")
            
            elif choice == '8':
                if (current_dir / 'gpu_monitor_gui.py').exists():
                    launch_tool("GPU Monitor", 'gpu_monitor_gui.py')
                else:
                    print("[ERROR] gpu_monitor_gui.py not found")
            
            elif choice == '9':
                if (current_dir / 'cpu_monitor_gui.py').exists():
                    launch_tool("CPU Monitor", 'cpu_monitor_gui.py')
                else:
                    print("[ERROR] cpu_monitor_gui.py not found")
            
            elif choice == '0':
                print("📦 Installing dependencies...")
                deps = ['matplotlib', 'numpy', 'psutil']
                for dep in deps:
                    try:
                        subprocess.run([sys.executable, '-m', 'pip', 'install', dep], 
                                     capture_output=True, text=True)
                        print(f"[OK] {dep} installed")
                    except:
                        print(f"[ERROR] Failed to install {dep}")
                print("📦 Installation complete!")
            
            else:
                print("[ERROR] Invalid choice!")
            
            # Always wait for user input before continuing
            input("\n[REFRESH] Press Enter to continue (or 'q' to quit): ")
            user_input = input().strip().lower()
            if user_input == 'q':
                print("👋 Goodbye!")
                break
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"[ERROR] Error: {e}")
            input("[REFRESH] Press Enter to continue...")

if __name__ == "__main__":
    print("[HOME] Starting Stay-Open Launcher...")
    print("💡 This console will stay open until you close it!")
    print()
    
    try:
        main_loop()
    except Exception as e:
        print(f"[ERROR] Fatal error: {e}")
        input("[REFRESH] Press Enter to exit...")
    
    print("👋 Launcher closed!")
