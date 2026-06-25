#!/usr/bin/env python3
"""
Windows Assistant Integration for Homelab Portal
Handles bidirectional communication with Windows Assistant
"""

import json
import threading
import time
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

@dataclass
class AssistantDevice:
    """Windows Assistant device representation"""
    device_id: str
    name: str
    version: str
    capabilities: List[str]
    last_seen: datetime
    status: str = "online"
    system_info: Dict[str, Any] = None
    current_context: Dict[str, Any] = None

class WindowsAssistantIntegration:
    """Integration handler for Windows Assistant in Homelab Portal"""
    
    def __init__(self, event_bus, logger=None):
        self.event_bus = event_bus
        self.logger = logger or logging.getLogger("WindowsAssistantIntegration")
        
        # Registered assistants
        self.registered_assistants: Dict[str, AssistantDevice] = {}
        
        # Integration settings
        self.settings = {
            'auto_register': True,
            'sync_interval': 30,  # seconds
            'command_timeout': 10,  # seconds
            'max_assistants': 5
        }
        
        # Command queue for assistants
        self.command_queue: Dict[str, List[Dict]] = {}
        
        # Start background threads
        self.running = False
        self.start_integration()
    
    def start_integration(self):
        """Start the Windows Assistant integration service"""
        try:
            self.running = True
            
            # Start monitoring thread
            threading.Thread(target=self._assistant_monitor, daemon=True).start()
            
            # Start command processor
            threading.Thread(target=self._command_processor, daemon=True).start()
            
            self.logger.info("Windows Assistant integration started")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start Windows Assistant integration: {e}")
            return False
    
    def stop_integration(self):
        """Stop the Windows Assistant integration service"""
        try:
            self.running = False
            self.registered_assistants.clear()
            self.command_queue.clear()
            self.logger.info("Windows Assistant integration stopped")
            return True
        except Exception as e:
            self.logger.error(f"Failed to stop Windows Assistant integration: {e}")
            return False
    
    def register_assistant(self, registration_data: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new Windows Assistant"""
        try:
            device_id = registration_data.get('device_id', f"assistant_{int(time.time())}")
            
            # Check if already registered
            if device_id in self.registered_assistants:
                # Update existing registration
                assistant = self.registered_assistants[device_id]
                assistant.last_seen = datetime.now()
                assistant.system_info = registration_data.get('system_info', {})
                self.logger.info(f"Updated Windows Assistant registration: {device_id}")
            else:
                # Check limit
                if len(self.registered_assistants) >= self.settings['max_assistants']:
                    return {
                        'success': False,
                        'error': 'Maximum number of assistants reached'
                    }
                
                # Create new assistant device
                assistant = AssistantDevice(
                    device_id=device_id,
                    name=registration_data.get('name', 'Windows Assistant'),
                    version=registration_data.get('version', '1.0'),
                    capabilities=registration_data.get('capabilities', []),
                    last_seen=datetime.now(),
                    system_info=registration_data.get('system_info', {})
                )
                
                self.registered_assistants[device_id] = assistant
                self.command_queue[device_id] = []
                
                # Publish registration event
                self._publish_event('assistant_registered', {
                    'device_id': device_id,
                    'name': assistant.name,
                    'capabilities': assistant.capabilities
                })
                
                self.logger.info(f"Registered new Windows Assistant: {device_id}")
            
            return {
                'success': True,
                'device_id': device_id,
                'status': 'registered'
            }
            
        except Exception as e:
            self.logger.error(f"Assistant registration error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def unregister_assistant(self, device_id: str) -> Dict[str, Any]:
        """Unregister a Windows Assistant"""
        try:
            if device_id in self.registered_assistants:
                assistant = self.registered_assistants.pop(device_id)
                self.command_queue.pop(device_id, None)
                
                # Publish unregistration event
                self._publish_event('assistant_unregistered', {
                    'device_id': device_id,
                    'name': assistant.name
                })
                
                self.logger.info(f"Unregistered Windows Assistant: {device_id}")
                return {'success': True}
            else:
                return {'success': False, 'error': 'Assistant not found'}
                
        except Exception as e:
            self.logger.error(f"Assistant unregistration error: {e}")
            return {'success': False, 'error': str(e)}
    
    def receive_system_data(self, device_id: str, system_data: Dict[str, Any]) -> Dict[str, Any]:
        """Receive system data from Windows Assistant"""
        try:
            if device_id not in self.registered_assistants:
                return {'success': False, 'error': 'Assistant not registered'}
            
            # Update assistant info
            assistant = self.registered_assistants[device_id]
            assistant.last_seen = datetime.now()
            assistant.current_context = system_data.get('assistant', {})
            
            # Publish system data event
            self._publish_event('assistant_system_data', {
                'device_id': device_id,
                'system_data': system_data,
                'timestamp': datetime.now().isoformat()
            })
            
            # Generate commands based on system data
            commands = self._generate_commands(device_id, system_data)
            if commands:
                self.command_queue[device_id].extend(commands)
            
            return {
                'success': True,
                'commands': commands
            }
            
        except Exception as e:
            self.logger.error(f"System data processing error: {e}")
            return {'success': False, 'error': str(e)}
    
    def receive_message(self, device_id: str, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Receive message from Windows Assistant"""
        try:
            if device_id not in self.registered_assistants:
                return {'success': False, 'error': 'Assistant not registered'}
            
            # Publish message event
            self._publish_event('assistant_message', {
                'device_id': device_id,
                'message': message_data,
                'timestamp': datetime.now().isoformat()
            })
            
            return {'success': True}
            
        except Exception as e:
            self.logger.error(f"Message processing error: {e}")
            return {'success': False, 'error': str(e)}
    
    def send_command(self, device_id: str, command: Dict[str, Any]) -> Dict[str, Any]:
        """Send command to Windows Assistant"""
        try:
            if device_id not in self.registered_assistants:
                return {'success': False, 'error': 'Assistant not registered'}
            
            # Add command to queue
            self.command_queue[device_id].append(command)
            
            self.logger.info(f"Command queued for assistant {device_id}: {command.get('type')}")
            return {'success': True}
            
        except Exception as e:
            self.logger.error(f"Command queuing error: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_assistant_status(self, device_id: str = None) -> Dict[str, Any]:
        """Get status of registered assistants"""
        try:
            if device_id:
                if device_id in self.registered_assistants:
                    assistant = self.registered_assistants[device_id]
                    return {
                        'device_id': device_id,
                        'name': assistant.name,
                        'status': assistant.status,
                        'last_seen': assistant.last_seen.isoformat(),
                        'capabilities': assistant.capabilities,
                        'current_context': assistant.current_context
                    }
                else:
                    return {'error': 'Assistant not found'}
            else:
                # Return all assistants
                return {
                    'assistants': {
                        device_id: {
                            'name': assistant.name,
                            'status': assistant.status,
                            'last_seen': assistant.last_seen.isoformat(),
                            'capabilities': assistant.capabilities
                        }
                        for device_id, assistant in self.registered_assistants.items()
                    },
                    'total_count': len(self.registered_assistants)
                }
                
        except Exception as e:
            self.logger.error(f"Status retrieval error: {e}")
            return {'error': str(e)}
    
    def _generate_commands(self, device_id: str, system_data: Dict[str, Any]) -> List[Dict]:
        """Generate commands based on system data"""
        commands = []
        
        try:
            system = system_data.get('system', {})
            assistant = system_data.get('assistant', {})
            
            # CPU monitoring commands
            cpu_percent = system.get('cpu', {}).get('percent', 0)
            if cpu_percent > 80:
                commands.append({
                    'type': 'system_alert',
                    'data': {
                        'type': 'warning',
                        'message': f'High CPU usage: {cpu_percent}%'
                    }
                })
            
            # Memory monitoring commands
            memory_percent = system.get('memory', {}).get('percent', 0)
            if memory_percent > 85:
                commands.append({
                    'type': 'resource_request',
                    'data': {
                        'resource': 'memory',
                        'action': 'clean'
                    }
                })
            
            # Disk monitoring commands
            disk_percent = system.get('disk', {}).get('percent', 0)
            if disk_percent > 90:
                commands.append({
                    'type': 'system_alert',
                    'data': {
                        'type': 'error',
                        'message': f'Low disk space: {disk_percent:.1f}% used'
                    }
                })
            
            # Context-aware help commands
            active_app = assistant.get('active_application', '')
            if 'notepad' in active_app.lower():
                commands.append({
                    'type': 'show_help',
                    'data': {
                        'message': 'Need help with text editing? I can assist with formatting and shortcuts!'
                    }
                })
            elif 'file explorer' in active_app.lower():
                commands.append({
                    'type': 'show_help',
                    'data': {
                        'message': 'File Explorer tips: Use Ctrl+N for new window, Ctrl+Shift+N for new folder!'
                    }
                })
            
            # User activity-based commands
            user_activity = assistant.get('user_activity', '')
            if user_activity == 'idle':
                commands.append({
                    'type': 'message',
                    'data': {
                        'message': 'I notice you\'ve been idle. Need help with anything?',
                        'priority': 'low'
                    }
                })
            
        except Exception as e:
            self.logger.error(f"Command generation error: {e}")
        
        return commands
    
    def _assistant_monitor(self):
        """Monitor registered assistants for timeouts"""
        while self.running:
            try:
                current_time = datetime.now()
                timeout_threshold = 120  # 2 minutes
                
                # Check for inactive assistants
                inactive_assistants = []
                for device_id, assistant in self.registered_assistants.items():
                    time_diff = (current_time - assistant.last_seen).total_seconds()
                    if time_diff > timeout_threshold:
                        assistant.status = "offline"
                        inactive_assistants.append(device_id)
                    else:
                        assistant.status = "online"
                
                # Remove offline assistants after extended timeout
                extended_timeout = 300  # 5 minutes
                for device_id in inactive_assistants[:]:
                    assistant = self.registered_assistants.get(device_id)
                    if assistant:
                        time_diff = (current_time - assistant.last_seen).total_seconds()
                        if time_diff > extended_timeout:
                            self.unregister_assistant(device_id)
                            self.logger.info(f"Removed inactive assistant: {device_id}")
                
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Assistant monitor error: {e}")
                time.sleep(30)
    
    def _command_processor(self):
        """Process command queue for assistants"""
        while self.running:
            try:
                for device_id, commands in self.command_queue.items():
                    if commands:
                        # Process commands for this assistant
                        processed_commands = []
                        for command in commands:
                            # Mark command as processed (in real implementation, would send to assistant)
                            processed_commands.append(command)
                            
                            # Publish command event
                            self._publish_event('assistant_command', {
                                'device_id': device_id,
                                'command': command,
                                'timestamp': datetime.now().isoformat()
                            })
                        
                        # Clear processed commands
                        self.command_queue[device_id] = [
                            cmd for cmd in commands if cmd not in processed_commands
                        ]
                
                time.sleep(5)  # Process every 5 seconds
                
            except Exception as e:
                self.logger.error(f"Command processor error: {e}")
                time.sleep(5)
    
    def _publish_event(self, event_type: str, data: Dict[str, Any]):
        """Publish event to event bus"""
        try:
            if self.event_bus:
                self.event_bus.publish_sync(
                    'WINDOWS_ASSISTANT',
                    'windows_assistant_integration',
                    {
                        'event_type': event_type,
                        'data': data,
                        'timestamp': datetime.now().isoformat()
                    }
                )
        except Exception as e:
            self.logger.error(f"Event publishing error: {e}")
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Get integration status"""
        return {
            'running': self.running,
            'registered_assistants': len(self.registered_assistants),
            'pending_commands': sum(len(cmds) for cmds in self.command_queue.values()),
            'settings': self.settings,
            'last_check': datetime.now().isoformat()
        }
