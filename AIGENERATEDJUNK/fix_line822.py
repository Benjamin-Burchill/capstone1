#!/usr/bin/env python3
"""Fix line 822 syntax error"""

def fix_line822():
    with open('08.11_terrain_kent_smooth.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Fix line 822 (index 821)
    if len(lines) > 821:
        line = lines[821]
        if '\\n    print(' in line:
            # Split the line properly
            lines[821] = '    print("  • Full 59km x 59km map visible from overview")\n'
            lines.insert(822, '    print("\\nStarting SMOOTH terrain generation...")\n')
            print("Fixed line 822 syntax error")
    
    # Write back the fixed file
    with open('08.11_terrain_kent_smooth.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("✅ Line 822 syntax error fixed!")

if __name__ == "__main__":
    fix_line822()
