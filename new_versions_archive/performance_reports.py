#!/usr/bin/env python3
"""
Performance Reports Generator
Generates comprehensive performance reports with analytics and insights.
"""

import sqlite3
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
# import pandas as pd  # Removed dependency

class PerformanceReports:
    """Generates comprehensive performance reports"""
    
    def __init__(self, db_path="system_monitoring.db"):
        self.db_path = os.path.join(os.path.dirname(__file__), db_path)
        
    def generate_daily_report(self, date=None) -> Dict[str, Any]:
        """Generate daily performance report"""
        if date is None:
            date = datetime.now().date()
        
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Get metrics for the specified date
            start_time = datetime.combine(date, datetime.min.time())
            end_time = start_time + timedelta(days=1)
            
            query = '''
                SELECT * FROM system_metrics 
                WHERE timestamp BETWEEN ? AND ?
                ORDER BY timestamp
            '''
            
            cursor.execute(query, (start_time, end_time))
            rows = cursor.fetchall()
            
            # Convert to list of dictionaries
            columns = ['id', 'timestamp', 'cpu_usage', 'cpu_freq', 'cpu_temp', 'ram_usage', 'ram_used', 'ram_total', 'gpu_usage', 'gpu_memory_used', 'gpu_memory_total', 'gpu_temp', 'network_sent', 'network_recv', 'disk_read', 'disk_write', 'disk_queue']
            df = [dict(zip(columns, row)) for row in rows]
            conn.close()
            
            if len(df) == 0:
                return {"error": "No data available for the specified date"}
            
            # Calculate statistics
            report = {
                "date": date.isoformat(),
                "generated_at": datetime.now().isoformat(),
                "summary": self._calculate_summary_stats(df),
                "cpu_analysis": self._analyze_cpu_performance(df),
                "memory_analysis": self._analyze_memory_performance(df),
                "gpu_analysis": self._analyze_gpu_performance(df),
                "network_analysis": self._analyze_network_performance(df),
                "disk_analysis": self._analyze_disk_performance(df),
                "alerts_summary": self._get_alerts_summary(date),
                "recommendations": self._generate_recommendations(df),
                "health_score": self._calculate_health_score(df)
            }
            
            return report
            
        except Exception as e:
            return {"error": f"Failed to generate report: {e}"}
    
    def generate_weekly_report(self, start_date=None) -> Dict[str, Any]:
        """Generate weekly performance report"""
        if start_date is None:
            start_date = datetime.now().date() - timedelta(days=7)
        
        end_date = start_date + timedelta(days=7)
        
        try:
            conn = sqlite3.connect(self.db_path)
            
            query = '''
                SELECT * FROM system_metrics 
                WHERE timestamp BETWEEN ? AND ?
                ORDER BY timestamp
            '''
            
            cursor.execute(query, (start_date, end_date))
            rows = cursor.fetchall()
            
            # Convert to list of dictionaries
            columns = ['id', 'timestamp', 'cpu_usage', 'cpu_freq', 'cpu_temp', 'ram_usage', 'ram_used', 'ram_total', 'gpu_usage', 'gpu_memory_used', 'gpu_memory_total', 'gpu_temp', 'network_sent', 'network_recv', 'disk_read', 'disk_write', 'disk_queue']
            df = [dict(zip(columns, row)) for row in rows]
            conn.close()
            
            if len(df) == 0:
                return {"error": "No data available for the specified period"}
            
            # Generate daily summaries
            daily_reports = []
            for day in range(7):
                current_date = start_date + timedelta(days=day)
                daily_report = self.generate_daily_report(current_date)
                if "error" not in daily_report:
                    daily_reports.append(daily_report)
            
            # Weekly summary
            report = {
                "period": f"{start_date.isoformat()} to {end_date.isoformat()}",
                "generated_at": datetime.now().isoformat(),
                "type": "weekly",
                "daily_reports": daily_reports,
                "weekly_summary": self._calculate_weekly_summary(daily_reports),
                "trends": self._analyze_trends(df),
                "performance_comparison": self._compare_daily_performance(daily_reports),
                "weekly_recommendations": self._generate_weekly_recommendations(daily_reports),
                "overall_health_score": self._calculate_weekly_health_score(daily_reports)
            }
            
            return report
            
        except Exception as e:
            return {"error": f"Failed to generate weekly report: {e}"}
    
    def _calculate_summary_stats(self, df: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate summary statistics"""
        if not df:
            return {"error": "No data available"}
        
        # Extract values from list of dictionaries
        cpu_values = [row['cpu_usage'] for row in df]
        memory_values = [row['ram_usage'] for row in df]
        gpu_values = [row['gpu_usage'] for row in df if 'gpu_usage' in row]
        network_sent = [row['network_sent'] for row in df]
        network_recv = [row['network_recv'] for row in df]
        disk_read = [row['disk_read'] for row in df]
        disk_write = [row['disk_write'] for row in df]
        timestamps = [row['timestamp'] for row in df]
        
        return {
            "total_data_points": len(df),
            "monitoring_period": {
                "start": min(timestamps),
                "end": max(timestamps)
            },
            "average_cpu": sum(cpu_values) / len(cpu_values),
            "max_cpu": max(cpu_values),
            "average_memory": sum(memory_values) / len(memory_values),
            "max_memory": max(memory_values),
            "average_gpu": sum(gpu_values) / len(gpu_values) if gpu_values else 0,
            "max_gpu": max(gpu_values) if gpu_values else 0,
            "total_network_io": sum(network_sent) + sum(network_recv),
            "total_disk_io": sum(disk_read) + sum(disk_write)
        }
    
    def _analyze_cpu_performance(self, df: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze CPU performance in detail"""
        cpu_values = [row['cpu_usage'] for row in df]
        
        if not cpu_values:
            return {"error": "No CPU data available"}
        
        # Calculate statistics
        avg_cpu = sum(cpu_values) / len(cpu_values)
        max_cpu = max(cpu_values)
        min_cpu = min(cpu_values)
        
        # Standard deviation
        variance = sum((x - avg_cpu) ** 2 for x in cpu_values) / len(cpu_values)
        std_dev = variance ** 0.5
        
        # Usage distribution
        idle = sum(1 for x in cpu_values if x < 20)
        light = sum(1 for x in cpu_values if 20 <= x < 50)
        moderate = sum(1 for x in cpu_values if 50 <= x < 80)
        heavy = sum(1 for x in cpu_values if 80 <= x < 95)
        critical = sum(1 for x in cpu_values if x >= 95)
        
        return {
            "average_usage": avg_cpu,
            "peak_usage": max_cpu,
            "minimum_usage": min_cpu,
            "standard_deviation": std_dev,
            "usage_distribution": {
                "idle": idle,
                "light": light,
                "moderate": moderate,
                "heavy": heavy,
                "critical": critical
            },
            "performance_trend": self._calculate_trend(cpu_values),
            "efficiency_score": self._calculate_cpu_efficiency(df),
            "bottleneck_periods": self._identify_bottleneck_periods(cpu_values, threshold=80)
        }
    
    def _analyze_memory_performance(self, df: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze memory performance in detail"""
        memory_values = [row['ram_usage'] for row in df]
        
        if not memory_values:
            return {"error": "No memory data available"}
        
        # Calculate statistics
        avg_memory = sum(memory_values) / len(memory_values)
        max_memory = max(memory_values)
        min_memory = min(memory_values)
        
        # Standard deviation
        variance = sum((x - avg_memory) ** 2 for x in memory_values) / len(memory_values)
        std_dev = variance ** 0.5
        
        # Usage distribution
        free = sum(1 for x in memory_values if x < 50)
        light = sum(1 for x in memory_values if 50 <= x < 70)
        moderate = sum(1 for x in memory_values if 70 <= x < 85)
        heavy = sum(1 for x in memory_values if 85 <= x < 95)
        critical = sum(1 for x in memory_values if x >= 95)
        
        # Available memory
        available_memory = [(row['ram_total'] - row['ram_used']) for row in df]
        avg_available = sum(available_memory) / len(available_memory)
        min_available = min(available_memory)
        
        return {
            "average_usage": avg_memory,
            "peak_usage": max_memory,
            "minimum_usage": min_memory,
            "standard_deviation": std_dev,
            "usage_distribution": {
                "free": free,
                "light": light,
                "moderate": moderate,
                "heavy": heavy,
                "critical": critical
            },
            "memory_pressure_events": sum(1 for x in memory_values if x > 90),
            "average_available_gb": avg_available,
            "minimum_available_gb": min_available,
            "memory_leak_indicators": self._detect_memory_leaks(df)
        }
    
    def _analyze_gpu_performance(self, df: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze GPU performance in detail"""
        gpu_values = [row['gpu_usage'] for row in df if 'gpu_usage' in row]
        
        if not gpu_values or sum(gpu_values) == 0:
            return {"status": "No GPU data available"}
        
        # Calculate statistics
        avg_gpu = sum(gpu_values) / len(gpu_values)
        max_gpu = max(gpu_values)
        min_gpu = min(gpu_values)
        
        # Standard deviation
        variance = sum((x - avg_gpu) ** 2 for x in gpu_values) / len(gpu_values)
        std_dev = variance ** 0.5
        
        # Usage distribution
        idle = sum(1 for x in gpu_values if x < 20)
        light = sum(1 for x in gpu_values if 20 <= x < 50)
        moderate = sum(1 for x in gpu_values if 50 <= x < 80)
        heavy = sum(1 for x in gpu_values if 80 <= x < 95)
        critical = sum(1 for x in gpu_values if x >= 95)
        
        # GPU memory utilization
        gpu_memory_ratios = []
        for row in df:
            if 'gpu_memory_used' in row and 'gpu_memory_total' in row and row['gpu_memory_total'] > 0:
                gpu_memory_ratios.append((row['gpu_memory_used'] / row['gpu_memory_total']) * 100)
        
        avg_gpu_memory = sum(gpu_memory_ratios) / len(gpu_memory_ratios) if gpu_memory_ratios else 0
        peak_gpu_memory = max(gpu_memory_ratios) if gpu_memory_ratios else 0
        
        return {
            "average_usage": avg_gpu,
            "peak_usage": max_gpu,
            "minimum_usage": min_gpu,
            "standard_deviation": std_dev,
            "usage_distribution": {
                "idle": idle,
                "light": light,
                "moderate": moderate,
                "heavy": heavy,
                "critical": critical
            },
            "memory_utilization": {
                "average_gpu_memory": avg_gpu_memory,
                "peak_gpu_memory": peak_gpu_memory
            },
            "thermal_performance": self._analyze_thermal_performance(df),
            "gaming_periods": self._identify_gaming_periods(df)
        }
    
    def _analyze_network_performance(self, df: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze network performance"""
        network_sent = [row['network_sent'] for row in df]
        network_recv = [row['network_recv'] for row in df]
        total_io = [sent + recv for sent, recv in zip(network_sent, network_recv)]
        
        return {
            "total_sent_mb": sum(network_sent),
            "total_received_mb": sum(network_recv),
            "total_io_mb": sum(total_io),
            "average_send_rate": self._calculate_diff_average(network_sent),
            "average_receive_rate": self._calculate_diff_average(network_recv),
            "peak_send_rate": self._calculate_diff_max(network_sent),
            "peak_receive_rate": self._calculate_diff_max(network_recv),
            "network_activity_periods": self._identify_network_activity_periods(total_io),
            "bandwidth_utilization": self._calculate_bandwidth_utilization(df)
        }
    
    def _analyze_disk_performance(self, df: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze disk performance"""
        disk_read = [row['disk_read'] for row in df]
        disk_write = [row['disk_write'] for row in df]
        total_io = [read + write for read, write in zip(disk_read, disk_write)]
        
        return {
            "total_read_mb": sum(disk_read),
            "total_write_mb": sum(disk_write),
            "total_io_mb": sum(total_io),
            "average_read_rate": self._calculate_diff_average(disk_read),
            "average_write_rate": self._calculate_diff_average(disk_write),
            "peak_read_rate": self._calculate_diff_max(disk_read),
            "peak_write_rate": self._calculate_diff_max(disk_write),
            "disk_activity_periods": self._identify_disk_activity_periods(total_io),
            "io_efficiency": self._calculate_io_efficiency(df)
        }
    
    def _get_alerts_summary(self, date) -> Dict[str, Any]:
        """Get alerts summary for the date"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            start_time = datetime.combine(date, datetime.min.time())
            end_time = start_time + timedelta(days=1)
            
            query = '''
                SELECT alert_type, severity, COUNT(*) as count
                FROM alerts 
                WHERE timestamp BETWEEN ? AND ?
                GROUP BY alert_type, severity
                ORDER BY count DESC
            '''
            
            cursor = conn.cursor()
            cursor.execute(query, (start_time, end_time))
            
            alerts = []
            for row in cursor.fetchall():
                alerts.append({
                    "type": row[0],
                    "severity": row[1],
                    "count": row[2]
                })
            
            conn.close()
            
            return {
                "total_alerts": sum(alert["count"] for alert in alerts),
                "alerts_by_type": alerts,
                "critical_alerts": sum(alert["count"] for alert in alerts if alert["severity"] == "critical"),
                "warning_alerts": sum(alert["count"] for alert in alerts if alert["severity"] == "warning")
            }
            
        except Exception as e:
            return {"error": f"Failed to get alerts summary: {e}"}
    
    def _generate_recommendations(self, df: List[Dict[str, Any]]) -> List[str]:
        """Generate performance recommendations"""
        recommendations = []
        
        if not df:
            return recommendations
        
        # CPU recommendations
        cpu_values = [row['cpu_usage'] for row in df]
        avg_cpu = sum(cpu_values) / len(cpu_values)
        if avg_cpu > 80:
            recommendations.append("CPU usage is consistently high. Consider upgrading CPU or optimizing background processes.")
        elif avg_cpu > 60:
            recommendations.append("CPU usage is moderately high. Review running processes for optimization opportunities.")
        
        # Memory recommendations
        memory_values = [row['ram_usage'] for row in df]
        avg_memory = sum(memory_values) / len(memory_values)
        if avg_memory > 85:
            recommendations.append("Memory usage is critical. Consider adding more RAM or closing memory-intensive applications.")
        elif avg_memory > 70:
            recommendations.append("Memory usage is high. Monitor for memory leaks and consider optimization.")
        
        # GPU recommendations
        gpu_values = [row['gpu_usage'] for row in df if 'gpu_usage' in row]
        if gpu_values and sum(gpu_values) > 0:
            avg_gpu = sum(gpu_values) / len(gpu_values)
            if avg_gpu > 80:
                recommendations.append("GPU usage is consistently high. Check for background processes or consider GPU upgrade.")
        
        # Disk recommendations
        disk_read = [row['disk_read'] for row in df]
        disk_write = [row['disk_write'] for row in df]
        disk_io = sum(disk_read) + sum(disk_write)
        if disk_io > 10000:  # 10GB+ in a day
            recommendations.append("High disk I/O detected. Consider SSD upgrade or disk cleanup.")
        
        # Network recommendations
        network_sent = [row['network_sent'] for row in df]
        network_recv = [row['network_recv'] for row in df]
        network_io = sum(network_sent) + sum(network_recv)
        if network_io > 5000:  # 5GB+ in a day
            recommendations.append("High network usage detected. Monitor for unusual network activity.")
        
        return recommendations
    
    def _calculate_health_score(self, df: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate overall system health score"""
        scores = {}
        
        if not df:
            return {"overall": 100, "components": {"cpu": 100, "memory": 100, "gpu": 100}, "grade": "A", "status": "Excellent"}
        
        # CPU health score (0-100)
        cpu_values = [row['cpu_usage'] for row in df]
        avg_cpu = sum(cpu_values) / len(cpu_values)
        cpu_score = max(0, 100 - avg_cpu)
        scores['cpu'] = cpu_score
        
        # Memory health score (0-100)
        memory_values = [row['ram_usage'] for row in df]
        avg_memory = sum(memory_values) / len(memory_values)
        memory_score = max(0, 100 - avg_memory)
        scores['memory'] = memory_score
        
        # GPU health score (0-100)
        gpu_values = [row['gpu_usage'] for row in df if 'gpu_usage' in row]
        if gpu_values and sum(gpu_values) > 0:
            avg_gpu = sum(gpu_values) / len(gpu_values)
            gpu_score = max(0, 100 - avg_gpu)
            scores['gpu'] = gpu_score
        else:
            scores['gpu'] = 100  # No GPU usage = good score
        
        # Overall health score
        overall_score = sum(scores.values()) / len(scores)
        
        return {
            "overall": overall_score,
            "components": scores,
            "grade": self._get_health_grade(overall_score),
            "status": self._get_health_status(overall_score)
        }
    
    def _get_health_grade(self, score: float) -> str:
        """Get health grade from score"""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
    
    def _get_health_status(self, score: float) -> str:
        """Get health status from score"""
        if score >= 85:
            return "Excellent"
        elif score >= 70:
            return "Good"
        elif score >= 55:
            return "Fair"
        elif score >= 40:
            return "Poor"
        else:
            return "Critical"
    
    def _calculate_trend(self, data: List[float]) -> str:
        """Calculate trend direction"""
        if len(data) < 2:
            return "insufficient_data"
        
        # Simple linear trend
        x = list(range(len(data)))
        try:
            slope = np.polyfit(x, data, 1)[0]
            
            if slope > 0.5:
                return "increasing"
            elif slope < -0.5:
                return "decreasing"
            else:
                return "stable"
        except:
            return "stable"
    
    def _calculate_cpu_efficiency(self, df: List[Dict[str, Any]]) -> float:
        """Calculate CPU efficiency score"""
        # Efficiency based on usage vs performance
        cpu_values = [row['cpu_usage'] for row in df]
        avg_cpu = sum(cpu_values) / len(cpu_values)
        
        # Standard deviation
        variance = sum((x - avg_cpu) ** 2 for x in cpu_values) / len(cpu_values)
        cpu_std = variance ** 0.5
        
        # Lower standard deviation with reasonable usage = more efficient
        efficiency = max(0, 100 - (avg_cpu + cpu_std))
        return efficiency
    
    def _identify_bottleneck_periods(self, data: List[float], threshold: float) -> List[Dict]:
        """Identify periods where performance is bottlenecked"""
        bottleneck_periods = []
        in_bottleneck = False
        start_idx = 0
        
        for i, value in enumerate(data):
            if value >= threshold and not in_bottleneck:
                in_bottleneck = True
                start_idx = i
            elif value < threshold and in_bottleneck:
                in_bottleneck = False
                bottleneck_periods.append({
                    "start": start_idx,
                    "end": i,
                    "duration": i - start_idx,
                    "peak_value": max(data[start_idx:i])
                })
        
        return bottleneck_periods
    
    def _detect_memory_leaks(self, df: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect potential memory leaks"""
        memory_values = [row['ram_usage'] for row in df]
        
        # Check for steady increase over time
        if len(memory_values) < 10:
            return {"status": "insufficient_data"}
        
        # Calculate trend
        x = list(range(len(memory_values)))
        try:
            slope = np.polyfit(x, memory_values, 1)[0]
        except:
            slope = 0
        
        # Check for high usage with increasing trend
        avg_usage = sum(memory_values) / len(memory_values)
        
        leak_indicators = {
            "increasing_trend": slope > 0.1,
            "high_average_usage": avg_usage > 80,
            "potential_leak": slope > 0.1 and avg_usage > 80,
            "trend_slope": slope,
            "average_usage": avg_usage
        }
        
        return leak_indicators
    
    def _analyze_thermal_performance(self, df: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze thermal performance"""
        gpu_temps = [row.get('gpu_temp', 0) for row in df if 'gpu_temp' in row]
        
        if not gpu_temps:
            return {"status": "No temperature data"}
        
        return {
            "average_temperature": sum(gpu_temps) / len(gpu_temps),
            "peak_temperature": max(gpu_temps),
            "thermal_throttling_events": sum(1 for temp in gpu_temps if temp > 85),
            "temperature_stability": self._calculate_std(gpu_temps),
            "thermal_efficiency": max(0, 100 - sum(gpu_temps) / len(gpu_temps))
        }
    
    def _identify_gaming_periods(self, df: List[Dict[str, Any]]) -> List[Dict]:
        """Identify potential gaming periods"""
        gaming_periods = []
        
        gpu_values = [row.get('gpu_usage', 0) for row in df if 'gpu_usage' in row]
        if not gpu_values:
            return gaming_periods
        
        # Gaming typically involves high GPU and CPU usage
        cpu_values = [row.get('cpu_usage', 0) for row in df if 'cpu_usage' in row]
        
        in_gaming = False
        start_idx = 0
        
        for i, (gpu, cpu) in enumerate(zip(gpu_values, cpu_values)):
            if gpu > 70 and cpu > 50 and not in_gaming:
                in_gaming = True
                start_idx = i
            elif (gpu < 50 or cpu < 30) and in_gaming:
                in_gaming = False
                gaming_periods.append({
                    "start": start_idx,
                    "end": i,
                    "duration": i - start_idx,
                    "peak_gpu": max(gpu_values[start_idx:i]),
                    "peak_cpu": max(cpu_values[start_idx:i])
                })
        
        return gaming_periods
    
    def _identify_network_activity_periods(self, network_data: List[float]) -> List[Dict]:
        """Identify periods of high network activity"""
        activity_periods = []
        if not network_data:
            return activity_periods
        
        # Calculate threshold (top 20% of usage)
        sorted_data = sorted(network_data)
        threshold_index = int(len(sorted_data) * 0.8)
        threshold = sorted_data[threshold_index] if threshold_index < len(sorted_data) else sorted_data[-1]
        
        in_activity = False
        start_idx = 0
        
        for i, value in enumerate(network_data):
            if value >= threshold and not in_activity:
                in_activity = True
                start_idx = i
            elif value < threshold and in_activity:
                in_activity = False
                activity_periods.append({
                    "start": start_idx,
                    "end": i,
                    "duration": i - start_idx,
                    "peak_usage": max(network_data[start_idx:i])
                })
        
        return activity_periods
    
    def _calculate_bandwidth_utilization(self, df: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate bandwidth utilization metrics"""
        # This would require network interface speed data
        # For now, return relative utilization
        network_io = [row['network_sent'] + row['network_recv'] for row in df]
        
        return {
            "average_utilization": sum(network_io) / len(network_io),
            "peak_utilization": max(network_io),
            "utilization_variance": self._calculate_variance(network_io),
            "efficiency_score": max(0, 100 - self._calculate_std(network_io))
        }
    
    def _identify_disk_activity_periods(self, disk_data: List[float]) -> List[Dict]:
        """Identify periods of high disk activity"""
        activity_periods = []
        if not disk_data:
            return activity_periods
        
        # Calculate threshold (top 20% of usage)
        sorted_data = sorted(disk_data)
        threshold_index = int(len(sorted_data) * 0.8)
        threshold = sorted_data[threshold_index] if threshold_index < len(sorted_data) else sorted_data[-1]
        
        in_activity = False
        start_idx = 0
        
        for i, value in enumerate(disk_data):
            if value >= threshold and not in_activity:
                in_activity = True
                start_idx = i
            elif value < threshold and in_activity:
                in_activity = False
                activity_periods.append({
                    "start": start_idx,
                    "end": i,
                    "duration": i - start_idx,
                    "peak_usage": max(disk_data[start_idx:i])
                })
        
        return activity_periods
    
    def _calculate_io_efficiency(self, df: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate I/O efficiency metrics"""
        disk_read = [row['disk_read'] for row in df]
        disk_write = [row['disk_write'] for row in df]
        
        return {
            "read_efficiency": max(0, 100 - self._calculate_std(disk_read)),
            "write_efficiency": max(0, 100 - self._calculate_std(disk_write)),
            "overall_efficiency": max(0, 100 - (self._calculate_std(disk_read) + self._calculate_std(disk_write)) / 2),
            "io_balance": abs(sum(disk_read) / len(disk_read) - sum(disk_write) / len(disk_write)) / (sum(disk_read) / len(disk_read) + sum(disk_write) / len(disk_write) + 1)
        }
    
    def _calculate_weekly_summary(self, daily_reports: List[Dict]) -> Dict[str, Any]:
        """Calculate weekly summary from daily reports"""
        if not daily_reports:
            return {"error": "No daily reports available"}
        
        summary = {
            "total_days": len(daily_reports),
            "average_cpu_usage": sum(r["summary"]["average_cpu"] for r in daily_reports) / len(daily_reports),
            "peak_cpu_usage": max(r["summary"]["max_cpu"] for r in daily_reports),
            "average_memory_usage": sum(r["summary"]["average_memory"] for r in daily_reports) / len(daily_reports),
            "peak_memory_usage": max(r["summary"]["max_memory"] for r in daily_reports),
            "total_alerts": sum(r["alerts_summary"]["total_alerts"] for r in daily_reports),
            "critical_alerts": sum(r["alerts_summary"]["critical_alerts"] for r in daily_reports),
            "average_health_score": sum(r["health_score"]["overall"] for r in daily_reports) / len(daily_reports)
        }
        
        return summary
    
    def _analyze_trends(self, df: List[Dict[str, Any]]) -> Dict[str, str]:
        """Analyze trends across the week"""
        trends = {}
        
        for metric in ['cpu_usage', 'ram_usage', 'gpu_usage']:
            values = [row.get(metric, 0) for row in df if metric in row]
            if values:
                trends[metric] = self._calculate_trend(values)
        
        return trends
    
    def _compare_daily_performance(self, daily_reports: List[Dict]) -> Dict[str, Any]:
        """Compare performance across days"""
        if not daily_reports:
            return {"error": "No daily reports available"}
        
        comparison = {
            "best_day": max(daily_reports, key=lambda x: x["health_score"]["overall"]),
            "worst_day": min(daily_reports, key=lambda x: x["health_score"]["overall"]),
            "most_stable": min(daily_reports, key=lambda x: x["summary"].get("standard_deviation", 100)),
            "most_alerts": max(daily_reports, key=lambda x: x["alerts_summary"]["total_alerts"])
        }
        
        return comparison
    
    def _generate_weekly_recommendations(self, daily_reports: List[Dict]) -> List[str]:
        """Generate weekly recommendations"""
        recommendations = []
        
        if not daily_reports:
            return recommendations
        
        avg_cpu = sum(r["summary"]["average_cpu"] for r in daily_reports) / len(daily_reports)
        avg_memory = sum(r["summary"]["average_memory"] for r in daily_reports) / len(daily_reports)
        total_alerts = sum(r["alerts_summary"]["total_alerts"] for r in daily_reports)
        
        if avg_cpu > 70:
            recommendations.append("Consistently high CPU usage throughout the week. Consider hardware upgrade or process optimization.")
        
        if avg_memory > 80:
            recommendations.append("Memory usage remains high. Consider RAM upgrade or memory optimization.")
        
        if total_alerts > 50:
            recommendations.append("High number of alerts this week. Review system configuration and performance issues.")
        
        return recommendations
    
    def _calculate_weekly_health_score(self, daily_reports: List[Dict]) -> Dict[str, Any]:
        """Calculate weekly health score"""
        if not daily_reports:
            return {"error": "No daily reports available"}
        
        scores = [r["health_score"]["overall"] for r in daily_reports]
        
        return {
            "average": sum(scores) / len(scores),
            "minimum": min(scores),
            "maximum": max(scores),
            "trend": self._calculate_trend(pd.Series(scores)),
            "consistency": max(0, 100 - pd.Series(scores).std()),
            "grade": self._get_health_grade(sum(scores) / len(scores))
        }
    
    def export_report_to_html(self, report: Dict[str, Any], file_path: str) -> bool:
        """Export report to HTML format"""
        try:
            html_content = self._generate_html_report(report)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return True
        except Exception as e:
            print(f"Error exporting HTML report: {e}")
            return False
    
    def _generate_html_report(self, report: Dict[str, Any]) -> str:
        """Generate HTML report content"""
        if "error" in report:
            return f"<html><body><h1>Error</h1><p>{report['error']}</p></body></html>"
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Performance Report - {report.get('date', report.get('period', 'Unknown'))}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                .metric {{ display: inline-block; margin: 10px; padding: 10px; background-color: #f9f9f9; border-radius: 3px; }}
                .health-score {{ font-size: 24px; font-weight: bold; color: {'green' if report.get('health_score', {}).get('overall', 0) > 70 else 'orange' if report.get('health_score', {}).get('overall', 0) > 40 else 'red'}; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Performance Report</h1>
                <p>Date: {report.get('date', report.get('period', 'Unknown'))}</p>
                <p>Generated: {report.get('generated_at', 'Unknown')}</p>
            </div>
            
            <div class="section">
                <h2>System Health Score</h2>
                <div class="health-score">{report.get('health_score', {}).get('overall', 'N/A')}/100</div>
                <p>Grade: {report.get('health_score', {}).get('grade', 'N/A')} ({report.get('health_score', {}).get('status', 'N/A')})</p>
            </div>
            
            <div class="section">
                <h2>Summary Statistics</h2>
                <div class="metric">Average CPU: {report.get('summary', {}).get('average_cpu', 'N/A'):.1f}%</div>
                <div class="metric">Peak CPU: {report.get('summary', {}).get('max_cpu', 'N/A'):.1f}%</div>
                <div class="metric">Average Memory: {report.get('summary', {}).get('average_memory', 'N/A'):.1f}%</div>
                <div class="metric">Peak Memory: {report.get('summary', {}).get('max_memory', 'N/A'):.1f}%</div>
            </div>
            
            <div class="section">
                <h2>Alerts Summary</h2>
                <p>Total Alerts: {report.get('alerts_summary', {}).get('total_alerts', 0)}</p>
                <p>Critical: {report.get('alerts_summary', {}).get('critical_alerts', 0)}</p>
                <p>Warnings: {report.get('alerts_summary', {}).get('warning_alerts', 0)}</p>
            </div>
            
            <div class="section">
                <h2>Recommendations</h2>
                <ul>
        """
        
        for recommendation in report.get('recommendations', []):
            html += f"<li>{recommendation}</li>"
        
        html += """
                </ul>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _calculate_diff_average(self, values: List[float]) -> float:
        """Calculate average difference between consecutive values"""
        if len(values) < 2:
            return 0
        diffs = [values[i] - values[i-1] for i in range(1, len(values))]
        return sum(diffs) / len(diffs) if diffs else 0
    
    def _calculate_diff_max(self, values: List[float]) -> float:
        """Calculate maximum difference between consecutive values"""
        if len(values) < 2:
            return 0
        diffs = [values[i] - values[i-1] for i in range(1, len(values))]
        return max(diffs) if diffs else 0
    
    def _calculate_std(self, values: List[float]) -> float:
        """Calculate standard deviation"""
        if len(values) < 2:
            return 0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5
    
    def _calculate_variance(self, values: List[float]) -> float:
        """Calculate variance"""
        if len(values) < 2:
            return 0
        mean = sum(values) / len(values)
        return sum((x - mean) ** 2 for x in values) / len(values)
