#!/usr/bin/env python3
"""
Performance Profiling and Optimization Tools
Advanced profiling for identifying bottlenecks and optimization opportunities
"""

import time
import threading
import psutil
import cProfile
import pstats
import io
import json
import tracemalloc
import gc
from typing import Dict, List, Optional, Callable, Any, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

@dataclass
class ProfileResult:
    """Profile analysis result"""
    function_name: str
    total_time: float
    cumulative_time: float
    calls: int
    avg_time: float
    per_call_time: float
    self_time: float
    memory_usage: int
    cpu_usage: float

@dataclass
class PerformanceMetrics:
    """Comprehensive performance metrics"""
    timestamp: float
    cpu_percent: float
    memory_mb: float
    memory_percent: float
    disk_read_mb: float
    disk_write_mb: float
    network_sent_mb: float
    network_recv_mb: float
    thread_count: int
    context_switches: int
    page_faults: int

class RealTimeProfiler:
    """Real-time performance profiler for DMA operations"""
    
    def __init__(self, sample_interval: float = 0.1):
        self.sample_interval = sample_interval
        self.running = False
        self.profiler_thread = None
        
        # Performance data storage
        self.metrics_history: List[PerformanceMetrics] = []
        self.function_profiles: Dict[str, ProfileResult] = {}
        self.bottleneck_functions: List[str] = []
        
        # Profiling state
        self.cpu_profiler = None
        self.memory_profiler = None
        self.call_stack_profiler = None
        
        # Thread safety
        self.lock = threading.RLock()
        
        # Process handle
        self.process = psutil.Process()
    
    def start_profiling(self):
        """Start real-time profiling"""
        with self.lock:
            self.running = True
            
            # Start CPU profiling
            self.cpu_profiler = cProfile.Profile()
            self.cpu_profiler.enable()
            
            # Start memory profiling
            tracemalloc.start()
            
            # Start monitoring thread
            self.profiler_thread = threading.Thread(target=self._profiling_worker)
            self.profiler_thread.daemon = True
            self.profiler_thread.start()
    
    def stop_profiling(self):
        """Stop profiling and analyze results"""
        with self.lock:
            self.running = False
            
            if self.profiler_thread:
                self.profiler_thread.join(timeout=2.0)
            
            # Stop CPU profiling
            if self.cpu_profiler:
                self.cpu_profiler.disable()
                self._analyze_cpu_profile()
            
            # Stop memory profiling
            snapshot = tracemalloc.take_snapshot()
            self._analyze_memory_profile(snapshot)
            
            # Identify bottlenecks
            self._identify_bottlenecks()
    
    def _profiling_worker(self):
        """Background profiling worker thread"""
        while self.running:
            try:
                # Collect system metrics
                metrics = self._collect_metrics()
                
                with self.lock:
                    self.metrics_history.append(metrics)
                    
                    # Keep only last 1000 samples
                    if len(self.metrics_history) > 1000:
                        self.metrics_history = self.metrics_history[-1000:]
                
                time.sleep(self.sample_interval)
                
            except Exception as e:
                print(f"Profiling worker error: {e}")
                time.sleep(1.0)
    
    def _collect_metrics(self) -> PerformanceMetrics:
        """Collect current system metrics"""
        try:
            # CPU and memory
            cpu_percent = self.process.cpu_percent()
            memory_info = self.process.memory_info()
            
            # Disk I/O
            disk_io = self.process.io_counters()
            
            # Network I/O
            network_io = self.process.io_counters()
            
            # Thread and context switches
            threads = self.process.threads()
            num_threads = len(threads)
            
            # Get context switches (platform dependent)
            try:
                context_switches = self.process.num_ctx_switches()
            except:
                context_switches = 0
            
            # Get page faults
            try:
                page_faults = self.process.num_page_faults()
            except:
                page_faults = 0
            
            return PerformanceMetrics(
                timestamp=time.time(),
                cpu_percent=cpu_percent,
                memory_mb=memory_info.rss / (1024 * 1024),
                memory_percent=memory_info.percent,
                disk_read_mb=disk_io.read_bytes / (1024 * 1024),
                disk_write_mb=disk_io.write_bytes / (1024 * 1024),
                network_sent_mb=network_io.send_bytes / (1024 * 1024),
                network_recv_mb=network_io.recv_bytes / (1024 * 1024),
                thread_count=num_threads,
                context_switches=context_switches,
                page_faults=page_faults
            )
        
        except Exception as e:
            print(f"Metrics collection error: {e}")
            return PerformanceMetrics(time.time(), 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    
    def _analyze_cpu_profile(self):
        """Analyze CPU profiling results"""
        if not self.cpu_profiler:
            return
        
        # Create stats object
        stats = pstats.Stats(self.cpu_profiler)
        
        # Sort by cumulative time
        stats.sort_stats('cumulative')
        
        # Extract top functions
        for func_info in stats.stats_info:
            if func_info.calls > 0:
                result = ProfileResult(
                    function_name=func_info.funcname,
                    total_time=func_info.totaltime,
                    cumulative_time=func_info.cumtime,
                    calls=func_info.calls,
                    avg_time=func_info.totaltime / func_info.calls,
                    per_call_time=func_info.perccall,
                    self_time=func_info.inlinetime,
                    memory_usage=0,  # Will be filled later
                    cpu_usage=0   # Will be calculated later
                )
                
                self.function_profiles[func_info.funcname] = result
    
    def _analyze_memory_profile(self, snapshot):
        """Analyze memory profiling results"""
        try:
            # Get top memory allocations
            top_stats = snapshot.statistics('lineno')
            
            for stat in top_stats[:20]:  # Top 20 allocations
                func_name = f"{stat.traceback[0].filename}:{stat.traceback[0].lineno}"
                
                if func_name in self.function_profiles:
                    self.function_profiles[func_name].memory_usage = stat.size
        
        except Exception as e:
            print(f"Memory profile analysis error: {e}")
    
    def _identify_bottlenecks(self):
        """Identify performance bottlenecks"""
        self.bottleneck_functions.clear()
        
        # Sort functions by total time
        sorted_functions = sorted(
            self.function_profiles.values(),
            key=lambda x: x.total_time,
            reverse=True
        )
        
        # Identify top bottlenecks
        for i, func in enumerate(sorted_functions[:10]):
            if func.total_time > 0.001:  # More than 1ms
                self.bottleneck_functions.append(func.function_name)
    
    def profile_function(self, func: Callable, *args, **kwargs) -> ProfileResult:
        """Profile a specific function"""
        # Create temporary profiler
        profiler = cProfile.Profile()
        
        # Profile the function
        start_time = time.time()
        start_memory = self.process.memory_info().rss
        
        profiler.enable()
        result = func(*args, **kwargs)
        profiler.disable()
        
        end_time = time.time()
        end_memory = self.process.memory_info().rss
        
        # Analyze results
        stats = pstats.Stats(profiler)
        stats.sort_stats('cumulative')
        
        if stats.stats_info:
            func_info = stats.stats_info[0]
            
            return ProfileResult(
                function_name=func_info.funcname,
                total_time=func_info.totaltime,
                cumulative_time=func_info.cumtime,
                calls=func_info.calls,
                avg_time=func_info.totaltime / func_info.calls,
                per_call_time=func_info.perccall,
                self_time=func_info.inlinetime,
                memory_usage=end_memory - start_memory,
                cpu_usage=0
            )
        
        return ProfileResult(
            function_name=func.__name__,
            total_time=end_time - start_time,
            cumulative_time=end_time - start_time,
            calls=1,
            avg_time=end_time - start_time,
            per_call_time=end_time - start_time,
            self_time=end_time - start_time,
            memory_usage=end_memory - start_memory,
            cpu_usage=0
        )
    
    def get_metrics_summary(self) -> Dict:
        """Get summary of collected metrics"""
        if not self.metrics_history:
            return {}
        
        # Calculate averages and extremes
        cpu_values = [m.cpu_percent for m in self.metrics_history]
        memory_values = [m.memory_mb for m in self.metrics_history]
        throughput_values = [(m.network_sent_mb + m.network_recv_mb) / 
                          (m.timestamp - self.metrics_history[0].timestamp) 
                          if len(self.metrics_history) > 1 else 0
                          for m in self.metrics_history]
        
        return {
            'avg_cpu': np.mean(cpu_values) if cpu_values else 0,
            'max_cpu': np.max(cpu_values) if cpu_values else 0,
            'avg_memory_mb': np.mean(memory_values) if memory_values else 0,
            'max_memory_mb': np.max(memory_values) if memory_values else 0,
            'avg_throughput_mbps': np.mean(throughput_values) if throughput_values else 0,
            'max_throughput_mbps': np.max(throughput_values) if throughput_values else 0,
            'total_samples': len(self.metrics_history),
            'profile_duration': self.metrics_history[-1].timestamp - self.metrics_history[0].timestamp if len(self.metrics_history) > 1 else 0
        }
    
    def get_bottleneck_report(self) -> Dict:
        """Get detailed bottleneck analysis"""
        if not self.bottleneck_functions:
            return {}
        
        report = {
            'top_bottlenecks': [],
            'recommendations': []
        }
        
        for func_name in self.bottleneck_functions:
            if func_name in self.function_profiles:
                func = self.function_profiles[func_name]
                
                report['top_bottlenecks'].append({
                    'function': func_name,
                    'total_time': func.total_time,
                    'calls': func.calls,
                    'avg_time': func.avg_time,
                    'memory_usage': func.memory_usage
                })
                
                # Generate recommendations
                if func.total_time > 0.1:  # > 100ms
                    report['recommendations'].append(
                        f"Function {func_name} is very slow ({func.total_time:.3f}s). "
                        f"Consider optimizing or caching results."
                    )
                
                if func.memory_usage > 1024 * 1024:  # > 1MB
                    report['recommendations'].append(
                        f"Function {func_name} uses {func.memory_usage / (1024*1024):.1f}MB memory. "
                        f"Consider reducing memory allocations."
                    )
                
                if func.calls > 1000:
                    report['recommendations'].append(
                        f"Function {func_name} called {func.calls} times. "
                        f"Consider batching or reducing call frequency."
                    )
        
        return report
    
    def generate_performance_report(self, output_file: str = "performance_report.html"):
        """Generate comprehensive performance report"""
        try:
            # Create HTML report
            html_content = self._generate_html_report()
            
            with open(output_file, 'w') as f:
                f.write(html_content)
            
            print(f"Performance report saved to {output_file}")
            
        except Exception as e:
            print(f"Failed to generate report: {e}")
    
    def _generate_html_report(self) -> str:
        """Generate HTML performance report"""
        metrics_summary = self.get_metrics_summary()
        bottleneck_report = self.get_bottleneck_report()
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Software-Defined RDMA Performance Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }}
                .section {{ margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }}
                .metric {{ display: inline-block; margin: 10px; padding: 10px; background: #ecf0f1; border-radius: 3px; }}
                table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .bottleneck {{ background: #fff3cd; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Software-Defined RDMA Performance Report</h1>
                <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="section">
                <h2>Performance Summary</h2>
                <div class="metric">Avg CPU: {metrics_summary.get('avg_cpu', 0):.1f}%</div>
                <div class="metric">Max CPU: {metrics_summary.get('max_cpu', 0):.1f}%</div>
                <div class="metric">Avg Memory: {metrics_summary.get('avg_memory_mb', 0):.1f}MB</div>
                <div class="metric">Max Memory: {metrics_summary.get('max_memory_mb', 0):.1f}MB</div>
                <div class="metric">Avg Throughput: {metrics_summary.get('avg_throughput_mbps', 0):.1f}MB/s</div>
                <div class="metric">Max Throughput: {metrics_summary.get('max_throughput_mbps', 0):.1f}MB/s</div>
                <div class="metric">Duration: {metrics_summary.get('profile_duration', 0):.1f}s</div>
            </div>
            
            <div class="section">
                <h2>Performance Bottlenecks</h2>
                <table>
                    <tr><th>Function</th><th>Total Time</th><th>Calls</th><th>Avg Time</th><th>Memory Usage</th></tr>
        """
        
        for bottleneck in bottleneck_report.get('top_bottlenecks', []):
            html += f"""
                    <tr class="bottleneck">
                        <td>{bottleneck['function']}</td>
                        <td>{bottleneck['total_time']:.6f}s</td>
                        <td>{bottleneck['calls']}</td>
                        <td>{bottleneck['avg_time']:.6f}s</td>
                        <td>{bottleneck['memory_usage'] / (1024*1024):.1f}MB</td>
                    </tr>
            """
        
        html += """
                </table>
            </div>
            
            <div class="section">
                <h2>Optimization Recommendations</h2>
                <ul>
        """
        
        for recommendation in bottleneck_report.get('recommendations', []):
            html += f"<li>{recommendation}</li>"
        
        html += """
                </ul>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def create_performance_charts(self, output_file: str = "performance_charts.png"):
        """Create performance visualization charts"""
        try:
            if not self.metrics_history:
                print("No metrics data available for charts")
                return
            
            # Extract data
            timestamps = [m.timestamp for m in self.metrics_history]
            cpu_usage = [m.cpu_percent for m in self.metrics_history]
            memory_usage = [m.memory_mb for m in self.metrics_history]
            network_usage = [(m.network_sent_mb + m.network_recv_mb) for m in self.metrics_history]
            
            # Create subplots
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
            
            # CPU usage chart
            ax1.plot(timestamps, cpu_usage, 'b-', label='CPU Usage')
            ax1.set_title('CPU Usage Over Time')
            ax1.set_xlabel('Time')
            ax1.set_ylabel('CPU %')
            ax1.grid(True)
            ax1.legend()
            
            # Memory usage chart
            ax2.plot(timestamps, memory_usage, 'r-', label='Memory Usage')
            ax2.set_title('Memory Usage Over Time')
            ax2.set_xlabel('Time')
            ax2.set_ylabel('Memory (MB)')
            ax2.grid(True)
            ax2.legend()
            
            # Network usage chart
            ax3.plot(timestamps, network_usage, 'g-', label='Network Usage')
            ax3.set_title('Network Usage Over Time')
            ax3.set_xlabel('Time')
            ax3.set_ylabel('Network (MB)')
            ax3.grid(True)
            ax3.legend()
            
            # Combined performance chart
            ax4.plot(timestamps, cpu_usage, 'b-', alpha=0.7, label='CPU')
            ax4.plot(timestamps, memory_usage, 'r-', alpha=0.7, label='Memory')
            ax4.plot(timestamps, network_usage, 'g-', alpha=0.7, label='Network')
            ax4.set_title('Combined Performance Metrics')
            ax4.set_xlabel('Time')
            ax4.set_ylabel('Usage')
            ax4.grid(True)
            ax4.legend()
            
            plt.tight_layout()
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"Performance charts saved to {output_file}")
            
        except Exception as e:
            print(f"Failed to create charts: {e}")

class OptimizationAdvisor:
    """AI-powered optimization advisor"""
    
    def __init__(self):
        self.optimization_rules = self._load_optimization_rules()
    
    def _load_optimization_rules(self) -> Dict:
        """Load optimization rules"""
        return {
            'high_cpu': {
                'threshold': 80.0,
                'recommendations': [
                    "Reduce CPU-intensive operations",
                    "Use more efficient algorithms",
                    "Enable CPU optimization features",
                    "Consider hardware acceleration"
                ]
            },
            'high_memory': {
                'threshold': 85.0,
                'recommendations': [
                    "Reduce memory allocations",
                    "Use memory pools or object caching",
                    "Implement zero-copy operations",
                    "Profile for memory leaks"
                ]
            },
            'high_latency': {
                'threshold': 0.001,  # 1ms
                'recommendations': [
                    "Optimize critical path",
                    "Use lock-free data structures",
                    "Reduce system call overhead",
                    "Enable kernel bypass features"
                ]
            },
            'low_throughput': {
                'threshold': 100.0,  # MB/s
                'recommendations': [
                    "Increase parallelism",
                    "Optimize network stack",
                    "Use larger packet sizes",
                    "Enable hardware offload"
                ]
            }
        }
    
    def analyze_performance(self, metrics_summary: Dict, bottleneck_report: Dict) -> Dict:
        """Analyze performance and provide recommendations"""
        analysis = {
            'issues': [],
            'recommendations': [],
            'priority_actions': [],
            'optimization_score': 100
        }
        
        # Check each metric against thresholds
        for metric, rule in self.optimization_rules.items():
            if metric in metrics_summary:
                value = metrics_summary[metric]
                threshold = rule['threshold']
                
                if (metric == 'high_cpu' and value > threshold) or \
                   (metric == 'high_memory' and value > threshold) or \
                   (metric == 'high_latency' and value > threshold) or \
                   (metric == 'low_throughput' and value < threshold):
                    
                    analysis['issues'].append(metric)
                    analysis['recommendations'].extend(rule['recommendations'])
                    analysis['optimization_score'] -= 25
        
        # Add bottleneck-specific recommendations
        for bottleneck in bottleneck_report.get('top_bottlenecks', []):
            if bottleneck['total_time'] > 0.1:  # > 100ms
                analysis['priority_actions'].append(
                    f"Optimize {bottleneck['function']} (slow function)"
                )
            
            if bottleneck['memory_usage'] > 1024 * 1024:  # > 1MB
                analysis['priority_actions'].append(
                    f"Reduce memory usage in {bottleneck['function']}"
                )
        
        return analysis

def demo_performance_profiler():
    """Demonstration of performance profiler"""
    print("Performance Profiler Demo")
    print("=" * 30)
    
    # Create profiler
    profiler = RealTimeProfiler(sample_interval=0.1)
    
    # Test function to profile
    def test_function():
        # Simulate some work
        time.sleep(0.01)
        data = [i for i in range(1000)]
        return sum(data)
    
    # Profile the function
    print("Profiling test function...")
    result = profiler.profile_function(test_function)
    
    print(f"Function profiling result:")
    print(f"  Function: {result.function_name}")
    print(f"  Total time: {result.total_time:.6f}s")
    print(f"  Calls: {result.calls}")
    print(f"  Memory usage: {result.memory_usage} bytes")
    
    # Start real-time profiling
    print("\nStarting real-time profiling...")
    profiler.start_profiling()
    
    # Simulate some work
    for i in range(50):
        test_function()
        time.sleep(0.1)
    
    # Stop profiling
    profiler.stop_profiling()
    
    # Get results
    metrics_summary = profiler.get_metrics_summary()
    bottleneck_report = profiler.get_bottleneck_report()
    
    print(f"\nMetrics Summary:")
    for key, value in metrics_summary.items():
        print(f"  {key}: {value}")
    
    print(f"\nTop Bottlenecks:")
    for bottleneck in bottleneck_report.get('top_bottlenecks', [])[:3]:
        print(f"  {bottleneck['function']}: {bottleneck['total_time']:.6f}s")
    
    print(f"\nRecommendations:")
    for rec in bottleneck_report.get('recommendations', [])[:3]:
        print(f"  • {rec}")
    
    # Generate reports
    profiler.generate_performance_report("demo_performance_report.html")
    profiler.create_performance_charts("demo_performance_charts.png")
    
    # Optimization analysis
    advisor = OptimizationAdvisor()
    analysis = advisor.analyze_performance(metrics_summary, bottleneck_report)
    
    print(f"\nOptimization Analysis:")
    print(f"  Issues: {analysis['issues']}")
    print(f"  Optimization Score: {analysis['optimization_score']}")
    print(f"  Priority Actions: {len(analysis['priority_actions'])}")

if __name__ == "__main__":
    demo_performance_profiler()
