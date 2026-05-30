#!/usr/bin/env python3
"""
Find failed Python files from test results
"""

import json

def find_failed_python_files():
    try:
        with open('test_results.json', 'r') as f:
            data = json.load(f)
        
        failed_files = []
        python_results = data.get('python_files', {})
        
        for file_path, result in python_results.items():
            if not result.get('passed', False):
                failed_files.append({
                    'file': file_path,
                    'message': result.get('message', 'Unknown error'),
                    'details': result.get('details', {})
                })
        
        print(f"Found {len(failed_files)} failed Python files:")
        for i, failed in enumerate(failed_files, 1):
            print(f"{i}. {failed['file']} - {failed['message']}")
        
        return failed_files
        
    except Exception as e:
        print(f"Error reading test results: {e}")
        return []

if __name__ == "__main__":
    find_failed_python_files()
