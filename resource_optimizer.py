#!/usr/bin/env python3
"""
Windows 11 Resource Sharing Optimization Algorithm
Advanced abstraction layer for intelligent resource management and allocation.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import psutil
import threading
import time
import gc
import os
import subprocess
import platform
from datetime import datetime
import json
import math
from collections import deque
import numpy as np
import sys
import pystray
from PIL import Image, ImageDraw

# Import monitoring modules
try:
    import GPUtil
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False

try:
    import nvidia_ml_py3 as nvml
    NVML_AVAILABLE = True
    try:
        nvml.nvmlInit()
    except:
        NVML_AVAILABLE = False
        nvml = None
except ImportError:
    NVML_AVAILABLE = False
    nvml = None

try:
    import wmi
    WMI_AVAILABLE = True
except ImportError:
    WMI_AVAILABLE = False

class ResourceOptimizer:
    """Advanced Windows 11 Resource Sharing Optimization Algorithm"""
    
    def __init__(self):
        self.optimization_active = False
        self.monitoring_thread = None
        self.resource_history = deque(maxlen=300)  # 5 minutes at 1-second intervals
        
        # Resource allocation weights
        self.allocation_weights = {
            'gaming': {'cpu': 0.7, 'gpu': 0.8, 'ram': 0.6, 'io': 0.5},
            'productivity': {'cpu': 0.5, 'gpu': 0.3, 'ram': 0.7, 'io': 0.6},
            'multimedia': {'cpu': 0.4, 'gpu': 0.6, 'ram': 0.5, 'io': 0.7},
            'development': {'cpu': 0.6, 'gpu': 0.4, 'ram': 0.8, 'io': 0.5},
            'balanced': {'cpu': 0.5, 'gpu': 0.5, 'ram': 0.5, 'io': 0.5}
        }
        
        # Windows 11 specific optimization parameters
        self.win11_params = {
            'memory_compression': True,
            'standby_list_optimization': True,
            'process_priority_boost': True,
            'io_priority_adjustment': True,
            'cpu_affinity_optimization': True,
            'gpu_scheduler_tuning': True,
            'network_priority_optimization': True
        }
        
        # Resource thresholds
        self.thresholds = {
            'cpu_high': 80.0,
            'cpu_critical': 95.0,
            'ram_high': 85.0,
            'ram_critical': 95.0,
            'gpu_high': 85.0,
            'gpu_critical': 95.0,
            'io_high': 80.0,
            'io_critical': 95.0
        }
        
        # Process classification
        self.process_classes = {
            'critical': ['system', 'csrss', 'winlogon', 'services', 'lsass'],
            'gaming': ['steam', 'epicgameslauncher', 'origin', 'uplay', 'battle.net'],
            'productivity': ['chrome', 'firefox', 'msedge', 'office', 'winword', 'excel'],
            'multimedia': ['vlc', 'mpc', 'spotify', 'itunes', 'photoshop'],
            'development': ['code', 'python', 'node', 'java', 'docker'],
            'background': ['onedrive', 'dropbox', 'googledrive', 'discord', 'slack']
        }
        
        self.current_profile = 'balanced'
        self.optimization_level = 'adaptive'
        
    def get_resource_snapshot(self):
        """Get comprehensive resource snapshot"""
        try:
            snapshot = {
                'timestamp': time.time(),
                'cpu': {
                    'usage': psutil.cpu_percent(interval=None),  # Faster - no blocking
                    'freq': psutil.cpu_freq().current if psutil.cpu_freq() else 0,
                    'temp': self.get_cpu_temperature(),
                    'load_avg': psutil.getloadavg()[0] if hasattr(psutil, 'getloadavg') else 0,
                    'processes': self.get_cpu_processes()
                },
                'memory': {
                    'usage': psutil.virtual_memory().percent,
                    'available': psutil.virtual_memory().available / (1024**3),
                    'swap': psutil.swap_memory().percent if psutil.swap_memory() else 0,
                    'standby': self.get_standby_memory(),
                    'compressed': self.get_compressed_memory()
                },
                'gpu': {
                    'usage': self.get_gpu_usage(),
                    'memory': self.get_gpu_memory(),
                    'temp': self.get_gpu_temperature(),
                    'freq': self.get_gpu_frequency(),
                    'processes': self.get_gpu_processes()
                },
                'disk': {
                    'usage': self.get_disk_usage(),
                    'io': self.get_disk_io(),
                    'queue_length': self.get_disk_queue_length()
                },
                'network': {
                    'io': self.get_network_io(),
                    'latency': self.get_network_latency()
                }
            }
            
            self.resource_history.append(snapshot)
            return snapshot
            
        except Exception as e:
            print(f"Error getting resource snapshot: {e}")
            return None
    
    def get_cpu_temperature(self):
        """Get CPU temperature"""
        try:
            if WMI_AVAILABLE:
                c = wmi.WMI()
                for temp in c.Win32_TemperatureProbe():
                    if temp.CurrentTemperature:
                        return temp.CurrentTemperature - 273.15
            return 0.0
        except:
            return 0.0
    
    def get_gpu_usage(self):
        """Get GPU usage"""
        try:
            if NVML_AVAILABLE and self.gpu_count > 0:
                handle = nvml.nvmlDeviceGetHandleByIndex(0)
                util = nvml.nvmlDeviceGetUtilizationRates(handle)
                return util.gpu
            elif GPU_AVAILABLE:
                gpus = GPUtil.getGPUs()
                if gpus:
                    return gpus[0].load * 100
            return 0.0
        except:
            return 0.0
    
    def get_gpu_memory(self):
        """Get GPU memory usage"""
        try:
            if NVML_AVAILABLE and self.gpu_count > 0:
                handle = nvml.nvmlDeviceGetHandleByIndex(0)
                mem_info = nvml.nvmlDeviceGetMemoryInfo(handle)
                return (mem_info.used / mem_info.total) * 100
            elif GPU_AVAILABLE:
                gpus = GPUtil.getGPUs()
                if gpus:
                    return gpus[0].memoryUtil * 100
            return 0.0
        except:
            return 0.0
    
    def get_gpu_temperature(self):
        """Get GPU temperature"""
        try:
            if NVML_AVAILABLE and self.gpu_count > 0:
                handle = nvml.nvmlDeviceGetHandleByIndex(0)
                return nvml.nvmlDeviceGetTemperature(handle, nvml.NVML_TEMPERATURE_GPU)
            elif GPU_AVAILABLE:
                gpus = GPUtil.getGPUs()
                if gpus:
                    return gpus[0].temperature
            return 0.0
        except:
            return 0.0
    
    def get_gpu_frequency(self):
        """Get GPU frequency"""
        try:
            if NVML_AVAILABLE and self.gpu_count > 0:
                handle = nvml.nvmlDeviceGetHandleByIndex(0)
                return nvml.nvmlDeviceGetClockInfo(handle, nvml.NVML_GRAPHICS_CLOCK) / 1000
            return 0.0
        except:
            return 0.0
    
    def get_standby_memory(self):
        """Get standby memory usage"""
        try:
            if platform.system() == "Windows":
                result = subprocess.run(['powershell', '-Command', 
                                      '(Get-Counter -Counter "\\Memory\\Standby Cache Reserve Bytes").CounterSamples.CookedValue'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    standby_bytes = float(result.stdout.strip())
                    return standby_bytes / (1024**3)  # Convert to GB
            return 0.0
        except:
            return 0.0
    
    def get_compressed_memory(self):
        """Get compressed memory usage"""
        try:
            if platform.system() == "Windows":
                result = subprocess.run(['powershell', '-Command', 
                                      '(Get-Counter -Counter "\\Memory\\Compressed Bytes").CounterSamples.CookedValue'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    compressed_bytes = float(result.stdout.strip())
                    return compressed_bytes / (1024**3)  # Convert to GB
            return 0.0
        except:
            return 0.0
    
    def get_disk_usage(self):
        """Get disk usage"""
        try:
            disk_usage = {}
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_usage[partition.device] = {
                        'used_percent': (usage.used / usage.total) * 100,
                        'free_gb': usage.free / (1024**3)
                    }
                except:
                    continue
            return disk_usage
        except:
            return {}
    
    def get_disk_io(self):
        """Get disk I/O statistics"""
        try:
            io = psutil.disk_io_counters()
            return {
                'read_mb': io.read_bytes / (1024**2),
                'write_mb': io.write_bytes / (1024**2),
                'read_ops': io.read_count,
                'write_ops': io.write_count
            }
        except:
            return {}
    
    def get_disk_queue_length(self):
        """Get disk queue length"""
        try:
            if platform.system() == "Windows":
                result = subprocess.run(['powershell', '-Command', 
                                      '(Get-Counter -Counter "\\PhysicalDisk(_Total)\\Avg. Disk Queue Length").CounterSamples.CookedValue'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    return float(result.stdout.strip())
            return 0.0
        except:
            return 0.0
    
    def get_network_io(self):
        """Get network I/O statistics"""
        try:
            io = psutil.net_io_counters()
            return {
                'sent_mb': io.bytes_sent / (1024**2),
                'recv_mb': io.bytes_recv / (1024**2),
                'packets_sent': io.packets_sent,
                'packets_recv': io.packets_recv
            }
        except:
            return {}
    
    def get_network_latency(self):
        """Get network latency"""
        try:
            import socket
            start_time = time.time()
            socket.create_connection(("8.8.8.8", 53), timeout=2).close()
            return (time.time() - start_time) * 1000  # Convert to ms
        except:
            return 0.0
    
    def get_cpu_processes(self):
        """Get CPU-intensive processes"""
        processes = []
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    pinfo = proc.info
                    if pinfo['cpu_percent'] > 5:  # Only include processes using >5% CPU
                        processes.append({
                            'pid': pinfo['pid'],
                            'name': pinfo['name'],
                            'cpu': pinfo['cpu_percent'],
                            'memory': pinfo['memory_percent'],
                            'class': self.classify_process(pinfo['name'])
                        })
                except:
                    continue
            return sorted(processes, key=lambda x: x['cpu'], reverse=True)[:10]
        except:
            return []
    
    def get_gpu_processes(self):
        """Get GPU-intensive processes"""
        processes = []
        try:
            if NVML_AVAILABLE and self.gpu_count > 0:
                handle = nvml.nvmlDeviceGetHandleByIndex(0)
                procs = nvml.nvmlDeviceGetGraphicsRunningProcesses(handle)
                for proc in procs:
                    try:
                        ps_proc = psutil.Process(proc.pid)
                        processes.append({
                            'pid': proc.pid,
                            'name': ps_proc.name(),
                            'memory_mb': proc.usedGpuMemory / (1024**2),
                            'class': self.classify_process(ps_proc.name())
                        })
                    except:
                        continue
            return sorted(processes, key=lambda x: x['memory_mb'], reverse=True)[:10]
        except:
            return []
    
    def classify_process(self, process_name):
        """Classify process by type"""
        process_name = process_name.lower()
        
        for class_name, processes in self.process_classes.items():
            for proc in processes:
                if proc in process_name:
                    return class_name
        
        return 'unknown'
    
    def analyze_resource_patterns(self):
        """Analyze resource usage patterns"""
        if len(self.resource_history) < 10:
            return None
        
        recent_data = list(self.resource_history)[-60:]  # Last 60 seconds
        
        patterns = {
            'cpu_trend': self.calculate_trend([d['cpu']['usage'] for d in recent_data]),
            'memory_trend': self.calculate_trend([d['memory']['usage'] for d in recent_data]),
            'gpu_trend': self.calculate_trend([d['gpu']['usage'] for d in recent_data]),
            'io_trend': self.calculate_trend([d['disk']['io'].get('read_mb', 0) + d['disk']['io'].get('write_mb', 0) for d in recent_data]),
            'volatility': self.calculate_volatility(recent_data),
            'bottlenecks': self.identify_bottlenecks(recent_data)
        }
        
        return patterns
    
    def calculate_trend(self, values):
        """Calculate trend direction and slope"""
        if len(values) < 2:
            return 0.0
        
        x = np.arange(len(values))
        y = np.array(values)
        
        # Linear regression
        slope = np.polyfit(x, y, 1)[0]
        
        return slope
    
    def calculate_volatility(self, data):
        """Calculate resource volatility"""
        volatility = {}
        
        for resource in ['cpu', 'memory', 'gpu']:
            values = [d[resource]['usage'] for d in data]
            volatility[resource] = np.std(values) if values else 0.0
        
        return volatility
    
    def identify_bottlenecks(self, data):
        """Identify resource bottlenecks"""
        bottlenecks = []
        
        for d in data:
            if d['cpu']['usage'] > self.thresholds['cpu_high']:
                bottlenecks.append({'type': 'cpu', 'severity': 'high' if d['cpu']['usage'] > self.thresholds['cpu_critical'] else 'medium'})
            
            if d['memory']['usage'] > self.thresholds['ram_high']:
                bottlenecks.append({'type': 'memory', 'severity': 'high' if d['memory']['usage'] > self.thresholds['ram_critical'] else 'medium'})
            
            if d['gpu']['usage'] > self.thresholds['gpu_high']:
                bottlenecks.append({'type': 'gpu', 'severity': 'high' if d['gpu']['usage'] > self.thresholds['gpu_critical'] else 'medium'})
        
        return bottlenecks
    
    def optimize_resource_allocation(self, profile=None):
        """Optimize resource allocation based on profile and patterns"""
        if profile:
            self.current_profile = profile
        
        patterns = self.analyze_resource_patterns()
        if not patterns:
            return False
        
        # Calculate optimal allocation
        weights = self.allocation_weights[self.current_profile]
        
        # Apply Windows 11 specific optimizations
        optimizations = []
        
        # CPU optimization
        if patterns['cpu_trend'] > 0.5:  # Increasing CPU usage
            optimizations.append(self.optimize_cpu_allocation(weights['cpu']))
        
        # Memory optimization
        if patterns['memory_trend'] > 0.5:  # Increasing memory usage
            optimizations.append(self.optimize_memory_allocation(weights['ram']))
        
        # GPU optimization
        if patterns['gpu_trend'] > 0.5:  # Increasing GPU usage
            optimizations.append(self.optimize_gpu_allocation(weights['gpu']))
        
        # I/O optimization
        if patterns['io_trend'] > 0.5:  # Increasing I/O usage
            optimizations.append(self.optimize_io_allocation(weights['io']))
        
        # Apply optimizations
        for opt in optimizations:
            try:
                opt()
            except Exception as e:
                print(f"Optimization failed: {e}")
        
        return True
    
    def optimize_cpu_allocation(self, weight):
        """Optimize CPU allocation"""
        def optimize():
            # Adjust process priorities
            processes = self.get_cpu_processes()
            
            for proc in processes:
                try:
                    ps_proc = psutil.Process(proc['pid'])
                    
                    if proc['class'] == 'critical':
                        ps_proc.nice(psutil.HIGH_PRIORITY_CLASS)
                    elif proc['class'] == 'gaming' and self.current_profile == 'gaming':
                        ps_proc.nice(psutil.HIGH_PRIORITY_CLASS)
                    elif proc['class'] == 'background':
                        ps_proc.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
                    elif proc['class'] == 'productivity' and self.current_profile == 'productivity':
                        ps_proc.nice(psutil.ABOVE_NORMAL_PRIORITY_CLASS)
                    
                except:
                    continue
            
            # Optimize CPU affinity for multi-threaded applications
            if self.win11_params['cpu_affinity_optimization']:
                self.optimize_cpu_affinity()
        
        return optimize
    
    def optimize_memory_allocation(self, weight):
        """Optimize memory allocation"""
        def optimize():
            # Clear standby memory
            if self.win11_params['standby_list_optimization']:
                try:
                    subprocess.run(['powershell', '-Command', 
                                  'Clear-StandbyList'], capture_output=True, text=True, timeout=10)
                except:
                    pass
            
            # Optimize memory compression
            if self.win11_params['memory_compression']:
                try:
                    subprocess.run(['powershell', '-Command', 
                                  'Enable-MMAgent -MemoryCompression'], capture_output=True, text=True, timeout=5)
                except:
                    pass
            
            # Force garbage collection
            gc.collect()
        
        return optimize
    
    def optimize_gpu_allocation(self, weight):
        """Optimize GPU allocation"""
        def optimize():
            if not NVML_AVAILABLE:
                return
            
            try:
                handle = nvml.nvmlDeviceGetHandleByIndex(0)
                
                # Adjust GPU power management
                if self.win11_params['gpu_scheduler_tuning']:
                    # Set power management mode
                    nvml.nvmlDeviceSetPowerManagementMode(handle, 1)  # Auto power management
                
                # Optimize GPU scheduling
                if self.current_profile == 'gaming':
                    # Prioritize gaming applications
                    processes = self.get_gpu_processes()
                    for proc in processes:
                        if proc['class'] == 'gaming':
                            # Set high priority for gaming processes
                            try:
                                ps_proc = psutil.Process(proc['pid'])
                                ps_proc.nice(psutil.HIGH_PRIORITY_CLASS)
                            except:
                                continue
                
            except Exception as e:
                print(f"GPU optimization failed: {e}")
        
        return optimize
    
    def optimize_io_allocation(self, weight):
        """Optimize I/O allocation"""
        def optimize():
            # Adjust I/O priorities
            processes = self.get_cpu_processes()
            
            for proc in processes:
                try:
                    ps_proc = psutil.Process(proc['pid'])
                    
                    if proc['class'] == 'critical':
                        # Set high I/O priority for critical processes
                        if platform.system() == "Windows":
                            subprocess.run(['powershell', '-Command', 
                                          f'Set-Process -Id {proc["pid"]} -PriorityClass High'], 
                                          capture_output=True, text=True, timeout=5)
                    elif proc['class'] == 'background':
                        # Set low I/O priority for background processes
                        if platform.system() == "Windows":
                            subprocess.run(['powershell', '-Command', 
                                          f'Set-Process -Id {proc["pid"]} -PriorityClass Low'], 
                                          capture_output=True, text=True, timeout=5)
                
                except:
                    continue
        
        return optimize
    
    def optimize_cpu_affinity(self):
        """Optimize CPU affinity for multi-threaded applications"""
        try:
            processes = self.get_cpu_processes()
            
            for proc in processes:
                if proc['cpu'] > 20:  # High CPU usage processes
                    try:
                        ps_proc = psutil.Process(proc['pid'])
                        
                        # Set affinity to all available cores for high-usage processes
                        cpu_count = psutil.cpu_count(logical=True)
                        ps_proc.cpu_affinity(list(range(cpu_count)))
                    
                    except:
                        continue
        except:
            pass
    
    def continuous_optimization_loop(self):
        """Safe continuous background optimization loop"""
        optimization_history = deque(maxlen=100)
        last_optimization_time = 0
        profile_switch_cooldown = 60  # Increased to 60 seconds between profile switches
        last_snapshot_time = 0
        system_stable_count = 0
        
        while self.optimization_active:
            try:
                current_time = time.time()
                
                # Rate limiting - only check every 3 seconds minimum
                if current_time - last_snapshot_time < 3:
                    time.sleep(1)
                    continue
                
                last_snapshot_time = current_time
                
                # Quick system stability check
                if not self.is_system_stable():
                    system_stable_count += 1
                    if system_stable_count > 3:  # If unstable for 3 consecutive checks
                        time.sleep(10)  # Wait longer before trying again
                        system_stable_count = 0
                    continue
                else:
                    system_stable_count = 0
                
                # Get resource snapshot with timeout
                snapshot = self.get_resource_snapshot_safe()
                if not snapshot:
                    time.sleep(5)
                    continue
                
                # Analyze patterns with safety check
                patterns = self.analyze_resource_patterns_safe()
                if not patterns:
                    time.sleep(5)
                    continue
                
                # Detect current activity type
                detected_profile = self.detect_activity_type(snapshot, patterns)
                
                # Auto-switch profile if significantly different and cooldown passed
                if (detected_profile != self.current_profile and 
                    current_time - last_optimization_time > profile_switch_cooldown):
                    
                    if self.should_switch_profile(detected_profile, patterns):
                        self.current_profile = detected_profile
                        last_optimization_time = current_time
                
                # Calculate resource pressure
                pressure_score = self.calculate_pressure_score(snapshot)
                
                # Apply optimizations with much longer intervals
                if current_time - last_optimization_time > 15:  # Minimum 15 seconds between optimizations
                    if pressure_score >= 3:
                        # Critical pressure - careful optimization
                        self.apply_safe_emergency_optimization(snapshot)
                        last_optimization_time = current_time
                    elif pressure_score >= 2:
                        # High pressure - moderate optimization
                        self.apply_safe_standard_optimization(snapshot, patterns)
                        last_optimization_time = current_time
                    elif pressure_score >= 1 and patterns['volatility']['cpu'] > 25:  # Higher threshold
                        # Medium pressure with high volatility - light optimization
                        self.apply_safe_maintenance_optimization(snapshot, patterns)
                        last_optimization_time = current_time
                
                # Conservative sleep based on pressure
                if pressure_score >= 3:
                    time.sleep(3)  # Much slower response for critical situations
                elif pressure_score >= 2:
                    time.sleep(5)  # Slower response for high pressure
                else:
                    time.sleep(8)  # Much slower response for normal conditions
                
            except Exception as e:
                print(f"Continuous optimization error: {e}")
                time.sleep(10)  # Longer error recovery time
    
    def detect_activity_type(self, snapshot, patterns):
        """Detect current activity type based on resource usage patterns"""
        cpu_usage = snapshot['cpu']['usage']
        gpu_usage = snapshot['gpu']['usage']
        memory_usage = snapshot['memory']['usage']
        
        # Check for gaming activity
        if gpu_usage > 60 and cpu_usage > 40:
            # Check for gaming processes
            gpu_processes = snapshot['gpu'].get('processes', [])
            if any(proc.get('class') == 'gaming' for proc in gpu_processes):
                return 'gaming'
        
        # Check for development activity
        if memory_usage > 70 and cpu_usage > 50:
            cpu_processes = snapshot['cpu'].get('processes', [])
            if any(proc.get('class') == 'development' for proc in cpu_processes):
                return 'development'
        
        # Check for multimedia activity
        if gpu_usage > 40 and memory_usage > 50:
            gpu_processes = snapshot['gpu'].get('processes', [])
            if any(proc.get('class') == 'multimedia' for proc in gpu_processes):
                return 'multimedia'
        
        # Check for productivity activity
        if cpu_usage > 30 and memory_usage > 60:
            cpu_processes = snapshot['cpu'].get('processes', [])
            if any(proc.get('class') == 'productivity' for proc in cpu_processes):
                return 'productivity'
        
        # Default to balanced
        return 'balanced'
    
    def should_switch_profile(self, new_profile, patterns):
        """Determine if profile should be switched"""
        # Don't switch if current profile is working well
        if patterns.get('volatility', {}).get('cpu', 0) < 10:
            return False
        
        # Switch if new profile is significantly better suited
        profile_confidence = self.calculate_profile_confidence(new_profile, patterns)
        current_confidence = self.calculate_profile_confidence(self.current_profile, patterns)
        
        return profile_confidence > current_confidence + 0.2  # 20% improvement threshold
    
    def calculate_profile_confidence(self, profile, patterns):
        """Calculate confidence score for a profile"""
        weights = self.allocation_weights[profile]
        confidence = 0
        
        # CPU confidence
        if patterns.get('cpu_trend', 0) > 0:
            confidence += weights['cpu'] * 0.3
        
        # Memory confidence
        if patterns.get('memory_trend', 0) > 0:
            confidence += weights['ram'] * 0.3
        
        # GPU confidence
        if patterns.get('gpu_trend', 0) > 0:
            confidence += weights['gpu'] * 0.3
        
        # I/O confidence
        if patterns.get('io_trend', 0) > 0:
            confidence += weights['io'] * 0.1
        
        return confidence
    
    def calculate_pressure_score(self, snapshot):
        """Calculate overall resource pressure score"""
        score = 0
        
        # CPU pressure
        if snapshot['cpu']['usage'] > self.thresholds['cpu_critical']:
            score += 3
        elif snapshot['cpu']['usage'] > self.thresholds['cpu_high']:
            score += 2
        elif snapshot['cpu']['usage'] > 70:
            score += 1
        
        # Memory pressure
        if snapshot['memory']['usage'] > self.thresholds['ram_critical']:
            score += 3
        elif snapshot['memory']['usage'] > self.thresholds['ram_high']:
            score += 2
        elif snapshot['memory']['usage'] > 75:
            score += 1
        
        # GPU pressure
        if snapshot['gpu']['usage'] > self.thresholds['gpu_critical']:
            score += 3
        elif snapshot['gpu']['usage'] > self.thresholds['gpu_high']:
            score += 2
        elif snapshot['gpu']['usage'] > 70:
            score += 1
        
        # Temperature pressure
        if snapshot['cpu']['temp'] > 85:
            score += 2
        elif snapshot['cpu']['temp'] > 75:
            score += 1
        
        if snapshot['gpu']['temp'] > 85:
            score += 2
        elif snapshot['gpu']['temp'] > 75:
            score += 1
        
        return score
    
    def apply_emergency_optimization(self, snapshot):
        """Apply emergency optimization for critical situations"""
        # Aggressive process priority management
        self.emergency_process_prioritization(snapshot)
        
        # Force memory cleanup
        self.emergency_memory_cleanup()
        
        # Reduce background activity
        self.emergency_background_throttling()
        
        # Thermal management
        if snapshot['cpu']['temp'] > 85 or snapshot['gpu']['temp'] > 85:
            self.thermal_throttling()
    
    def apply_aggressive_optimization(self, snapshot, patterns):
        """Apply aggressive optimization for high pressure"""
        # Standard optimizations with higher intensity
        self.optimize_resource_allocation()
        
        # Additional memory management
        if patterns.get('memory_trend', 0) > 1:
            self.aggressive_memory_optimization()
        
        # CPU affinity optimization
        self.optimize_cpu_affinity()
        
        # I/O prioritization
        self.optimize_io_allocation(0.8)
    
    def apply_standard_optimization(self, snapshot, patterns):
        """Apply standard optimization for medium pressure"""
        # Balanced optimization
        self.optimize_resource_allocation()
        
        # Light memory management
        if patterns.get('memory_trend', 0) > 0.5:
            self.standard_memory_optimization()
        
        # Process priority adjustment
        self.standard_process_prioritization(snapshot)
    
    def apply_maintenance_optimization(self, snapshot, patterns):
        """Apply maintenance optimization for normal conditions"""
        # Preventive optimizations
        if patterns.get('volatility', {}).get('cpu', 0) > 15:
            self.cpu_stabilization()
        
        # Light memory management
        self.maintenance_memory_cleanup()
        
        # Background process management
        self.background_process_management()
    
    def emergency_process_prioritization(self, snapshot):
        """Emergency process prioritization"""
        try:
            # Boost critical and foreground processes
            processes = snapshot['cpu'].get('processes', [])
            
            for proc in processes[:5]:  # Top 5 CPU processes
                if proc.get('class') in ['critical', 'gaming']:
                    try:
                        ps_proc = psutil.Process(proc['pid'])
                        ps_proc.nice(psutil.HIGH_PRIORITY_CLASS)
                    except:
                        continue
            
            # Throttle background processes
            for proc in processes:
                if proc.get('class') == 'background':
                    try:
                        ps_proc = psutil.Process(proc['pid'])
                        ps_proc.nice(psutil.IDLE_PRIORITY_CLASS)
                    except:
                        continue
        
        except Exception as e:
            print(f"Emergency process prioritization failed: {e}")
    
    def emergency_memory_cleanup(self):
        """Emergency memory cleanup"""
        try:
            # Clear standby memory
            subprocess.run(['powershell', '-Command', 'Clear-StandbyList'], 
                          capture_output=True, text=True, timeout=10)
            
            # Force garbage collection multiple times
            for _ in range(3):
                gc.collect()
                time.sleep(0.1)
            
            # Clear system cache
            if platform.system() == "Windows":
                subprocess.run(['ipconfig', '/flushdns'], capture_output=True, text=True)
        
        except Exception as e:
            print(f"Emergency memory cleanup failed: {e}")
    
    def emergency_background_throttling(self):
        """Emergency background process throttling"""
        try:
            background_processes = ['onedrive', 'dropbox', 'googledrive', 'discord', 'slack']
            
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    proc_name = proc.info['name'].lower()
                    if any(bg_proc in proc_name for bg_proc in background_processes):
                        ps_proc = psutil.Process(proc.info['pid'])
                        ps_proc.nice(psutil.IDLE_PRIORITY_CLASS)
                except:
                    continue
        
        except Exception as e:
            print(f"Emergency background throttling failed: {e}")
    
    def thermal_throttling(self):
        """Apply thermal throttling"""
        try:
            # Reduce CPU frequency limits
            if platform.system() == "Windows":
                subprocess.run(['powercfg', '/setactive', 'scminim'], capture_output=True, text=True)
            
            # Throttle GPU if possible
            if NVML_AVAILABLE:
                handle = nvml.nvmlDeviceGetHandleByIndex(0)
                nvml.nvmlDeviceSetPowerManagementLimit(handle, int(nvml.nvmlDeviceGetPowerManagementLimit(handle) * 0.8))
        
        except Exception as e:
            print(f"Thermal throttling failed: {e}")
    
    def aggressive_memory_optimization(self):
        """Aggressive memory optimization"""
        try:
            # Clear all possible memory
            subprocess.run(['powershell', '-Command', 'Clear-StandbyList'], 
                          capture_output=True, text=True, timeout=10)
            
            # Disable memory compression temporarily
            subprocess.run(['powershell', '-Command', 'Disable-MMAgent -MemoryCompression'], 
                          capture_output=True, text=True, timeout=5)
            
            # Force garbage collection
            gc.collect()
            
            # Re-enable memory compression
            time.sleep(1)
            subprocess.run(['powershell', '-Command', 'Enable-MMAgent -MemoryCompression'], 
                          capture_output=True, text=True, timeout=5)
        
        except Exception as e:
            print(f"Aggressive memory optimization failed: {e}")
    
    def standard_memory_optimization(self):
        """Standard memory optimization"""
        try:
            # Clear standby memory
            subprocess.run(['powershell', '-Command', 'Clear-StandbyList'], 
                          capture_output=True, text=True, timeout=5)
            
            # Garbage collection
            gc.collect()
        
        except Exception as e:
            print(f"Standard memory optimization failed: {e}")
    
    def maintenance_memory_cleanup(self):
        """Maintenance memory cleanup"""
        try:
            # Light garbage collection
            gc.collect()
            
            # Clear DNS cache
            subprocess.run(['ipconfig', '/flushdns'], capture_output=True, text=True)
        
        except Exception as e:
            print(f"Maintenance memory cleanup failed: {e}")
    
    def cpu_stabilization(self):
        """CPU stabilization for high volatility"""
        try:
            # Optimize CPU affinity for volatile processes
            processes = self.get_cpu_processes()
            
            for proc in processes:
                if proc['cpu'] > 15:  # High CPU usage
                    try:
                        ps_proc = psutil.Process(proc['pid'])
                        # Spread across all cores for stability
                        cpu_count = psutil.cpu_count(logical=True)
                        ps_proc.cpu_affinity(list(range(cpu_count)))
                    except:
                        continue
        
        except Exception as e:
            print(f"CPU stabilization failed: {e}")
    
    def background_process_management(self):
        """Background process management"""
        try:
            # Monitor and adjust background processes
            background_processes = ['onedrive', 'dropbox', 'googledrive']
            
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
                try:
                    proc_name = proc.info['name'].lower()
                    if any(bg_proc in proc_name for bg_proc in background_processes):
                        if proc.info['cpu_percent'] > 10:  # If using significant CPU
                            ps_proc = psutil.Process(proc.info['pid'])
                            ps_proc.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
                except:
                    continue
        
        except Exception as e:
            print(f"Background process management failed: {e}")
    
    def standard_process_prioritization(self, snapshot):
        """Standard process prioritization"""
        try:
            processes = snapshot['cpu'].get('processes', [])
            
            for proc in processes:
                try:
                    ps_proc = psutil.Process(proc['pid'])
                    
                    if proc.get('class') == 'critical':
                        ps_proc.nice(psutil.HIGH_PRIORITY_CLASS)
                    elif proc.get('class') == 'gaming' and self.current_profile == 'gaming':
                        ps_proc.nice(psutil.HIGH_PRIORITY_CLASS)
                    elif proc.get('class') == 'background':
                        ps_proc.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
                    elif proc.get('class') == 'productivity' and self.current_profile == 'productivity':
                        ps_proc.nice(psutil.ABOVE_NORMAL_PRIORITY_CLASS)
                
                except:
                    continue
        
        except Exception as e:
            print(f"Standard process prioritization failed: {e}")
    
    def start_optimization(self, profile='balanced'):
        """Start continuous resource optimization"""
        if self.optimization_active:
            return False
        
        self.current_profile = profile
        self.optimization_active = True
        
        # Start continuous optimization thread
        self.monitoring_thread = threading.Thread(target=self.continuous_optimization_loop, daemon=True)
        self.monitoring_thread.start()
        
        return True
    
    def stop_optimization(self):
        """Stop resource optimization"""
        self.optimization_active = False
        
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        
        return True
    
    def is_system_stable(self):
        """Quick system stability check"""
        try:
            # Check CPU responsiveness
            start_time = time.time()
            cpu_percent = psutil.cpu_percent(interval=0.1)
            response_time = time.time() - start_time
            
            # If CPU check takes too long, system might be unstable
            if response_time > 2.0:
                return False
            
            # Check for extreme CPU usage that might indicate system freeze
            if cpu_percent > 98:
                return False
            
            # Check memory availability
            memory = psutil.virtual_memory()
            if memory.available < (100 * 1024 * 1024):  # Less than 100MB available
                return False
            
            return True
            
        except Exception:
            return False
    
    def get_resource_snapshot_safe(self):
        """Get resource snapshot with timeout and safety checks"""
        try:
            # Use shorter intervals to prevent blocking
            snapshot = {
                'timestamp': time.time(),
                'cpu': {
                    'usage': psutil.cpu_percent(interval=0.1),
                    'freq': psutil.cpu_freq().current if psutil.cpu_freq() else 0,
                    'temp': self.get_cpu_temperature(),
                    'load_avg': psutil.getloadavg()[0] if hasattr(psutil, 'getloadavg') else 0,
                    'processes': self.get_cpu_processes_safe()
                },
                'memory': {
                    'usage': psutil.virtual_memory().percent,
                    'available': psutil.virtual_memory().available / (1024**3),
                    'swap': psutil.swap_memory().percent if psutil.swap_memory() else 0,
                    'standby': self.get_standby_memory_safe(),
                    'compressed': self.get_compressed_memory_safe()
                },
                'gpu': {
                    'usage': self.get_gpu_usage_safe(),
                    'memory': self.get_gpu_memory_safe(),
                    'temp': self.get_gpu_temperature_safe(),
                    'freq': self.get_gpu_frequency_safe(),
                    'processes': self.get_gpu_processes_safe()
                },
                'disk': {
                    'usage': self.get_disk_usage_safe(),
                    'io': self.get_disk_io_safe(),
                    'queue_length': self.get_disk_queue_length_safe()
                },
                'network': {
                    'io': self.get_network_io_safe(),
                    'latency': self.get_network_latency_safe()
                }
            }
            
            self.resource_history.append(snapshot)
            return snapshot
            
        except Exception as e:
            print(f"Error getting safe resource snapshot: {e}")
            return None
    
    def get_cpu_processes_safe(self):
        """Get CPU processes safely with limited scope"""
        processes = []
        try:
            # Limit to top 5 processes to prevent blocking
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    pinfo = proc.info
                    if pinfo['cpu_percent'] > 10:  # Only include processes using >10% CPU
                        processes.append({
                            'pid': pinfo['pid'],
                            'name': pinfo['name'],
                            'cpu': pinfo['cpu_percent'],
                            'memory': pinfo['memory_percent'],
                            'class': self.classify_process(pinfo['name'])
                        })
                        if len(processes) >= 5:  # Limit to 5 processes
                            break
                except:
                    continue
            return sorted(processes, key=lambda x: x['cpu'], reverse=True)
        except:
            return []
    
    def get_standby_memory_safe(self):
        """Get standby memory usage safely"""
        try:
            if platform.system() == "Windows":
                # Use shorter timeout
                result = subprocess.run(['powershell', '-Command', 
                                      '(Get-Counter -Counter "\\Memory\\Standby Cache Reserve Bytes").CounterSamples.CookedValue'], 
                                      capture_output=True, text=True, timeout=3)
                if result.returncode == 0:
                    standby_bytes = float(result.stdout.strip())
                    return standby_bytes / (1024**3)
            return 0.0
        except:
            return 0.0
    
    def get_compressed_memory_safe(self):
        """Get compressed memory usage safely"""
        try:
            if platform.system() == "Windows":
                result = subprocess.run(['powershell', '-Command', 
                                      '(Get-Counter -Counter "\\Memory\\Compressed Bytes").CounterSamples.CookedValue'], 
                                      capture_output=True, text=True, timeout=3)
                if result.returncode == 0:
                    compressed_bytes = float(result.stdout.strip())
                    return compressed_bytes / (1024**3)
            return 0.0
        except:
            return 0.0
    
    def get_gpu_usage_safe(self):
        """Get GPU usage safely"""
        try:
            if NVML_AVAILABLE and hasattr(self, 'gpu_count') and self.gpu_count > 0:
                handle = nvml.nvmlDeviceGetHandleByIndex(0)
                util = nvml.nvmlDeviceGetUtilizationRates(handle)
                return util.gpu
            elif GPU_AVAILABLE:
                gpus = GPUtil.getGPUs()
                if gpus:
                    return gpus[0].load * 100
            return 0.0
        except:
            return 0.0
    
    def get_gpu_memory_safe(self):
        """Get GPU memory usage safely"""
        try:
            if NVML_AVAILABLE and hasattr(self, 'gpu_count') and self.gpu_count > 0:
                handle = nvml.nvmlDeviceGetHandleByIndex(0)
                mem_info = nvml.nvmlDeviceGetMemoryInfo(handle)
                return (mem_info.used / mem_info.total) * 100
            elif GPU_AVAILABLE:
                gpus = GPUtil.getGPUs()
                if gpus:
                    return gpus[0].memoryUtil * 100
            return 0.0
        except:
            return 0.0
    
    def get_gpu_temperature_safe(self):
        """Get GPU temperature safely"""
        try:
            if NVML_AVAILABLE and hasattr(self, 'gpu_count') and self.gpu_count > 0:
                handle = nvml.nvmlDeviceGetHandleByIndex(0)
                return nvml.nvmlDeviceGetTemperature(handle, nvml.NVML_TEMPERATURE_GPU)
            elif GPU_AVAILABLE:
                gpus = GPUtil.getGPUs()
                if gpus:
                    return gpus[0].temperature
            return 0.0
        except:
            return 0.0
    
    def get_gpu_frequency_safe(self):
        """Get GPU frequency safely"""
        try:
            if NVML_AVAILABLE and hasattr(self, 'gpu_count') and self.gpu_count > 0:
                handle = nvml.nvmlDeviceGetHandleByIndex(0)
                return nvml.nvmlDeviceGetClockInfo(handle, nvml.NVML_GRAPHICS_CLOCK) / 1000
            return 0.0
        except:
            return 0.0
    
    def get_gpu_processes_safe(self):
        """Get GPU processes safely"""
        processes = []
        try:
            if NVML_AVAILABLE and hasattr(self, 'gpu_count') and self.gpu_count > 0:
                handle = nvml.nvmlDeviceGetHandleByIndex(0)
                procs = nvml.nvmlDeviceGetGraphicsRunningProcesses(handle)
                for proc in procs[:3]:  # Limit to 3 processes
                    try:
                        ps_proc = psutil.Process(proc.pid)
                        processes.append({
                            'pid': proc.pid,
                            'name': ps_proc.name(),
                            'memory_mb': proc.usedGpuMemory / (1024**2),
                            'class': self.classify_process(ps_proc.name())
                        })
                    except:
                        continue
            return processes
        except:
            return []
    
    def get_disk_usage_safe(self):
        """Get disk usage safely"""
        try:
            disk_usage = {}
            # Limit to first 3 partitions
            for i, partition in enumerate(psutil.disk_partitions()):
                if i >= 3:
                    break
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_usage[partition.device] = {
                        'used_percent': (usage.used / usage.total) * 100,
                        'free_gb': usage.free / (1024**3)
                    }
                except:
                    continue
            return disk_usage
        except:
            return {}
    
    def get_disk_io_safe(self):
        """Get disk I/O safely"""
        try:
            io = psutil.disk_io_counters()
            return {
                'read_mb': io.read_bytes / (1024**2),
                'write_mb': io.write_bytes / (1024**2),
                'read_ops': io.read_count,
                'write_ops': io.write_count
            }
        except:
            return {}
    
    def get_disk_queue_length_safe(self):
        """Get disk queue length safely"""
        try:
            if platform.system() == "Windows":
                result = subprocess.run(['powershell', '-Command', 
                                      '(Get-Counter -Counter "\\PhysicalDisk(_Total)\\Avg. Disk Queue Length").CounterSamples.CookedValue'], 
                                      capture_output=True, text=True, timeout=3)
                if result.returncode == 0:
                    return float(result.stdout.strip())
            return 0.0
        except:
            return 0.0
    
    def get_network_io_safe(self):
        """Get network I/O safely"""
        try:
            io = psutil.net_io_counters()
            return {
                'sent_mb': io.bytes_sent / (1024**2),
                'recv_mb': io.bytes_recv / (1024**2),
                'packets_sent': io.packets_sent,
                'packets_recv': io.packets_recv
            }
        except:
            return {}
    
    def get_network_latency_safe(self):
        """Get network latency safely"""
        try:
            import socket
            start_time = time.time()
            socket.create_connection(("8.8.8.8", 53), timeout=1).close()
            return (time.time() - start_time) * 1000  # Convert to ms
        except:
            return 0.0
    
    def analyze_resource_patterns_safe(self):
        """Analyze resource patterns safely"""
        if len(self.resource_history) < 5:  # Reduced from 10
            return None
        
        recent_data = list(self.resource_history)[-30:]  # Reduced from 60
        
        patterns = {
            'cpu_trend': self.calculate_trend([d['cpu']['usage'] for d in recent_data]),
            'memory_trend': self.calculate_trend([d['memory']['usage'] for d in recent_data]),
            'gpu_trend': self.calculate_trend([d['gpu']['usage'] for d in recent_data]),
            'io_trend': self.calculate_trend([d['disk']['io'].get('read_mb', 0) + d['disk']['io'].get('write_mb', 0) for d in recent_data]),
            'volatility': self.calculate_volatility(recent_data),
            'bottlenecks': self.identify_bottlenecks(recent_data)
        }
        
        return patterns
    
    def apply_safe_emergency_optimization(self, snapshot):
        """Apply safe emergency optimization"""
        try:
            # Very limited process priority management
            self.safe_process_prioritization(snapshot)
            
            # Light memory cleanup only
            self.safe_memory_cleanup()
            
            # Skip aggressive background throttling to prevent freezes
            
        except Exception as e:
            print(f"Safe emergency optimization failed: {e}")
    
    def apply_safe_standard_optimization(self, snapshot, patterns):
        """Apply safe standard optimization"""
        try:
            # Very light memory optimization only
            if patterns.get('memory_trend', 0) > 0.5:
                self.safe_memory_cleanup()
            
            # Skip aggressive CPU affinity changes
            
        except Exception as e:
            print(f"Safe standard optimization failed: {e}")
    
    def apply_safe_maintenance_optimization(self, snapshot, patterns):
        """Apply safe maintenance optimization"""
        try:
            # Only very light memory management
            if patterns.get('volatility', {}).get('cpu', 0) > 25:  # Higher threshold
                self.safe_memory_cleanup()
            
        except Exception as e:
            print(f"Safe maintenance optimization failed: {e}")
    
    def safe_process_prioritization(self, snapshot):
        """Safe process prioritization"""
        try:
            # Only boost critical processes, no throttling
            processes = snapshot['cpu'].get('processes', [])
            
            for proc in processes[:2]:  # Only top 2 processes
                if proc.get('class') == 'critical':
                    try:
                        ps_proc = psutil.Process(proc['pid'])
                        ps_proc.nice(psutil.HIGH_PRIORITY_CLASS)
                    except:
                        continue
        
        except Exception as e:
            print(f"Safe process prioritization failed: {e}")
    
    def safe_memory_cleanup(self):
        """Safe memory cleanup"""
        try:
            # Only light garbage collection
            gc.collect()
            
        except Exception as e:
            print(f"Safe memory cleanup failed: {e}")
    
    def get_optimization_status(self):
        """Get current optimization status"""
        return {
            'active': self.optimization_active,
            'profile': self.current_profile,
            'resource_count': len(self.resource_history),
            'last_snapshot': self.resource_history[-1] if self.resource_history else None,
            'patterns': self.analyze_resource_patterns_safe()
        }

class SystemTrayApp:
    """System tray integration for Resource Optimizer"""
    
    def __init__(self, optimizer):
        self.optimizer = optimizer
        self.icon = None
        self.gui_window = None
        self.running = True
        
    def create_icon_image(self, status="inactive"):
        """Create icon image for system tray"""
        # Create a simple icon
        image = Image.new('RGB', (64, 64), color='black')
        draw = ImageDraw.Draw(image)
        
        # Draw brain icon with status color
        if status == "active":
            color = 'green'
        elif status == "warning":
            color = 'yellow'
        elif status == "critical":
            color = 'red'
        else:
            color = 'gray'
        
        # Simple brain shape
        draw.ellipse([10, 15, 54, 49], fill=color, outline='white', width=2)
        draw.ellipse([20, 10, 44, 25], fill=color, outline='white', width=2)
        draw.ellipse([15, 35, 25, 45], fill=color, outline='white', width=2)
        draw.ellipse([39, 35, 49, 45], fill=color, outline='white', width=2)
        
        return image
    
    def get_status(self):
        """Get current optimization status"""
        if not self.optimizer.optimization_active:
            return "inactive"
        
        snapshot = self.optimizer.get_resource_snapshot()
        if not snapshot:
            return "inactive"
        
        pressure_score = self.optimizer.calculate_pressure_score(snapshot)
        
        if pressure_score >= 3:
            return "critical"
        elif pressure_score >= 2:
            return "warning"
        else:
            return "active"
    
    def update_icon(self):
        """Update system tray icon based on status"""
        if self.icon:
            status = self.get_status()
            image = self.create_icon_image(status)
            self.icon.image = image
            self.icon.update_menu()
    
    def show_gui(self):
        """Show the main GUI window"""
        if self.gui_window is None or not tk.Toplevel.winfo_exists(self.gui_window):
            self.gui_window = tk.Tk()
            self.gui_app = ResourceOptimizerGUI(self.gui_window, self.optimizer, self)
        else:
            self.gui_window.lift()
            self.gui_window.focus_force()
    
    def quit_app(self):
        """Quit the application"""
        self.running = False
        self.optimizer.stop_optimization()
        if self.icon:
            self.icon.stop()
        if self.gui_window:
            self.gui_window.destroy()
        sys.exit(0)
    
    def create_menu(self):
        """Create system tray menu"""
        menu = pystray.Menu(
            pystray.MenuItem("Show Dashboard", self.show_gui),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Start Optimization", self.start_optimization),
            pystray.MenuItem("Stop Optimization", self.stop_optimization),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Exit", self.quit_app)
        )
        return menu
    
    def start_optimization(self):
        """Start optimization from tray"""
        try:
            profile = self.optimizer.current_profile
            if self.optimizer.start_optimization(profile):
                self.update_icon()
                self.show_notification("Resource Optimizer", f"Started {profile} optimization")
                # Update GUI if it's open
                if self.gui_window and hasattr(self, 'gui_app'):
                    self.gui_app.start_btn.config(state='disabled')
                    self.gui_app.stop_btn.config(state='normal')
                    self.gui_app.log_message(f"🚀 Optimization started with {profile} profile (from tray)")
            else:
                self.show_notification("Resource Optimizer", "Failed to start optimization")
        except Exception as e:
            self.show_notification("Resource Optimizer", f"Error starting optimization: {e}")
    
    def stop_optimization(self):
        """Stop optimization from tray"""
        try:
            if self.optimizer.stop_optimization():
                self.update_icon()
                self.show_notification("Resource Optimizer", "Optimization stopped")
                # Update GUI if it's open
                if self.gui_window and hasattr(self, 'gui_app'):
                    self.gui_app.start_btn.config(state='normal')
                    self.gui_app.stop_btn.config(state='disabled')
                    self.gui_app.log_message("⏹️ Optimization stopped (from tray)")
            else:
                self.show_notification("Resource Optimizer", "Failed to stop optimization")
        except Exception as e:
            self.show_notification("Resource Optimizer", f"Error stopping optimization: {e}")
    
    def show_notification(self, title, message):
        """Show system notification"""
        if self.icon:
            self.icon.notify(message, title)
    
    def run(self):
        """Run the system tray app"""
        # Create initial icon
        image = self.create_icon_image("inactive")
        
        # Create menu
        menu = self.create_menu()
        
        # Create and run icon
        self.icon = pystray.Icon("resource_optimizer", image, "Windows 11 Resource Optimizer", menu)
        self.icon.run()

class ResourceOptimizerGUI:
    """GUI for Windows 11 Resource Optimizer"""
    
    def __init__(self, root, optimizer=None, tray_app=None):
        self.root = root
        self.root.title("🧠 Windows 11 Resource Sharing Optimizer")
        self.root.geometry("1200x800")
        self.root.configure(bg='#0f0f0f')
        self.root.resizable(True, True)
        
        # System tray integration
        self.tray_app = tray_app
        
        # Monitoring control
        self.monitoring_active = False
        self.monitor_thread = None
        self.cached_snapshot = None
        
        # Color scheme
        self.colors = {
            'bg': '#0f0f0f',
            'card': '#1e1e1e',
            'primary': '#00d4ff',
            'success': '#00ff88',
            'warning': '#ffaa00',
            'danger': '#ff4444',
            'text': '#ffffff',
            'text_secondary': '#a0a0a0'
        }
        
        # Initialize optimizer
        self.optimizer = optimizer if optimizer else ResourceOptimizer()
        
        # Handle window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Create GUI
        self.create_widgets()
        
        # Start monitoring
        self.start_monitoring()
        
        # Update tray status periodically
        if self.tray_app:
            self.update_tray_status()
    
    def on_closing(self):
        """Handle window closing - minimize to tray instead of closing"""
        self.stop_monitoring()
        if self.tray_app:
            self.root.withdraw()  # Hide window
            self.tray_app.show_notification("Resource Optimizer", "Minimized to system tray")
        else:
            self.stop_optimization()
            self.root.destroy()
    
    def update_tray_status(self):
        """Update system tray status"""
        if self.tray_app:
            self.tray_app.update_icon()
            
            # Update profile display if it changed
            current_profile = self.optimizer.current_profile
            if self.profile_var.get() != current_profile:
                self.profile_var.set(current_profile)
                self.profile_display.config(text=f"Profile: {current_profile.capitalize()}")
            
            # Schedule next update
            self.root.after(5000, self.update_tray_status)  # Update every 5 seconds
    
    def create_widgets(self):
        """Create GUI widgets"""
        # Main container
        main_container = tk.Frame(self.root, bg=self.colors['bg'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        header_frame = tk.Frame(main_container, bg=self.colors['bg'])
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = tk.Label(header_frame, text="🧠 Windows 11 Resource Sharing Optimizer", 
                              font=('Segoe UI', 20, 'bold'), 
                              fg=self.colors['primary'], bg=self.colors['bg'])
        title_label.pack(pady=(10, 5))
        
        subtitle_label = tk.Label(header_frame, text="Intelligent Resource Management & Allocation Algorithm", 
                                 font=('Segoe UI', 11), 
                                 fg=self.colors['text_secondary'], bg=self.colors['bg'])
        subtitle_label.pack(pady=(0, 10))
        
        # Control panel
        control_frame = tk.Frame(main_container, bg=self.colors['card'], relief='solid', bd=1)
        control_frame.pack(fill=tk.X, pady=(0, 20))
        
        control_title = tk.Label(control_frame, text="🎛️ Optimization Controls", 
                                font=('Segoe UI', 14, 'bold'), 
                                fg=self.colors['primary'], bg=self.colors['card'])
        control_title.pack(pady=(15, 10))
        
        # Profile selection
        profile_frame = tk.Frame(control_frame, bg=self.colors['card'])
        profile_frame.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        tk.Label(profile_frame, text="Profile:", font=('Segoe UI', 11), 
                fg=self.colors['text'], bg=self.colors['card']).pack(side=tk.LEFT, padx=(0, 10))
        
        self.profile_var = tk.StringVar(value='balanced')
        profiles = ['balanced', 'gaming', 'productivity', 'multimedia', 'development']
        
        for profile in profiles:
            rb = tk.Radiobutton(profile_frame, text=profile.capitalize(), 
                              variable=self.profile_var, value=profile,
                              bg=self.colors['card'], fg=self.colors['text'],
                              selectcolor=self.colors['card'], 
                              activebackground=self.colors['card'],
                              font=('Segoe UI', 10),
                              command=lambda p=profile: self.on_profile_change(p))
            rb.pack(side=tk.LEFT, padx=10)
        
        # Control buttons
        button_frame = tk.Frame(control_frame, bg=self.colors['card'])
        button_frame.pack(pady=(0, 20))
        
        self.start_btn = tk.Button(button_frame, text="▶️ Start Optimization", 
                                  font=('Segoe UI', 11, 'bold'), 
                                  bg=self.colors['success'], fg=self.colors['bg'],
                                  relief='flat', bd=0, cursor='hand2', padx=20, pady=8,
                                  command=self.start_optimization)
        self.start_btn.pack(side=tk.LEFT, padx=10)
        
        self.stop_btn = tk.Button(button_frame, text="⏹️ Stop Optimization", 
                                 font=('Segoe UI', 11, 'bold'), 
                                 bg=self.colors['danger'], fg=self.colors['bg'],
                                 relief='flat', bd=0, cursor='hand2', padx=20, pady=8,
                                 command=self.stop_optimization, state='disabled')
        self.stop_btn.pack(side=tk.LEFT, padx=10)
        
        # Status display
        status_frame = tk.Frame(main_container, bg=self.colors['card'], relief='solid', bd=1)
        status_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Enhanced status header
        status_header = tk.Frame(status_frame, bg=self.colors['card'])
        status_header.pack(fill=tk.X, padx=20, pady=(15, 10))
        
        status_title = tk.Label(status_header, text="📊 Resource Status", 
                               font=('Segoe UI', 14, 'bold'), 
                               fg=self.colors['primary'], bg=self.colors['card'])
        status_title.pack(side=tk.LEFT)
        
        # Active optimization indicator
        self.active_indicator = tk.Label(status_header, text="● INACTIVE", 
                                        font=('Segoe UI', 10, 'bold'), 
                                        fg=self.colors['text_secondary'], bg=self.colors['card'])
        self.active_indicator.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Current profile display
        self.profile_display = tk.Label(status_header, text="Profile: Balanced", 
                                       font=('Segoe UI', 10, 'bold'), 
                                       fg=self.colors['primary'], bg=self.colors['card'])
        self.profile_display.pack(side=tk.RIGHT, padx=(20, 0))
        
        # Resource displays
        self.resource_frame = tk.Frame(status_frame, bg=self.colors['card'])
        self.resource_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Create resource labels
        self.create_resource_displays()
        
        # Optimization intensity display
        intensity_frame = tk.Frame(status_frame, bg=self.colors['card'])
        intensity_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        self.intensity_label = tk.Label(intensity_frame, text="Optimization: Idle", 
                                       font=('Segoe UI', 10, 'bold'), 
                                       fg=self.colors['text_secondary'], bg=self.colors['card'])
        self.intensity_label.pack(side=tk.LEFT)
        
        self.pressure_label = tk.Label(intensity_frame, text="Pressure: Low", 
                                      font=('Segoe UI', 10), 
                                      fg=self.colors['success'], bg=self.colors['card'])
        self.pressure_label.pack(side=tk.RIGHT)
        
        # Optimization log
        log_frame = tk.Frame(main_container, bg=self.colors['card'], relief='solid', bd=1)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        log_title = tk.Label(log_frame, text="📋 Optimization Log", 
                            font=('Segoe UI', 14, 'bold'), 
                            fg=self.colors['primary'], bg=self.colors['card'])
        log_title.pack(pady=(15, 10))
        
        # Log text widget
        self.log_text = tk.Text(log_frame, height=8, bg=self.colors['bg'], fg=self.colors['text'],
                               font=('Consolas', 9), relief='flat', bd=0)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Scrollbar for log
        scrollbar = tk.Scrollbar(self.log_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.log_text.yview)
    
    def create_resource_displays(self):
        """Create resource display widgets"""
        # CPU Display
        cpu_frame = tk.Frame(self.resource_frame, bg=self.colors['card'], relief='solid', bd=1)
        cpu_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(cpu_frame, text="CPU", font=('Segoe UI', 12, 'bold'), 
                fg=self.colors['primary'], bg=self.colors['card']).pack(pady=(10, 5))
        
        self.cpu_usage_label = tk.Label(cpu_frame, text="0%", font=('Segoe UI', 16, 'bold'), 
                                       fg=self.colors['text'], bg=self.colors['card'])
        self.cpu_usage_label.pack(expand=True)
        
        self.cpu_temp_label = tk.Label(cpu_frame, text="0°C", font=('Segoe UI', 10), 
                                      fg=self.colors['text_secondary'], bg=self.colors['card'])
        self.cpu_temp_label.pack(pady=(5, 10))
        
        # Memory Display
        mem_frame = tk.Frame(self.resource_frame, bg=self.colors['card'], relief='solid', bd=1)
        mem_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(mem_frame, text="Memory", font=('Segoe UI', 12, 'bold'), 
                fg=self.colors['primary'], bg=self.colors['card']).pack(pady=(10, 5))
        
        self.mem_usage_label = tk.Label(mem_frame, text="0%", font=('Segoe UI', 16, 'bold'), 
                                       fg=self.colors['text'], bg=self.colors['card'])
        self.mem_usage_label.pack(expand=True)
        
        self.mem_available_label = tk.Label(mem_frame, text="0 GB free", font=('Segoe UI', 10), 
                                           fg=self.colors['text_secondary'], bg=self.colors['card'])
        self.mem_available_label.pack(pady=(5, 10))
        
        # GPU Display
        gpu_frame = tk.Frame(self.resource_frame, bg=self.colors['card'], relief='solid', bd=1)
        gpu_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(gpu_frame, text="GPU", font=('Segoe UI', 12, 'bold'), 
                fg=self.colors['primary'], bg=self.colors['card']).pack(pady=(10, 5))
        
        self.gpu_usage_label = tk.Label(gpu_frame, text="0%", font=('Segoe UI', 16, 'bold'), 
                                       fg=self.colors['text'], bg=self.colors['card'])
        self.gpu_usage_label.pack(expand=True)
        
        self.gpu_temp_label = tk.Label(gpu_frame, text="0°C", font=('Segoe UI', 10), 
                                      fg=self.colors['text_secondary'], bg=self.colors['card'])
        self.gpu_temp_label.pack(pady=(5, 10))
        
        # I/O Display
        io_frame = tk.Frame(self.resource_frame, bg=self.colors['card'], relief='solid', bd=1)
        io_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(io_frame, text="I/O", font=('Segoe UI', 12, 'bold'), 
                fg=self.colors['primary'], bg=self.colors['card']).pack(pady=(10, 5))
        
        self.io_queue_label = tk.Label(io_frame, text="0", font=('Segoe UI', 16, 'bold'), 
                                      fg=self.colors['text'], bg=self.colors['card'])
        self.io_queue_label.pack(expand=True)
        
        self.io_ops_label = tk.Label(io_frame, text="0 ops/s", font=('Segoe UI', 10), 
                                    fg=self.colors['text_secondary'], bg=self.colors['card'])
        self.io_ops_label.pack(pady=(5, 10))
    
    def on_profile_change(self, profile):
        """Handle profile change from radio buttons"""
        if self.optimizer.optimization_active:
            # If optimization is running, update the optimizer profile
            self.optimizer.current_profile = profile
            self.log_message(f"🔄 Switched to {profile} profile")
        else:
            # If optimization is not running, just update the display
            self.profile_display.config(text=f"Profile: {profile.capitalize()}")
    
    def start_optimization(self):
        """Start resource optimization"""
        try:
            profile = self.profile_var.get()
            self.log_message(f"🔄 Starting optimization with {profile} profile...")
            
            # Update button states immediately for feedback
            self.start_btn.config(state='disabled', text="⏳ Starting...")
            self.root.update_idletasks()
            
            if self.optimizer.start_optimization(profile):
                self.start_btn.config(state='disabled', text="▶️ Start Optimization")
                self.stop_btn.config(state='normal')
                self.log_message(f"🚀 Optimization started with {profile} profile")
            else:
                self.start_btn.config(state='normal', text="▶️ Start Optimization")
                self.log_message("❌ Failed to start optimization")
                messagebox.showerror("Error", "Failed to start optimization")
        except Exception as e:
            self.start_btn.config(state='normal', text="▶️ Start Optimization")
            self.log_message(f"❌ Error starting optimization: {e}")
            messagebox.showerror("Error", f"Error starting optimization: {e}")
    
    def stop_optimization(self):
        """Stop resource optimization"""
        try:
            self.log_message("🔄 Stopping optimization...")
            
            # Update button states immediately for feedback
            self.stop_btn.config(state='disabled', text="⏳ Stopping...")
            self.root.update_idletasks()
            
            if self.optimizer.stop_optimization():
                self.start_btn.config(state='normal', text="▶️ Start Optimization")
                self.stop_btn.config(state='disabled', text="⏹️ Stop Optimization")
                self.log_message("⏹️ Optimization stopped")
            else:
                self.stop_btn.config(state='normal', text="⏹️ Stop Optimization")
                self.log_message("❌ Failed to stop optimization")
                messagebox.showerror("Error", "Failed to stop optimization")
        except Exception as e:
            self.stop_btn.config(state='normal', text="⏹️ Stop Optimization")
            self.log_message(f"❌ Error stopping optimization: {e}")
            messagebox.showerror("Error", f"Error stopping optimization: {e}")
    
    def log_message(self, message):
        """Add message to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
    
    def update_display(self):
        """Update resource displays with continuous optimization status"""
        snapshot = self.optimizer.get_resource_snapshot()
        if not snapshot:
            return
        
        # Update resource displays
        self.cpu_usage_label.config(text=f"{snapshot['cpu']['usage']:.1f}%")
        self.cpu_temp_label.config(text=f"{snapshot['cpu']['temp']:.1f}°C")
        
        self.mem_usage_label.config(text=f"{snapshot['memory']['usage']:.1f}%")
        self.mem_available_label.config(text=f"{snapshot['memory']['available']:.1f} GB free")
        
        self.gpu_usage_label.config(text=f"{snapshot['gpu']['usage']:.1f}%")
        self.gpu_temp_label.config(text=f"{snapshot['gpu']['temp']:.1f}°C")
        
        self.io_queue_label.config(text=f"{snapshot['disk']['queue_length']:.1f}")
        io_ops = snapshot['disk']['io'].get('read_ops', 0) + snapshot['disk']['io'].get('write_ops', 0)
        self.io_ops_label.config(text=f"{io_ops} ops")
        
        # Update optimization status
        if self.optimizer.optimization_active:
            self.active_indicator.config(text="● ACTIVE", fg=self.colors['success'])
            
            # Calculate pressure score
            pressure_score = self.optimizer.calculate_pressure_score(snapshot)
            
            # Update pressure display
            if pressure_score >= 3:
                self.pressure_label.config(text="Pressure: Critical", fg=self.colors['danger'])
                self.intensity_label.config(text="Optimization: Emergency", fg=self.colors['danger'])
            elif pressure_score >= 2:
                self.pressure_label.config(text="Pressure: High", fg=self.colors['warning'])
                self.intensity_label.config(text="Optimization: Aggressive", fg=self.colors['warning'])
            elif pressure_score >= 1:
                self.pressure_label.config(text="Pressure: Medium", fg=self.colors['primary'])
                self.intensity_label.config(text="Optimization: Standard", fg=self.colors['primary'])
            else:
                self.pressure_label.config(text="Pressure: Low", fg=self.colors['success'])
                self.intensity_label.config(text="Optimization: Maintenance", fg=self.colors['text_secondary'])
            
            # Update profile display
            self.profile_display.config(text=f"Profile: {self.optimizer.current_profile.capitalize()}")
            
            # Log optimization activity periodically
            if not hasattr(self, 'last_log_time'):
                self.last_log_time = 0
            
            current_time = time.time()
            if current_time - self.last_log_time > 30:  # Log every 30 seconds
                self.log_optimization_status(snapshot, pressure_score)
                self.last_log_time = current_time
        else:
            self.active_indicator.config(text="● INACTIVE", fg=self.colors['text_secondary'])
            self.intensity_label.config(text="Optimization: Idle", fg=self.colors['text_secondary'])
            self.pressure_label.config(text="Pressure: Low", fg=self.colors['success'])
    
    def log_optimization_status(self, snapshot, pressure_score):
        """Log optimization status"""
        profile = self.optimizer.current_profile
        cpu_usage = snapshot['cpu']['usage']
        mem_usage = snapshot['memory']['usage']
        gpu_usage = snapshot['gpu']['usage']
        
        status_msg = f"🔄 {profile.capitalize()} profile active | "
        status_msg += f"CPU: {cpu_usage:.1f}% | "
        status_msg += f"RAM: {mem_usage:.1f}% | "
        status_msg += f"GPU: {gpu_usage:.1f}% | "
        status_msg += f"Pressure: {pressure_score}"
        
        self.log_message(status_msg)
    
    def start_monitoring(self):
        """Start monitoring thread"""
        self.monitoring_active = True
        
        def monitor():
            while self.monitoring_active:
                try:
                    # Get snapshot in background thread to avoid blocking GUI
                    snapshot = self.optimizer.get_resource_snapshot()
                    if snapshot and self.root.winfo_exists():
                        self.cached_snapshot = snapshot
                        # Update GUI from main thread
                        self.root.after(0, lambda: self.update_display_with_snapshot(snapshot))
                    time.sleep(2)  # Increased from 1 to 2 seconds to reduce lag
                except:
                    break
        
        self.monitor_thread = threading.Thread(target=monitor, daemon=True)
        self.monitor_thread.start()
    
    def update_display_with_snapshot(self, snapshot):
        """Update display with pre-fetched snapshot (called from main thread)"""
        if not snapshot:
            return
        
        # Update resource displays
        self.cpu_usage_label.config(text=f"{snapshot['cpu']['usage']:.1f}%")
        self.cpu_temp_label.config(text=f"{snapshot['cpu']['temp']:.1f}°C")
        
        self.mem_usage_label.config(text=f"{snapshot['memory']['usage']:.1f}%")
        self.mem_available_label.config(text=f"{snapshot['memory']['available']:.1f} GB free")
        
        self.gpu_usage_label.config(text=f"{snapshot['gpu']['usage']:.1f}%")
        self.gpu_temp_label.config(text=f"{snapshot['gpu']['temp']:.1f}°C")
        
        self.io_queue_label.config(text=f"{snapshot['disk']['queue_length']:.1f}")
        io_ops = snapshot['disk']['io'].get('read_ops', 0) + snapshot['disk']['io'].get('write_ops', 0)
        self.io_ops_label.config(text=f"{io_ops} ops")
        
        # Update optimization status
        if self.optimizer.optimization_active:
            self.active_indicator.config(text="● ACTIVE", fg=self.colors['success'])
            
            # Calculate pressure score
            pressure_score = self.optimizer.calculate_pressure_score(snapshot)
            
            # Update pressure display
            if pressure_score >= 3:
                self.pressure_label.config(text="Pressure: Critical", fg=self.colors['danger'])
                self.intensity_label.config(text="Optimization: Emergency", fg=self.colors['danger'])
            elif pressure_score >= 2:
                self.pressure_label.config(text="Pressure: High", fg=self.colors['warning'])
                self.intensity_label.config(text="Optimization: Aggressive", fg=self.colors['warning'])
            elif pressure_score >= 1:
                self.pressure_label.config(text="Pressure: Medium", fg=self.colors['primary'])
                self.intensity_label.config(text="Optimization: Standard", fg=self.colors['primary'])
            else:
                self.pressure_label.config(text="Pressure: Low", fg=self.colors['success'])
                self.intensity_label.config(text="Optimization: Maintenance", fg=self.colors['text_secondary'])
            
            # Update profile display
            self.profile_display.config(text=f"Profile: {self.optimizer.current_profile.capitalize()}")
            
            # Log optimization activity periodically
            if not hasattr(self, 'last_log_time'):
                self.last_log_time = 0
            
            current_time = time.time()
            if current_time - self.last_log_time > 30:  # Log every 30 seconds
                self.log_optimization_status(snapshot, pressure_score)
                self.last_log_time = current_time
        else:
            self.active_indicator.config(text="● INACTIVE", fg=self.colors['text_secondary'])
            self.intensity_label.config(text="Optimization: Idle", fg=self.colors['text_secondary'])
            self.pressure_label.config(text="Pressure: Low", fg=self.colors['success'])
    
    def stop_monitoring(self):
        """Stop monitoring thread"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)

def main():
    """Main function with system tray support"""
    # Check command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "--tray":
        # Run in system tray mode
        optimizer = ResourceOptimizer()
        tray_app = SystemTrayApp(optimizer)
        
        # Start optimization automatically in tray mode
        optimizer.start_optimization('balanced')
        tray_app.show_notification("Resource Optimizer", "Started in system tray with balanced profile")
        
        # Run system tray
        tray_app.run()
    else:
        # Run in normal GUI mode
        root = tk.Tk()
        app = ResourceOptimizerGUI(root)
        root.mainloop()

if __name__ == "__main__":
    main()
