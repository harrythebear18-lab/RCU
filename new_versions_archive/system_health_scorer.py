#!/usr/bin/env python3
"""
System Health Scorer
Calculates comprehensive system health scores with analytics and recommendations.
"""

import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
import sqlite3
import os
from collections import deque
import json

class SystemHealthScorer:
    """Calculates and analyzes system health scores"""
    
    def __init__(self, db_path="system_monitoring.db"):
        self.db_path = os.path.join(os.path.dirname(__file__), db_path)
        
        # Health scoring configuration
        self.scoring_weights = {
            "cpu": 0.25,      # CPU performance weight
            "memory": 0.25,   # Memory usage weight
            "gpu": 0.20,      # GPU performance weight
            "disk": 0.15,     # Disk I/O weight
            "network": 0.10,   # Network performance weight
            "temperature": 0.05 # Temperature weight
        }
        
        # Thresholds for scoring
        self.thresholds = {
            "cpu": {"excellent": 30, "good": 50, "fair": 70, "poor": 85},
            "memory": {"excellent": 40, "good": 60, "fair": 75, "poor": 90},
            "gpu": {"excellent": 20, "good": 40, "fair": 70, "poor": 85},
            "disk": {"excellent": 1000, "good": 5000, "fair": 10000, "poor": 20000},  # MB/s
            "network": {"excellent": 1000, "good": 5000, "fair": 10000, "poor": 20000},  # MB/s
            "temperature": {"excellent": 40, "good": 60, "fair": 75, "poor": 85}  # Celsius
        }
        
        # Health score history
        self.health_history = deque(maxlen=1000)
    
    def calculate_current_health_score(self, current_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate current system health score"""
        component_scores = {}
        
        # CPU Health Score
        component_scores["cpu"] = self._calculate_cpu_score(current_metrics["cpu"])
        
        # Memory Health Score
        component_scores["memory"] = self._calculate_memory_score(current_metrics["memory"])
        
        # GPU Health Score
        component_scores["gpu"] = self._calculate_gpu_score(current_metrics["gpu"])
        
        # Disk Health Score
        component_scores["disk"] = self._calculate_disk_score(current_metrics["disk"])
        
        # Network Health Score
        component_scores["network"] = self._calculate_network_score(current_metrics["network"])
        
        # Temperature Health Score
        component_scores["temperature"] = self._calculate_temperature_score(current_metrics)
        
        # Calculate weighted overall score
        overall_score = sum(
            score * self.scoring_weights[component]
            for component, score in component_scores.items()
        )
        
        # Determine health grade and status
        grade = self._get_grade(overall_score)
        status = self._get_status(overall_score)
        
        # Generate recommendations
        recommendations = self._generate_health_recommendations(component_scores, current_metrics)
        
        # Calculate stability score
        stability_score = self._calculate_stability_score(component_scores)
        
        health_score = {
            "overall": overall_score,
            "grade": grade,
            "status": status,
            "components": component_scores,
            "weights": self.scoring_weights,
            "recommendations": recommendations,
            "stability": stability_score,
            "calculated_at": datetime.now().isoformat(),
            "trend": self._calculate_trend(),
            "risk_factors": self._identify_risk_factors(component_scores, current_metrics)
        }
        
        # Store in history
        self.health_history.append({
            "timestamp": datetime.now(),
            "score": overall_score,
            "components": component_scores
        })
        
        return health_score
    
    def calculate_historical_health_analysis(self, hours: int = 24) -> Dict[str, Any]:
        """Analyze health score trends over time"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Get historical metrics
            query = '''
                SELECT * FROM system_metrics 
                WHERE timestamp > datetime('now', '-{} hours')
                ORDER BY timestamp
            '''.format(hours)
            
            cursor = conn.cursor()
            cursor.execute(query)
            metrics_data = cursor.fetchall()
            conn.close()
            
            if not metrics_data:
                return {"error": "No historical data available"}
            
            # Calculate health scores for each data point
            health_scores = []
            for row in metrics_data:
                metrics = self._convert_row_to_metrics(row)
                health_score = self.calculate_current_health_score(metrics)
                health_scores.append(health_score)
            
            # Analyze trends
            analysis = self._analyze_health_trends(health_scores)
            
            return {
                "period_hours": hours,
                "data_points": len(health_scores),
                "analysis": analysis,
                "scores": health_scores[-100:],  # Last 100 scores
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Failed to analyze historical health: {e}"}
    
    def _calculate_cpu_score(self, cpu_metrics: Dict[str, Any]) -> float:
        """Calculate CPU health score"""
        cpu_usage = cpu_metrics.get("usage", 0)
        cpu_temp = cpu_metrics.get("temp", 0)
        
        # Base score from usage
        thresholds = self.thresholds["cpu"]
        if cpu_usage <= thresholds["excellent"]:
            usage_score = 100
        elif cpu_usage <= thresholds["good"]:
            usage_score = 85 - ((cpu_usage - thresholds["good"]) / (thresholds["fair"] - thresholds["good"])) * 35
        elif cpu_usage <= thresholds["fair"]:
            usage_score = 50 - ((cpu_usage - thresholds["fair"]) / (thresholds["poor"] - thresholds["fair"])) * 35
        elif cpu_usage <= thresholds["poor"]:
            usage_score = 15 - ((cpu_usage - thresholds["poor"]) / (100 - thresholds["poor"])) * 15
        else:
            usage_score = 0
        
        # Temperature penalty
        temp_thresholds = self.thresholds["temperature"]
        if cpu_temp <= temp_thresholds["excellent"]:
            temp_penalty = 0
        elif cpu_temp <= temp_thresholds["good"]:
            temp_penalty = 5
        elif cpu_temp <= temp_thresholds["fair"]:
            temp_penalty = 10
        elif cpu_temp <= temp_thresholds["poor"]:
            temp_penalty = 20
        else:
            temp_penalty = 30
        
        return max(0, usage_score - temp_penalty)
    
    def _calculate_memory_score(self, memory_metrics: Dict[str, Any]) -> float:
        """Calculate memory health score"""
        memory_usage = memory_metrics.get("usage", 0)
        available_gb = memory_metrics.get("available", 0)
        
        # Base score from usage
        thresholds = self.thresholds["memory"]
        if memory_usage <= thresholds["excellent"]:
            usage_score = 100
        elif memory_usage <= thresholds["good"]:
            usage_score = 85 - ((memory_usage - thresholds["good"]) / (thresholds["fair"] - thresholds["good"])) * 35
        elif memory_usage <= thresholds["fair"]:
            usage_score = 50 - ((memory_usage - thresholds["fair"]) / (thresholds["poor"] - thresholds["fair"])) * 35
        elif memory_usage <= thresholds["poor"]:
            usage_score = 15 - ((memory_usage - thresholds["poor"]) / (100 - thresholds["poor"])) * 15
        else:
            usage_score = 0
        
        # Available memory bonus
        if available_gb > 4:
            memory_bonus = min(10, available_gb / 2)
        else:
            memory_bonus = 0
        
        return min(100, usage_score + memory_bonus)
    
    def _calculate_gpu_score(self, gpu_metrics: Dict[str, Any]) -> float:
        """Calculate GPU health score"""
        gpu_usage = gpu_metrics.get("usage", 0)
        gpu_temp = gpu_metrics.get("temp", 0)
        gpu_memory_usage = 0
        
        # Calculate GPU memory usage
        if gpu_metrics.get("memory_total", 0) > 0:
            gpu_memory_usage = (gpu_metrics.get("memory_used", 0) / gpu_metrics["memory_total"]) * 100
        
        # Base score from usage
        thresholds = self.thresholds["gpu"]
        if gpu_usage <= thresholds["excellent"]:
            usage_score = 100
        elif gpu_usage <= thresholds["good"]:
            usage_score = 85 - ((gpu_usage - thresholds["good"]) / (thresholds["fair"] - thresholds["good"])) * 35
        elif gpu_usage <= thresholds["fair"]:
            usage_score = 50 - ((gpu_usage - thresholds["fair"]) / (thresholds["poor"] - thresholds["fair"])) * 35
        elif gpu_usage <= thresholds["poor"]:
            usage_score = 15 - ((gpu_usage - thresholds["poor"]) / (100 - thresholds["poor"])) * 15
        else:
            usage_score = 0
        
        # Memory usage penalty
        if gpu_memory_usage > 80:
            usage_score -= 10
        elif gpu_memory_usage > 90:
            usage_score -= 20
        
        # Temperature penalty
        temp_thresholds = self.thresholds["temperature"]
        if gpu_temp <= temp_thresholds["excellent"]:
            temp_penalty = 0
        elif gpu_temp <= temp_thresholds["good"]:
            temp_penalty = 5
        elif gpu_temp <= temp_thresholds["fair"]:
            temp_penalty = 10
        elif gpu_temp <= temp_thresholds["poor"]:
            temp_penalty = 20
        else:
            temp_penalty = 30
        
        return max(0, usage_score - temp_penalty)
    
    def _calculate_disk_score(self, disk_metrics: Dict[str, Any]) -> float:
        """Calculate disk health score"""
        disk_read = disk_metrics.get("read", 0)
        disk_write = disk_metrics.get("write", 0)
        disk_queue = disk_metrics.get("queue", 0)
        
        # Calculate total I/O rate (MB/s)
        total_io = disk_read + disk_write
        
        # Score based on I/O performance
        thresholds = self.thresholds["disk"]
        if total_io <= thresholds["excellent"]:
            io_score = 100
        elif total_io <= thresholds["good"]:
            io_score = 85 - ((total_io - thresholds["good"]) / (thresholds["fair"] - thresholds["good"])) * 35
        elif total_io <= thresholds["fair"]:
            io_score = 50 - ((total_io - thresholds["fair"]) / (thresholds["poor"] - thresholds["fair"])) * 35
        elif total_io <= thresholds["poor"]:
            io_score = 15 - ((total_io - thresholds["poor"]) / (thresholds["poor"] * 2)) * 15
        else:
            io_score = 0
        
        # Queue length penalty
        if disk_queue > 10:
            io_score -= 20
        elif disk_queue > 5:
            io_score -= 10
        elif disk_queue > 2:
            io_score -= 5
        
        return max(0, io_score)
    
    def _calculate_network_score(self, network_metrics: Dict[str, Any]) -> float:
        """Calculate network health score"""
        network_sent = network_metrics.get("sent", 0)
        network_recv = network_metrics.get("recv", 0)
        
        # Calculate total network I/O rate (MB/s)
        total_io = network_sent + network_recv
        
        # Score based on network performance
        thresholds = self.thresholds["network"]
        if total_io <= thresholds["excellent"]:
            io_score = 100
        elif total_io <= thresholds["good"]:
            io_score = 85 - ((total_io - thresholds["good"]) / (thresholds["fair"] - thresholds["good"])) * 35
        elif total_io <= thresholds["fair"]:
            io_score = 50 - ((total_io - thresholds["fair"]) / (thresholds["poor"] - thresholds["fair"])) * 35
        elif total_io <= thresholds["poor"]:
            io_score = 15 - ((total_io - thresholds["poor"]) / (thresholds["poor"] * 2)) * 15
        else:
            io_score = 0
        
        return max(0, io_score)
    
    def _calculate_temperature_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate temperature health score"""
        cpu_temp = metrics.get("cpu", {}).get("temp", 0)
        gpu_temp = metrics.get("gpu", {}).get("temp", 0)
        
        # Use the higher temperature
        max_temp = max(cpu_temp, gpu_temp)
        
        # Score based on temperature
        thresholds = self.thresholds["temperature"]
        if max_temp <= thresholds["excellent"]:
            temp_score = 100
        elif max_temp <= thresholds["good"]:
            temp_score = 85 - ((max_temp - thresholds["good"]) / (thresholds["fair"] - thresholds["good"])) * 35
        elif max_temp <= thresholds["fair"]:
            temp_score = 50 - ((max_temp - thresholds["fair"]) / (thresholds["poor"] - thresholds["fair"])) * 35
        elif max_temp <= thresholds["poor"]:
            temp_score = 15 - ((max_temp - thresholds["poor"]) / (100 - thresholds["poor"])) * 15
        else:
            temp_score = 0
        
        return temp_score
    
    def _get_grade(self, score: float) -> str:
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
    
    def _get_status(self, score: float) -> str:
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
    
    def _generate_health_recommendations(self, component_scores: Dict[str, float], 
                                       current_metrics: Dict[str, Any]) -> List[str]:
        """Generate health recommendations based on scores"""
        recommendations = []
        
        # CPU recommendations
        cpu_score = component_scores.get("cpu", 100)
        if cpu_score < 70:
            cpu_usage = current_metrics["cpu"]["usage"]
            if cpu_usage > 80:
                recommendations.append("CPU usage is high. Consider closing unnecessary applications or upgrading CPU.")
            if current_metrics["cpu"]["temp"] > 75:
                recommendations.append("CPU temperature is elevated. Check cooling system and ventilation.")
        
        # Memory recommendations
        memory_score = component_scores.get("memory", 100)
        if memory_score < 70:
            memory_usage = current_metrics["memory"]["usage"]
            if memory_usage > 85:
                recommendations.append("Memory usage is critical. Consider adding more RAM or closing memory-intensive applications.")
            elif memory_usage > 70:
                recommendations.append("Memory usage is high. Monitor for memory leaks and optimize applications.")
        
        # GPU recommendations
        gpu_score = component_scores.get("gpu", 100)
        if gpu_score < 70:
            gpu_usage = current_metrics["gpu"]["usage"]
            if gpu_usage > 80:
                recommendations.append("GPU usage is high. Check for background processes or consider GPU upgrade.")
            if current_metrics["gpu"]["temp"] > 80:
                recommendations.append("GPU temperature is high. Improve cooling or reduce GPU load.")
        
        # Disk recommendations
        disk_score = component_scores.get("disk", 100)
        if disk_score < 70:
            recommendations.append("Disk I/O is high. Consider SSD upgrade or disk cleanup.")
        
        # Network recommendations
        network_score = component_scores.get("network", 100)
        if network_score < 70:
            recommendations.append("Network usage is high. Check for unusual network activity.")
        
        # Overall recommendations
        overall_score = sum(component_scores.values()) / len(component_scores)
        if overall_score < 50:
            recommendations.append("System health is critical. Immediate attention required.")
        elif overall_score < 70:
            recommendations.append("System health needs improvement. Review all components.")
        
        return recommendations
    
    def _calculate_stability_score(self, component_scores: Dict[str, float]) -> Dict[str, Any]:
        """Calculate system stability score"""
        if len(self.health_history) < 10:
            return {"score": 100, "trend": "insufficient_data"}
        
        # Get recent scores
        recent_scores = [entry["score"] for entry in list(self.health_history)[-10:]]
        
        # Calculate stability (lower standard deviation = more stable)
        std_dev = np.std(recent_scores)
        stability_score = max(0, 100 - (std_dev * 2))  # Scale standard deviation to 0-100
        
        # Calculate trend
        if len(recent_scores) >= 5:
            recent_trend = np.polyfit(range(5), recent_scores[-5:], 1)[0]
            if recent_trend > 0.5:
                trend = "improving"
            elif recent_trend < -0.5:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"
        
        return {
            "score": stability_score,
            "trend": trend,
            "standard_deviation": std_dev,
            "recent_average": np.mean(recent_scores)
        }
    
    def _calculate_trend(self) -> str:
        """Calculate overall health trend"""
        if len(self.health_history) < 20:
            return "insufficient_data"
        
        # Get last 20 scores
        scores = [entry["score"] for entry in list(self.health_history)[-20:]]
        
        # Calculate trend
        x = np.arange(len(scores))
        slope = np.polyfit(x, scores, 1)[0]
        
        if slope > 0.5:
            return "improving"
        elif slope < -0.5:
            return "declining"
        else:
            return "stable"
    
    def _identify_risk_factors(self, component_scores: Dict[str, float], 
                               current_metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify potential risk factors"""
        risks = []
        
        # High CPU usage risk
        if component_scores.get("cpu", 100) < 50:
            risks.append({
                "type": "cpu_overload",
                "severity": "high" if component_scores["cpu"] < 30 else "medium",
                "description": "CPU usage is consistently high",
                "impact": "System responsiveness and performance"
            })
        
        # Memory exhaustion risk
        if component_scores.get("memory", 100) < 50:
            risks.append({
                "type": "memory_exhaustion",
                "severity": "high" if component_scores["memory"] < 30 else "medium",
                "description": "Memory usage is approaching critical levels",
                "impact": "System crashes and application failures"
            })
        
        # Thermal throttling risk
        max_temp = max(current_metrics["cpu"]["temp"], current_metrics["gpu"]["temp"])
        if max_temp > 80:
            risks.append({
                "type": "thermal_throttling",
                "severity": "high" if max_temp > 90 else "medium",
                "description": f"High temperature detected: {max_temp:.1f}°C",
                "impact": "Performance degradation and hardware damage"
            })
        
        # Disk bottleneck risk
        if component_scores.get("disk", 100) < 50:
            risks.append({
                "type": "disk_bottleneck",
                "severity": "medium",
                "description": "Disk I/O is creating system bottlenecks",
                "impact": "Slow application loading and data access"
            })
        
        return risks
    
    def _convert_row_to_metrics(self, row: tuple) -> Dict[str, Any]:
        """Convert database row to metrics dictionary"""
        return {
            "cpu": {
                "usage": row[2] if len(row) > 2 else 0,
                "freq": row[3] if len(row) > 3 else 0,
                "temp": row[4] if len(row) > 4 else 0
            },
            "memory": {
                "usage": row[5] if len(row) > 5 else 0,
                "used": row[6] if len(row) > 6 else 0,
                "total": row[7] if len(row) > 7 else 1,
                "available": (row[7] - row[6]) if len(row) > 7 else 1
            },
            "gpu": {
                "usage": row[8] if len(row) > 8 else 0,
                "memory_used": row[9] if len(row) > 9 else 0,
                "memory_total": row[10] if len(row) > 10 else 1,
                "temp": row[11] if len(row) > 11 else 0
            },
            "disk": {
                "read": row[13] if len(row) > 13 else 0,
                "write": row[14] if len(row) > 14 else 0,
                "queue": row[15] if len(row) > 15 else 0
            },
            "network": {
                "sent": row[12] if len(row) > 12 else 0,
                "recv": row[13] if len(row) > 13 else 0
            }
        }
    
    def _analyze_health_trends(self, health_scores: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze health score trends"""
        if not health_scores:
            return {"error": "No health scores available"}
        
        # Extract overall scores
        overall_scores = [score["overall"] for score in health_scores]
        
        # Calculate statistics
        analysis = {
            "average_score": np.mean(overall_scores),
            "min_score": np.min(overall_scores),
            "max_score": np.max(overall_scores),
            "standard_deviation": np.std(overall_scores),
            "score_distribution": {
                "excellent": len([s for s in overall_scores if s >= 85]),
                "good": len([s for s in overall_scores if 70 <= s < 85]),
                "fair": len([s for s in overall_scores if 55 <= s < 70]),
                "poor": len([s for s in overall_scores if 40 <= s < 55]),
                "critical": len([s for s in overall_scores if s < 40])
            }
        }
        
        # Calculate trend
        if len(overall_scores) >= 10:
            x = np.arange(len(overall_scores))
            slope = np.polyfit(x, overall_scores, 1)[0]
            if slope > 0.5:
                analysis["trend"] = "improving"
            elif slope < -0.5:
                analysis["trend"] = "declining"
            else:
                analysis["trend"] = "stable"
        else:
            analysis["trend"] = "insufficient_data"
        
        # Component analysis
        component_analysis = {}
        for component in ["cpu", "memory", "gpu", "disk", "network", "temperature"]:
            component_scores = [score["components"].get(component, 100) for score in health_scores]
            component_analysis[component] = {
                "average": np.mean(component_scores),
                "min": np.min(component_scores),
                "max": np.max(component_scores),
                "standard_deviation": np.std(component_scores)
            }
        
        analysis["components"] = component_analysis
        
        return analysis
    
    def get_health_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get comprehensive health summary"""
        try:
            # Get current health score
            current_metrics = self._get_current_metrics()
            current_health = self.calculate_current_health_score(current_metrics)
            
            # Get historical analysis
            historical_analysis = self.calculate_historical_health_analysis(hours)
            
            # Combine into summary
            summary = {
                "current_health": current_health,
                "historical_analysis": historical_analysis,
                "summary_at": datetime.now().isoformat(),
                "recommendations": current_health["recommendations"],
                "risk_factors": current_health["risk_factors"],
                "action_items": self._generate_action_items(current_health, historical_analysis)
            }
            
            return summary
            
        except Exception as e:
            return {"error": f"Failed to generate health summary: {e}"}
    
    def _get_current_metrics(self) -> Dict[str, Any]:
        """Get current system metrics"""
        # This would integrate with the actual monitoring system
        # For now, return default metrics
        return {
            "cpu": {"usage": 50, "freq": 3000, "temp": 65},
            "memory": {"usage": 60, "used": 8, "total": 16, "available": 8},
            "gpu": {"usage": 30, "memory_used": 4, "memory_total": 8, "temp": 70},
            "disk": {"read": 1000, "write": 500, "queue": 1},
            "network": {"sent": 1000, "recv": 2000}
        }
    
    def _generate_action_items(self, current_health: Dict[str, Any], 
                              historical_analysis: Dict[str, Any]) -> List[str]:
        """Generate actionable items based on health analysis"""
        action_items = []
        
        # Current health actions
        if current_health["overall"] < 70:
            action_items.append("Schedule system maintenance to address performance issues")
        
        # Component-specific actions
        components = current_health["components"]
        
        if components.get("cpu", 100) < 60:
            action_items.append("Review CPU-intensive processes and optimize scheduling")
        
        if components.get("memory", 100) < 60:
            action_items.append("Consider memory upgrade or application optimization")
        
        if components.get("disk", 100) < 60:
            action_items.append("Plan disk cleanup and consider SSD upgrade")
        
        # Trend-based actions
        if "analysis" in historical_analysis:
            trend = historical_analysis["analysis"].get("trend", "stable")
            if trend == "declining":
                action_items.append("Investigate causes of performance degradation")
            elif trend == "improving":
                action_items.append("Continue current optimization practices")
        
        # Risk-based actions
        risks = current_health.get("risk_factors", [])
        high_risks = [risk for risk in risks if risk["severity"] == "high"]
        if high_risks:
            action_items.append(f"Address {len(high_risks)} high-priority risk factors immediately")
        
        return action_items
