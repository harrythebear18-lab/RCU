#!/usr/bin/env python3
"""
Automated Responses System
Handles automatic system responses to alerts and performance issues.
"""

import os
import json
import subprocess
import threading
import time
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
import queue
import sqlite3
from enum import Enum

class ResponseType(Enum):
    """Types of automated responses"""
    PROCESS_TERMINATION = "process_termination"
    MEMORY_CLEANUP = "memory_cleanup"
    DISK_CLEANUP = "disk_cleanup"
    SERVICE_RESTART = "service_restart"
    PRIORITY_ADJUSTMENT = "priority_adjustment"
    NOTIFICATION = "notification"
    LOGGING = "logging"
    CUSTOM_SCRIPT = "custom_script"

class ResponseSeverity(Enum):
    """Severity levels for responses"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AutomatedResponseManager:
    """Manages automated system responses to alerts"""
    
    def __init__(self, settings_file="automated_responses_settings.json"):
        self.settings_file = os.path.join(os.path.dirname(__file__), settings_file)
        self.db_path = os.path.join(os.path.dirname(__file__), "system_monitoring.db")
        
        # Response queue
        self.response_queue = queue.Queue()
        self.running = False
        self.response_thread = None
        
        # Response history
        self.response_history = []
        
        # Load settings
        self.settings = self.load_settings()
        
        # Response rules
        self.response_rules = self.load_response_rules()
        
        # Custom response handlers
        self.custom_handlers = {}
        
        # Start response manager if enabled
        if self.settings.get("enabled", False):
            self.start_response_manager()
    
    def load_settings(self) -> Dict[str, Any]:
        """Load automated response settings"""
        default_settings = {
            "enabled": False,
            "auto_approve_critical": True,
            "auto_approve_high": False,
            "auto_approve_medium": False,
            "auto_approve_low": False,
            "max_responses_per_hour": 10,
            "response_timeout": 30,
            "log_all_responses": True,
            "require_confirmation": True,
            "safe_mode": True,
            "excluded_processes": ["system", "csrss", "winlogon", "lsass"],
            "backup_before_actions": True
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
            print(f"Error loading response settings: {e}")
            return default_settings
    
    def save_settings(self, settings: Dict[str, Any]) -> bool:
        """Save automated response settings"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving response settings: {e}")
            return False
    
    def load_response_rules(self) -> List[Dict[str, Any]]:
        """Load response rules"""
        default_rules = [
            {
                "id": "cpu_critical",
                "name": "Critical CPU Usage Response",
                "trigger": {
                    "metric": "cpu_usage",
                    "operator": ">=",
                    "value": 95,
                    "duration": 30  # seconds
                },
                "responses": [
                    {
                        "type": ResponseType.PRIORITY_ADJUSTMENT,
                        "action": "lower_critical_process_priorities",
                        "severity": ResponseSeverity.HIGH
                    },
                    {
                        "type": ResponseType.NOTIFICATION,
                        "action": "send_critical_cpu_alert",
                        "severity": ResponseSeverity.MEDIUM
                    }
                ],
                "enabled": True
            },
            {
                "id": "memory_critical",
                "name": "Critical Memory Usage Response",
                "trigger": {
                    "metric": "memory_usage",
                    "operator": ">=",
                    "value": 95,
                    "duration": 30
                },
                "responses": [
                    {
                        "type": ResponseType.MEMORY_CLEANUP,
                        "action": "aggressive_memory_cleanup",
                        "severity": ResponseSeverity.HIGH
                    },
                    {
                        "type": ResponseType.PROCESS_TERMINATION,
                        "action": "terminate_memory_intensive_processes",
                        "severity": ResponseSeverity.CRITICAL
                    }
                ],
                "enabled": True
            },
            {
                "id": "gpu_critical",
                "name": "Critical GPU Usage Response",
                "trigger": {
                    "metric": "gpu_usage",
                    "operator": ">=",
                    "value": 95,
                    "duration": 30
                },
                "responses": [
                    {
                        "type": ResponseType.PRIORITY_ADJUSTMENT,
                        "action": "lower_gpu_process_priorities",
                        "severity": ResponseSeverity.MEDIUM
                    }
                ],
                "enabled": True
            },
            {
                "id": "temperature_critical",
                "name": "Critical Temperature Response",
                "trigger": {
                    "metric": "temperature",
                    "operator": ">=",
                    "value": 85,
                    "duration": 60
                },
                "responses": [
                    {
                        "type": ResponseType.NOTIFICATION,
                        "action": "send_thermal_alert",
                        "severity": ResponseSeverity.HIGH
                    },
                    {
                        "type": ResponseType.PRIORITY_ADJUSTMENT,
                        "action": "reduce_process_priorities",
                        "severity": ResponseSeverity.MEDIUM
                    }
                ],
                "enabled": True
            },
            {
                "id": "disk_high_io",
                "name": "High Disk I/O Response",
                "trigger": {
                    "metric": "disk_io",
                    "operator": ">=",
                    "value": 10000,  # MB/s
                    "duration": 60
                },
                "responses": [
                    {
                        "type": ResponseType.DISK_CLEANUP,
                        "action": "temp_file_cleanup",
                        "severity": ResponseSeverity.MEDIUM
                    }
                ],
                "enabled": True
            }
        ]
        
        return default_rules
    
    def start_response_manager(self):
        """Start the automated response manager"""
        if not self.running:
            self.running = True
            self.response_thread = threading.Thread(target=self._response_worker, daemon=True)
            self.response_thread.start()
    
    def stop_response_manager(self):
        """Stop the automated response manager"""
        self.running = False
        if self.response_thread:
            self.response_thread.join(timeout=5)
    
    def process_alert(self, alert: Dict[str, Any]) -> bool:
        """Process an alert and trigger automated responses"""
        if not self.settings.get("enabled", False):
            return False
        
        # Check response rate limit
        if not self._check_response_rate_limit():
            return False
        
        # Find matching response rules
        matching_rules = self._find_matching_rules(alert)
        
        if not matching_rules:
            return False
        
        # Queue responses
        for rule in matching_rules:
            for response in rule["responses"]:
                response_data = {
                    "rule_id": rule["id"],
                    "rule_name": rule["name"],
                    "alert": alert,
                    "response": response,
                    "timestamp": datetime.now().isoformat()
                }
                
                # Check if auto-approval is enabled for this severity
                if self._should_auto_approve(response["severity"]):
                    response_data["auto_approved"] = True
                else:
                    response_data["auto_approved"] = False
                
                self.response_queue.put(response_data)
        
        return True
    
    def _response_worker(self):
        """Background worker for processing responses"""
        while self.running:
            try:
                # Get response from queue
                response_data = self.response_queue.get(timeout=10)
                
                # Process response
                self._execute_response(response_data)
                
                # Mark task as done
                self.response_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error in response worker: {e}")
    
    def _execute_response(self, response_data: Dict[str, Any]):
        """Execute an automated response"""
        try:
            response = response_data["response"]
            response_type = response["type"]
            action = response["action"]
            
            # Log response execution
            self._log_response(response_data)
            
            # Execute response based on type
            if response_type == ResponseType.PROCESS_TERMINATION:
                self._execute_process_termination(action, response_data)
            elif response_type == ResponseType.MEMORY_CLEANUP:
                self._execute_memory_cleanup(action, response_data)
            elif response_type == ResponseType.DISK_CLEANUP:
                self._execute_disk_cleanup(action, response_data)
            elif response_type == ResponseType.SERVICE_RESTART:
                self._execute_service_restart(action, response_data)
            elif response_type == ResponseType.PRIORITY_ADJUSTMENT:
                self._execute_priority_adjustment(action, response_data)
            elif response_type == ResponseType.NOTIFICATION:
                self._execute_notification(action, response_data)
            elif response_type == ResponseType.LOGGING:
                self._execute_logging(action, response_data)
            elif response_type == ResponseType.CUSTOM_SCRIPT:
                self._execute_custom_script(action, response_data)
            
            # Record response in history
            self.response_history.append({
                "timestamp": response_data["timestamp"],
                "rule_id": response_data["rule_id"],
                "action": action,
                "severity": response["severity"],
                "success": True
            })
            
        except Exception as e:
            print(f"Error executing response: {e}")
            self.response_history.append({
                "timestamp": response_data["timestamp"],
                "rule_id": response_data["rule_id"],
                "action": response_data["response"]["action"],
                "severity": response_data["response"]["severity"],
                "success": False,
                "error": str(e)
            })
    
    def _execute_process_termination(self, action: str, response_data: Dict[str, Any]):
        """Execute process termination response"""
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
                        print(f"Terminated process: {proc.info['name']} (PID: {proc.info['pid']})")
                    except:
                        pass
    
    def _execute_memory_cleanup(self, action: str, response_data: Dict[str, Any]):
        """Execute memory cleanup response"""
        if action == "aggressive_memory_cleanup":
            import gc
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
    
    def _execute_disk_cleanup(self, action: str, response_data: Dict[str, Any]):
        """Execute disk cleanup response"""
        if action == "temp_file_cleanup":
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
    
    def _execute_service_restart(self, action: str, response_data: Dict[str, Any]):
        """Execute service restart response"""
        # This would implement Windows service restart functionality
        # For safety, this is a placeholder
        pass
    
    def _execute_priority_adjustment(self, action: str, response_data: Dict[str, Any]):
        """Execute priority adjustment response"""
        if action == "lower_critical_process_priorities":
            # Lower priorities of high CPU usage processes
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
                try:
                    if proc.info['cpu_percent'] > 80:
                        proc.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
                except:
                    pass
        elif action == "lower_gpu_process_priorities":
            # Lower priorities of GPU-intensive processes
            # This would require GPU-specific APIs
            pass
        elif action == "reduce_process_priorities":
            # Reduce all non-critical process priorities
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if proc.info['name'].lower() not in self.settings.get("excluded_processes", []):
                        proc.nice(psutil.IDLE_PRIORITY_CLASS)
                except:
                    pass
    
    def _execute_notification(self, action: str, response_data: Dict[str, Any]):
        """Execute notification response"""
        # This would integrate with the notification system
        alert = response_data["alert"]
        print(f"Notification: {alert.get('message', 'System alert')}")
    
    def _execute_logging(self, action: str, response_data: Dict[str, Any]):
        """Execute logging response"""
        # Log to database
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO automated_responses 
                (timestamp, rule_id, action, severity, alert_details)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                response_data["timestamp"],
                response_data["rule_id"],
                response_data["response"]["action"],
                response_data["response"]["severity"].value,
                json.dumps(response_data["alert"])
            ))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error logging response: {e}")
    
    def _execute_custom_script(self, action: str, response_data: Dict[str, Any]):
        """Execute custom script response"""
        # This would execute custom scripts
        # For safety, this is a placeholder
        pass
    
    def _find_matching_rules(self, alert: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find response rules that match the alert"""
        matching_rules = []
        
        for rule in self.response_rules:
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
        elif metric == "temperature":
            return max(alert.get("cpu_temp", 0), alert.get("gpu_temp", 0))
        elif metric == "disk_io":
            return alert.get("disk_read", 0) + alert.get("disk_write", 0)
        
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
    
    def _should_auto_approve(self, severity: ResponseSeverity) -> bool:
        """Check if response should be auto-approved based on severity"""
        if severity == ResponseSeverity.CRITICAL:
            return self.settings.get("auto_approve_critical", True)
        elif severity == ResponseSeverity.HIGH:
            return self.settings.get("auto_approve_high", False)
        elif severity == ResponseSeverity.MEDIUM:
            return self.settings.get("auto_approve_medium", False)
        elif severity == ResponseSeverity.LOW:
            return self.settings.get("auto_approve_low", False)
        
        return False
    
    def _check_response_rate_limit(self) -> bool:
        """Check if response rate limit is exceeded"""
        max_responses = self.settings.get("max_responses_per_hour", 10)
        
        # Count responses in the last hour
        one_hour_ago = datetime.now() - timedelta(hours=1)
        recent_responses = [
            r for r in self.response_history 
            if datetime.fromisoformat(r["timestamp"]) > one_hour_ago
        ]
        
        return len(recent_responses) < max_responses
    
    def _log_response(self, response_data: Dict[str, Any]):
        """Log response execution"""
        if not self.settings.get("log_all_responses", True):
            return
        
        log_entry = {
            "timestamp": response_data["timestamp"],
            "rule_id": response_data["rule_id"],
            "action": response_data["response"]["action"],
            "severity": response_data["response"]["severity"].value,
            "auto_approved": response_data.get("auto_approved", False)
        }
        
        print(f"Automated Response: {log_entry}")
    
    def add_custom_rule(self, rule: Dict[str, Any]) -> bool:
        """Add a custom response rule"""
        try:
            # Validate rule structure
            required_fields = ["id", "name", "trigger", "responses", "enabled"]
            for field in required_fields:
                if field not in rule:
                    return False
            
            # Check for duplicate ID
            if any(r["id"] == rule["id"] for r in self.response_rules):
                return False
            
            # Add rule
            self.response_rules.append(rule)
            return True
            
        except Exception as e:
            print(f"Error adding custom rule: {e}")
            return False
    
    def remove_rule(self, rule_id: str) -> bool:
        """Remove a response rule"""
        try:
            self.response_rules = [r for r in self.response_rules if r["id"] != rule_id]
            return True
        except Exception as e:
            print(f"Error removing rule: {e}")
            return False
    
    def enable_rule(self, rule_id: str) -> bool:
        """Enable a response rule"""
        for rule in self.response_rules:
            if rule["id"] == rule_id:
                rule["enabled"] = True
                return True
        return False
    
    def disable_rule(self, rule_id: str) -> bool:
        """Disable a response rule"""
        for rule in self.response_rules:
            if rule["id"] == rule_id:
                rule["enabled"] = False
                return True
        return False
    
    def get_response_statistics(self) -> Dict[str, Any]:
        """Get response statistics"""
        one_hour_ago = datetime.now() - timedelta(hours=1)
        one_day_ago = datetime.now() - timedelta(days=1)
        
        recent_hour = [r for r in self.response_history if datetime.fromisoformat(r["timestamp"]) > one_hour_ago]
        recent_day = [r for r in self.response_history if datetime.fromisoformat(r["timestamp"]) > one_day_ago]
        
        return {
            "total_responses": len(self.response_history),
            "responses_last_hour": len(recent_hour),
            "responses_last_day": len(recent_day),
            "success_rate": sum(1 for r in recent_day if r.get("success", False)) / len(recent_day) if recent_day else 0,
            "queue_size": self.response_queue.qsize(),
            "enabled_rules": len([r for r in self.response_rules if r.get("enabled", True)]),
            "total_rules": len(self.response_rules),
            "auto_approve_settings": {
                "critical": self.settings.get("auto_approve_critical", True),
                "high": self.settings.get("auto_approve_high", False),
                "medium": self.settings.get("auto_approve_medium", False),
                "low": self.settings.get("auto_approve_low", False)
            }
        }
    
    def get_response_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get response history"""
        return self.response_history[-limit:]
    
    def get_rules(self) -> List[Dict[str, Any]]:
        """Get all response rules"""
        return self.response_rules.copy()
    
    def update_settings(self, new_settings: Dict[str, Any]) -> bool:
        """Update response settings"""
        try:
            self.settings.update(new_settings)
            return self.save_settings(self.settings)
        except Exception as e:
            print(f"Error updating settings: {e}")
            return False
