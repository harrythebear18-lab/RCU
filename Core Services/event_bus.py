#!/usr/bin/env python3
"""
Central Event Bus for Homelab System
Provides unified inter-service communication and event handling
"""

import asyncio
import json
import time
import threading
import logging
import os
import sys
from datetime import datetime
from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import weakref
import queue
import hashlib
from pathlib import Path

# Add path handling
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

parent_dir = current_dir.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

# OS path functions usage
os.path.join(current_dir, 'data')
os.path.exists(current_dir)
os.path.dirname(__file__)
os.path.abspath(__file__)

class EventPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

class EventType(Enum):
    SYSTEM = "system"
    MONITORING = "monitoring"
    NETWORK = "network"
    SECURITY = "security"
    CONFIGURATION = "configuration"
    USER_ACTION = "user_action"
    ERROR = "error"
    RESOURCE = "resource"
    INFO = "info"
    WARNING = "warning"

@dataclass
class Event:
    id: str
    type: EventType
    priority: EventPriority
    source: str
    timestamp: datetime
    data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None

class EventBus:
    """Central event bus for homelab system communication"""
    
    def __init__(self):
        self._subscribers: Dict[EventType, List[Callable]] = {}
        self._event_queue = asyncio.Queue()
        self._running = False
        self._event_history: List[Event] = []
        self._max_history = 1000
        self._lock = threading.Lock()
        self._logger = self._setup_logger()
        self._event_stats = {
            'total_events': 0,
            'events_by_type': {},
            'events_by_priority': {},
            'processing_times': []
        }
        
    def _setup_logger(self) -> logging.Logger:
        """Setup event bus logger"""
        logger = logging.getLogger('EventBus')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
        
    def generate_event_id(self) -> str:
        """Generate unique event ID"""
        timestamp = str(time.time())
        return hashlib.md5(f"{timestamp}{id(self)}".encode()).hexdigest()[:16]
        
    def subscribe(self, event_type: EventType, callback: Callable[[Event], None]) -> str:
        """Subscribe to event type"""
        with self._lock:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []
            
            self._subscribers[event_type].append(callback)
            subscription_id = f"{event_type.value}_{len(self._subscribers[event_type])}"
            
        self._logger.info(f"Subscribed to {event_type.value} events: {subscription_id}")
        return subscription_id
        
    def unsubscribe(self, event_type: EventType, callback: Callable[[Event], None]):
        """Unsubscribe from event type"""
        with self._lock:
            if event_type in self._subscribers:
                try:
                    self._subscribers[event_type].remove(callback)
                    self._logger.info(f"Unsubscribed from {event_type.value} events")
                except ValueError:
                    self._logger.warning(f"Callback not found for {event_type.value}")
                    
    async def publish(self, event_type: EventType, source: str, data: Dict[str, Any], 
                      priority: EventPriority = EventPriority.MEDIUM, 
                      metadata: Optional[Dict[str, Any]] = None) -> str:
        """Publish event to subscribers"""
        event = Event(
            id=self.generate_event_id(),
            type=event_type,
            priority=priority,
            source=source,
            timestamp=datetime.now(),
            data=data,
            metadata=metadata or {}
        )
        
        # Add to queue for processing
        await self._event_queue.put(event)
        
        # Update statistics
        self._update_stats(event)
        
        self._logger.debug(f"Published {event_type.value} event from {source}")
        return event.id
        
    def publish_sync(self, event_type: EventType, source: str, data: Dict[str, Any],
                    priority: EventPriority = EventPriority.MEDIUM,
                    metadata: Optional[Dict[str, Any]] = None) -> str:
        """Synchronous publish for compatibility"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(
                self.publish(event_type, source, data, priority, metadata)
            )
        finally:
            loop.close()
            
    async def _process_event(self, event: Event):
        """Process single event"""
        start_time = time.time()
        
        try:
            # Get subscribers for this event type
            subscribers = []
            with self._lock:
                if event.type in self._subscribers:
                    subscribers = list(self._subscribers[event.type])
                    
            # Notify all subscribers
            for callback in subscribers:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(event)
                    else:
                        callback(event)
                except Exception as e:
                    self._logger.error(f"Error in event callback: {e}")
                    
            # Add to history
            with self._lock:
                self._event_history.append(event)
                if len(self._event_history) > self._max_history:
                    self._event_history.pop(0)
                    
            processing_time = time.time() - start_time
            self._event_stats['processing_times'].append(processing_time)
            
            self._logger.debug(f"Processed {event.type.value} event in {processing_time:.3f}s")
            
        except Exception as e:
            self._logger.error(f"Error processing event {event.id}: {e}")
            
    def _update_stats(self, event: Event):
        """Update event statistics"""
        self._event_stats['total_events'] += 1
        
        event_type = event.type.value
        if event_type not in self._event_stats['events_by_type']:
            self._event_stats['events_by_type'][event_type] = 0
        self._event_stats['events_by_type'][event_type] += 1
        
        priority = event.priority.name
        if priority not in self._event_stats['events_by_priority']:
            self._event_stats['events_by_priority'][priority] = 0
        self._event_stats['events_by_priority'][priority] += 1
        
    async def start(self):
        """Start event bus processing"""
        if self._running:
            return
            
        self._running = True
        self._logger.info("Event bus started")
        
        # Start processing loop
        while self._running:
            try:
                # Get event from queue with timeout
                event = await asyncio.wait_for(self._event_queue.get(), timeout=1.0)
                await self._process_event(event)
            except asyncio.TimeoutError:
                # No events to process, continue
                continue
            except Exception as e:
                self._logger.error(f"Error in event processing loop: {e}")
                
    def stop(self):
        """Stop event bus processing"""
        self._running = False
        self._logger.info("Event bus stopped")
        
    def get_event_history(self, event_type: Optional[EventType] = None, 
                          limit: Optional[int] = None) -> List[Event]:
        """Get event history"""
        with self._lock:
            history = self._event_history.copy()
            
        if event_type:
            history = [e for e in history if e.type == event_type]
            
        if limit:
            history = history[-limit:]
            
        return history
        
    def get_statistics(self) -> Dict[str, Any]:
        """Get event bus statistics"""
        with self._lock:
            stats = self._event_stats.copy()
            
        # Calculate average processing time
        if stats['processing_times']:
            stats['avg_processing_time'] = sum(stats['processing_times']) / len(stats['processing_times'])
            stats['max_processing_time'] = max(stats['processing_times'])
            stats['min_processing_time'] = min(stats['processing_times'])
        else:
            stats['avg_processing_time'] = 0
            stats['max_processing_time'] = 0
            stats['min_processing_time'] = 0
            
        stats['queue_size'] = self._event_queue.qsize()
        stats['history_size'] = len(self._event_history)
        stats['subscribers_count'] = sum(len(subs) for subs in self._subscribers.values())
        
        return stats

# Global event bus instance
_event_bus = None

def get_event_bus() -> EventBus:
    """Get global event bus instance"""
    global _event_bus
    if _event_bus is None:
        _event_bus = EventBus()
    return _event_bus

# Convenience functions for common events
async def publish_system_event(source: str, data: Dict[str, Any], 
                             priority: EventPriority = EventPriority.MEDIUM):
    """Publish system event"""
    bus = get_event_bus()
    return await bus.publish(EventType.SYSTEM, source, data, priority)

async def publish_monitoring_event(source: str, data: Dict[str, Any],
                                 priority: EventPriority = EventPriority.MEDIUM):
    """Publish monitoring event"""
    bus = get_event_bus()
    return await bus.publish(EventType.MONITORING, source, data, priority)

async def publish_error_event(source: str, error: str, 
                            priority: EventPriority = EventPriority.HIGH):
    """Publish error event"""
    bus = get_event_bus()
    return await bus.publish(EventType.ERROR, source, {'error': error}, priority)

async def publish_resource_event(source: str, data: Dict[str, Any],
                                priority: EventPriority = EventPriority.MEDIUM):
    """Publish resource event"""
    bus = get_event_bus()
    return await bus.publish(EventType.RESOURCE, source, data, priority)

# Synchronous versions for compatibility
def publish_system_event_sync(source: str, data: Dict[str, Any], 
                             priority: EventPriority = EventPriority.MEDIUM):
    """Publish system event (synchronous)"""
    bus = get_event_bus()
    return bus.publish_sync(EventType.SYSTEM, source, data, priority)

def publish_monitoring_event_sync(source: str, data: Dict[str, Any],
                                 priority: EventPriority = EventPriority.MEDIUM):
    """Publish monitoring event (synchronous)"""
    bus = get_event_bus()
    return bus.publish_sync(EventType.MONITORING, source, data, priority)

if __name__ == "__main__":
    """Main execution block for event bus"""
    try:
        # Initialize and start the event bus
        event_bus = get_event_bus()
        print("Event bus started successfully")
        
        # Keep the event bus running
        event_bus.start()
        
        # Example usage
        print("Event bus is running. Press Ctrl+C to stop.")
        
        # Keep the main thread alive
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nStopping event bus...")
        event_bus.stop()
        print("Event bus stopped")
    except Exception as e:
        print(f"Event bus error: {e}")

def publish_error_event_sync(source: str, error: str, 
                            priority: EventPriority = EventPriority.HIGH):
    """Publish error event (synchronous)"""
    bus = get_event_bus()
    return bus.publish_sync(EventType.ERROR, source, {'error': error}, priority)

def publish_resource_event_sync(source: str, data: Dict[str, Any],
                                priority: EventPriority = EventPriority.MEDIUM):
    """Publish resource event (synchronous)"""
    bus = get_event_bus()
    return bus.publish_sync(EventType.RESOURCE, source, data, priority)
