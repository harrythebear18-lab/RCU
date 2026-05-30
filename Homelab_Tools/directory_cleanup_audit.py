#!/usr/bin/env python3
"""
Directory Cleanup Audit
Comprehensive audit to identify duplicate, broken, and unnecessary files for cleanup
"""

import os
import json
from pathlib import Path
from datetime import datetime
import hashlib

class DirectoryCleanupAudit:
    def __init__(self, base_path=None):
        self.base_path = Path(base_path) if base_path else Path(__file__).parent
        self.audit_results = {
            'timestamp': datetime.now().isoformat(),
            'duplicate_files': [],
            'broken_launchers': [],
            'unused_files': [],
            'test_files': [],
            'debug_files': [],
            'backup_files': [],
            'temporary_files': [],
            'recommended_for_deletion': [],
            'keep_files': [],
            'statistics': {}
        }
        
    def run_audit(self):
        """Run comprehensive directory audit"""
        print("🔍 Starting Directory Cleanup Audit...")
        
        # Scan all Python files
        all_py_files = list(self.base_path.glob("**/*.py"))
        
        # Analyze file categories
        self.analyze_dashboard_launchers(all_py_files)
        self.analyze_test_files(all_py_files)
        self.analyze_debug_files(all_py_files)
        self.analyze_backup_files(all_py_files)
        self.analyze_temporary_files(all_py_files)
        self.analyze_duplicate_files(all_py_files)
        
        # Generate recommendations
        self.generate_cleanup_recommendations()
        
        # Calculate statistics
        self.calculate_statistics(all_py_files)
        
        # Save results
        self.save_audit_results()
        
        print(f"✅ Audit completed. Found {len(self.audit_results['recommended_for_deletion'])} files for deletion.")
        
    def analyze_dashboard_launchers(self, py_files):
        """Analyze dashboard and launcher files"""
        dashboard_files = [f for f in py_files if 'dashboard' in f.name.lower()]
        launcher_files = [f for f in py_files if 'launcher' in f.name.lower()]
        
        # Identify working files (keep these)
        working_dashboards = ['streamlined_dashboard.py', 'simple_dashboard.py']
        working_launchers = ['simple_launcher.py', 'homelab_launcher.py']
        
        for file in dashboard_files:
            if file.name in working_dashboards:
                self.audit_results['keep_files'].append(str(file))
            else:
                self.audit_results['broken_launchers'].append(str(file))
                
        for file in launcher_files:
            if file.name in working_launchers:
                self.audit_results['keep_files'].append(str(file))
            else:
                self.audit_results['broken_launchers'].append(str(file))
    
    def analyze_test_files(self, py_files):
        """Analyze test files"""
        test_indicators = ['test_', '_test', 'debug_', 'temp_', 'tmp_']
        
        for file in py_files:
            if any(indicator in file.name.lower() for indicator in test_indicators):
                self.audit_results['test_files'].append(str(file))
    
    def analyze_debug_files(self, py_files):
        """Analyze debug files"""
        debug_indicators = ['debug_', 'fix_', 'check_', 'verify_']
        
        for file in py_files:
            if any(indicator in file.name.lower() for indicator in debug_indicators):
                self.audit_results['debug_files'].append(str(file))
    
    def analyze_backup_files(self, py_files):
        """Analyze backup files"""
        backup_indicators = ['backup_', '_backup', '_old', '_orig', 'copy_', 'duplicate_']
        
        for file in py_files:
            if any(indicator in file.name.lower() for indicator in backup_indicators):
                self.audit_results['backup_files'].append(str(file))
    
    def analyze_temporary_files(self, py_files):
        """Analyze temporary files"""
        temp_indicators = ['temp_', 'tmp_', 'temporary_']
        
        for file in py_files:
            if any(indicator in file.name.lower() for indicator in temp_indicators):
                self.audit_results['temporary_files'].append(str(file))
    
    def analyze_duplicate_files(self, py_files):
        """Analyze potentially duplicate files"""
        file_hashes = {}
        
        for file in py_files:
            try:
                # Calculate file hash
                with open(file, 'rb') as f:
                    file_hash = hashlib.md5(f.read()).hexdigest()
                
                if file_hash in file_hashes:
                    file_hashes[file_hash].append(str(file))
                else:
                    file_hashes[file_hash] = [str(file)]
            except Exception as e:
                print(f"Error hashing {file}: {e}")
        
        # Find duplicates
        for hash_val, files in file_hashes.items():
            if len(files) > 1:
                self.audit_results['duplicate_files'].extend(files[1:])  # Keep first, mark rest as duplicates
    
    def generate_cleanup_recommendations(self):
        """Generate cleanup recommendations"""
        # Files to delete: test, debug, backup, temporary, broken launchers, and duplicates
        categories_to_delete = [
            self.audit_results['test_files'],
            self.audit_results['debug_files'],
            self.audit_results['backup_files'],
            self.audit_results['temporary_files'],
            self.audit_results['broken_launchers'],
            self.audit_results['duplicate_files']
        ]
        
        for category in categories_to_delete:
            self.audit_results['recommended_for_deletion'].extend(category)
        
        # Remove any files that are in keep list
        keep_set = set(self.audit_results['keep_files'])
        self.audit_results['recommended_for_deletion'] = [
            f for f in self.audit_results['recommended_for_deletion'] 
            if f not in keep_set
        ]
    
    def calculate_statistics(self, all_py_files):
        """Calculate audit statistics"""
        self.audit_results['statistics'] = {
            'total_python_files': len(all_py_files),
            'files_to_keep': len(self.audit_results['keep_files']),
            'files_to_delete': len(self.audit_results['recommended_for_deletion']),
            'duplicate_files': len(self.audit_results['duplicate_files']),
            'test_files': len(self.audit_results['test_files']),
            'debug_files': len(self.audit_results['debug_files']),
            'backup_files': len(self.audit_results['backup_files']),
            'temporary_files': len(self.audit_results['temporary_files']),
            'broken_launchers': len(self.audit_results['broken_launchers']),
            'space_saved_estimate': len(self.audit_results['recommended_for_deletion']) * 50  # KB estimate
        }
    
    def save_audit_results(self):
        """Save audit results to JSON file"""
        output_file = self.base_path / 'directory_cleanup_audit_results.json'
        
        with open(output_file, 'w') as f:
            json.dump(self.audit_results, f, indent=2)
        
        print(f"📄 Audit results saved to: {output_file}")
    
    def print_summary(self):
        """Print audit summary"""
        stats = self.audit_results['statistics']
        
        print("\n" + "="*60)
        print("📊 DIRECTORY CLEANUP AUDIT SUMMARY")
        print("="*60)
        print(f"Total Python files: {stats['total_python_files']}")
        print(f"Files to keep: {stats['files_to_keep']}")
        print(f"Files recommended for deletion: {stats['files_to_delete']}")
        print(f"Estimated space saved: ~{stats['space_saved_estimate']} KB")
        
        print(f"\n📋 BREAKDOWN:")
        print(f"  • Duplicate files: {stats['duplicate_files']}")
        print(f"  • Test files: {stats['test_files']}")
        print(f"  • Debug files: {stats['debug_files']}")
        print(f"  • Backup files: {stats['backup_files']}")
        print(f"  • Temporary files: {stats['temporary_files']}")
        print(f"  • Broken launchers: {stats['broken_launchers']}")
        
        print(f"\n✅ FILES TO KEEP:")
        for file in self.audit_results['keep_files']:
            print(f"  • {Path(file).name}")
        
        if self.audit_results['recommended_for_deletion']:
            print(f"\n🗑️  FILES TO DELETE (Top 10):")
            for file in self.audit_results['recommended_for_deletion'][:10]:
                print(f"  • {Path(file).name}")
            if len(self.audit_results['recommended_for_deletion']) > 10:
                print(f"  ... and {len(self.audit_results['recommended_for_deletion']) - 10} more")
        
        print("="*60)

def main():
    """Main function"""
    auditor = DirectoryCleanupAudit()
    auditor.run_audit()
    auditor.print_summary()

if __name__ == "__main__":
    main()
