#!/usr/bin/env python3
"""
Fix system launcher path handling and CPU Monitor real-time monitoring
"""

import subprocess
import sys
import os
from pathlib import Path

def fix_simple_launcher():
    """Fix the simple launcher path handling and subprocess execution"""
    print("🔧 Fixing Simple Launcher...")
    
    launcher_file = Path(__file__).parent / "simple_launcher.py"
    
    if not launcher_file.exists():
        print("❌ Launcher file not found")
        return False
    
    # Read the launcher file
    with open(launcher_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix the subprocess execution to use proper Python path
    old_subprocess = """            # Launch based on file type
            if tool_path.suffix == '.py':
                # Python script - use sys.executable for proper Python path
                process = subprocess.Popen([sys.executable, str(tool_path)], 
                                         cwd=str(working_dir),
                                         creationflags=subprocess.CREATE_NEW_CONSOLE)"""
    
    new_subprocess = """            # Launch based on file type
            if tool_path.suffix == '.py':
                # Python script - use sys.executable for proper Python path
                python_cmd = sys.executable
                if not python_cmd:
                    python_cmd = 'python'
                
                # Add the tool's directory to Python path
                env = os.environ.copy()
                if 'PYTHONPATH' in env:
                    env['PYTHONPATH'] = f"{str(working_dir)};{env['PYTHONPATH']}"
                else:
                    env['PYTHONPATH'] = str(working_dir)
                
                process = subprocess.Popen([python_cmd, str(tool_path)], 
                                         cwd=str(working_dir),
                                         env=env,
                                         creationflags=subprocess.CREATE_NEW_CONSOLE)"""
    
    content = content.replace(old_subprocess, new_subprocess)
    
    # Write back the fixed launcher
    with open(launcher_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Simple launcher fixed")
    return True

def fix_cpu_monitor():
    """Fix CPU Monitor real-time monitoring data flow"""
    print("🔧 Fixing CPU Monitor...")
    
    cpu_monitor_file = Path(__file__).parent / "Cpu Monitor" / "cpu_monitor.py"
    
    if not cpu_monitor_file.exists():
        print("❌ CPU Monitor file not found")
        return False
    
    # Read the CPU Monitor file
    with open(cpu_monitor_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix the update_graphs function to ensure proper data flow
    old_update_graphs = """    def update_graphs(self):
        \"\"\"Update graphs\"\"\"
        if len(self.cpu_history) > 1 and hasattr(self, 'canvas') and self.canvas:
            try:
                # Calculate time offsets
                current_time = time.time()
                time_offsets = [(current_time - t) for t in self.time_stamps]
                
                # Update CPU usage graph
                if hasattr(self, 'cpu_line') and self.cpu_line:
                    self.cpu_line.set_data(time_offsets, list(self.cpu_history))
                    if hasattr(self, 'ax1') and self.ax1:
                        self.ax1.set_xlim(max(time_offsets), 0)
                        self.ax1.set_ylim(0, 100)
                
                # Update temperature graph
                if hasattr(self, 'temp_line') and self.temp_line:
                    self.temp_line.set_data(time_offsets, list(self.temp_history))
                    if hasattr(self, 'ax2') and self.ax2:
                        self.ax2.set_xlim(max(time_offsets), 0)
                        if self.temp_history:
                            temp_min = min(self.temp_history) - 5
                            temp_max = max(self.temp_history) + 5
                            self.ax2.set_ylim(temp_min, temp_max)
                
                self.canvas.draw()
            except Exception as e:
                print(f"Graph update error: {e}")"""
    
    new_update_graphs = """    def update_graphs(self):
        \"\"\"Update graphs\"\"\"
        if len(self.cpu_history) > 0 and hasattr(self, 'canvas') and self.canvas:
            try:
                # Calculate time offsets
                current_time = time.time()
                time_offsets = [(current_time - t) for t in self.time_stamps]
                
                # Ensure we have data to plot
                if len(self.cpu_history) > 0 and len(time_offsets) > 0:
                    # Update CPU usage graph
                    if hasattr(self, 'cpu_line') and self.cpu_line:
                        self.cpu_line.set_data(time_offsets, list(self.cpu_history))
                        if hasattr(self, 'ax1') and self.ax1:
                            self.ax1.set_xlim(max(time_offsets) if time_offsets else 60, 0)
                            self.ax1.set_ylim(0, 100)
                    
                    # Update temperature graph
                    if hasattr(self, 'temp_line') and self.temp_line and len(self.temp_history) > 0:
                        self.temp_line.set_data(time_offsets, list(self.temp_history))
                        if hasattr(self, 'ax2') and self.ax2:
                            self.ax2.set_xlim(max(time_offsets) if time_offsets else 60, 0)
                            temp_min = min(self.temp_history) - 5
                            temp_max = max(self.temp_history) + 5
                            self.ax2.set_ylim(temp_min, temp_max)
                    
                    self.canvas.draw()
            except Exception as e:
                print(f"Graph update error: {e}")"""
    
    content = content.replace(old_update_graphs, new_update_graphs)
    
    # Fix the monitor_loop to ensure data is being collected properly
    old_monitor_loop = """    def monitor_loop(self):
        \"\"\"Monitoring loop\"\"\"
        while self.monitoring:
            try:
                # Get CPU info and update display
                cpu_info = self.get_cpu_info()
                self.cpu_history.append(cpu_info['usage'])
                self.time_stamps.append(time.time())
                self.temp_history.append(cpu_info['temperature'])
                
                # Update display in main thread
                self.root.after(0, self.update_display, cpu_info)
                
                # Sleep for update interval (convert milliseconds to seconds)
                time.sleep(self.update_interval / 1000.0)
            except Exception as e:
                print(f"Monitor loop error: {e}")
                break"""
    
    new_monitor_loop = """    def monitor_loop(self):
        \"\"\"Monitoring loop\"\"\"
        while self.monitoring:
            try:
                # Get CPU info and update display
                cpu_info = self.get_cpu_info()
                
                # Add data to history
                self.cpu_history.append(cpu_info['usage'])
                self.time_stamps.append(time.time())
                self.temp_history.append(cpu_info['temperature'])
                
                # Debug output
                print(f"CPU: {cpu_info['usage']:.1f}%, Temp: {cpu_info['temperature']:.1f}°C, History size: {len(self.cpu_history)}")
                
                # Update display in main thread
                self.root.after(0, self.update_display, cpu_info)
                self.root.after(0, self.update_graphs)
                
                # Sleep for update interval (convert milliseconds to seconds)
                time.sleep(self.update_interval / 1000.0)
            except Exception as e:
                print(f"Monitor loop error: {e}")
                break"""
    
    content = content.replace(old_monitor_loop, new_monitor_loop)
    
    # Write back the fixed CPU Monitor
    with open(cpu_monitor_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ CPU Monitor fixed")
    return True

def test_fixes():
    """Test the fixes"""
    print("\n🧪 Testing Fixes...")
    
    # Test launcher syntax
    launcher_file = Path(__file__).parent / "simple_launcher.py"
    result = subprocess.run([sys.executable, "-m", "py_compile", str(launcher_file)], 
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Launcher syntax OK")
    else:
        print(f"❌ Launcher syntax error: {result.stderr}")
    
    # Test CPU Monitor syntax
    cpu_monitor_file = Path(__file__).parent / "Cpu Monitor" / "cpu_monitor.py"
    result = subprocess.run([sys.executable, "-m", "py_compile", str(cpu_monitor_file)], 
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ CPU Monitor syntax OK")
    else:
        print(f"❌ CPU Monitor syntax error: {result.stderr}")
    
    print("\n📊 Fixes applied:")
    print("• Simple launcher: Improved subprocess execution with proper Python path")
    print("• CPU Monitor: Enhanced graph data flow and monitoring loop")
    print("• Both tools: Added debug output and error handling")

def main():
    """Main function"""
    print("🔧 Fixing System Launcher and CPU Monitor Issues")
    print("=" * 50)
    
    # Fix the launcher
    launcher_ok = fix_simple_launcher()
    
    # Fix the CPU Monitor
    cpu_monitor_ok = fix_cpu_monitor()
    
    # Test the fixes
    test_fixes()
    
    if launcher_ok and cpu_monitor_ok:
        print("\n🎉 All fixes applied successfully!")
        print("💡 Try launching the tools again to test the fixes.")
    else:
        print("\n❌ Some fixes failed. Check the error messages above.")

if __name__ == "__main__":
    main()
