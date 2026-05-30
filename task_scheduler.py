#!/usr/bin/env python3
"""
Task Scheduling System
Automated maintenance scheduling and task management.
"""

import os
import json
import schedule
import time
import threading
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
import sqlite3
from enum import Enum

class TaskStatus(Enum):
    """Task status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskPriority(Enum):
    """Task priority enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class TaskType(Enum):
    """Task type enumeration"""
    CLEANUP = "cleanup"
    OPTIMIZATION = "optimization"
    BACKUP = "backup"
    SCAN = "scan"
    MAINTENANCE = "maintenance"
    CUSTOM = "custom"

class Task:
    """Task class for scheduled operations"""
    
    def __init__(self, task_id: str, name: str, task_type: TaskType, 
                 action: Callable, schedule_pattern: str, 
                 priority: TaskPriority = TaskPriority.MEDIUM,
                 enabled: bool = True, **kwargs):
        self.task_id = task_id
        self.name = name
        self.task_type = task_type
        self.action = action
        self.schedule_pattern = schedule_pattern
        self.priority = priority
        self.enabled = enabled
        self.kwargs = kwargs
        self.status = TaskStatus.PENDING
        self.created_at = datetime.now()
        self.last_run = None
        self.next_run = None
        self.run_count = 0
        self.failure_count = 0
        self.last_result = None
        self.error_message = None

