#!/usr/bin/env python3
"""Fix syntax error in line 833"""

def fix_syntax_error():
    with open('08.12_terrain_kent_camera_fixed.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Fix line 833 (index 832)
    if len(lines) > 832:
        line = lines[832]
        if '\\n    print(' in line:
            # Split the line properly
            lines[832] = '    print("  • No more grid-aligned movement - true camera-relative controls!")\n'
            lines.insert(833, '    print("🏔️ REALISTIC MOUNTAIN SYSTEM:")\n')
            print("Fixed line 833 syntax error")
    
    # Write back the fixed file
    with open('08.12_terrain_kent_camera_fixed.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("✅ Syntax error fixed!")

if __name__ == "__main__":
    fix_syntax_error()
