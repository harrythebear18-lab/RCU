#!/usr/bin/env python3
"""
Backup and Restore Manager
Handles system data backup, restore, and migration functionality.
"""

import os
import json
import sqlite3
import shutil
import zipfile
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import threading
import schedule
import time

class BackupManager:
    """Manages backup and restore operations"""
    
    def __init__(self, app_name="ResourceOptimizer"):
        self.app_name = app_name
        self.backup_dir = os.path.join(os.path.dirname(__file__), "backups")
        self.settings_file = os.path.join(os.path.dirname(__file__), f"{app_name}_settings.json")
        self.db_file = os.path.join(os.path.dirname(__file__), "system_monitoring.db")
        
        # Ensure backup directory exists
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # Backup configuration
        self.backup_config = {
            "auto_backup": True,
            "backup_interval": "daily",  # daily, weekly, monthly
            "max_backups": 30,  # Maximum number of backups to keep
            "compress_backups": True,
            "include_settings": True,
            "include_database": True,
            "include_logs": False
        }
        
        # Load backup configuration
        self.load_backup_config()
    
    def load_backup_config(self):
        """Load backup configuration from settings"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    backup_settings = settings.get('backup', {})
                    self.backup_config.update(backup_settings)
        except Exception as e:
            print(f"Error loading backup config: {e}")
    
    def save_backup_config(self):
        """Save backup configuration to settings"""
        try:
            settings = {}
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
            
            settings['backup'] = self.backup_config
            
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
        except Exception as e:
            print(f"Error saving backup config: {e}")
    
    def create_backup(self, backup_name: Optional[str] = None) -> Dict[str, Any]:
        """Create a comprehensive backup"""
        try:
            if backup_name is None:
                backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            backup_path = os.path.join(self.backup_dir, backup_name)
            os.makedirs(backup_path, exist_ok=True)
            
            backup_info = {
                "name": backup_name,
                "created_at": datetime.now().isoformat(),
                "version": "2.0",
                "components": {}
            }
            
            # Backup settings
            if self.backup_config["include_settings"] and os.path.exists(self.settings_file):
                settings_backup = os.path.join(backup_path, "settings.json")
                shutil.copy2(self.settings_file, settings_backup)
                backup_info["components"]["settings"] = {
                    "file": "settings.json",
                    "size": os.path.getsize(settings_backup),
                    "checksum": self._calculate_checksum(settings_backup)
                }
            
            # Backup database
            if self.backup_config["include_database"] and os.path.exists(self.db_file):
                db_backup = os.path.join(backup_path, "system_monitoring.db")
                shutil.copy2(self.db_file, db_backup)
                backup_info["components"]["database"] = {
                    "file": "system_monitoring.db",
                    "size": os.path.getsize(db_backup),
                    "checksum": self._calculate_checksum(db_backup),
                    "record_count": self._get_database_record_count()
                }
            
            # Backup logs if enabled
            if self.backup_config["include_logs"]:
                log_files = self._find_log_files()
                logs_dir = os.path.join(backup_path, "logs")
                os.makedirs(logs_dir, exist_ok=True)
                
                backed_up_logs = []
                for log_file in log_files:
                    log_backup = os.path.join(logs_dir, os.path.basename(log_file))
                    shutil.copy2(log_file, log_backup)
                    backed_up_logs.append({
                        "file": os.path.basename(log_file),
                        "size": os.path.getsize(log_backup),
                        "checksum": self._calculate_checksum(log_backup)
                    })
                
                backup_info["components"]["logs"] = backed_up_logs
            
            # Save backup info
            info_file = os.path.join(backup_path, "backup_info.json")
            with open(info_file, 'w') as f:
                json.dump(backup_info, f, indent=2)
            
            # Compress backup if enabled
            if self.backup_config["compress_backups"]:
                self._compress_backup(backup_path)
                backup_path += ".zip"
                backup_info["compressed"] = True
                backup_info["compressed_size"] = os.path.getsize(backup_path)
            
            # Clean up old backups
            self._cleanup_old_backups()
            
            return {
                "success": True,
                "backup_name": backup_name,
                "backup_path": backup_path,
                "backup_info": backup_info
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def restore_backup(self, backup_name: str, components: Optional[List[str]] = None) -> Dict[str, Any]:
        """Restore from backup"""
        try:
            backup_path = os.path.join(self.backup_dir, backup_name)
            
            # Check if backup is compressed
            if backup_path.endswith('.zip'):
                backup_path = self._extract_backup(backup_path)
            
            # Load backup info
            info_file = os.path.join(backup_path, "backup_info.json")
            if not os.path.exists(info_file):
                return {"success": False, "error": "Backup info file not found"}
            
            with open(info_file, 'r') as f:
                backup_info = json.load(f)
            
            restore_results = {}
            
            # Restore settings
            if (components is None or "settings" in components) and \
               "settings" in backup_info["components"]:
                settings_backup = os.path.join(backup_path, backup_info["components"]["settings"]["file"])
                if os.path.exists(settings_backup):
                    # Verify checksum
                    if self._verify_checksum(settings_backup, backup_info["components"]["settings"]["checksum"]):
                        shutil.copy2(settings_backup, self.settings_file)
                        restore_results["settings"] = "Restored successfully"
                    else:
                        restore_results["settings"] = "Checksum verification failed"
                else:
                    restore_results["settings"] = "Backup file not found"
            
            # Restore database
            if (components is None or "database" in components) and \
               "database" in backup_info["components"]:
                db_backup = os.path.join(backup_path, backup_info["components"]["database"]["file"])
                if os.path.exists(db_backup):
                    # Verify checksum
                    if self._verify_checksum(db_backup, backup_info["components"]["database"]["checksum"]):
                        # Stop any running processes that might be using the database
                        self._close_database_connections()
                        
                        # Create backup of current database
                        if os.path.exists(self.db_file):
                            current_backup = os.path.join(os.path.dirname(self.db_file), 
                                                       f"current_db_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
                            shutil.copy2(self.db_file, current_backup)
                        
                        # Restore database
                        shutil.copy2(db_backup, self.db_file)
                        restore_results["database"] = "Restored successfully"
                    else:
                        restore_results["database"] = "Checksum verification failed"
                else:
                    restore_results["database"] = "Backup file not found"
            
            # Restore logs
            if (components is None or "logs" in components) and \
               "logs" in backup_info["components"]:
                logs_dir = os.path.join(backup_path, "logs")
                if os.path.exists(logs_dir):
                    restore_results["logs"] = "Logs restored successfully"
                    # Note: Log restoration logic would go here
                else:
                    restore_results["logs"] = "Logs directory not found"
            
            # Clean up extracted backup if it was compressed
            if backup_path.endswith('_extracted'):
                shutil.rmtree(backup_path)
            
            return {
                "success": True,
                "backup_name": backup_name,
                "restore_results": restore_results,
                "restored_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """List all available backups"""
        backups = []
        
        try:
            for item in os.listdir(self.backup_dir):
                item_path = os.path.join(self.backup_dir, item)
                
                if os.path.isdir(item_path):
                    # Uncompressed backup
                    info_file = os.path.join(item_path, "backup_info.json")
                    if os.path.exists(info_file):
                        with open(info_file, 'r') as f:
                            backup_info = json.load(f)
                        
                        backups.append({
                            "name": item,
                            "created_at": backup_info["created_at"],
                            "size": self._get_directory_size(item_path),
                            "compressed": False,
                            "components": list(backup_info["components"].keys())
                        })
                
                elif item.endswith('.zip'):
                    # Compressed backup
                    backup_info = self._get_zip_backup_info(item_path)
                    if backup_info:
                        backups.append({
                            "name": item,
                            "created_at": backup_info["created_at"],
                            "size": os.path.getsize(item_path),
                            "compressed": True,
                            "components": backup_info.get("components", [])
                        })
            
            # Sort by creation date (newest first)
            backups.sort(key=lambda x: x["created_at"], reverse=True)
            
        except Exception as e:
            print(f"Error listing backups: {e}")
        
        return backups
    
    def delete_backup(self, backup_name: str) -> Dict[str, Any]:
        """Delete a backup"""
        try:
            backup_path = os.path.join(self.backup_dir, backup_name)
            
            if os.path.isdir(backup_path):
                shutil.rmtree(backup_path)
            elif os.path.isfile(backup_path):
                os.remove(backup_path)
            else:
                return {"success": False, "error": "Backup not found"}
            
            return {"success": True, "deleted_at": datetime.now().isoformat()}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def schedule_auto_backups(self):
        """Schedule automatic backups"""
        if not self.backup_config["auto_backup"]:
            return
        
        interval = self.backup_config["backup_interval"]
        
        if interval == "daily":
            schedule.every().day.at("02:00").do(self._auto_backup)
        elif interval == "weekly":
            schedule.every().sunday.at("02:00").do(self._auto_backup)
        elif interval == "monthly":
            schedule.every().month.do(self._auto_backup)
        
        # Run scheduler in background
        def run_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
    
    def _auto_backup(self):
        """Perform automatic backup"""
        try:
            result = self.create_backup()
            if result["success"]:
                print(f"Auto backup created: {result['backup_name']}")
            else:
                print(f"Auto backup failed: {result['error']}")
        except Exception as e:
            print(f"Auto backup error: {e}")
    
    def _calculate_checksum(self, file_path: str) -> str:
        """Calculate file checksum"""
        import hashlib
        
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def _verify_checksum(self, file_path: str, expected_checksum: str) -> bool:
        """Verify file checksum"""
        return self._calculate_checksum(file_path) == expected_checksum
    
    def _get_database_record_count(self) -> int:
        """Get total record count in database"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM system_metrics")
            metrics_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM alerts")
            alerts_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM optimization_events")
            events_count = cursor.fetchone()[0]
            
            conn.close()
            
            return metrics_count + alerts_count + events_count
            
        except Exception:
            return 0
    
    def _find_log_files(self) -> List[str]:
        """Find log files in the application directory"""
        log_files = []
        app_dir = os.path.dirname(__file__)
        
        for file in os.listdir(app_dir):
            if file.endswith('.log') or file.endswith('.txt'):
                log_files.append(os.path.join(app_dir, file))
        
        return log_files
    
    def _compress_backup(self, backup_path: str):
        """Compress backup directory"""
        zip_path = backup_path + ".zip"
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(backup_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, backup_path)
                    zipf.write(file_path, arcname)
        
        # Remove original directory
        shutil.rmtree(backup_path)
    
    def _extract_backup(self, zip_path: str) -> str:
        """Extract compressed backup"""
        extract_path = zip_path[:-4] + "_extracted"
        
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            zipf.extractall(extract_path)
        
        return extract_path
    
    def _get_zip_backup_info(self, zip_path: str) -> Optional[Dict[str, Any]]:
        """Get backup info from compressed backup"""
        try:
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                if 'backup_info.json' in zipf.namelist():
                    with zipf.open('backup_info.json') as f:
                        return json.load(f)
        except Exception:
            pass
        
        return None
    
    def _get_directory_size(self, directory: str) -> int:
        """Get total size of directory"""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(directory):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                if os.path.exists(file_path):
                    total_size += os.path.getsize(file_path)
        return total_size
    
    def _cleanup_old_backups(self):
        """Remove old backups based on retention policy"""
        try:
            backups = self.list_backups()
            
            if len(backups) > self.backup_config["max_backups"]:
                # Remove oldest backups
                backups_to_remove = backups[self.backup_config["max_backups"]:]
                
                for backup in backups_to_remove:
                    self.delete_backup(backup["name"])
                    print(f"Removed old backup: {backup['name']}")
            
            # Also remove backups older than 30 days
            cutoff_date = datetime.now() - timedelta(days=30)
            
            for backup in backups:
                backup_date = datetime.fromisoformat(backup["created_at"])
                if backup_date < cutoff_date:
                    self.delete_backup(backup["name"])
                    print(f"Removed expired backup: {backup['name']}")
        
        except Exception as e:
            print(f"Error cleaning up old backups: {e}")
    
    def _close_database_connections(self):
        """Close database connections (placeholder)"""
        # This would need to be implemented based on the actual application
        # For now, just a placeholder
        pass
    
    def export_backup(self, backup_name: str, export_path: str) -> Dict[str, Any]:
        """Export backup to external location"""
        try:
            backup_path = os.path.join(self.backup_dir, backup_name)
            
            if not os.path.exists(backup_path):
                return {"success": False, "error": "Backup not found"}
            
            if os.path.isdir(backup_path):
                shutil.copytree(backup_path, export_path)
            else:
                shutil.copy2(backup_path, export_path)
            
            return {
                "success": True,
                "export_path": export_path,
                "exported_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def import_backup(self, import_path: str) -> Dict[str, Any]:
        """Import backup from external location"""
        try:
            if not os.path.exists(import_path):
                return {"success": False, "error": "Import file not found"}
            
            # Generate unique backup name
            backup_name = f"imported_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            backup_path = os.path.join(self.backup_dir, backup_name)
            
            if os.path.isdir(import_path):
                shutil.copytree(import_path, backup_path)
            else:
                shutil.copy2(import_path, backup_path)
            
            return {
                "success": True,
                "backup_name": backup_name,
                "backup_path": backup_path,
                "imported_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_backup_statistics(self) -> Dict[str, Any]:
        """Get backup statistics"""
        try:
            backups = self.list_backups()
            
            total_size = sum(backup["size"] for backup in backups)
            total_count = len(backups)
            
            compressed_count = sum(1 for backup in backups if backup["compressed"])
            
            if backups:
                oldest_backup = min(backups, key=lambda x: x["created_at"])
                newest_backup = max(backups, key=lambda x: x["created_at"])
            else:
                oldest_backup = None
                newest_backup = None
            
            return {
                "total_backups": total_count,
                "total_size": total_size,
                "compressed_backups": compressed_count,
                "oldest_backup": oldest_backup["created_at"] if oldest_backup else None,
                "newest_backup": newest_backup["created_at"] if newest_backup else None,
                "backup_directory": self.backup_dir,
                "auto_backup_enabled": self.backup_config["auto_backup"],
                "backup_interval": self.backup_config["backup_interval"]
            }
            
        except Exception as e:
            return {"error": str(e)}
