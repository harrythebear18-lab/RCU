#!/usr/bin/env python3
"""
Check specific failures from verification results
"""

import json

def check_failures():
    try:
        with open('final_verification_results.json', 'r') as f:
            data = json.load(f)
        
        print("FAILURES BY CATEGORY:")
        print("=" * 50)
        
        total_failures = 0
        for category in data:
            if category == 'overall':
                continue
                
            category_failures = []
            for k, v in data[category].items():
                if not v['passed']:
                    category_failures.append((k, v['message']))
            
            if category_failures:
                print(f"\n{category.upper()} ({len(category_failures)} failures):")
                for i, (file_path, message) in enumerate(category_failures, 1):
                    print(f"  {i}. {file_path} - {message}")
                    total_failures += 1
        
        print(f"\nTOTAL FAILURES: {total_failures}")
        return total_failures
        
    except Exception as e:
        print(f"Error: {e}")
        return 0

if __name__ == "__main__":
    check_failures()
