#!/usr/bin/env python3
"""
Test Per-Core Temperature Detection
Test individual core temperature estimation for 12-core CPU
"""

import psutil
import platform
import subprocess
import wmi

def test_per_core_temperatures():
    """Test per-core temperature detection"""
    print("🌡️  Testing Per-Core Temperature Detection")
    print("=" * 50)
    
    # Get CPU info
    cpu_count = psutil.cpu_count()
    logical_count = psutil.cpu_count(logical=True)
    print(f"Physical Cores: {cpu_count}")
    print(f"Logical Cores: {logical_count}")
    print()
    
    # Test per-core usage
    print("📊 Per-Core Usage Analysis")
    try:
        core_usage = psutil.cpu_percent(interval=1, percpu=True)
        print(f"Found {len(core_usage)} core readings")
        
        for i, usage in enumerate(core_usage):
            print(f"  Core {i}: {usage:.1f}%")
            
            # Estimate temperature for this core
            base_temp = 35  # Base idle temperature
            usage_factor = 0.5  # Temperature increase per % usage
            core_offset = (i % 4) * 2  # Heat distribution offset
            
            core_temp = base_temp + (usage * usage_factor) + core_offset
            core_temp = min(max(core_temp, 30), 95)  # Clamp to reasonable range
            
            print(f"    Est. Temp: {core_temp:.1f}°C")
            
            # Temperature status
            if core_temp < 50:
                status = "Cool"
            elif core_temp < 70:
                status = "Normal"
            elif core_temp < 85:
                status = "Warm"
            else:
                status = "Hot"
            
            print(f"    Status: {status}")
        
        # Calculate average temperature
        avg_temp = sum([
            35 + (usage * 0.5) + ((i % 4) * 2)
            for i, usage in enumerate(core_usage)
        ]) / len(core_usage)
        
        print(f"\n🎯 Average CPU Temperature: {avg_temp:.1f}°C")
        
        # Hottest and coolest cores
        core_temps = [
            35 + (usage * 0.5) + ((i % 4) * 2)
            for i, usage in enumerate(core_usage)
        ]
        
        hottest_core = core_temps.index(max(core_temps))
        coolest_core = core_temps.index(min(core_temps))
        
        print(f"🔥 Hottest Core: {hottest_core} at {max(core_temps):.1f}°C")
        print(f"❄️  Coolest Core: {coolest_core} at {min(core_temps):.1f}°C")
        
        # Temperature distribution
        temp_ranges = {
            'Cool (30-50°C)': sum(1 for t in core_temps if t < 50),
            'Normal (50-70°C)': sum(1 for t in core_temps if 50 <= t < 70),
            'Warm (70-85°C)': sum(1 for t in core_temps if 70 <= t < 85),
            'Hot (85°C+)': sum(1 for t in core_temps if t >= 85)
        }
        
        print(f"\n📈 Temperature Distribution:")
        for range_name, count in temp_ranges.items():
            percentage = (count / len(core_temps)) * 100
            print(f"  {range_name}: {count} cores ({percentage:.1f}%)")
        
    except Exception as e:
        print(f"❌ Per-core analysis failed: {e}")
    
    print()
    
    # Test overall CPU info
    print("📊 Overall CPU Information")
    try:
        cpu_freq = psutil.cpu_freq()
        overall_usage = psutil.cpu_percent(interval=1)
        
        print(f"Overall Usage: {overall_usage:.1f}%")
        if cpu_freq:
            print(f"Current Frequency: {cpu_freq.current:.0f} MHz")
            print(f"Min/Max Frequency: {cpu_freq.min:.0f} - {cpu_freq.max:.0f} MHz")
        
        # Better overall temperature estimate
        idle_temp = 35
        load_temp = 75
        estimated_temp = idle_temp + (overall_usage / 100.0) * (load_temp - idle_temp)
        print(f"Overall Temperature: {estimated_temp:.1f}°C")
        
    except Exception as e:
        print(f"❌ CPU info failed: {e}")
    
    print()
    
    # Test thermal zones (if available)
    print("📊 Thermal Zone Information")
    try:
        if platform.system() == "Windows":
            c = wmi.WMI()
            
            # Try to get thermal zones
            try:
                thermal_zones = c.MSAcpi_ThermalZoneTemperature()
                print(f"Found {len(thermal_zones)} thermal zones")
                
                for i, zone in enumerate(thermal_zones):
                    if hasattr(zone, 'CurrentTemperature') and zone.CurrentTemperature:
                        celsius = (zone.CurrentTemperature - 2732) / 10.0
                        print(f"  Zone {i}: {celsius:.1f}°C")
                    else:
                        print(f"  Zone {i}: No temperature data")
            except Exception as e:
                print(f"  Thermal zones not accessible: {e}")
        
    except Exception as e:
        print(f"❌ Thermal zone test failed: {e}")
    
    print()
    print("🎯 Per-Core Temperature Test Complete!")

if __name__ == "__main__":
    test_per_core_temperatures()
