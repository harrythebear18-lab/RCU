#!/usr/bin/env python3
"""
Frontend-Backend Mixer Layer
Provides seamless integration between frontend GUI and backend services
"""

import logging
import time
import json
import threading
import queue
from typing import Dict, List, Any, Optional, Callable, Union
from abc import ABC, abstractmethod
from enum import Enum
from dataclasses import dataclass, asdict
import asyncio
import websockets
from pathlib import Path

class ComponentType(Enum):
    """Component types for the mixer layer"""
    FRONTEND_GUI = "frontend_gui"
    BACKEND_API = "backend_api"
    WEB_INTERFACE = "web_interface"
    MOBILE_PWA = "mobile_pwa"
    CLI_TOOL = "cli_tool"
    BATCH_SCRIPT = "batch_script"

class MessageType(Enum):
    """Message types for frontend-backend communication"""
    DATA_UPDATE = "data_update"
    COMMAND_REQUEST = "command_request"
    COMMAND_RESPONSE = "command_response"
    EVENT_NOTIFICATION = "event_notification"
    STATUS_UPDATE = "status_update"
    ERROR_REPORT = "error_report"
    CONFIG_CHANGE = "config_change"

@dataclass
class MixerMessage:
    """Message format for frontend-backend communication"""
    message_type: MessageType
    source: ComponentType
    target: ComponentType
    timestamp: float
    data: Dict[str, Any]
    message_id: Optional[str] = None
    correlation_id: Optional[str] = None
    error: Optional[str] = None

