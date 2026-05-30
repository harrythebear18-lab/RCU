#!/usr/bin/env python3
"""
Real-time CPU Optimizer for Ultra-Low Latency
Optimizes CPU affinity, scheduling, and system parameters
"""

import os
import sys
import ctypes
import ctypes.util
import threading
import time
import psutil
import subprocess
from typing import List, Dict, Optional, Tuple
import numpy as np

# C library for system calls
libc = ctypes.CDLL(ctypes.util.find_library('c'), use_errno=True)

# Scheduling constants
SCHED_NORMAL = 0
SCHED_FIFO = 1
SCHED_RR = 2
SCHED_BATCH = 3
SCHED_IDLE = 5

# CPU affinity constants
CPU_SETSIZE = 1024

class CPUSet(ctypes.Structure):
    """CPU set structure for affinity"""
    _fields_ = [('bits', ctypes.c_ulong * (CPU_SETSIZE // (8 * ctypes.sizeof(ctypes.c_ulong))))]

class SchedParam(ctypes.Structure):
    """Scheduling parameters structure"""
    _fields_ = [('sched_priority', ctypes.c_int)]

class RealTimeOptimizer:
    """Optimizes system for real-time ultra-low latency operations"""
    
    def __init__(self):
        self.original_affinity = None
        self.original_priority = None
        self.original_scheduler = None
        self.optimized_threads = []
        self.system_tweaks_applied = False
        
        # CPU topology information
        self.cpu_topology = self._detect_cpu_topology()
        self.num_cores = psutil.cpu_count(logical=False)
        self.num_threads = psutil.cpu_count(logical=True)
        
        # Performance cores (Intel P-cores or high-performance cores)
        self.performance_cores = self._identify_performance_cores()
        
        # System limits
        self.rtprio_limit = self._get_rtprio_limit()
        self.cpu_isolated = self._check_cpu_isolation()
    
    def _detect_cpu_topology(self) -> Dict:
        """Detect CPU topology (cores, threads, NUMA)"""
        topology = {
            'cores': [],
            'threads_per_core': 0,
            'numa_nodes': [],
            'cache_levels': {}
        }
        
        try:
            # Get core information
            for i in range(psutil.cpu_count(logical=True)):
                topology['cores'].append({
                    'id': i,
                    'physical_id': psutil.cpu_count(logical=False),
                    'core_id': i // (psutil.cpu_count(logical=True) // psutil.cpu_count(logical=False))
                })
            
            # Detect threads per core
            topology['threads_per_core'] = self.num_threads // self.num_cores
            
            # Detect NUMA nodes
            try:
                numa_output = subprocess.check_output(['numactl', '--hardware'], stderr=subprocess.DEVNULL).decode()
                topology['numa_nodes'] = self._parse_numa_output(numa_output)
            except:
                topology['numa_nodes'] = [{'id': 0, 'cpus': list(range(self.num_threads))}]
            
            # Get cache information
            topology['cache_levels'] = self._detect_cache_levels()
            
        except Exception as e:
            print(f"CPU topology detection failed: {e}")
            # Fallback
            topology['cores'] = [{'id': i} for i in range(self.num_threads)]
            topology['threads_per_core'] = 1
            topology['numa_nodes'] = [{'id': 0, 'cpus': list(range(self.num_threads))}]
        
        return topology
    
    def _parse_numa_output(self, output: str) -> List[Dict]:
        """Parse numactl output to get NUMA node information"""
        nodes = []
        current_node = None
        
        for line in output.split('\n'):
            if 'node' in line and 'cpus:' in line:
                parts = line.split()
                node_id = int(parts[1])
                cpus_start = line.index('cpus:') + 6
                cpus_str = line[cpus_start:].strip()
                cpus = []
                
                for cpu_range in cpus_str.split(','):
                    if '-' in cpu_range:
                        start, end = map(int, cpu_range.split('-'))
                        cpus.extend(range(start, end + 1))
                    else:
                        cpus.append(int(cpu_range))
                
                nodes.append({'id': node_id, 'cpus': cpus})
        
        return nodes if nodes else [{'id': 0, 'cpus': list(range(self.num_threads))}]
    
    def _detect_cache_levels(self) -> Dict:
        """Detect CPU cache levels and sizes"""
        cache_info = {}
        
        try:
            # Read cache information from /sys/cpu
            for cpu in range(self.num_threads):
                cpu_cache = {}
                cache_path = f'/sys/devices/system/cpu/cpu{cpu}/cache'
                
                if os.path.exists(cache_path):
                    for cache_dir in os.listdir(cache_path):
                        if cache_dir.startswith('index'):
                            level_path = f'{cache_path}/{cache_dir}/level'
                            size_path = f'{cache_path}/{cache_dir}/size'
                            type_path = f'{cache_path}/{cache_dir}/type'
                            
                            if os.path.exists(level_path):
                                with open(level_path) as f:
                                    level = int(f.read().strip())
                                
                                cache_level = f'L{level}'
                                if cache_level not in cpu_cache:
                                    cpu_cache[cache_level] = {}
                                
                                if os.path.exists(size_path):
                                    with open(size_path) as f:
                                        size_str = f.read().strip()
                                        cpu_cache[cache_level]['size'] = size_str
                                
                                if os.path.exists(type_path):
                                    with open(type_path) as f:
                                        cache_type = f.read().strip()
                                        cpu_cache[cache_level]['type'] = cache_type
                
                if cpu_cache:
                    cache_info[cpu] = cpu_cache
        
        except Exception as e:
            print(f"Cache detection failed: {e}")
        
        return cache_info
    
    def _identify_performance_cores(self) -> List[int]:
        """Identify performance cores (P-cores on Intel, or high-frequency cores)"""
        performance_cores = []
        
        try:
            # Try to detect Intel P-cores vs E-cores
            cpu_freq = psutil.cpu_freq(percpu=True)
            if cpu_freq:
                # Sort cores by frequency and take top performers
                freq_with_cores = [(freq.current, i) for i, freq in enumerate(cpu_freq) if freq]
                freq_with_cores.sort(reverse=True)
                
                # Assume top 50% are performance cores
                num_perf = max(1, len(freq_with_cores) // 2)
                performance_cores = [core for _, core in freq_with_cores[:num_perf]]
            
            # Fallback: use even-numbered cores (common for performance cores)
            if not performance_cores:
                performance_cores = [i for i in range(self.num_threads) if i % 2 == 0]
        
        except Exception as e:
            print(f"Performance core detection failed: {e}")
            # Fallback to first half of cores
            performance_cores = list(range(self.num_threads // 2))
        
        return performance_cores
    
    def _get_rtprio_limit(self) -> int:
        """Get real-time priority limit for current user"""
        try:
            with open('/proc/sys/kernel/sched_rt_runtime_us') as f:
                return int(f.read().strip())
        except:
            return 950000  # Default
    
    def _check_cpu_isolation(self) -> bool:
        """Check if CPUs are isolated for real-time tasks"""
        try:
            with open('/proc/cmdline') as f:
                cmdline = f.read()
                return 'isolcpus=' in cmdline
        except:
            return False
    
    def set_cpu_affinity(self, pid: int, cpu_list: List[int]) -> bool:
        """Set CPU affinity for process"""
        try:
            # Create CPU set
            cpu_set = CPUSet()
            
            for cpu in cpu_list:
                if 0 <= cpu < CPU_SETSIZE:
                    cpu_set.bits[cpu // (8 * ctypes.sizeof(ctypes.c_ulong))] |= (1 << (cpu % (8 * ctypes.sizeof(ctypes.c_ulong))))
            
            # Set affinity
            result = libc.sched_setaffinity(pid, ctypes.sizeof(cpu_set), ctypes.byref(cpu_set))
            
            if result == 0:
                return True
            else:
                error = ctypes.get_errno()
                print(f"Failed to set CPU affinity: {os.strerror(error)}")
                return False
        
        except Exception as e:
            print(f"CPU affinity error: {e}")
            return False
    
    def get_cpu_affinity(self, pid: int) -> List[int]:
        """Get current CPU affinity for process"""
        try:
            cpu_set = CPUSet()
            
            result = libc.sched_getaffinity(pid, ctypes.sizeof(cpu_set), ctypes.byref(cpu_set))
            
            if result == 0:
                cpu_list = []
                for cpu in range(self.num_threads):
                    if cpu_set.bits[cpu // (8 * ctypes.sizeof(ctypes.c_ulong))] & (1 << (cpu % (8 * ctypes.sizeof(ctypes.c_ulong)))):
                        cpu_list.append(cpu)
                return cpu_list
            else:
                return []
        
        except Exception as e:
            print(f"Failed to get CPU affinity: {e}")
            return []
    
    def set_realtime_priority(self, pid: int, priority: int, scheduler: int = SCHED_FIFO) -> bool:
        """Set real-time scheduling priority"""
        try:
            param = SchedParam()
            param.sched_priority = priority
            
            result = libc.sched_setscheduler(pid, scheduler, ctypes.byref(param))
            
            if result == 0:
                return True
            else:
                error = ctypes.get_errno()
                print(f"Failed to set real-time priority: {os.strerror(error)}")
                return False
        
        except Exception as e:
            print(f"Real-time priority error: {e}")
            return False
    
    def get_scheduler(self, pid: int) -> Tuple[int, int]:
        """Get current scheduler and priority"""
        try:
            param = SchedParam()
            scheduler = libc.sched_getscheduler(pid)
            
            if scheduler >= 0:
                result = libc.sched_getparam(pid, ctypes.byref(param))
                if result == 0:
                    return scheduler, param.sched_priority
            
            return SCHED_NORMAL, 0
        
        except Exception as e:
            print(f"Failed to get scheduler: {e}")
            return SCHED_NORMAL, 0
    
    def optimize_process(self, pid: int = None, priority: int = 80, 
                        cpu_cores: List[int] = None, scheduler: int = SCHED_FIFO) -> bool:
        """Optimize a process for ultra-low latency"""
        if pid is None:
            pid = os.getpid()
        
        # Store original settings
        self.original_affinity = self.get_cpu_affinity(pid)
        self.original_scheduler, self.original_priority = self.get_scheduler(pid)
        
        success = True
        
        # Set CPU affinity
        if cpu_cores is None:
            # Use performance cores
            cpu_cores = self.performance_cores[:min(4, len(self.performance_cores))]
        
        if not self.set_cpu_affinity(pid, cpu_cores):
            print(f"Failed to set CPU affinity for PID {pid}")
            success = False
        else:
            print(f"Set CPU affinity for PID {pid} to cores: {cpu_cores}")
        
        # Set real-time priority
        if not self.set_realtime_priority(pid, priority, scheduler):
            print(f"Failed to set real-time priority for PID {pid}")
            success = False
        else:
            print(f"Set real-time priority for PID {pid}: {priority} ({self._scheduler_name(scheduler)})")
        
        return success
    
    def optimize_thread(self, thread: threading.Thread, priority: int = 80, 
                       cpu_core: int = None) -> bool:
        """Optimize a specific thread"""
        try:
            # Get thread ID
            thread_id = ctypes.c_ulong(thread.ident)
            
            # Set CPU affinity for thread
            if cpu_core is not None:
                if not self.set_cpu_affinity(thread_id.value, [cpu_core]):
                    print(f"Failed to set CPU affinity for thread {thread.ident}")
                    return False
            
            # Set real-time priority for thread
            if not self.set_realtime_priority(thread_id.value, priority):
                print(f"Failed to set real-time priority for thread {thread.ident}")
                return False
            
            self.optimized_threads.append(thread)
            print(f"Optimized thread {thread.ident} (core: {cpu_core}, priority: {priority})")
            return True
        
        except Exception as e:
            print(f"Thread optimization failed: {e}")
            return False
    
    def apply_system_tweaks(self) -> bool:
        """Apply system-wide optimizations for ultra-low latency"""
        if self.system_tweaks_applied:
            return True
        
        try:
            # Check if running as root
            if os.geteuid() != 0:
                print("System tweaks require root privileges")
                return False
            
            tweaks_applied = []
            
            # Disable CPU frequency scaling
            try:
                subprocess.run(['cpupower', 'frequency-set', '--governor', 'performance'], 
                             check=True, capture_output=True)
                tweaks_applied.append("CPU governor set to performance")
            except:
                pass
            
            # Increase network buffer sizes
            try:
                with open('/proc/sys/net/core/rmem_max', 'w') as f:
                    f.write('134217728')  # 128MB
                with open('/proc/sys/net/core/wmem_max', 'w') as f:
                    f.write('134217728')  # 128MB
                tweaks_applied.append("Network buffer sizes increased")
            except:
                pass
            
            # Disable CPU idle states
            try:
                for cpu in range(self.num_threads):
                    idle_path = f'/sys/devices/system/cpu/cpu{cpu}/cpuidle/state*/disable'
                    subprocess.run(f'echo 1 | tee {idle_path}', shell=True, check=True)
                tweaks_applied.append("CPU idle states disabled")
            except:
                pass
            
            # Increase real-time runtime
            try:
                with open('/proc/sys/kernel/sched_rt_runtime_us', 'w') as f:
                    f.write('-1')  # Unlimited
                tweaks_applied.append("Real-time runtime unlimited")
            except:
                pass
            
            # Increase file descriptor limits
            try:
                with open('/proc/sys/fs/file-max', 'w') as f:
                    f.write('10000000')
                tweaks_applied.append("File descriptor limits increased")
            except:
                pass
            
            self.system_tweaks_applied = True
            
            print("System tweaks applied:")
            for tweak in tweaks_applied:
                print(f"  ✓ {tweak}")
            
            return True
        
        except Exception as e:
            print(f"System tweaks failed: {e}")
            return False
    
    def restore_original_settings(self, pid: int = None):
        """Restore original process settings"""
        if pid is None:
            pid = os.getpid()
        
        if self.original_affinity:
            self.set_cpu_affinity(pid, self.original_affinity)
            print(f"Restored CPU affinity: {self.original_affinity}")
        
        if self.original_scheduler is not None and self.original_priority is not None:
            self.set_realtime_priority(pid, self.original_priority, self.original_scheduler)
            print(f"Restored scheduler: {self._scheduler_name(self.original_scheduler)} priority {self.original_priority}")
    
    def _scheduler_name(self, scheduler: int) -> str:
        """Get scheduler name from constant"""
        names = {
            SCHED_NORMAL: "NORMAL",
            SCHED_FIFO: "FIFO",
            SCHED_RR: "RR",
            SCHED_BATCH: "BATCH",
            SCHED_IDLE: "IDLE"
        }
        return names.get(scheduler, "UNKNOWN")
    
    def get_optimization_report(self) -> Dict:
        """Get comprehensive optimization report"""
        return {
            'cpu_topology': self.cpu_topology,
            'num_cores': self.num_cores,
            'num_threads': self.num_threads,
            'performance_cores': self.performance_cores,
            'rtprio_limit': self.rtprio_limit,
            'cpu_isolated': self.cpu_isolated,
            'system_tweaks_applied': self.system_tweaks_applied,
            'optimized_threads': len(self.optimized_threads)
        }
    
    def benchmark_optimization_impact(self) -> Dict:
        """Benchmark the impact of optimizations"""
        print("Benchmarking optimization impact...")
        
        # Test without optimization
        baseline_latency = self._measure_latency()
        
        # Apply optimization
        self.optimize_process(priority=90)
        
        # Test with optimization
        optimized_latency = self._measure_latency()
        
        # Calculate improvement
        improvement = (baseline_latency - optimized_latency) / baseline_latency * 100
        
        results = {
            'baseline_latency_ns': baseline_latency,
            'optimized_latency_ns': optimized_latency,
            'improvement_percent': improvement,
            'latency_reduction_ns': baseline_latency - optimized_latency
        }
        
        print(f"Optimization Results:")
        print(f"  Baseline latency: {baseline_latency:.2f} ns")
        print(f"  Optimized latency: {optimized_latency:.2f} ns")
        print(f"  Improvement: {improvement:.1f}%")
        
        return results
    
    def _measure_latency(self) -> float:
        """Measure current system latency"""
        # Simple latency measurement using time differences
        measurements = []
        
        for _ in range(1000):
            start = time.time_ns()
            # Do minimal work
            dummy = sum(range(100))
            end = time.time_ns()
            measurements.append(end - start)
        
        # Remove outliers and average
        measurements.sort()
        trimmed = measurements[100:-100]  # Remove top/bottom 10%
        return sum(trimmed) / len(trimmed)

class UltraLowLatencyThread(threading.Thread):
    """Thread with built-in optimization"""
    
    def __init__(self, target, args=(), kwargs={}, cpu_core=None, priority=80):
        super().__init__(target=target, args=args, kwargs=kwargs)
        self.cpu_core = cpu_core
        self.priority = priority
        self.optimizer = RealTimeOptimizer()
        self.optimized = False
    
    def run(self):
        """Run thread with optimizations"""
        if self.cpu_core is not None or self.priority > 0:
            # Apply optimizations before starting
            thread_id = ctypes.c_ulong(self.ident)
            
            if self.cpu_core is not None:
                self.optimizer.set_cpu_affinity(thread_id.value, [self.cpu_core])
            
            if self.priority > 0:
                self.optimizer.set_realtime_priority(thread_id.value, self.priority)
            
            self.optimized = True
        
        # Run the actual target
        super().run()

def demo_realtime_optimization():
    """Demonstration of real-time CPU optimization"""
    print("Real-time CPU Optimization Demo")
    print("=" * 40)
    
    optimizer = RealTimeOptimizer()
    
    # Show system information
    report = optimizer.get_optimization_report()
    print(f"System Information:")
    print(f"  CPU cores: {report['num_cores']} physical, {report['num_threads']} logical")
    print(f"  Performance cores: {report['performance_cores']}")
    print(f"  CPU isolated: {report['cpu_isolated']}")
    print(f"  Real-time priority limit: {report['rtprio_limit']} μs")
    
    # Optimize current process
    print(f"\nOptimizing current process (PID: {os.getpid()})...")
    if optimizer.optimize_process(priority=85, cpu_cores=report['performance_cores'][:2]):
        print("Process optimization successful")
    else:
        print("Process optimization failed")
    
    # Create optimized thread
    def worker_thread():
        print(f"Worker thread running (PID: {os.getpid()}, TID: {threading.get_ident()})")
        for i in range(10):
            time.sleep(0.1)
            print(f"  Worker iteration {i}")
    
    print(f"\nCreating optimized worker thread...")
    worker = UltraLowLatencyThread(
        target=worker_thread,
        cpu_core=report['performance_cores'][0],
        priority=90
    )
    worker.start()
    worker.join()
    
    # Benchmark optimization impact
    print(f"\nBenchmarking optimization impact...")
    benchmark_results = optimizer.benchmark_optimization_impact()
    
    # Restore original settings
    print(f"\nRestoring original settings...")
    optimizer.restore_original_settings()
    
    print(f"Demo completed!")

if __name__ == "__main__":
    demo_realtime_optimization()
