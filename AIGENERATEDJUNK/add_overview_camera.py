#!/usr/bin/env python3
"""Add overview camera function to the terrain file"""

def add_overview_camera():
    with open('08.11_terrain_kent_smooth.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find the reset_camera function and add overview_camera after it
    new_lines = []
    i = 0
    while i < len(lines):
        new_lines.append(lines[i])
        
        # After reset_camera function, add overview_camera
        if 'def reset_camera(self):' in lines[i]:
            # Skip to end of reset_camera function
            i += 1
            while i < len(lines) and not (lines[i].strip() == '' and not lines[i].startswith('    ')):
                new_lines.append(lines[i])
                i += 1
            
            # Add overview camera function
            overview_function = [
                '    \n',
                '    def overview_camera(self):\n',
                '        """Move camera to high overview position to see entire map"""\n',
                '        self.camera_pos = Point3(0, 0, 25000)  # 25km high for full overview\n',
                '        self.camera_hpr = Vec3(0, -89, 0)  # Looking straight down\n',
                '        self.camera.setPos(self.camera_pos)\n',
                '        self.camera.setHpr(self.camera_hpr)\n',
                '        self.logger.info("Camera moved to overview position - 25km high, full map view")\n',
                '        print("OVERVIEW MODE: 25km altitude - Full 59km x 59km map visible")\n'
            ]
            new_lines.extend(overview_function)
            continue
        
        # Add key binding for overview camera
        if 'self.accept("r", self.reset_camera)' in lines[i]:
            new_lines.append('        self.accept("o", self.overview_camera)  # O key for overview\n')
        
        # Update controls text
        if 'R: Reset",' in lines[i]:
            new_lines[-1] = lines[i].replace('R: Reset",', 'R: Reset | O: Overview",')
        
        i += 1
    
    # Write the updated file
    with open('08.11_terrain_kent_smooth.py', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print("✅ Overview camera function added!")
    print("📷 Press 'O' key for 25km altitude overview")

if __name__ == "__main__":
    add_overview_camera()
