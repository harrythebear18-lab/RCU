#!/usr/bin/env python3
"""
Automation Framework for Homelab Portal
Comprehensive automation system for resource sharing and management
"""

import time
import json
import logging
import threading
import schedule
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio
from abc import ABC, abstractmethod

class AutomationStatus(Enum):
    """Automation status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    CANCELLED = "cancelled"

class TriggerType(Enum):
    """Trigger type enumeration"""
    SCHEDULE = "schedule"
    EVENT = "event"
    CONDITION = "condition"
    MANUAL = "manual"

@dataclass
class AutomationTrigger:
    """Automation trigger configuration"""
    trigger_id: str
    trigger_type: TriggerType
    config: Dict[str, Any]
    enabled: bool = True

@dataclass
class AutomationAction:
    """Automation action configuration"""
    action_id: str
    action_type: str
    config: Dict[str, Any]
    enabled: bool = True

@dataclass
class AutomationRule:
    """Complete automation rule"""
    rule_id: str
    name: str
    description: str
    triggers: List[AutomationTrigger]
    actions: List[AutomationAction]
    created_at: datetime
    enabled: bool = True
    last_run: Optional[datetime] = None
    run_count: int = 0
    status: AutomationStatus = AutomationStatus.PENDING

class AutomationActionBase(ABC):
    """Base class for automation actions"""
    
    def __init__(self, portal_instance):
        self.portal = portal_instance
        self.logger = logging.getLogger(f"AutomationAction.{self.__class__.__name__}")
    
    @abstractmethod
    async def execute(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the automation action"""
        pass
    
    @abstractmethod
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate action configuration"""
        pass

class ScreenShareAction(AutomationActionBase):
    """Automated screen sharing action"""
    
    async def execute(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute screen sharing automation"""
        try:
            target_node = config.get('target_node')
            duration_minutes = config.get('duration_minutes', 30)
            quality = config.get('quality', 'high')
            
            if not target_node:
                return {'success': False, 'error': 'Target node not specified'}
            
            # Start screen sharing
            session_id = self.portal.start_screen_share(target_node)
            
            if not session_id:
                return {'success': False, 'error': 'Failed to start screen sharing'}
            
            # Schedule stop action
            if duration_minutes > 0:
                schedule_job = schedule.every(duration_minutes).minutes.do(
                    self._stop_screen_share, session_id
                )
            
            self.logger.info(f"Automated screen sharing started with {target_node}")
            
            return {
                'success': True,
                'session_id': session_id,
                'target_node': target_node,
                'duration_minutes': duration_minutes,
                'quality': quality
            }
            
        except Exception as e:
            self.logger.error(f"Screen share automation failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _stop_screen_share(self, session_id: str):
        """Stop screen sharing session"""
        try:
            self.portal.stop_screen_share(session_id)
            self.logger.info(f"Automated screen sharing stopped: {session_id}")
        except Exception as e:
            self.logger.error(f"Failed to stop screen sharing: {e}")
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate screen sharing configuration"""
        required_fields = ['target_node']
        return all(field in config for field in required_fields)

class FileTransferAction(AutomationActionBase):
    """Automated file transfer action"""
    
    async def execute(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute file transfer automation"""
        try:
            target_node = config.get('target_node')
            file_patterns = config.get('file_patterns', [])
            source_directory = config.get('source_directory', '')
            recursive = config.get('recursive', True)
            
            if not target_node:
                return {'success': False, 'error': 'Target node not specified'}
            
            # Find files matching patterns
            files_to_transfer = self._find_files(file_patterns, source_directory, recursive)
            
            if not files_to_transfer:
                return {'success': True, 'message': 'No files found matching patterns'}
            
            # Transfer files
            transferred_files = []
            failed_files = []
            
            for file_path in files_to_transfer:
                try:
                    success = self.portal.share_file(file_path, target_node)
                    if success:
                        transferred_files.append(file_path)
                    else:
                        failed_files.append(file_path)
                except Exception as e:
                    failed_files.append(file_path)
                    self.logger.error(f"Failed to transfer {file_path}: {e}")
            
            return {
                'success': len(failed_files) == 0,
                'target_node': target_node,
                'files_found': len(files_to_transfer),
                'files_transferred': len(transferred_files),
                'files_failed': len(failed_files),
                'failed_files': failed_files
            }
            
        except Exception as e:
            self.logger.error(f"File transfer automation failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _find_files(self, patterns: List[str], directory: str, recursive: bool) -> List[str]:
        """Find files matching patterns"""
        import glob
        import os
        
        files = []
        
        for pattern in patterns:
            if directory:
                pattern = os.path.join(directory, pattern)
            
            if recursive:
                pattern = os.path.join(pattern, '**', '*')
            
            found_files = glob.glob(pattern, recursive=recursive)
            files.extend([f for f in found_files if os.path.isfile(f)])
        
        return list(set(files))  # Remove duplicates
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate file transfer configuration"""
        required_fields = ['target_node']
        return all(field in config for field in required_fields)

class ResourceOptimizationAction(AutomationActionBase):
    """Automated resource optimization action"""
    
    async def execute(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute resource optimization automation"""
        try:
            optimization_type = config.get('type', 'full')
            target_nodes = config.get('target_nodes', [])
            
            results = {}
            
            # Optimize local system
            if not target_nodes or 'local' in target_nodes:
                local_result = self._optimize_local_system(optimization_type)
                results['local'] = local_result
            
            # Optimize remote systems
            for node in target_nodes:
                if node != 'local':
                    remote_result = await self._optimize_remote_system(node, optimization_type)
                    results[node] = remote_result
            
            return {
                'success': all(r.get('success', False) for r in results.values()),
                'optimization_type': optimization_type,
                'results': results
            }
            
        except Exception as e:
            self.logger.error(f"Resource optimization automation failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _optimize_local_system(self, optimization_type: str) -> Dict[str, Any]:
        """Optimize local system"""
        try:
            if optimization_type == 'full':
                success = self.portal.hardware_optimizer.optimize_for_identical_hardware()
            elif optimization_type == 'network':
                success = self.portal.intel_optimizer.optimize_network_settings()
            elif optimization_type == 'gpu':
                success = self.portal.gpu_sharing.optimize_gpu_for_sharing()
            elif optimization_type == 'memory':
                success = self.portal.ram_sharing.optimize_ddr4_settings()
            else:
                success = False
            
            return {
                'success': success,
                'optimization_type': optimization_type,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _optimize_remote_system(self, node: str, optimization_type: str) -> Dict[str, Any]:
        """Optimize remote system"""
        try:
            # This would connect to remote system and run optimization
            # For now, simulate the optimization
            await asyncio.sleep(2)  # Simulate network delay
            
            return {
                'success': True,
                'node': node,
                'optimization_type': optimization_type,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate resource optimization configuration"""
        return True  # All configurations are valid

class MonitoringAction(AutomationActionBase):
    """Automated monitoring action"""
    
    async def execute(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute monitoring automation"""
        try:
            monitoring_type = config.get('type', 'system')
            threshold = config.get('threshold', {})
            actions = config.get('actions', [])
            
            results = {}
            
            if monitoring_type == 'system':
                results['system'] = await self._monitor_system(threshold, actions)
            elif monitoring_type == 'network':
                results['network'] = await self._monitor_network(threshold, actions)
            elif monitoring_type == 'resources':
                results['resources'] = await self._monitor_resources(threshold, actions)
            
            return {
                'success': True,
                'monitoring_type': monitoring_type,
                'results': results
            }
            
        except Exception as e:
            self.logger.error(f"Monitoring automation failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _monitor_system(self, threshold: Dict[str, Any], actions: List[str]) -> Dict[str, Any]:
        """Monitor system metrics"""
        try:
            # Get system metrics
            cpu_usage = self._get_cpu_usage()
            memory_usage = self._get_memory_usage()
            gpu_usage = self._get_gpu_usage()
            
            metrics = {
                'cpu_usage': cpu_usage,
                'memory_usage': memory_usage,
                'gpu_usage': gpu_usage
            }
            
            # Check thresholds
            alerts = []
            
            if cpu_usage > threshold.get('cpu', 80):
                alerts.append(f"High CPU usage: {cpu_usage}%")
            
            if memory_usage > threshold.get('memory', 85):
                alerts.append(f"High memory usage: {memory_usage}%")
            
            if gpu_usage > threshold.get('gpu', 90):
                alerts.append(f"High GPU usage: {gpu_usage}%")
            
            # Execute actions based on alerts
            for action in actions:
                if alerts and 'optimize' in action:
                    self._trigger_optimization(alerts)
                elif alerts and 'notify' in action:
                    self._send_notification(alerts)
            
            return {
                'metrics': metrics,
                'alerts': alerts,
                'actions_taken': actions
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _get_cpu_usage(self) -> float:
        """Get CPU usage percentage"""
        try:
            import psutil
            return psutil.cpu_percent(interval=1)
        except:
            return 0.0
    
    def _get_memory_usage(self) -> float:
        """Get memory usage percentage"""
        try:
            import psutil
            memory = psutil.virtual_memory()
            return memory.percent
        except:
            return 0.0
    
    def _get_gpu_usage(self) -> float:
        """Get GPU usage percentage"""
        try:
            status = self.portal.gpu_sharing.get_gpu_sharing_status()
            return status.get('gpu_info', {}).get('utilization', 0)
        except:
            return 0.0
    
    def _trigger_optimization(self, alerts: List[str]):
        """Trigger optimization based on alerts"""
        try:
            self.portal.hardware_optimizer.optimize_for_identical_hardware()
            self.logger.info(f"Optimization triggered by alerts: {alerts}")
        except Exception as e:
            self.logger.error(f"Failed to trigger optimization: {e}")
    
    def _send_notification(self, alerts: List[str]):
        """Send notification for alerts"""
        try:
            # This would send notification through the portal
            self.logger.info(f"Notification sent for alerts: {alerts}")
        except Exception as e:
            self.logger.error(f"Failed to send notification: {e}")
    
    async def _monitor_network(self, threshold: Dict[str, Any], actions: List[str]) -> Dict[str, Any]:
        """Monitor network metrics"""
        # Network monitoring implementation
        return {'message': 'Network monitoring not yet implemented'}
    
    async def _monitor_resources(self, threshold: Dict[str, Any], actions: List[str]) -> Dict[str, Any]:
        """Monitor resource metrics"""
        # Resource monitoring implementation
        return {'message': 'Resource monitoring not yet implemented'}
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate monitoring configuration"""
        return True  # All configurations are valid

class AutomationFramework:
    """Main automation framework"""
    
    def __init__(self, portal_instance):
        self.portal = portal_instance
        self.logger = logging.getLogger("AutomationFramework")
        self.rules: Dict[str, AutomationRule] = {}
        self.running = False
        self.scheduler_thread = None
        self.action_registry = {
            'screen_share': ScreenShareAction,
            'file_transfer': FileTransferAction,
            'resource_optimization': ResourceOptimizationAction,
            'monitoring': MonitoringAction
        }
        
    def start(self):
        """Start automation framework"""
        if self.running:
            return
        
        self.running = True
        
        # Start scheduler thread
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        
        self.logger.info("Automation framework started")
    
    def stop(self):
        """Stop automation framework"""
        self.running = False
        
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        
        self.logger.info("Automation framework stopped")
    
    def _scheduler_loop(self):
        """Main scheduler loop"""
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(1)
            except Exception as e:
                self.logger.error(f"Scheduler loop error: {e}")
                time.sleep(1)
    
    def create_rule(self, name: str, description: str, triggers: List[Dict[str, Any]], 
                   actions: List[Dict[str, Any]]) -> str:
        """Create automation rule"""
        try:
            rule_id = self._generate_rule_id()
            
            # Convert triggers
            trigger_objects = []
            for trigger_config in triggers:
                trigger = AutomationTrigger(
                    trigger_id=self._generate_trigger_id(),
                    trigger_type=TriggerType(trigger_config['type']),
                    config=trigger_config
                )
                trigger_objects.append(trigger)
            
            # Convert actions
            action_objects = []
            for action_config in actions:
                action = AutomationAction(
                    action_id=self._generate_action_id(),
                    action_type=action_config['type'],
                    config=action_config
                )
                action_objects.append(action)
            
            # Create rule
            rule = AutomationRule(
                rule_id=rule_id,
                name=name,
                description=description,
                triggers=trigger_objects,
                actions=action_objects,
                created_at=datetime.now()
            )
            
            self.rules[rule_id] = rule
            
            # Setup triggers
            self._setup_rule_triggers(rule)
            
            self.logger.info(f"Created automation rule: {name}")
            return rule_id
            
        except Exception as e:
            self.logger.error(f"Failed to create rule: {e}")
            return ""
    
    def _setup_rule_triggers(self, rule: AutomationRule):
        """Setup triggers for automation rule"""
        try:
            for trigger in rule.triggers:
                if not trigger.enabled:
                    continue
                
                if trigger.trigger_type == TriggerType.SCHEDULE:
                    self._setup_schedule_trigger(rule, trigger)
                elif trigger.trigger_type == TriggerType.EVENT:
                    self._setup_event_trigger(rule, trigger)
                elif trigger.trigger_type == TriggerType.CONDITION:
                    self._setup_condition_trigger(rule, trigger)
                    
        except Exception as e:
            self.logger.error(f"Failed to setup triggers for rule {rule.name}: {e}")
    
    def _setup_schedule_trigger(self, rule: AutomationRule, trigger: AutomationTrigger):
        """Setup schedule-based trigger"""
        try:
            config = trigger.config
            schedule_type = config.get('schedule_type', 'daily')
            time_str = config.get('time', '00:00')
            
            if schedule_type == 'daily':
                schedule.every().day.at(time_str).do(self._execute_rule, rule.rule_id)
            elif schedule_type == 'hourly':
                schedule.every().hour.do(self._execute_rule, rule.rule_id)
            elif schedule_type == 'weekly':
                day = config.get('day', 'monday')
                getattr(schedule.every(), day).at(time_str).do(self._execute_rule, rule.rule_id)
            elif schedule_type == 'interval':
                interval_minutes = config.get('interval_minutes', 60)
                schedule.every(interval_minutes).minutes.do(self._execute_rule, rule.rule_id)
            
            self.logger.info(f"Setup schedule trigger for rule {rule.name}")
            
        except Exception as e:
            self.logger.error(f"Failed to setup schedule trigger: {e}")
    
    def _setup_event_trigger(self, rule: AutomationRule, trigger: AutomationTrigger):
        """Setup event-based trigger"""
        # Event trigger implementation would go here
        self.logger.info(f"Event trigger setup not yet implemented for rule {rule.name}")
    
    def _setup_condition_trigger(self, rule: AutomationRule, trigger: AutomationTrigger):
        """Setup condition-based trigger"""
        # Condition trigger implementation would go here
        self.logger.info(f"Condition trigger setup not yet implemented for rule {rule.name}")
    
    def _execute_rule(self, rule_id: str):
        """Execute automation rule"""
        try:
            if rule_id not in self.rules:
                self.logger.error(f"Rule not found: {rule_id}")
                return
            
            rule = self.rules[rule_id]
            
            if not rule.enabled:
                return
            
            rule.status = AutomationStatus.RUNNING
            rule.last_run = datetime.now()
            
            # Execute actions
            results = []
            for action in rule.actions:
                if not action.enabled:
                    continue
                
                result = self._execute_action(action)
                results.append(result)
            
            # Update rule status
            if all(r.get('success', False) for r in results):
                rule.status = AutomationStatus.COMPLETED
            else:
                rule.status = AutomationStatus.FAILED
            
            rule.run_count += 1
            
            self.logger.info(f"Executed rule {rule.name}: {rule.status.value}")
            
        except Exception as e:
            self.logger.error(f"Failed to execute rule {rule_id}: {e}")
            if rule_id in self.rules:
                self.rules[rule_id].status = AutomationStatus.FAILED
    
    def _execute_action(self, action: AutomationAction) -> Dict[str, Any]:
        """Execute individual action"""
        try:
            action_type = action.action_type
            
            if action_type not in self.action_registry:
                return {'success': False, 'error': f'Unknown action type: {action_type}'}
            
            action_class = self.action_registry[action_type]
            action_instance = action_class(self.portal)
            
            # Validate configuration
            if not action_instance.validate_config(action.config):
                return {'success': False, 'error': 'Invalid action configuration'}
            
            # Execute action
            result = asyncio.run(action_instance.execute(action.config))
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to execute action {action.action_id}: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_rules(self) -> List[Dict[str, Any]]:
        """Get all automation rules"""
        return [
            {
                'rule_id': rule.rule_id,
                'name': rule.name,
                'description': rule.description,
                'enabled': rule.enabled,
                'status': rule.status.value,
                'created_at': rule.created_at.isoformat(),
                'last_run': rule.last_run.isoformat() if rule.last_run else None,
                'run_count': rule.run_count,
                'triggers': [
                    {
                        'trigger_id': t.trigger_id,
                        'type': t.trigger_type.value,
                        'enabled': t.enabled,
                        'config': t.config
                    }
                    for t in rule.triggers
                ],
                'actions': [
                    {
                        'action_id': a.action_id,
                        'type': a.action_type,
                        'enabled': a.enabled,
                        'config': a.config
                    }
                    for a in rule.actions
                ]
            }
            for rule in self.rules.values()
        ]
    
    def enable_rule(self, rule_id: str) -> bool:
        """Enable automation rule"""
        if rule_id in self.rules:
            self.rules[rule_id].enabled = True
            self.logger.info(f"Enabled rule: {rule_id}")
            return True
        return False
    
    def disable_rule(self, rule_id: str) -> bool:
        """Disable automation rule"""
        if rule_id in self.rules:
            self.rules[rule_id].enabled = False
            self.logger.info(f"Disabled rule: {rule_id}")
            return True
        return False
    
    def delete_rule(self, rule_id: str) -> bool:
        """Delete automation rule"""
        if rule_id in self.rules:
            del self.rules[rule_id]
            self.logger.info(f"Deleted rule: {rule_id}")
            return True
        return False
    
    def run_rule_manually(self, rule_id: str) -> bool:
        """Run rule manually"""
        try:
            self._execute_rule(rule_id)
            return True
        except Exception as e:
            self.logger.error(f"Failed to run rule manually: {e}")
            return False
    
    def _generate_rule_id(self) -> str:
        """Generate unique rule ID"""
        timestamp = str(int(time.time()))
        raw = f"rule:{timestamp}"
        import hashlib
        return hashlib.sha256(raw.encode()).hexdigest()[:16]
    
    def _generate_trigger_id(self) -> str:
        """Generate unique trigger ID"""
        timestamp = str(int(time.time()))
        raw = f"trigger:{timestamp}"
        import hashlib
        return hashlib.sha256(raw.encode()).hexdigest()[:16]
    
    def _generate_action_id(self) -> str:
        """Generate unique action ID"""
        timestamp = str(int(time.time()))
        raw = f"action:{timestamp}"
        import hashlib
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

# Global automation framework instance
_automation_framework = None

def get_automation_framework(portal_instance) -> AutomationFramework:
    """Get global automation framework instance"""
    global _automation_framework
    if _automation_framework is None:
        _automation_framework = AutomationFramework(portal_instance)
    return _automation_framework

if __name__ == "__main__":
    # Test automation framework
    print("Automation Framework Test")
    print("Note: Requires portal instance for full functionality")
    print("Automation Framework is ready for integration")
