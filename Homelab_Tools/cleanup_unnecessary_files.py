#!/usr/bin/env python3
"""
Cleanup Unnecessary Files
Safely removes files identified by the directory cleanup audit
"""

import os
import json
import shutil
from pathlib import Path
from datetime import datetime

class FileCleaner:
    def __init__(self, base_path=None):
        self.base_path = Path(base_path) if base_path else Path(__file__).parent
        self.audit_file = self.base_path / 'directory_cleanup_audit_results.json'
        self.backup_dir = self.base_path / 'cleanup_backup'
        self.cleanup_log = []
        
    def load_audit_results(self):
        """Load audit results from JSON file"""
        try:
            with open(self.audit_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Audit file not found: {self.audit_file}")
            return None
    
    def create_backup(self):
        """Create backup directory for files to be deleted"""
        if not self.backup_dir.exists():
            self.backup_dir.mkdir(exist_ok=True)
            print(f"📁 Created backup directory: {self.backup_dir}")
    
    def backup_file(self, file_path):
        """Backup a file before deletion"""
        try:
            src = Path(file_path)
            if src.exists():
                # Create relative path in backup
                rel_path = src.relative_to(self.base_path)
                backup_path = self.backup_dir / rel_path
                
                # Create parent directories if needed
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Copy file to backup
                shutil.copy2(src, backup_path)
                return True
        except Exception as e:
            print(f"⚠️  Error backing up {file_path}: {e}")
        return False
    
    def delete_file(self, file_path):
        """Delete a file after backing it up"""
        try:
            path = Path(file_path)
            if path.exists():
                # Backup first
                if self.backup_file(file_path):
                    # Delete the file
                    path.unlink()
                    self.cleanup_log.append({
                        'action': 'deleted',
                        'file': str(file_path),
                        'timestamp': datetime.now().isoformat()
                    })
                    return True
                else:
                    print(f"⚠️  Skipped deletion (backup failed): {file_path}")
            else:
                self.cleanup_log.append({
                    'action': 'skipped_not_found',
                    'file': str(file_path),
                    'timestamp': datetime.now().isoformat()
                })
        except Exception as e:
            print(f"❌ Error deleting {file_path}: {e}")
            self.cleanup_log.append({
                'action': 'error',
                'file': str(file_path),
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
        return False
    
    def run_cleanup(self, dry_run=True):
        """Run the cleanup process"""
        audit_results = self.load_audit_results()
        if not audit_results:
            return
        
        files_to_delete = audit_results.get('recommended_for_deletion', [])
        
        if not files_to_delete:
            print("✅ No files to delete!")
            return
        
        print(f"🔍 Found {len(files_to_delete)} files for deletion")
        
        if dry_run:
            print("\n🔍 DRY RUN - No files will be deleted:")
            for file_path in files_to_delete:
                print(f"  • {Path(file_path).name}")
            print(f"\n💡 To actually delete files, run with dry_run=False")
        else:
            print(f"\n🗑️  STARTING CLEANUP (Files will be backed up to: {self.backup_dir})")
            
            # Create backup directory
            self.create_backup()
            
            # Delete files
            deleted_count = 0
            for file_path in files_to_delete:
                print(f"  🗑️  {Path(file_path).name}")
                if self.delete_file(file_path):
                    deleted_count += 1
            
            # Save cleanup log
            self.save_cleanup_log()
            
            print(f"\n✅ Cleanup completed!")
            print(f"  • Files processed: {len(files_to_delete)}")
            print(f"  • Files deleted: {deleted_count}")
            print(f"  • Backup location: {self.backup_dir}")
            print(f"  • Cleanup log: cleanup_log.json")
    
    def save_cleanup_log(self):
        """Save cleanup log to JSON file"""
        log_file = self.base_path / 'cleanup_log.json'
        
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'backup_directory': str(self.backup_dir),
            'actions': self.cleanup_log
        }
        
        with open(log_file, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        print(f"📄 Cleanup log saved to: {log_file}")
    
    def restore_from_backup(self):
        """Restore files from backup"""
        if not self.backup_dir.exists():
            print(f"❌ Backup directory not found: {self.backup_dir}")
            return
        
        print(f"🔄 Restoring files from backup: {self.backup_dir}")
        
        restored_count = 0
        for backup_file in self.backup_dir.rglob('*'):
            if backup_file.is_file():
                # Calculate original path
                rel_path = backup_file.relative_to(self.backup_dir)
                original_path = self.base_path / rel_path
                
                # Create parent directories if needed
                original_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Restore file
                shutil.copy2(backup_file, original_path)
                restored_count += 1
                print(f"  ✅ Restored: {rel_path}")
        
        print(f"\n✅ Restored {restored_count} files from backup")

def main():
    """Main function"""
    import sys
    
    cleaner = FileCleaner()
    
    # Check command line arguments
    dry_run = '--execute' not in sys.argv
    
    if '--restore' in sys.argv:
        cleaner.restore_from_backup()
    else:
        cleaner.run_cleanup(dry_run=dry_run)

if __name__ == "__main__":
    main()
