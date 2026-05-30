#!/usr/bin/env python3
"""
Ultra-Low-Latency Benchmarking Suite
Comprehensive performance testing for all DMA implementations
"""

import time
import threading
import statistics
import json
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List, Tuple, Optional, Callable
import subprocess
import os
import sys

# Import our optimized modules
try:
    from ultra_low_latency_userspace import UltraLowLatencyDMA
    from raw_network_bypass import KernelBypassManager
    from realtime_cpu_optimizer import RealTimeOptimizer
    from zero_copy_rdmda import ZeroCopyRDMAServer, ZeroCopyRDMAClient
    from udp_memory_bridge import UDPMemoryBridgeServer, UDPMemoryBridgeClient
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

class LatencyBenchmark:
    """Ultra-precise latency benchmarking"""
    
    def __init__(self):
        self.results = {}
        self.cpu_optimizer = RealTimeOptimizer()
        self.baseline_latency = None
        
        # High-precision timing
        self.use_rdtsc = self._check_rdtsc_available()
        
        # Benchmark configuration
        self.test_sizes = [64, 256, 1024, 4096, 16384]  # bytes
        self.iterations = {
            'warmup': 100,
            'quick': 1000,
            'comprehensive': 10000,
            'stress': 100000
        }
    
    def _check_rdtsc_available(self) -> bool:
        """Check if RDTSC is available for ultra-precise timing"""
        try:
            import ctypes
            rdtsc_asm = ctypes.CDLL(None)
            rdtsc = rdtsc_asm.rdtsc
            rdtsc.argtypes = []
            rdtsc.restype = ctypes.c_uint64
            
            # Try to call RDTSC
            result = rdtsc()
            return result > 0
        except:
            return False
    
    def _get_timestamp(self) -> int:
        """Get highest precision timestamp available"""
        if self.use_rdtsc:
            try:
                import ctypes
                rdtsc_asm = ctypes.CDLL(None)
                return rdtsc_asm.rdtsc()
            except:
                pass
        
        return time.time_ns()
    
    def _cycles_to_nanoseconds(self, cycles: int) -> float:
        """Convert CPU cycles to nanoseconds"""
        # Estimate CPU frequency (could be made more accurate)
        cpu_freq = 3.0e9  # 3 GHz default
        return (cycles / cpu_freq) * 1e9
    
    def measure_latency(self, func: Callable, iterations: int = 1000, 
                       warmup: int = 100) -> Dict:
        """Measure function latency with ultra-high precision"""
        latencies = []
        
        # Warmup
        for _ in range(warmup):
            func()
        
        # Actual measurement
        for _ in range(iterations):
            start = self._get_timestamp()
            result = func()
            end = self._get_timestamp()
            
            if result is not None:  # Only count successful operations
                latency_cycles = end - start
                latency_ns = self._cycles_to_nanoseconds(latency_cycles)
                latencies.append(latency_ns)
        
        if not latencies:
            return {'error': 'No successful measurements'}
        
        # Calculate statistics
        return {
            'mean_ns': statistics.mean(latencies),
            'median_ns': statistics.median(latencies),
            'min_ns': min(latencies),
            'max_ns': max(latencies),
            'std_ns': statistics.stdev(latencies) if len(latencies) > 1 else 0,
            'p95_ns': np.percentile(latencies, 95),
            'p99_ns': np.percentile(latencies, 99),
            'p999_ns': np.percentile(latencies, 99.9),
            'samples': len(latencies),
            'success_rate': len(latencies) / iterations * 100
        }
    
    def benchmark_zero_copy_rdma(self) -> Dict:
        """Benchmark Zero-Copy RDMA implementation"""
        print("Benchmarking Zero-Copy RDMA...")
        
        server = ZeroCopyRDMAServer(port=25555)
        client = ZeroCopyRDMAClient(port=25555)
        
        # Start server in background
        server_thread = threading.Thread(target=server.start_server)
        server_thread.daemon = True
        server_thread.start()
        time.sleep(0.5)
        
        results = {}
        
        try:
            for size in self.test_sizes:
                print(f"  Testing {size} byte transfers...")
                
                # Create test region
                test_data = b'X' * size
                server.create_shared_memory_region(f"benchmark_{size}", size * 2)
                
                # Benchmark write
                def write_func():
                    return client.write_memory(f"benchmark_{size}", 0, test_data)
                
                write_results = self.measure_latency(write_func, self.iterations['comprehensive'])
                
                # Benchmark read
                def read_func():
                    return client.read_memory(f"benchmark_{size}", 0, size)
                
                read_results = self.measure_latency(read_func, self.iterations['comprehensive'])
                
                results[f'size_{size}'] = {
                    'write': write_results,
                    'read': read_results,
                    'throughput_mbps': (size * 2) / (write_results['mean_ns'] + read_results['mean_ns']) * 1e3
                }
        
        finally:
            server.stop()
        
        return results
    
    def benchmark_udp_bridge(self) -> Dict:
        """Benchmark UDP Memory Bridge"""
        print("Benchmarking UDP Memory Bridge...")
        
        server = UDPMemoryBridgeServer(port=25556)
        client = UDPMemoryBridgeClient(port=25556)
        
        # Add test region
        test_data = b'X' * 16384
        server.add_memory_region("benchmark", 0x1000, test_data)
        
        # Start server
        server_thread = threading.Thread(target=server.start_server)
        server_thread.daemon = True
        server_thread.start()
        time.sleep(0.5)
        
        results = {}
        
        try:
            if client.connect():
                for size in self.test_sizes:
                    print(f"  Testing {size} byte transfers...")
                    
                    def read_func():
                        return client.read_memory(0x1000, size)
                    
                    read_results = self.measure_latency(read_func, self.iterations['comprehensive'])
                    results[f'size_{size}'] = {
                        'read': read_results,
                        'throughput_mbps': size / read_results['mean_ns'] * 1e3
                    }
                
                client.disconnect()
        
        finally:
            server.stop()
        
        return results
    
    def benchmark_ultra_dma(self) -> Dict:
        """Benchmark Ultra-Low-Latency DMA"""
        print("Benchmarking Ultra-Low-Latency DMA...")
        
        dma = UltraLowLatencyDMA()
        
        if not dma.open():
            return {'error': 'Failed to open ultra DMA device'}
        
        results = {}
        
        try:
            # Add region
            region_id = dma.add_region(0x10000000, 1024*1024, "192.168.1.100", 9999)
            
            for size in self.test_sizes:
                print(f"  Testing {size} byte transfers...")
                
                test_data = b'X' * size
                
                def write_func():
                    return dma.write_memory_ultra_fast(region_id, 0, test_data)
                
                write_results = self.measure_latency(write_func, self.iterations['stress'])
                
                results[f'size_{size}'] = {
                    'write': write_results,
                    'throughput_mbps': size / write_results['mean_ns'] * 1e3
                }
        
        finally:
            dma.close()
        
        return results
    
    def benchmark_kernel_bypass(self) -> Dict:
        """Benchmark Raw Network Bypass"""
        print("Benchmarking Raw Network Bypass...")
        
        manager = KernelBypassManager()
        
        if not manager.setup_interface("eth0", "192.168.1.100", 9999):
            return {'error': 'Failed to setup kernel bypass'}
        
        results = {}
        
        try:
            manager.start_workers()
            time.sleep(0.5)  # Let workers start
            
            for size in self.test_sizes:
                print(f"  Testing {size} byte transfers...")
                
                test_data = b'X' * size
                
                def send_func():
                    return manager.send_packet("eth0", test_data)
                
                send_results = self.measure_latency(send_func, self.iterations['stress'])
                
                results[f'size_{size}'] = {
                    'send': send_results,
                    'throughput_mbps': size / send_results['mean_ns'] * 1e3
                }
        
        finally:
            manager.stop()
        
        return results
    
    def benchmark_optimization_impact(self) -> Dict:
        """Benchmark the impact of CPU optimization"""
        print("Benchmarking CPU Optimization Impact...")
        
        # Baseline measurement
        baseline_results = self._measure_system_latency()
        
        # Apply optimizations
        self.cpu_optimizer.optimize_process(priority=90)
        
        # Optimized measurement
        optimized_results = self._measure_system_latency()
        
        # Calculate improvements
        improvements = {}
        for key in baseline_results:
            if key in optimized_results:
                baseline_val = baseline_results[key]
                optimized_val = optimized_results[key]
                
                if baseline_val > 0:
                    improvement = (baseline_val - optimized_val) / baseline_val * 100
                    improvements[key] = {
                        'baseline': baseline_val,
                        'optimized': optimized_val,
                        'improvement_percent': improvement
                    }
        
        # Restore original settings
        self.cpu_optimizer.restore_original_settings()
        
        return improvements
    
    def _measure_system_latency(self) -> Dict:
        """Measure system baseline latency"""
        def simple_operation():
            return sum(range(1000))
        
        def memory_operation():
            data = bytearray(1024)
            return len(data)
        
        def context_switch():
            threading.Event().set()
            return True
        
        return {
            'simple_op': self.measure_latency(simple_operation, self.iterations['comprehensive'])['mean_ns'],
            'memory_op': self.measure_latency(memory_operation, self.iterations['comprehensive'])['mean_ns'],
            'context_switch': self.measure_latency(context_switch, self.iterations['quick'])['mean_ns']
        }
    
    def run_comprehensive_benchmark(self) -> Dict:
        """Run comprehensive benchmark suite"""
        print("Starting Comprehensive Ultra-Low-Latency Benchmark")
        print("=" * 60)
        
        # System information
        system_info = self._get_system_info()
        
        # Optimization impact
        optimization_results = self.benchmark_optimization_impact()
        
        # Benchmark all implementations
        all_results = {
            'system_info': system_info,
            'optimization_impact': optimization_results,
            'benchmarks': {
                'zero_copy_rdma': self.benchmark_zero_copy_rdma(),
                'udp_bridge': self.benchmark_udp_bridge(),
                'ultra_dma': self.benchmark_ultra_dma(),
                'kernel_bypass': self.benchmark_kernel_bypass()
            }
        }
        
        # Generate summary
        summary = self._generate_summary(all_results)
        all_results['summary'] = summary
        
        return all_results
    
    def _get_system_info(self) -> Dict:
        """Get system information for benchmark context"""
        import psutil
        import platform
        
        return {
            'cpu_count': psutil.cpu_count(logical=True),
            'cpu_physical': psutil.cpu_count(logical=False),
            'cpu_freq': psutil.cpu_freq().current if psutil.cpu_freq() else None,
            'memory_gb': psutil.virtual_memory().total / (1024**3),
            'platform': platform.platform(),
            'python_version': platform.python_version(),
            'rdtsc_available': self.use_rdtsc
        }
    
    def _generate_summary(self, results: Dict) -> Dict:
        """Generate performance summary"""
        summary = {
            'best_implementation': None,
            'lowest_latency': float('inf'),
            'highest_throughput': 0,
            'optimization_benefits': {}
        }
        
        # Find best performing implementation
        for impl_name, impl_results in results['benchmarks'].items():
            if 'error' in impl_results:
                continue
            
            for size_key, size_results in impl_results.items():
                if 'write' in size_results:
                    latency = size_results['write']['mean_ns']
                    if latency < summary['lowest_latency']:
                        summary['lowest_latency'] = latency
                        summary['best_implementation'] = f"{impl_name}_{size_key}_write"
                
                if 'throughput_mbps' in size_results:
                    throughput = size_results['throughput_mbps']
                    if throughput > summary['highest_throughput']:
                        summary['highest_throughput'] = throughput
                        summary['best_implementation'] = f"{impl_name}_{size_key}"
        
        # Optimization benefits
        for op_name, benefits in results['optimization_impact'].items():
            summary['optimization_benefits'][op_name] = benefits['improvement_percent']
        
        return summary
    
    def save_results(self, results: Dict, filename: str = "ultra_latency_benchmark.json"):
        """Save benchmark results to file"""
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"Results saved to {filename}")
    
    def generate_report(self, results: Dict, filename: str = "ultra_latency_report.txt"):
        """Generate human-readable report"""
        with open(filename, 'w') as f:
            f.write("Ultra-Low-Latency DMA Benchmark Report\n")
            f.write("=" * 50 + "\n\n")
            
            # System info
            f.write("System Information:\n")
            f.write("-" * 20 + "\n")
            for key, value in results['system_info'].items():
                f.write(f"{key}: {value}\n")
            f.write("\n")
            
            # Optimization impact
            f.write("CPU Optimization Impact:\n")
            f.write("-" * 25 + "\n")
            for op, benefits in results['optimization_impact'].items():
                f.write(f"{op}: {benefits['improvement_percent']:.1f}% improvement\n")
            f.write("\n")
            
            # Benchmark results
            f.write("Benchmark Results:\n")
            f.write("-" * 18 + "\n")
            
            for impl_name, impl_results in results['benchmarks'].items():
                if 'error' in impl_results:
                    f.write(f"{impl_name}: ERROR - {impl_results['error']}\n")
                    continue
                
                f.write(f"\n{impl_name.upper()}:\n")
                
                for size_key, size_results in impl_results.items():
                    size = size_key.split('_')[1]
                    f.write(f"  {size} bytes:\n")
                    
                    if 'write' in size_results:
                        write_res = size_results['write']
                        f.write(f"    Write: {write_res['mean_ns']:.2f}ns avg, "
                               f"{write_res['p99_ns']:.2f}ns p99\n")
                    
                    if 'read' in size_results:
                        read_res = size_results['read']
                        f.write(f"    Read:  {read_res['mean_ns']:.2f}ns avg, "
                               f"{read_res['p99_ns']:.2f}ns p99\n")
                    
                    if 'throughput_mbps' in size_results:
                        f.write(f"    Throughput: {size_results['throughput_mbps']:.2f} MB/s\n")
            
            # Summary
            f.write(f"\nSUMMARY:\n")
            f.write("-" * 8 + "\n")
            summary = results['summary']
            f.write(f"Best implementation: {summary['best_implementation']}\n")
            f.write(f"Lowest latency: {summary['lowest_latency']:.2f} ns\n")
            f.write(f"Highest throughput: {summary['highest_throughput']:.2f} MB/s\n")
        
        print(f"Report saved to {filename}")
    
    def plot_results(self, results: Dict, filename: str = "ultra_latency_charts.png"):
        """Generate performance charts"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        # Latency comparison
        implementations = []
        latencies = []
        
        for impl_name, impl_results in results['benchmarks'].items():
            if 'error' in impl_results:
                continue
            
            for size_key, size_results in impl_results.items():
                if 'write' in size_results:
                    implementations.append(f"{impl_name}_{size_key.split('_')[1]}B")
                    latencies.append(size_results['write']['mean_ns'])
        
        if implementations:
            ax1.bar(implementations, latencies)
            ax1.set_title('Write Latency Comparison')
            ax1.set_ylabel('Latency (ns)')
            ax1.tick_params(axis='x', rotation=45)
        
        # Throughput comparison
        impls = []
        throughputs = []
        
        for impl_name, impl_results in results['benchmarks'].items():
            if 'error' in impl_results:
                continue
            
            for size_key, size_results in impl_results.items():
                if 'throughput_mbps' in size_results:
                    impls.append(f"{impl_name}_{size_key.split('_')[1]}B")
                    throughputs.append(size_results['throughput_mbps'])
        
        if impls:
            ax2.bar(impls, throughputs)
            ax2.set_title('Throughput Comparison')
            ax2.set_ylabel('Throughput (MB/s)')
            ax2.tick_params(axis='x', rotation=45)
        
        # Optimization impact
        ops = []
        improvements = []
        
        for op, benefits in results['optimization_impact'].items():
            ops.append(op)
            improvements.append(benefits['improvement_percent'])
        
        if ops:
            ax3.bar(ops, improvements)
            ax3.set_title('CPU Optimization Impact')
            ax3.set_ylabel('Improvement (%)')
            ax3.tick_params(axis='x', rotation=45)
        
        # Latency distribution (for best implementation)
        best_impl = results['summary']['best_implementation']
        if best_impl:
            # Find the implementation and plot latency distribution
            for impl_name, impl_results in results['benchmarks'].items():
                if best_impl.startswith(impl_name):
                    for size_key, size_results in impl_results.items():
                        if 'write' in size_results:
                            # Generate synthetic distribution based on stats
                            mean = size_results['write']['mean_ns']
                            std = size_results['write']['std_ns']
                            
                            samples = np.random.normal(mean, std, 1000)
                            ax4.hist(samples, bins=50, alpha=0.7)
                            ax4.set_title(f'Latency Distribution - {best_impl}')
                            ax4.set_xlabel('Latency (ns)')
                            ax4.set_ylabel('Frequency')
                            break
        
        plt.tight_layout()
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"Charts saved to {filename}")

def main():
    """Main benchmark execution"""
    print("Ultra-Low-Latency DMA Benchmark Suite")
    print("=" * 50)
    
    benchmark = LatencyBenchmark()
    
    # Run comprehensive benchmark
    results = benchmark.run_comprehensive_benchmark()
    
    # Save results
    timestamp = int(time.time())
    benchmark.save_results(results, f"benchmark_results_{timestamp}.json")
    benchmark.generate_report(results, f"benchmark_report_{timestamp}.txt")
    
    # Generate charts
    try:
        benchmark.plot_results(results, f"benchmark_charts_{timestamp}.png")
    except Exception as e:
        print(f"Failed to generate charts: {e}")
    
    # Print summary
    print("\n" + "=" * 50)
    print("BENCHMARK SUMMARY")
    print("=" * 50)
    summary = results['summary']
    print(f"Best implementation: {summary['best_implementation']}")
    print(f"Lowest latency: {summary['lowest_latency']:.2f} ns")
    print(f"Highest throughput: {summary['highest_throughput']:.2f} MB/s")
    
    print("\nCPU Optimization Benefits:")
    for op, benefit in summary['optimization_benefits'].items():
        print(f"  {op}: {benefit:.1f}% improvement")
    
    print(f"\nDetailed results saved to benchmark_*_{timestamp}.*")

if __name__ == "__main__":
    main()
