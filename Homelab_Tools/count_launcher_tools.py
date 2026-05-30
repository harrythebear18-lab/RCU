#!/usr/bin/env python3
"""
Count and verify all tools in the launcher
"""

def count_launcher_tools():
    """Count all tools in the launcher"""
    print("🔍 Counting Tools in Simple Launcher")
    print("=" * 50)
    
    # Read the launcher file
    with open("simple_launcher.py", 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Count tools by looking for tool definitions
    tool_count = 0
    categories = {}
    
    lines = content.split('\n')
    current_category = None
    
    for line in lines:
        line = line.strip()
        
        # Find category
        if line.startswith('"') and ':' in line and line.endswith('{'):
            current_category = line.split('"')[1]
            categories[current_category] = []
            print(f"\n📁 {current_category}:")
        
        # Find tool
        elif current_category and line.startswith('"') and '"' in line and ':' in line and not line.startswith('"path"'):
            tool_name = line.split('"')[1]
            if tool_name != 'path':
                categories[current_category].append(tool_name)
                print(f"  • {tool_name}")
                tool_count += 1
    
    print(f"\n📊 Summary:")
    print(f"  Total Tools: {tool_count}")
    print(f"  Categories: {len(categories)}")
    
    for category, tools in categories.items():
        print(f"  • {category}: {len(tools)} tools")
    
    return tool_count, categories

if __name__ == "__main__":
    count_launcher_tools()