class TaskScheduler:
    """Advanced Task Scheduler"""
    
    def __init__(self):
        self.db_path = os.path.join(os.path.dirname(__file__), 'task_scheduler.db')
        self.settings_file = os.path.join(os.path.dirname(__file__), 'scheduler_settings.json')
        self.log_file = os.path.join(os.path.dirname(__file__), 'scheduler.log')
        
        # Load settings
        self.settings = self.load_settings()
        
        # Initialize database
        self.init_database()
        
        # Setup logging
        self.setup_logging()
        
        # Task storage
        self.tasks = {}
        self.running_tasks = {}
        
        # Scheduler state
        self.scheduler_active = False
        self.scheduler_thread = None
        
        # Initialize default tasks
        self.initialize_default_tasks()
        
        # Load saved tasks
        self.load_tasks()
        
        # Start scheduler if enabled
        if self.settings.get('scheduler_enabled', True):
            self.start_scheduler()
    
    def load_settings(self) -> Dict[str, Any]:
        """Load scheduler settings"""
        default_settings = {
            'scheduler_enabled': True,
            'max_concurrent_tasks': 5,
            'task_timeout': 3600,  # 1 hour
            'retry_failed_tasks': True,
            'max_retries': 3,
            'retry_delay': 300,  # 5 minutes
            'log_level': 'INFO',
            'cleanup_completed_tasks': True,
            'task_retention_days': 30,
            'email_notifications': False,
            'system_startup_delay': 60  # 1 minute
        }
        
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                default_settings.update(loaded_settings)
            else:
                self.save_settings(default_settings)
            return default_settings
        except Exception:
            return default_settings
    
    def save_settings(self, settings: Dict[str, Any] = None) -> bool:
        """Save scheduler settings"""
        try:
            if settings:
                self.settings.update(settings)
            
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False
    
    def init_database(self):
        """Initialize scheduler database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                task_type TEXT NOT NULL,
                schedule_pattern TEXT NOT NULL,
                priority TEXT NOT NULL,
                enabled BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_run TIMESTAMP,
                next_run TIMESTAMP,
                run_count INTEGER DEFAULT 0,
                failure_count INTEGER DEFAULT 0,
                status TEXT DEFAULT 'pending',
                last_result TEXT,
                error_message TEXT,
                kwargs TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS task_executions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT NOT NULL,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                status TEXT NOT NULL,
                result TEXT,
                error_message TEXT,
                duration_seconds INTEGER,
                FOREIGN KEY (task_id) REFERENCES tasks (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS task_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                level TEXT NOT NULL,
                message TEXT NOT NULL,
                FOREIGN KEY (task_id) REFERENCES tasks (id)
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_tasks_next_run ON tasks(next_run)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_executions_task_id ON task_executions(task_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_executions_started_at ON task_executions(started_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_logs_task_id ON task_logs(task_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON task_logs(timestamp)')
        
        conn.commit()
        conn.close()
    
    def setup_logging(self):
        """Setup scheduler logging"""
        self.logger = logging.getLogger('TaskScheduler')
        
        log_level = getattr(logging, self.settings.get('log_level', 'INFO').upper())
        self.logger.setLevel(log_level)
        
        # Create file handler
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(log_level)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        # Add handler to logger
        self.logger.addHandler(file_handler)
    
    def initialize_default_tasks(self):
        """Initialize default scheduled tasks"""
        default_tasks = [
            {
                'task_id': 'daily_soft_cleanup',
                'name': 'Daily Soft Cleanup',
                'task_type': TaskType.CLEANUP,
                'schedule_pattern': 'daily',
                'priority': TaskPriority.MEDIUM,
                'action': self._daily_soft_cleanup
            },
            {
                'task_id': 'weekly_aggressive_cleanup',
                'name': 'Weekly Aggressive Cleanup',
                'task_type': TaskType.CLEANUP,
                'schedule_pattern': 'weekly',
                'priority': TaskPriority.HIGH,
                'action': self._weekly_aggressive_cleanup
            },
            {
                'task_id': 'monthly_deep_cleanup',
                'name': 'Monthly Deep Cleanup',
                'task_type': TaskType.CLEANUP,
                'schedule_pattern': 'monthly',
                'priority': TaskPriority.HIGH,
                'action': self._monthly_deep_cleanup
            },
            {
                'task_id': 'hourly_optimization',
                'name': 'Hourly System Optimization',
                'task_type': TaskType.OPTIMIZATION,
                'schedule_pattern': 'hourly',
                'priority': TaskPriority.MEDIUM,
                'action': self._hourly_optimization
            },
            {
                'task_id': 'daily_backup',
                'name': 'Daily System Backup',
                'task_type': TaskType.BACKUP,
                'schedule_pattern': 'daily',
                'priority': TaskPriority.HIGH,
                'action': self._daily_backup
            },
            {
                'task_id': 'weekly_security_scan',
                'name': 'Weekly Security Scan',
                'task_type': TaskType.SCAN,
                'schedule_pattern': 'weekly',
                'priority': TaskPriority.HIGH,
                'action': self._weekly_security_scan
            },
            {
                'task_id': 'daily_maintenance',
                'name': 'Daily System Maintenance',
                'task_type': TaskType.MAINTENANCE,
                'schedule_pattern': 'daily',
                'priority': TaskPriority.MEDIUM,
                'action': self._daily_maintenance
            }
        ]
        
        for task_config in default_tasks:
            task = Task(
                task_id=task_config['task_id'],
                name=task_config['name'],
                task_type=task_config['task_type'],
                action=task_config['action'],
                schedule_pattern=task_config['schedule_pattern'],
                priority=task_config['priority']
            )
            self.tasks[task.task_id] = task
    
    def load_tasks(self):
        """Load tasks from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM tasks')
            rows = cursor.fetchall()
            
            for row in rows:
                task_id = row[0]
                if task_id in self.tasks:
                    task = self.tasks[task_id]
                    task.last_run = datetime.fromisoformat(row[6]) if row[6] else None
                    task.next_run = datetime.fromisoformat(row[7]) if row[7] else None
                    task.run_count = row[8] or 0
                    task.failure_count = row[9] or 0
                    task.status = TaskStatus(row[10]) if row[10] else TaskStatus.PENDING
                    task.last_result = row[11]
                    task.error_message = row[12]
                    
                    if row[13]:
                        task.kwargs = json.loads(row[13])
            
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Failed to load tasks: {e}")
    
    def save_task(self, task: Task):
        """Save task to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO tasks 
                (id, name, task_type, schedule_pattern, priority, enabled,
                 created_at, last_run, next_run, run_count, failure_count,
                 status, last_result, error_message, kwargs)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                task.task_id, task.name, task.task_type.value, task.schedule_pattern,
                task.priority.value, task.enabled, task.created_at.isoformat(),
                task.last_run.isoformat() if task.last_run else None,
                task.next_run.isoformat() if task.next_run else None,
                task.run_count, task.failure_count, task.status.value,
                task.last_result, task.error_message, json.dumps(task.kwargs)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Failed to save task {task.task_id}: {e}")
    
    def add_task(self, task: Task) -> bool:
        """Add new task"""
        try:
            self.tasks[task.task_id] = task
            self.save_task(task)
            
            # Schedule the task
            if self.scheduler_active:
                self._schedule_task(task)
            
            self.logger.info(f"Task added: {task.name} ({task.task_id})")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add task: {e}")
            return False
    
    def remove_task(self, task_id: str) -> bool:
        """Remove task"""
        try:
            if task_id in self.tasks:
                task = self.tasks[task_id]
                
                # Cancel scheduled job
                if hasattr(self, f'job_{task_id}'):
                    job = getattr(self, f'job_{task_id}')
                    schedule.cancel_job(job)
                    delattr(self, f'job_{task_id}')
                
                # Remove from memory
                del self.tasks[task_id]
                
                # Remove from database
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
                conn.commit()
                conn.close()
                
                self.logger.info(f"Task removed: {task.name} ({task_id})")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to remove task {task_id}: {e}")
            return False
    
    def enable_task(self, task_id: str) -> bool:
        """Enable task"""
        if task_id in self.tasks:
            self.tasks[task_id].enabled = True
            self.save_task(self.tasks[task_id])
            
            if self.scheduler_active:
                self._schedule_task(self.tasks[task_id])
            
            return True
        return False
    
    def disable_task(self, task_id: str) -> bool:
        """Disable task"""
        if task_id in self.tasks:
            self.tasks[task_id].enabled = False
            self.save_task(self.tasks[task_id])
            
            # Cancel scheduled job
            if hasattr(self, f'job_{task_id}'):
                job = getattr(self, f'job_{task_id}')
                schedule.cancel_job(job)
                delattr(self, f'job_{task_id}')
            
            return True
        return False
    
    def run_task_now(self, task_id: str) -> bool:
        """Run task immediately"""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            return self._execute_task(task)
        return False
    
    def _schedule_task(self, task: Task):
        """Schedule a task"""
        if not task.enabled:
            return
        
        # Cancel existing job if any
        if hasattr(self, f'job_{task.task_id}'):
            job = getattr(self, f'job_{task.task_id}')
            schedule.cancel_job(job)
        
        # Schedule based on pattern
        if task.schedule_pattern == 'daily':
            job = schedule.every().day.do(self._execute_task, task)
        elif task.schedule_pattern == 'weekly':
            job = schedule.every().week.do(self._execute_task, task)
        elif task.schedule_pattern == 'monthly':
            job = schedule.every().month.do(self._execute_task, task)
        elif task.schedule_pattern == 'hourly':
            job = schedule.every().hour.do(self._execute_task, task)
        elif task.schedule_pattern.startswith('every_'):
            # Custom pattern like "every_2_hours", "every_30_minutes"
            parts = task.schedule_pattern.split('_')
            if len(parts) >= 3:
                interval = int(parts[1])
                unit = parts[2]
                
                if unit.startswith('hour'):
                    job = schedule.every(interval).hours.do(self._execute_task, task)
                elif unit.startswith('minute'):
                    job = schedule.every(interval).minutes.do(self._execute_task, task)
                elif unit.startswith('day'):
                    job = schedule.every(interval).days.do(self._execute_task, task)
        else:
            # Default to daily
            job = schedule.every().day.do(self._execute_task, task)
        
        # Store job reference
        setattr(self, f'job_{task.task_id}', job)
        
        # Update next run time
        task.next_run = job.next_run
        self.save_task(task)
    
    def _execute_task(self, task: Task) -> bool:
        """Execute a task"""
        if task.task_id in self.running_tasks:
            self.logger.warning(f"Task {task.task_id} is already running")
            return False
        
        # Check concurrent task limit
        if len(self.running_tasks) >= self.settings.get('max_concurrent_tasks', 5):
            self.logger.warning(f"Maximum concurrent tasks reached, skipping {task.task_id}")
            return False
        
        # Start task in separate thread
        task_thread = threading.Thread(target=self._run_task, args=(task,), daemon=True)
        task_thread.start()
        
        return True
    
    def _run_task(self, task: Task):
        """Run task in thread"""
        task_id = task.task_id
        self.running_tasks[task_id] = task
        
        start_time = datetime.now()
        
        try:
            # Update task status
            task.status = TaskStatus.RUNNING
            self.save_task(task)
            
            self.logger.info(f"Starting task: {task.name} ({task_id})")
            
            # Log task start
            self._log_task_event(task_id, 'INFO', f"Task started: {task.name}")
            
            # Execute task action
            result = task.action(**task.kwargs)
            
            # Update task with success
            task.status = TaskStatus.COMPLETED
            task.last_run = start_time
            task.run_count += 1
            task.last_result = str(result) if result else "Completed successfully"
            task.error_message = None
            
            # Calculate duration
            duration = int((datetime.now() - start_time).total_seconds())
            
            # Record execution
            self._record_task_execution(task_id, start_time, datetime.now(), 
                                       TaskStatus.COMPLETED, task.last_result, None, duration)
            
            self.logger.info(f"Task completed: {task.name} ({task_id}) in {duration}s")
            self._log_task_event(task_id, 'INFO', f"Task completed successfully in {duration}s")
            
        except Exception as e:
            # Update task with failure
            task.status = TaskStatus.FAILED
            task.last_run = start_time
            task.failure_count += 1
            task.error_message = str(e)
            
            # Calculate duration
            duration = int((datetime.now() - start_time).total_seconds())
            
            # Record execution
            self._record_task_execution(task_id, start_time, datetime.now(), 
                                       TaskStatus.FAILED, None, str(e), duration)
            
            self.logger.error(f"Task failed: {task.name} ({task_id}) - {e}")
            self._log_task_event(task_id, 'ERROR', f"Task failed: {e}")
            
            # Retry logic
            if (self.settings.get('retry_failed_tasks', True) and 
                task.failure_count <= self.settings.get('max_retries', 3)):
                
                retry_delay = self.settings.get('retry_delay', 300)
                self.logger.info(f"Scheduling retry for {task.name} in {retry_delay}s")
                
                # Schedule retry
                threading.Timer(retry_delay, self._execute_task, args=[task]).start()
        
        finally:
            # Remove from running tasks
            if task_id in self.running_tasks:
                del self.running_tasks[task_id]
            
            # Save task state
            self.save_task(task)
            
            # Update next run time
            if hasattr(self, f'job_{task_id}'):
                job = getattr(self, f'job_{task_id}')
                task.next_run = job.next_run
                self.save_task(task)
            
            # Cleanup old tasks if enabled
            if self.settings.get('cleanup_completed_tasks', True):
                self._cleanup_old_tasks()
    
    def _record_task_execution(self, task_id: str, started_at: datetime, 
                             completed_at: datetime, status: TaskStatus, 
                             result: str = None, error_message: str = None, 
                             duration: int = None):
        """Record task execution"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO task_executions 
                (task_id, started_at, completed_at, status, result, error_message, duration_seconds)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (task_id, started_at.isoformat(), completed_at.isoformat(), 
                  status.value, result, error_message, duration))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Failed to record task execution: {e}")
    
    def _log_task_event(self, task_id: str, level: str, message: str):
        """Log task event"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO task_logs (task_id, level, message)
                VALUES (?, ?, ?)
            ''', (task_id, level, message))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Failed to log task event: {e}")
    
    def _cleanup_old_tasks(self):
        """Clean up old task records"""
        try:
            retention_days = self.settings.get('task_retention_days', 30)
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Clean old executions
            cursor.execute('DELETE FROM task_executions WHERE started_at < ?', (cutoff_date.isoformat(),))
            
            # Clean old logs
            cursor.execute('DELETE FROM task_logs WHERE timestamp < ?', (cutoff_date.isoformat(),))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup old tasks: {e}")
    
    def start_scheduler(self):
        """Start the task scheduler"""
        if self.scheduler_active:
            return
        
        self.scheduler_active = True
        
        # Schedule all enabled tasks
        for task in self.tasks.values():
            if task.enabled:
                self._schedule_task(task)
        
        # Start scheduler thread
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        
        self.logger.info("Task scheduler started")
    
    def stop_scheduler(self):
        """Stop the task scheduler"""
        self.scheduler_active = False
        
        # Cancel all scheduled jobs
        schedule.clear()
        
        # Wait for scheduler thread
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        
        self.logger.info("Task scheduler stopped")
    
    def _scheduler_loop(self):
        """Scheduler main loop"""
        while self.scheduler_active:
            try:
                # Run pending jobs
                schedule.run_pending()
                
                # Sleep for a short interval
                time.sleep(1)
                
            except Exception as e:
                self.logger.error(f"Scheduler loop error: {e}")
                time.sleep(10)
    
    # Default task implementations
    def _daily_soft_cleanup(self):
        """Daily soft cleanup task"""
        try:
            # Import and run soft cleanup
            from soft_ram_cleaner import SoftRAMCleaner
            cleaner = SoftRAMCleaner()
            result = cleaner.perform_cleanup()
            return {"status": "success", "cleaned_items": result}
        except Exception as e:
            raise Exception(f"Soft cleanup failed: {e}")
    
    def _weekly_aggressive_cleanup(self):
        """Weekly aggressive cleanup task"""
        try:
            # Import and run aggressive cleanup
            from aggressive_ram_cleaner import AggressiveRAMCleaner
            cleaner = AggressiveRAMCleaner()
            result = cleaner.perform_cleanup()
            return {"status": "success", "cleaned_items": result}
        except Exception as e:
            raise Exception(f"Aggressive cleanup failed: {e}")
    
    def _monthly_deep_cleanup(self):
        """Monthly deep cleanup task"""
        try:
            # Import and run deep cleanup
            from system_cleanup_master import SystemCleanupMaster
            cleaner = SystemCleanupMaster()
            result = cleaner.perform_deep_cleanup()
            return {"status": "success", "cleaned_items": result}
        except Exception as e:
            raise Exception(f"Deep cleanup failed: {e}")
    
    def _hourly_optimization(self):
        """Hourly system optimization task"""
        try:
            # Import and run optimization
            from performance_optimizer import performance_optimizer
            result = performance_optimizer.optimize_system("light")
            return {"status": "success", "optimization_result": result}
        except Exception as e:
            raise Exception(f"Optimization failed: {e}")
    
    def _daily_backup(self):
        """Daily backup task"""
        try:
            # Import and run backup
            from backup_manager import BackupManager
            backup_mgr = BackupManager()
            result = backup_mgr.create_backup("daily")
            return {"status": "success", "backup_result": result}
        except Exception as e:
            raise Exception(f"Backup failed: {e}")
    
    def _weekly_security_scan(self):
        """Weekly security scan task"""
        try:
            # Import and run security scan
            from advanced_security import security_manager
            result = security_manager.privacy_cleanup()
            return {"status": "success", "security_result": result}
        except Exception as e:
            raise Exception(f"Security scan failed: {e}")
    
    def _daily_maintenance(self):
        """Daily system maintenance task"""
        try:
            # Run various maintenance tasks
            results = {}
            
            # Memory optimization
            from performance_optimizer import performance_optimizer
            results['memory_opt'] = performance_optimizer.optimize_system("light")
            
            # Database cleanup
            results['db_cleanup'] = self._cleanup_old_tasks()
            
            # Log cleanup
            results['log_cleanup'] = self._cleanup_logs()
            
            return {"status": "success", "maintenance_results": results}
        except Exception as e:
            raise Exception(f"Maintenance failed: {e}")
    
    def _cleanup_logs(self):
        """Cleanup old log files"""
        try:
            log_files = [
                'scheduler.log',
                'interventions.log',
                'security_audit.log'
            ]
            
            cleaned_files = []
            
            for log_file in log_files:
                log_path = os.path.join(os.path.dirname(__file__), log_file)
                if os.path.exists(log_path):
                    # Simple log rotation - truncate if too large
                    if os.path.getsize(log_path) > 10 * 1024 * 1024:  # 10MB
                        with open(log_path, 'w') as f:
                            f.write(f"Log truncated at {datetime.now()}\n")
                        cleaned_files.append(log_file)
            
            return {"cleaned_files": cleaned_files}
        except Exception as e:
            return {"error": str(e)}
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task status"""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            return {
                'task_id': task.task_id,
                'name': task.name,
                'type': task.task_type.value,
                'status': task.status.value,
                'priority': task.priority.value,
                'enabled': task.enabled,
                'last_run': task.last_run.isoformat() if task.last_run else None,
                'next_run': task.next_run.isoformat() if task.next_run else None,
                'run_count': task.run_count,
                'failure_count': task.failure_count,
                'last_result': task.last_result,
                'error_message': task.error_message
            }
        return None
    
    def get_all_tasks(self) -> List[Dict[str, Any]]:
        """Get all tasks status"""
        return [self.get_task_status(task_id) for task_id in self.tasks.keys()]
    
    def get_running_tasks(self) -> List[Dict[str, Any]]:
        """Get currently running tasks"""
        return [self.get_task_status(task_id) for task_id in self.running_tasks.keys()]
    
    def get_task_history(self, task_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get task execution history"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT started_at, completed_at, status, result, error_message, duration_seconds
                FROM task_executions
                WHERE task_id = ?
                ORDER BY started_at DESC
                LIMIT ?
            ''', (task_id, limit))
            
            rows = cursor.fetchall()
            conn.close()
            
            history = []
            for row in rows:
                history.append({
                    'started_at': row[0],
                    'completed_at': row[1],
                    'status': row[2],
                    'result': row[3],
                    'error_message': row[4],
                    'duration_seconds': row[5]
                })
            
            return history
            
        except Exception as e:
            self.logger.error(f"Failed to get task history: {e}")
            return []
    
    def get_scheduler_status(self) -> Dict[str, Any]:
        """Get scheduler status"""
        return {
            'scheduler_active': self.scheduler_active,
            'total_tasks': len(self.tasks),
            'enabled_tasks': len([t for t in self.tasks.values() if t.enabled]),
            'running_tasks': len(self.running_tasks),
            'next_runs': [
                {
                    'task_id': task.task_id,
                    'name': task.name,
                    'next_run': task.next_run.isoformat() if task.next_run else None
                }
                for task in self.tasks.values() 
                if task.enabled and task.next_run
            ]
        }

# Global scheduler instance
task_scheduler = TaskScheduler()

# Convenience functions
def add_task(task: Task) -> bool:
    """Add task"""
    return task_scheduler.add_task(task)

def run_task_now(task_id: str) -> bool:
    """Run task immediately"""
    return task_scheduler.run_task_now(task_id)

def get_task_status(task_id: str) -> Optional[Dict[str, Any]]:
    """Get task status"""
    return task_scheduler.get_task_status(task_id)

def get_all_tasks() -> List[Dict[str, Any]]:
    """Get all tasks"""
    return task_scheduler.get_all_tasks()

if __name__ == '__main__':
    # Test task scheduler
    print("Testing Task Scheduler")
    print(f"Scheduler enabled: {task_scheduler.settings.get('scheduler_enabled')}")
    print(f"Max concurrent tasks: {task_scheduler.settings.get('max_concurrent_tasks')}")
    
    # Get scheduler status
    status = task_scheduler.get_scheduler_status()
    print(f"Scheduler status: {status}")
    
    # Get all tasks
    tasks = task_scheduler.get_all_tasks()
    print(f"Total tasks: {len(tasks)}")
    
    for task in tasks:
        print(f"  {task['name']} - {task['status']} - {task['enabled']}")
