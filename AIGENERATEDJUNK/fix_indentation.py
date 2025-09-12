#!/usr/bin/env python3
"""Fix indentation error in the terrain file"""

def fix_indentation_error():
    with open('08.11_terrain_kent_smooth.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Fix line 813 (index 812) - remove extra indentation
    if len(lines) > 812:
        if '        print("🏔️ REALISTIC MOUNTAIN SYSTEM:")' in lines[812]:
            lines[812] = '    print("🏔️ REALISTIC MOUNTAIN SYSTEM:")\n'
            print("Fixed indentation on line 813")
        else:
            print(f"Line 813 content: {lines[812].strip()}")
    
    # Write back the fixed file
    with open('08.11_terrain_kent_smooth.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("✅ Indentation error fixed!")

if __name__ == "__main__":
    fix_indentation_error()
