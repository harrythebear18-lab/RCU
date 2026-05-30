#!/usr/bin/env python3
"""
Simple RAM Sharing GUI - No tkinter required
Uses console-based interface with menu system
"""

import subprocess
import threading
import time
import os
import sys
from datetime import datetime

class SimpleRAMSharingGUI:
    def __init__(self):
        self.running = True
        self.current_action = None
        
    def clear_screen(self):
        """Clear the console screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def print_header(self):
        """Print the main header"""
        self.clear_screen()
        print("=" * 60)
        print("    HOMELAB RAM SHARING MANAGER")
        print("=" * 60)
        print("Windows 10/11 Cross-Version Compatibility")
        print("Server: 192.168.1.186 | Client: 192.168.1.132")
        print("=" * 60)
        print()
        
    def print_menu(self):
        """Print the main menu"""
        print("MAIN MENU:")
        print("1. 🚀 Start RAM Sharing Server (PC 1)")
        print("2. 🔗 Connect to RAM Server (PC 2)")
        print("3. ⏹️ Stop Server / Disconnect")
        print("4. 🧪 Test Performance")
        print("5. 🔧 Fix Windows Compatibility")
        print("6. 📋 Show Status")
        print("7. 🧹 Cleanup All")
        print("8. ❌ Exit")
        print()
        
    def log(self, message, level="INFO"):
        """Log a message with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = {
            "INFO": "ℹ️",
            "SUCCESS": "✅",
            "ERROR": "❌",
            "WARNING": "⚠️"
        }.get(level, "ℹ️")
        print(f"[{timestamp}] {prefix} {message}")
        
    def wait_for_action(self):
        """Wait for user action to complete"""
        if self.current_action:
            print("\n⏳ Action in progress... Please wait")
            while self.current_action:
                time.sleep(0.1)
                
    def run_command(self, command, description=""):
        """Run a command and return result"""
        if description:
            self.log(f"Running: {description}")
            
        try:
            result = subprocess.run(command, shell=True, capture_output=True, 
                                  text=True, timeout=120)
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            self.log("Command timed out", "ERROR")
            return False, "", "Command timed out"
        except Exception as e:
            self.log(f"Command error: {str(e)}", "ERROR")
            return False, "", str(e)
            
    def start_server(self):
        """Start RAM sharing server"""
        if self.current_action:
            self.log("Another action is in progress", "WARNING")
            return
            
        self.current_action = "start_server"
        
        def run_server():
            try:
                self.log("Starting RAM sharing server...")
                
                script_path = "Robust_RAM_Sharing.ps1"
                command = f'powershell -ExecutionPolicy Bypass -File "{script_path}" -Action setup -RAMSizeGB 4 -DriveLetter R'
                
                success, stdout, stderr = self.run_command(command, "RAM Server Setup")
                
                if success:
                    self.log("Server started successfully", "SUCCESS")
                    self.log("RAM disk created and shared")
                    self.log("Available at: \\\\192.168.1.186\\RamDisk")
                else:
                    self.log(f"Server start failed: {stderr}", "ERROR")
                    
            except Exception as e:
                self.log(f"Error starting server: {str(e)}", "ERROR")
            finally:
                self.current_action = None
                
        threading.Thread(target=run_server, daemon=True).start()
        
    def connect_to_server(self):
        """Connect to RAM sharing server"""
        if self.current_action:
            self.log("Another action is in progress", "WARNING")
            return
            
        self.current_action = "connect"
        
        def connect():
            try:
                self.log("Connecting to RAM server...")
                
                script_path = "Robust_RAM_Sharing.ps1"
                command = f'powershell -ExecutionPolicy Bypass -File "{script_path}" -Action map -TargetIP 192.168.1.186'
                
                success, stdout, stderr = self.run_command(command, "Connect to Server")
                
                if success:
                    self.log("Connected successfully", "SUCCESS")
                    self.log("RAM disk mapped and ready to use")
                else:
                    self.log(f"Connection failed: {stderr}", "ERROR")
                    
            except Exception as e:
                self.log(f"Error connecting: {str(e)}", "ERROR")
            finally:
                self.current_action = None
                
        threading.Thread(target=connect, daemon=True).start()
        
    def stop_server(self):
        """Stop server and disconnect"""
        if self.current_action:
            self.log("Another action is in progress", "WARNING")
            return
            
        self.current_action = "stop"
        
        def stop():
            try:
                self.log("Stopping server/cleanup...")
                
                script_path = "Robust_RAM_Sharing.ps1"
                command = f'powershell -ExecutionPolicy Bypass -File "{script_path}" -Action cleanup'
                
                success, stdout, stderr = self.run_command(command, "Cleanup")
                
                if success:
                    self.log("Cleanup completed", "SUCCESS")
                else:
                    self.log(f"Cleanup failed: {stderr}", "ERROR")
                    
            except Exception as e:
                self.log(f"Error during cleanup: {str(e)}", "ERROR")
            finally:
                self.current_action = None
                
        threading.Thread(target=stop, daemon=True).start()
        
    def test_performance(self):
        """Test RAM sharing performance"""
        if self.current_action:
            self.log("Another action is in progress", "WARNING")
            return
            
        self.current_action = "test_perf"
        
        def test():
            try:
                self.log("Testing performance...")
                
                script_path = "Robust_RAM_Sharing.ps1"
                command = f'powershell -ExecutionPolicy Bypass -File "{script_path}" -Action test -DriveLetter R'
                
                success, stdout, stderr = self.run_command(command, "Performance Test")
                
                if success:
                    self.log("Performance test completed", "SUCCESS")
                    # Parse and display results
                    lines = stdout.split('\n')
                    for line in lines:
                        if 'Write:' in line or 'Read:' in line or 'MB/s' in line:
                            print(f"  {line.strip()}")
                else:
                    self.log(f"Performance test failed: {stderr}", "ERROR")
                    
            except Exception as e:
                self.log(f"Error testing performance: {str(e)}", "ERROR")
            finally:
                self.current_action = None
                
        threading.Thread(target=test, daemon=True).start()
        
    def fix_compatibility(self):
        """Fix Windows compatibility issues"""
        if self.current_action:
            self.log("Another action is in progress", "WARNING")
            return
            
        self.current_action = "compat_fix"
        
        def fix():
            try:
                self.log("Fixing Windows compatibility...")
                
                script_path = "Windows_Compatibility_Fix.ps1"
                command = f'powershell -ExecutionPolicy Bypass -File "{script_path}" -Action fix'
                
                success, stdout, stderr = self.run_command(command, "Compatibility Fix")
                
                if success:
                    self.log("Compatibility fixes applied", "SUCCESS")
                else:
                    self.log(f"Compatibility fix failed: {stderr}", "ERROR")
                    
            except Exception as e:
                self.log(f"Error fixing compatibility: {str(e)}", "ERROR")
            finally:
                self.current_action = None
                
        threading.Thread(target=fix, daemon=True).start()
        
    def show_status(self):
        """Show current status"""
        self.print_header()
        print("SYSTEM STATUS:")
        print()
        
        # Check if RAM disk exists
        success, _, _ = self.run_command('dir R:\ 2>nul', "Check RAM disk")
        if success:
            print("✅ RAM Disk: Available (R:)")
        else:
            print("❌ RAM Disk: Not found")
            
        # Check network connectivity
        success, _, _ = self.run_command('ping -n 1 192.168.1.132', "Ping client")
        if success:
            print("✅ Network: Client PC reachable")
        else:
            print("❌ Network: Client PC not reachable")
            
        # Check SMB share
        success, _, _ = self.run_command('net share | findstr RamDisk', "Check SMB share")
        if success:
            print("✅ SMB Share: Active")
        else:
            print("❌ SMB Share: Not found")
            
        print()
        print("Press Enter to return to menu...")
        input()
        
    def cleanup_all(self):
        """Clean up all components"""
        if self.current_action:
            self.log("Another action is in progress", "WARNING")
            return
            
        # Ask for confirmation
        self.print_header()
        print("⚠️  CLEANUP ALL COMPONENTS")
        print()
        print("This will:")
        print("- Stop RAM sharing server")
        print("- Remove all network shares")
        print("- Disconnect client connections")
        print("- Remove RAM disk")
        print()
        confirm = input("Are you sure? (y/N): ").lower().strip()
        
        if confirm == 'y':
            self.stop_server()
        else:
            self.log("Cleanup cancelled", "INFO")
            
    def run(self):
        """Main GUI loop"""
        while self.running:
            try:
                self.print_header()
                self.print_menu()
                
                if self.current_action:
                    print("⏳ Action in progress...")
                    time.sleep(1)
                    continue
                    
                choice = input("Select option (1-8): ").strip()
                
                if choice == "1":
                    self.start_server()
                    self.wait_for_action()
                elif choice == "2":
                    self.connect_to_server()
                    self.wait_for_action()
                elif choice == "3":
                    self.stop_server()
                    self.wait_for_action()
                elif choice == "4":
                    self.test_performance()
                    self.wait_for_action()
                elif choice == "5":
                    self.fix_compatibility()
                    self.wait_for_action()
                elif choice == "6":
                    self.show_status()
                elif choice == "7":
                    self.cleanup_all()
                    self.wait_for_action()
                elif choice == "8":
                    self.running = False
                else:
                    self.log("Invalid option", "WARNING")
                    time.sleep(1)
                    
            except KeyboardInterrupt:
                self.running = False
            except Exception as e:
                self.log(f"Error: {str(e)}", "ERROR")
                time.sleep(2)
                
        self.log("RAM Sharing Manager closed", "INFO")

def main():
    """Main entry point"""
    try:
        app = SimpleRAMSharingGUI()
        app.run()
    except KeyboardInterrupt:
        print("\nGoodbye!")
    except Exception as e:
        print(f"Fatal error: {e}")

if __name__ == "__main__":
    main()