class FrontendComponent(ABC):
    """Abstract base class for frontend components"""
    
    def __init__(self, component_id: str):
        self.component_id = component_id
        self.logger = logging.getLogger(f"Frontend_{component_id}")
        self.message_queue = queue.Queue()
        self.is_running = False
        
    @abstractmethod
    def send_message(self, message: MixerMessage) -> bool:
        """Send message to backend"""
        pass
    
    @abstractmethod
    def receive_message(self, message: MixerMessage) -> bool:
        """Receive message from backend"""
        pass
    
    @abstractmethod
    def update_data(self, data: Dict[str, Any]) -> None:
        """Update frontend data"""
        pass
    
    @abstractmethod
    def handle_command(self, command: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle command from backend"""
        pass

class BackendComponent(ABC):
    """Abstract base class for backend components"""
    
    def __init__(self, component_id: str):
        self.component_id = component_id
        self.logger = logging.getLogger(f"Backend_{component_id}")
        self.message_queue = queue.Queue()
        self.is_running = False
        
    @abstractmethod
    def send_message(self, message: MixerMessage) -> bool:
        """Send message to frontend"""
        pass
    
    @abstractmethod
    def receive_message(self, message: MixerMessage) -> bool:
        """Receive message from frontend"""
        pass
    
    @abstractmethod
    def process_command(self, command: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Process command from frontend"""
        pass
    
    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """Get component status"""
        pass

class TkinterFrontend(FrontendComponent):
    """Tkinter GUI frontend component"""
    
    def __init__(self, component_id: str, root_widget=None):
        super().__init__(component_id)
        self.root_widget = root_widget
        self.data_cache = {}
        self.command_handlers = {}
        
    def send_message(self, message: MixerMessage) -> bool:
        """Send message to backend via mixer"""
        try:
            # This would be handled by the mixer layer
            return True
        except Exception as e:
            self.logger.error(f"Failed to send message: {e}")
            return False
    
    def receive_message(self, message: MixerMessage) -> bool:
        """Receive message from backend"""
        try:
            if message.message_type == MessageType.DATA_UPDATE:
                self.update_data(message.data)
            elif message.message_type == MessageType.COMMAND_RESPONSE:
                self.handle_command_response(message.data)
            elif message.message_type == MessageType.STATUS_UPDATE:
                self.handle_status_update(message.data)
            return True
        except Exception as e:
            self.logger.error(f"Failed to receive message: {e}")
            return False
    
    def update_data(self, data: Dict[str, Any]) -> None:
        """Update frontend data"""
        try:
            self.data_cache.update(data)
            
            # Update GUI widgets if available
            if self.root_widget:
                self._update_gui_widgets(data)
                
        except Exception as e:
            self.logger.error(f"Failed to update data: {e}")
    
    def handle_command(self, command: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle command from backend"""
        try:
            if command in self.command_handlers:
                return self.command_handlers[command](params)
            else:
                return {'error': f'Unknown command: {command}'}
        except Exception as e:
            self.logger.error(f"Failed to handle command: {e}")
            return {'error': str(e)}
    
    def _update_gui_widgets(self, data: Dict[str, Any]) -> None:
        """Update GUI widgets with new data"""
        # This would be implemented based on specific GUI requirements
        pass
    
    def handle_command_response(self, data: Dict[str, Any]) -> None:
        """Handle command response from backend"""
        pass
    
    def handle_status_update(self, data: Dict[str, Any]) -> None:
        """Handle status update from backend"""
        pass
    
    def register_command_handler(self, command: str, handler: Callable):
        """Register command handler"""
        self.command_handlers[command] = handler

class FlaskBackend(BackendComponent):
    """Flask API backend component"""
    
    def __init__(self, component_id: str, app=None):
        super().__init__(component_id)
        self.app = app
        self.endpoints = {}
        self.status_cache = {}
        
    def send_message(self, message: MixerMessage) -> bool:
        """Send message to frontend via mixer"""
        try:
            # This would be handled by the mixer layer
            return True
        except Exception as e:
            self.logger.error(f"Failed to send message: {e}")
            return False
    
    def receive_message(self, message: MixerMessage) -> bool:
        """Receive message from frontend"""
        try:
            if message.message_type == MessageType.COMMAND_REQUEST:
                response = self.process_command(message.data.get('command', ''), message.data.get('params', {}))
                # Send response back
                return True
            elif message.message_type == MessageType.CONFIG_CHANGE:
                self.handle_config_change(message.data)
            return True
        except Exception as e:
            self.logger.error(f"Failed to receive message: {e}")
            return False
    
    def process_command(self, command: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Process command from frontend"""
        try:
            if command in self.endpoints:
                return self.endpoints[command](params)
            else:
                return {'error': f'Unknown command: {command}'}
        except Exception as e:
            self.logger.error(f"Failed to process command: {e}")
            return {'error': str(e)}
    
    def get_status(self) -> Dict[str, Any]:
        """Get component status"""
        return {
            'component_id': self.component_id,
            'is_running': self.is_running,
            'endpoints_count': len(self.endpoints),
            'last_update': time.time()
        }
    
    def register_endpoint(self, command: str, handler: Callable):
        """Register API endpoint"""
        self.endpoints[command] = handler
    
    def handle_config_change(self, data: Dict[str, Any]) -> None:
        """Handle configuration change"""
        pass

class FrontendBackendMixer:
    """Main mixer layer for frontend-backend integration"""
    
    def __init__(self):
        self.logger = logging.getLogger("FrontendBackendMixer")
        self.frontend_components: Dict[str, FrontendComponent] = {}
        self.backend_components: Dict[str, BackendComponent] = {}
        self.message_router = {}
        self.is_running = False
        self.worker_thread = None
        self.message_queue = queue.Queue()
        
    def register_frontend(self, component: FrontendComponent) -> str:
        """Register frontend component"""
        component_id = component.component_id
        self.frontend_components[component_id] = component
        self.logger.info(f"Registered frontend component: {component_id}")
        return component_id
    
    def register_backend(self, component: BackendComponent) -> str:
        """Register backend component"""
        component_id = component.component_id
        self.backend_components[component_id] = component
        self.logger.info(f"Registered backend component: {component_id}")
        return component_id
    
    def send_message(self, message: MixerMessage) -> bool:
        """Send message through mixer"""
        try:
            self.message_queue.put(message)
            return True
        except Exception as e:
            self.logger.error(f"Failed to send message: {e}")
            return False
    
    def route_message(self, message: MixerMessage) -> bool:
        """Route message to appropriate component"""
        try:
            target = message.target
            source = message.source
            
            # Route to frontend
            if target == ComponentType.FRONTEND_GUI or target in self.frontend_components:
                if target == ComponentType.FRONTEND_GUI:
                    # Send to all frontend components
                    for component in self.frontend_components.values():
                        component.receive_message(message)
                else:
                    # Send to specific frontend component
                    if target in self.frontend_components:
                        self.frontend_components[target].receive_message(message)
            
            # Route to backend
            elif target == ComponentType.BACKEND_API or target in self.backend_components:
                if target == ComponentType.BACKEND_API:
                    # Send to all backend components
                    for component in self.backend_components.values():
                        component.receive_message(message)
                else:
                    # Send to specific backend component
                    if target in self.backend_components:
                        self.backend_components[target].receive_message(message)
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to route message: {e}")
            return False
    
    def broadcast_data_update(self, data: Dict[str, Any]) -> None:
        """Broadcast data update to all frontend components"""
        message = MixerMessage(
            message_type=MessageType.DATA_UPDATE,
            source=ComponentType.BACKEND_API,
            target=ComponentType.FRONTEND_GUI,
            timestamp=time.time(),
            data=data
        )
        self.send_message(message)
    
    def broadcast_status_update(self, status: Dict[str, Any]) -> None:
        """Broadcast status update to all components"""
        message = MixerMessage(
            message_type=MessageType.STATUS_UPDATE,
            source=ComponentType.BACKEND_API,
            target=ComponentType.FRONTEND_GUI,
            timestamp=time.time(),
            data=status
        )
        self.send_message(message)
    
    def start_mixer(self) -> bool:
        """Start the mixer layer"""
        if self.is_running:
            return True
        
        self.is_running = True
        self.worker_thread = threading.Thread(target=self._mixer_loop, daemon=True)
        self.worker_thread.start()
        self.logger.info("Frontend-Backend mixer started")
        return True
    
    def stop_mixer(self) -> bool:
        """Stop the mixer layer"""
        self.is_running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=2)
        self.logger.info("Frontend-Backend mixer stopped")
        return True
    
    def _mixer_loop(self) -> None:
        """Main mixer loop"""
        while self.is_running:
            try:
                # Process messages from queue
                try:
                    message = self.message_queue.get(timeout=0.1)
                    self.route_message(message)
                except queue.Empty:
                    continue
                
                # Check for component updates
                self._check_component_updates()
                
            except Exception as e:
                self.logger.error(f"Error in mixer loop: {e}")
                time.sleep(0.1)
    
    def _check_component_updates(self) -> None:
        """Check for component updates"""
        try:
            # Check backend status updates
            for component in self.backend_components.values():
                status = component.get_status()
                if status.get('last_update', 0) > time.time() - 5:  # Recent update
                    self.broadcast_status_update(status)
        except Exception as e:
            self.logger.error(f"Error checking component updates: {e}")
    
    def get_mixer_status(self) -> Dict[str, Any]:
        """Get mixer status"""
        return {
            'is_running': self.is_running,
            'frontend_components': list(self.frontend_components.keys()),
            'backend_components': list(self.backend_components.keys()),
            'queue_size': self.message_queue.qsize(),
            'last_update': time.time()
        }

# Global instance
_frontend_backend_mixer = None

def get_frontend_backend_mixer() -> FrontendBackendMixer:
    """Get global frontend-backend mixer instance"""
    global _frontend_backend_mixer
    if _frontend_backend_mixer is None:
        _frontend_backend_mixer = FrontendBackendMixer()
    return _frontend_backend_mixer

def create_tkinter_frontend(component_id: str, root_widget=None) -> TkinterFrontend:
    """Create Tkinter frontend component"""
    frontend = TkinterFrontend(component_id, root_widget)
    mixer = get_frontend_backend_mixer()
    mixer.register_frontend(frontend)
    return frontend

def create_flask_backend(component_id: str, app=None) -> FlaskBackend:
    """Create Flask backend component"""
    backend = FlaskBackend(component_id, app)
    mixer = get_frontend_backend_mixer()
    mixer.register_backend(backend)
    return backend

def start_mixer() -> bool:
    """Start the frontend-backend mixer"""
    mixer = get_frontend_backend_mixer()
    return mixer.start_mixer()

def stop_mixer() -> bool:
    """Stop the frontend-backend mixer"""
    mixer = get_frontend_backend_mixer()
    return mixer.stop_mixer()

def broadcast_data(data: Dict[str, Any]) -> None:
    """Broadcast data to all frontend components"""
    mixer = get_frontend_backend_mixer()
    mixer.broadcast_data_update(data)

def broadcast_status(status: Dict[str, Any]) -> None:
    """Broadcast status to all components"""
    mixer = get_frontend_backend_mixer()
    mixer.broadcast_status_update(status)
