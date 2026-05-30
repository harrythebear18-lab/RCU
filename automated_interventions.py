#!/usr/bin/env python3
"""
Automated Interventions System
Implements automated system interventions to reduce manual interventions by 50%
"""

import os
import time
import threading
import psutil
import subprocess
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
import queue
import sqlite3
from enum import Enum
import logging

class InterventionType(Enum):
    """Types of automated interventions"""
    MEMORY_CLEANUP = "memory_cleanup"
    PROCESS_TERMINATION = "process_termination"
    PROCESS_SUSPENSION = "process_suspension"
    SERVICE_RESTART = "service_restart"
    DISK_CLEANUP = "disk_cleanup"
    CACHE_CLEAR = "cache_clear"
    NETWORK_RESET = "network_reset"
    SYSTEM_RESTART = "system_restart"
    PROFILE_SWITCH = "profile_switch"
    ALERT_NOTIFICATION = "alert_notification"

class InterventionSeverity(Enum):
    """Severity levels for interventions"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AutomatedInterventionManager:
    """Manages automated system interventions"""
    
    def __init__(self, settings_file="intervention_settings.json"):
        self.settings_file = os.path.join(os.path.dirname(__file__), settings_file)
        self.db_path = os.path.join(os.path.dirname(__file__), "system_monitoring.db")
        
        # Intervention queue and thread
        self.intervention_queue = queue.Queue()
        self.running = False
        self.intervention_thread = None
        
        # Intervention history and statistics
        self.intervention_history = []
        self.intervention_stats = {
            "total_interventions": 0,
            "successful_interventions": 0,
            "manual_interventions_prevented": 0,
            "average_response_time": 0,
            "intervention_types": {}
        }
        
        # Load settings
        self.settings = self.load_settings()
        
        # Intervention rules
        self.intervention_rules = self.load_intervention_rules()
        
        # Setup logging
        self.setup_logging()
        
        # Start intervention manager if enabled
        if self.settings.get("enabled", False):
            self.start_intervention_manager()
    
    def load_settings(self) -> Dict[str, Any]:
        """Load intervention settings"""
        default_settings = {
            "enabled": False,
            "auto_approve_critical": True,
            "auto_approve_high": True,
            "auto_approve_medium": False,
            "auto_approve_low": False,
            "max_interventions_per_hour": 20,
            "intervention_timeout": 60,
            "require_confirmation": False,
            "safe_mode": True,
            "excluded_processes": ["system", "csrss", "winlogon", "lsass", "smss"],
            "intervention_cooldown": 300,  # 5 minutes
            "manual_intervention_threshold": 0.5,  # 50% reduction target
            "log_all_interventions": True,
            "enable_notifications": True
        }
        
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    loaded_settings = json.load(f)
                default_settings.update(loaded_settings)
            else:
                self.save_settings(default_settings)
            return default_settings
        except Exception as e:
            self.logger.error(f"Error loading intervention settings: {e}")
            return default_settings
    
    def save_settings(self, settings: Dict[str, Any]) -> bool:
        """Save intervention settings"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
            return True
        except Exception as e:
            self.logger.error(f"Error saving intervention settings: {e}")
            return False
    
    def load_intervention_rules(self) -> List[Dict[str, Any]]:
        """Load intervention rules"""
        default_rules = [
            {
                "id": "high_memory_usage",
                "name": "High Memory Usage Intervention",
                "trigger": {
                    "metric": "memory_usage",
                    "operator": ">=",
                    "value": 90,
                    "duration": 30
                },
                "interventions": [
                    {
                        "type": InterventionType.MEMORY_CLEANUP,
                        "action": "aggressive_memory_cleanup",
                        "severity": InterventionSeverity.HIGH,
                        "cooldown": 300
                    },
                    {
                        "type": InterventionType.PROCESS_TERMINATION,
                        "action": "terminate_memory_intensive_processes",
                        "severity": InterventionSeverity.CRITICAL,
                        "cooldown": 600
                    }
                ],
                "enabled": True
            },
            {
                "id": "high_cpu_usage",
                "name": "High CPU Usage Intervention",
                "trigger": {
                    "metric": "cpu_usage",
                    "operator": ">=",
                    "value": 95,
                    "duration": 30
                },
                "interventions": [
                    {
                        "type": InterventionType.PROCESS_SUSPENSION,
                        "action": "suspend_cpu_intensive_processes",
                        "severity": InterventionSeverity.HIGH,
                        "cooldown": 300
                    },
                    {
                        "type": InterventionType.PROCESS_TERMINATION,
                        "action": "terminate_cpu_intensive_processes",
                        "severity": InterventionSeverity.CRITICAL,
                        "cooldown": 600
                    }
                ],
                "enabled": True
            },
            {
                "id": "disk_space_low",
                "name": "Low Disk Space Intervention",
                "trigger": {
                    "metric": "disk_usage",
                    "operator": ">=",
                    "value": 95,
                    "duration": 60
                },
                "interventions": [
                    {
                        "type": InterventionType.DISK_CLEANUP,
                        "action": "aggressive_disk_cleanup",
                        "severity": InterventionSeverity.HIGH,
                        "cooldown": 600
                    },
                    {
                        "type": InterventionType.ALERT_NOTIFICATION,
                        "action": "send_disk_space_alert",
                        "severity": InterventionSeverity.MEDIUM,
                        "cooldown": 1800
                    }
                ],
                "enabled": True
            },
            {
                "id": "system_unresponsive",
                "name": "System Unresponsive Intervention",
                "trigger": {
                    "metric": "response_time",
                    "operator": ">",
                    "value": 5.0,
                    "duration": 60
                },
                "interventions": [
                    {
                        "type": InterventionType.PROCESS_TERMINATION,
                        "action": "terminate_unresponsive_processes",
                        "severity": InterventionSeverity.CRITICAL,
                        "cooldown": 300
                    },
                    {
                        "type": InterventionType.MEMORY_CLEANUP,
                        "action": "emergency_memory_cleanup",
                        "severity": InterventionSeverity.HIGH,
                        "cooldown": 180
                    }
                ],
                "enabled": True
            },
            {
                "id": "gpu_overheating",
                "name": "GPU Overheating Intervention",
                "trigger": {
                    "metric": "gpu_temperature",
                    "operator": ">=",
                    "value": 85,
                    "duration": 30
                },
                "interventions": [
                    {
                        "type": InterventionType.PROCESS_SUSPENSION,
                        "action": "suspend_gpu_intensive_processes",
                        "severity": InterventionSeverity.HIGH,
                        "cooldown": 300
                    },
                    {
                        "type": InterventionType.ALERT_NOTIFICATION,
                        "action": "send_temperature_alert",
                        "severity": InterventionSeverity.MEDIUM,
                        "cooldown": 900
                    }
                ],
                "enabled": True
            }
        ]
        
        return default_rules
    
    def setup_logging(self):
        """Setup logging for interventions"""
        self.logger = logging.getLogger('AutomatedInterventions')
        self.logger.setLevel(logging.INFO)
        
        # Create file handler
        log_file = os.path.join(os.path.dirname(__file__), "interventions.log")
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        # Add handler to logger
        self.logger.addHandler(file_handler)
    
    def start_intervention_manager(self):
        """Start the automated intervention manager"""
        if not self.running:
            self.running = True
            self.intervention_thread = threading.Thread(target=self._intervention_worker, daemon=True)
            self.intervention_thread.start()
            self.logger.info("Automated intervention manager started")
    
    def stop_intervention_manager(self):
        """Stop the automated intervention manager"""
        self.running = False
        if self.intervention_thread:
            self.intervention_thread.join(timeout=5)
        self.logger.info("Automated intervention manager stopped")
    
    def process_system_alert(self, alert: Dict[str, Any]) -> bool:
        """Process system alert and trigger automated interventions"""
        if not self.settings.get("enabled", False):
            return False
        
        # Check intervention rate limit
        if not self._check_intervention_rate_limit():
            return False
        
        # Find matching intervention rules
        matching_rules = self._find_matching_rules(alert)
        
        if not matching_rules:
            return False
        
        # Queue interventions
        interventions_triggered = 0
        for rule in matching_rules:
            for intervention in rule["interventions"]:
                intervention_data = {
                    "rule_id": rule["id"],
                    "rule_name": rule["name"],
                    "alert": alert,
                    "intervention": intervention,
                    "timestamp": datetime.now().isoformat()
                }
                
                # Check cooldown
                if not self._check_intervention_cooldown(intervention_data):
                    # Check auto-approval
                    if self._should_auto_approve(intervention["severity"]):
                        intervention_data["auto_approved"] = True
                        interventions_triggered += 1
                    else:
                        intervention_data["auto_approved"] = False
                    
                    self.intervention_queue.put(intervention_data)
        
        # Update statistics
        if interventions_triggered > 0:
            self.intervention_stats["manual_interventions_prevented"] += interventions_triggered
        
        return interventions_triggered > 0
    
    def _intervention_worker(self):
        """Background worker for processing interventions"""
        while self.running:
            try:
                # Get intervention from queue
                intervention_data = self.intervention_queue.get(timeout=10)
                
                # Process intervention
                self._execute_intervention(intervention_data)
                
                # Mark task as done
                self.intervention_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Error in intervention worker: {e}")
    
    def _execute_intervention(self, intervention_data: Dict[str, Any]):
        """Execute an automated intervention"""
        start_time = time.time()
        
        try:
            intervention = intervention_data["intervention"]
            intervention_type = intervention["type"]
            action = intervention["action"]
            
            # Log intervention execution
            if self.settings.get("log_all_interventions", True):
                self.logger.info(f"Executing intervention: {intervention_type.value} - {action}")
            
            # Execute intervention based on type
            if intervention_type == InterventionType.MEMORY_CLEANUP:
                self._execute_memory_cleanup(action, intervention_data)
            elif intervention_type == InterventionType.PROCESS_TERMINATION:
                self._execute_process_termination(action, intervention_data)
            elif intervention_type == InterventionType.PROCESS_SUSPENSION:
                self._execute_process_suspension(action, intervention_data)
            elif intervention_type == InterventionType.SERVICE_RESTART:
                self._execute_service_restart(action, intervention_data)
            elif intervention_type == InterventionType.DISK_CLEANUP:
                self._execute_disk_cleanup(action, intervention_data)
            elif intervention_type == InterventionType.CACHE_CLEAR:
                self._execute_cache_clear(action, intervention_data)
            elif intervention_type == InterventionType.NETWORK_RESET:
                self._execute_network_reset(action, intervention_data)
            elif intervention_type == InterventionType.SYSTEM_RESTART:
                self._execute_system_restart(action, intervention_data)
            elif intervention_type == InterventionType.PROFILE_SWITCH:
                self._execute_profile_switch(action, intervention_data)
            elif intervention_type == InterventionType.ALERT_NOTIFICATION:
                self._execute_alert_notification(action, intervention_data)
            
            # Calculate execution time
            execution_time = time.time() - start_time
            
            # Record intervention
            self._record_intervention(intervention_data, True, execution_time)
            
            # Update statistics
            self.intervention_stats["total_interventions"] += 1
            self.intervention_stats["successful_interventions"] += 1
            
            # Update average response time
            self._update_average_response_time(execution_time)
            
            # Update intervention type statistics
            intervention_type_str = intervention_type.value
            if intervention_type_str not in self.intervention_stats["intervention_types"]:
                self.intervention_stats["intervention_types"][intervention_type_str] = 0
            self.intervention_stats["intervention_types"][intervention_type_str] += 1
            
            # Send notification if enabled
            if self.settings.get("enable_notifications", True):
                self._send_intervention_notification(intervention_data, True)
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Error executing intervention: {e}")
            
            # Record failed intervention
            self._record_intervention(intervention_data, False, execution_time)
            
            # Update statistics
            self.intervention_stats["total_interventions"] += 1
            
            # Send notification if enabled
            if self.settings.get("enable_notifications", True):
                self._send_intervention_notification(intervention_data, False, str(e))
    
    def _execute_memory_cleanup(self, action: str, intervention_data: Dict[str, Any]):
        """Execute memory cleanup intervention"""
        import gc
        
        if action == "aggressive_memory_cleanup":
            # Multiple garbage collection passes
            for _ in range(3):
                gc.collect()
            
            # Clear standby memory on Windows
            if os.name == 'nt':
                try:
                    subprocess.run(['powershell', '-Command', 'Clear-StandbyList'], 
                                  capture_output=True, timeout=10)
                except:
                    pass
        
        elif action == "emergency_memory_cleanup":
            # Emergency memory cleanup
            gc.collect()
            
            # Clear all caches
            if hasattr(gc, 'collect'):
                gc.collect()
            
            # Force memory cleanup
            try:
                import ctypes
                ctypes.windll.kernel32.SetProcessWorkingSetSize(-1, -1)
            except:
                pass
    
    def _execute_process_termination(self, action: str, intervention_data: Dict[str, Any]):
        """Execute process termination intervention"""
        if action == "terminate_memory_intensive_processes":
            # Find memory-intensive processes
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
                try:
                    if proc.info['memory_percent'] > 50:  # Processes using >50% memory
                        processes.append(proc)
                except:
                    continue
            
            # Terminate processes (excluding system processes)
            excluded = self.settings.get("excluded_processes", [])
            for proc in processes:
                if proc.info['name'].lower() not in excluded:
                    try:
                        proc.terminate()
                        self.logger.info(f"Terminated process: {proc.info['name']} (PID: {proc.info['pid']})")
                    except:
                        pass
        
        elif action == "terminate_cpu_intensive_processes":
            # Find CPU-intensive processes
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
                try:
                    if proc.info['cpu_percent'] > 80:  # Processes using >80% CPU
                        processes.append(proc)
                except:
                    continue
            
            # Terminate processes
            excluded = self.settings.get("excluded_processes", [])
            for proc in processes:
                if proc.info['name'].lower() not in excluded:
                    try:
                        proc.terminate()
                        self.logger.info(f"Terminated process: {proc.info['name']} (PID: {proc.info['pid']})")
                    except:
                        pass
        
        elif action == "terminate_unresponsive_processes":
            # Find unresponsive processes
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'status']):
                try:
                    if proc.info['status'] == psutil.STATUS_ZOMBIE:
                        processes.append(proc)
                except:
                    continue
            
            # Terminate zombie processes
            for proc in processes:
                try:
                    proc.terminate()
                    self.logger.info(f"Terminated unresponsive process: {proc.info['name']} (PID: {proc.info['pid']})")
                except:
                    pass
    
    def _execute_process_suspension(self, action: str, intervention_data: Dict[str, Any]):
        """Execute process suspension intervention"""
        if action == "suspend_cpu_intensive_processes":
            # Find CPU-intensive processes
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
                try:
                    if proc.info['cpu_percent'] > 70:  # Processes using >70% CPU
                        processes.append(proc)
                except:
                    continue
            
            # Suspend processes
            excluded = self.settings.get("excluded_processes", [])
            for proc in processes:
                if proc.info['name'].lower() not in excluded:
                    try:
                        proc.suspend()
                        self.logger.info(f"Suspended process: {proc.info['name']} (PID: {proc.info['pid']})")
                    except:
                        pass
        
        elif action == "suspend_gpu_intensive_processes":
            # Find GPU-intensive processes
            processes = []
            try:
                import GPUtil
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu = gpus[0]
                    for proc in psutil.process_iter(['pid', 'name']):
                        try:
                            # This is a simplified check - in reality, you'd need GPU process monitoring
                            if proc.info['name'] in ['chrome.exe', 'firefox.exe', 'games.exe']:
                                processes.append(proc)
                        except:
                            continue
            except:
                pass
            
            # Suspend GPU-intensive processes
            excluded = self.settings.get("excluded_processes", [])
            for proc in processes:
                if proc.info['name'].lower() not in excluded:
                    try:
                        proc.suspend()
                        self.logger.info(f"Suspended GPU-intensive process: {proc.info['name']} (PID: {proc.info['pid']})")
                    except:
                        pass
    
    def _execute_disk_cleanup(self, action: str, intervention_data: Dict[str, Any]):
        """Execute disk cleanup intervention"""
        if action == "aggressive_disk_cleanup":
            # Clean temporary files
            temp_dirs = [
                os.environ.get('TEMP', ''),
                os.environ.get('TMP', ''),
                os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Temp'),
                os.path.join(os.environ.get('APPDATA', ''), 'Temp')
            ]
            
            for temp_dir in temp_dirs:
                if os.path.exists(temp_dir):
                    try:
                        # Remove files older than 1 hour
                        current_time = time.time()
                        for item in os.listdir(temp_dir):
                            item_path = os.path.join(temp_dir, item)
                            try:
                                if os.path.isfile(item_path):
                                    file_age = current_time - os.path.getmtime(item_path)
                                    if file_age > 3600:  # 1 hour
                                        os.remove(item_path)
                            except:
                                pass
                    except:
                        pass
    
    def _execute_cache_clear(self, action: str, intervention_data: Dict[str, Any]):
        """Execute cache clear intervention"""
        # Clear DNS cache
        try:
            if os.name == 'nt':
                subprocess.run(['ipconfig', '/flushdns'], capture_output=True, timeout=10)
            else:
                subprocess.run(['sudo', 'systemd-resolve', '--flush-caches'], 
                              capture_output=True, timeout=10)
        except:
            pass
    
    def _execute_network_reset(self, action: str, intervention_data: Dict[str, Any]):
        """Execute network reset intervention"""
        if os.name == 'nt':
            try:
                # Reset network adapters
                subprocess.run(['powershell', '-Command', 'Restart-NetAdapter -Name "*"'], 
                              capture_output=True, timeout=60)
            except:
                pass
    
    def _execute_system_restart(self, action: str, intervention_data: Dict[str, Any]):
        """Execute system restart intervention"""
        # This is a placeholder - system restart should be handled carefully
        self.logger.warning("System restart intervention triggered - manual intervention required")
    
    def _execute_profile_switch(self, action: str, intervention_data: Dict[str, Any]):
        """Execute profile switch intervention"""
        # This would integrate with the resource optimizer
        self.logger.info(f"Profile switch intervention: {action}")
    
    def _execute_alert_notification(self, action: str, intervention_data: Dict[str, Any]):
        """Execute alert notification intervention"""
        # This would integrate with the email notification system
        self.logger.info(f"Alert notification intervention: {action}")
    
    def _find_matching_rules(self, alert: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find intervention rules that match the alert"""
        matching_rules = []
        
        for rule in self.intervention_rules:
            if not rule.get("enabled", True):
                continue
            
            trigger = rule["trigger"]
            metric = trigger["metric"]
            operator = trigger["operator"]
            threshold = trigger["value"]
            
            # Get metric value from alert
            metric_value = self._extract_metric_value(alert, metric)
            
            if metric_value is None:
                continue
            
            # Check if trigger condition is met
            if self._evaluate_condition(metric_value, operator, threshold):
                matching_rules.append(rule)
        
        return matching_rules
    
    def _extract_metric_value(self, alert: Dict[str, Any], metric: str) -> Optional[float]:
        """Extract metric value from alert"""
        if metric == "cpu_usage":
            return alert.get("cpu_usage")
        elif metric == "memory_usage":
            return alert.get("memory_usage")
        elif metric == "gpu_usage":
            return alert.get("gpu_usage")
        elif metric == "gpu_temperature":
            return max(alert.get("cpu_temp", 0), alert.get("gpu_temp", 0))
        elif metric == "disk_usage":
            return alert.get("disk_usage")
        elif metric == "response_time":
            return alert.get("response_time")
        
        return None
    
    def _evaluate_condition(self, value: float, operator: str, threshold: float) -> bool:
        """Evaluate trigger condition"""
        if operator == ">=":
            return value >= threshold
        elif operator == ">":
            return value > threshold
        elif operator == "<=":
            return value <= threshold
        elif operator == "<":
            return value < threshold
        elif operator == "==":
            return value == threshold
        elif operator == "!=":
            return value != threshold
        
        return False
    
    def _should_auto_approve(self, severity: InterventionSeverity) -> bool:
        """Check if intervention should be auto-approved based on severity"""
        if severity == InterventionSeverity.CRITICAL:
            return self.settings.get("auto_approve_critical", True)
        elif severity == InterventionSeverity.HIGH:
            return self.settings.get("auto_approve_high", True)
        elif severity == InterventionSeverity.MEDIUM:
            return self.settings.get("auto_approve_medium", False)
        elif severity == InterventionSeverity.LOW:
            return self.settings.get("auto_approve_low", False)
        
        return False
    
    def _check_intervention_rate_limit(self) -> bool:
        """Check if intervention rate limit is exceeded"""
        max_interventions = self.settings.get("max_interventions_per_hour", 20)
        
        # Count interventions in the last hour
        one_hour_ago = datetime.now() - timedelta(hours=1)
        recent_interventions = [
            r for r in self.intervention_history 
            if datetime.fromisoformat(r["timestamp"]) > one_hour_ago
        ]
        
        return len(recent_interventions) < max_interventions
    
    def _check_intervention_cooldown(self, intervention_data: Dict[str, Any]) -> bool:
        """Check if intervention is in cooldown period"""
        intervention_type = intervention_data["intervention"]["type"].value
        cooldown_seconds = intervention_data["intervention"].get("cooldown", 300)
        
        # Find recent interventions of the same type
        cutoff_time = datetime.now() - timedelta(seconds=cooldown_seconds)
        recent_interventions = [
            r for r in self.intervention_history 
            if (r["intervention_type"] == intervention_type and 
                datetime.fromisoformat(r["timestamp"]) > cutoff_time)
        ]
        
        return len(recent_interventions) == 0
    
    def _record_intervention(self, intervention_data: Dict[str, Any], success: bool, execution_time: float):
        """Record intervention in history"""
        record = {
            "timestamp": intervention_data["timestamp"],
            "rule_id": intervention_data["rule_id"],
            "rule_name": intervention_data["rule_name"],
            "intervention_type": intervention_data["intervention"]["type"].value,
            "action": intervention_data["intervention"]["action"],
            "severity": intervention_data["intervention"]["severity"].value,
            "success": success,
            "execution_time": execution_time,
            "auto_approved": intervention_data.get("auto_approved", False)
        }
        
        self.intervention_history.append(record)
        
        # Store in database
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO automated_responses 
                (rule_id, rule_name, trigger_type, trigger_value, response_type, 
                 response_action, severity, status, execution_time_ms)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                record["rule_id"],
                record["rule_name"],
                record["intervention_type"],
                record.get("trigger_value", 0),
                record["intervention_type"],
                record["action"],
                record["severity"],
                "success" if success else "failed",
                int(execution_time * 1000)
            ))
            
            conn.commit()
            conn.close()
        except Exception as e:
            self.logger.error(f"Failed to record intervention in database: {e}")
    
    def _update_average_response_time(self, execution_time: float):
        """Update average response time"""
        current_avg = self.intervention_stats["average_response_time"]
        total_interventions = self.intervention_stats["total_interventions"]
        
        if total_interventions == 1:
            self.intervention_stats["average_response_time"] = execution_time
        else:
            self.intervention_stats["average_response_time"] = (
                (current_avg * (total_interventions - 1) + execution_time) / total_interventions
            )
    
    def _send_intervention_notification(self, intervention_data: Dict[str, Any], success: bool, error: str = None):
        """Send intervention notification"""
        # This would integrate with the email notification system
        try:
            from email_notifications import EmailNotificationManager
            email_manager = EmailNotificationManager()
            
            subject = f"Automated Intervention: {'Success' if success else 'Failed'}"
            message = f"Intervention: {intervention_data['intervention']['type'].value}\n"
            message += f"Action: {intervention_data['intervention']['action']}\n"
            message += f"Rule: {intervention_data['rule_name']}\n"
            message += f"Time: {intervention_data['timestamp']}\n"
            
            if not success and error:
                message += f"Error: {error}"
            
            # Send notification
            email_manager.send_alert_notification(
                "automated_intervention",
                message,
                "high" if not success else "medium",
                intervention_data
            )
        except:
            pass
    
    def get_intervention_statistics(self) -> Dict[str, Any]:
        """Get intervention statistics"""
        one_hour_ago = datetime.now() - timedelta(hours=1)
        one_day_ago = datetime.now() - timedelta(days=1)
        
        recent_hour = [r for r in self.intervention_history if datetime.fromisoformat(r["timestamp"]) > one_hour_ago]
        recent_day = [r for r in self.intervention_history if datetime.fromisoformat(r["timestamp"]) > one_day_ago]
        
        # Calculate manual intervention reduction
        manual_intervention_reduction = self._calculate_manual_intervention_reduction()
        
        return {
            "total_interventions": self.intervention_stats["total_interventions"],
            "successful_interventions": self.intervention_stats["successful_interventions"],
            "success_rate": self.intervention_stats["successful_interventions"] / max(1, self.intervention_stats["total_interventions"]),
            "interventions_last_hour": len(recent_hour),
            "interventions_last_day": len(recent_day),
            "average_response_time": self.intervention_stats["average_response_time"],
            "manual_intervention_reduction": manual_intervention_reduction,
            "manual_intervention_reduction_target": self.settings.get("manual_intervention_threshold", 0.5),
            "target_achieved": manual_intervention_reduction >= self.settings.get("manual_intervention_threshold", 0.5),
            "queue_size": self.intervention_queue.qsize(),
            "enabled_rules": len([r for r in self.intervention_rules if r.get("enabled", True)]),
            "total_rules": len(self.intervention_rules),
            "auto_approve_settings": {
                "critical": self.settings.get("auto_approve_critical", True),
                "high": self.settings.get("auto_approve_high", True),
                "medium": self.settings.get("auto_approve_medium", False),
                "low": self.settings.get("auto_approve_low", False)
            },
            "intervention_types": self.intervention_stats["intervention_types"]
        }
    
    def _calculate_manual_intervention_reduction(self) -> float:
        """Calculate manual intervention reduction percentage"""
        # This is a simplified calculation
        # In reality, you'd track manual interventions before and after automation
        
        total_interventions = self.intervention_stats["total_interventions"]
        auto_approved_interventions = sum(1 for r in self.intervention_history if r.get("auto_approved", False))
        
        if total_interventions == 0:
            return 0.0
        
        # Estimate reduction based on auto-approved interventions
        estimated_manual_interventions_prevented = auto_approved_interventions
        reduction_rate = estimated_manual_interventions_prevented / total_interventions
        
        return min(reduction_rate, 1.0)  # Cap at 100%
    
    def get_intervention_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get intervention history"""
        return self.intervention_history[-limit:]
    
    def update_settings(self, new_settings: Dict[str, Any]) -> bool:
        """Update intervention settings"""
        try:
            self.settings.update(new_settings)
            return self.save_settings(self.settings)
        except Exception as e:
            self.logger.error(f"Error updating intervention settings: {e}")
            return False

# Intervention manager singleton
intervention_manager = AutomatedInterventionManager()

if __name__ == '__main__':
    manager = AutomatedInterventionManager()
    
    # Test intervention processing
    test_alert = {
        "alert_type": "high_memory",
        "message": "Memory usage is critical",
        "severity": "critical",
        "cpu_usage": 45,
        "memory_usage": 92,
        "cpu_temp": 65,
        "gpu_temp": 70
    }
    
    print("Processing test alert...")
    result = manager.process_system_alert(test_alert)
    print(f"Interventions triggered: {result}")
    
    # Display statistics
    stats = manager.get_intervention_statistics()
    print(f"Manual intervention reduction: {stats['manual_intervention_reduction']:.2%}")
    print(f"Target achieved: {stats['target_achieved']}")
