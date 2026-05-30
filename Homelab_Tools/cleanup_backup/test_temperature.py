#!/usr/bin/env python3
"""
Test CPU Temperature Detection
Quick test to verify temperature monitoring works
"""

import psutil
import platform
import subprocess
import wmi

def test_temperature_detection():
    """Test different temperature detection methods"""
    print("🌡️  Testing CPU Temperature Detection")
    print("=" * 50)
    
    print(f"Platform: {platform.system()}")
    print(f"Python: {platform.python_version()}")
    print()
    
    # Test 1: WMI Method
    print("📊 Method 1: WMI Detection")
    try:
        c = wmi.WMI()
        
        # Try different temperature sensors
        found_temp = False
        for sensor_class in ['Win32_TemperatureProbe', 'MSAcpi_ThermalZoneTemperature']:
            try:
                print(f"  Trying {sensor_class}...")
                if sensor_class == 'MSAcpi_ThermalZoneTemperature':
                    temps = c.query(f"SELECT * FROM {sensor_class}")
                    for temp in temps:
                        if hasattr(temp, 'CurrentTemperature') and temp.CurrentTemperature:
                            celsius = (temp.CurrentTemperature - 2732) / 10.0
                            print(f"  ✅ Temperature: {celsius:.1f}°C")
                            found_temp = True
                            break
                else:
                    temps = c.Win32_TemperatureProbe()
                    for temp in temps:
                        if hasattr(temp, 'CurrentReading') and temp.CurrentReading:
                            celsius = temp.CurrentReading / 10.0
                            print(f"  ✅ Temperature: {celsius:.1f}°C")
                            found_temp = True
                            break
            except Exception as e:
                print(f"  ❌ {sensor_class} failed: {e}")
                continue
            
            if found_temp:
                break
        
        if not found_temp:
            print("  ⚠️  No temperature sensors found via WMI")
    except Exception as e:
        print(f"  ❌ WMI failed: {e}")
    
    print()
    
    # Test 2: PowerShell Method
    print("📊 Method 2: PowerShell Detection")
    try:
        ps_commands = [
            'Get-WmiObject MSAcpi_ThermalZoneTemperature -Namespace "root/wmi" | Where-Object {$_.CurrentTemperature -ne 0} | Select-Object -First 1 | ForEach-Object {($_.CurrentTemperature - 2732) / 10.0}',
            'Get-WmiObject Win32_TemperatureProbe | Where-Object {$_.CurrentReading -ne 0} | Select-Object -First 1 | ForEach-Object {$_.CurrentReading / 10.0}'
        ]
        
        for i, cmd in enumerate(ps_commands, 1):
            try:
                print(f"  Command {i}: {cmd[:50]}...")
                result = subprocess.run(['powershell', '-Command', cmd], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0 and result.stdout.strip():
                    temp_value = result.stdout.strip()
                    try:
                        temp = float(temp_value)
                        if 0 < temp < 150:
                            print(f"  ✅ Temperature: {temp:.1f}°C")
                            break
                        else:
                            print(f"  ⚠️  Invalid temperature: {temp}")
                    except ValueError:
                        print(f"  ⚠️  Could not parse temperature: {temp_value}")
                else:
                    print(f"  ❌ Command failed")
            except Exception as e:
                print(f"  ❌ PowerShell failed: {e}")
    except Exception as e:
        print(f"  ❌ PowerShell method failed: {e}")
    
    print()
    
    # Test 3: psutil sensors
    print("📊 Method 3: psutil Sensors")
    try:
        temps = psutil.sensors_temperatures()
        if temps:
            print(f"  Found {len(temps)} temperature sensor groups:")
            for name, entries in temps.items():
                print(f"    {name}: {len(entries)} entries")
                if any(keyword in name.lower() for keyword in ['core', 'cpu', 'package', 'tdie', 'tctl']):
                    for entry in entries:
                        if hasattr(entry, 'current') and entry.current > 0:
                            print(f"  ✅ CPU Temperature: {entry.current:.1f}°C")
                            break
        else:
            print("  ⚠️  No temperature sensors found via psutil")
    except Exception as e:
        print(f"  ❌ psutil sensors failed: {e}")
    
    print()
    
    # Test 4: CPU Info
    print("📊 CPU Information")
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_freq = psutil.cpu_freq()
        cpu_count = psutil.cpu_count()
        
        print(f"  CPU Usage: {cpu_percent:.1f}%")
        print(f"  CPU Cores: {cpu_count}")
        if cpu_freq:
            print(f"  CPU Frequency: {cpu_freq.current:.0f} MHz")
        
        # Estimated temperature based on usage
        estimated_temp = 30 + (cpu_percent * 0.4)
        print(f"  Estimated Temperature: {estimated_temp:.1f}°C")
        
    except Exception as e:
        print(f"  ❌ CPU info failed: {e}")
    
    print()
    print("🎯 Temperature Detection Test Complete!")

if __name__ == "__main__":
    test_temperature_detection()
