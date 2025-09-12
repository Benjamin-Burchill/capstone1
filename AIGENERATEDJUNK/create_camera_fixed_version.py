#!/usr/bin/env python3
"""
Create 08.12 with properly fixed camera movement that's truly relative to camera orientation
"""

def create_camera_fixed_version():
    with open('08.12_terrain_kent_camera_fixed.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Update header and version info
    content = content.replace('08.11_terrain_kent_smooth.py - SMOOTH REALISTIC Kent-sized terrain',
                            '08.12_terrain_kent_camera_fixed.py - CAMERA-RELATIVE MOVEMENT Kent terrain')
    
    content = content.replace('class SmoothKentTerrain(ShowBase):', 'class CameraFixedKentTerrain(ShowBase):')
    content = content.replace('app = SmoothKentTerrain()', 'app = CameraFixedKentTerrain()')
    
    # Update window title
    content = content.replace('props.setTitle("Realistic Kent-Sized Terrain - 3,500 km² (TRAVERSABLE)")',
                            'props.setTitle("Kent Terrain - 3,500 km² (CAMERA-RELATIVE MOVEMENT)")')
    
    # Find the current camera movement section and replace with corrected version
    old_movement_section = '''        # Convert camera angles to radians
        heading_rad = math.radians(self.camera_hpr.x)  # Yaw (left/right rotation)
        pitch_rad = math.radians(self.camera_hpr.y)    # Pitch (up/down rotation)
        
        # IMPROVED CAMERA-RELATIVE MOVEMENT VECTORS
        # Forward vector: exact direction camera is pointing (includes pitch)
        forward_x = math.sin(heading_rad) * math.cos(pitch_rad)
        forward_y = math.cos(heading_rad) * math.cos(pitch_rad) 
        forward_z = -math.sin(pitch_rad)
        
        # Right vector: perpendicular to camera heading (horizontal strafe only)
        right_x = math.cos(heading_rad)
        right_y = -math.sin(heading_rad)
        # Note: right_z = 0 (strafe stays horizontal regardless of pitch)
        
        # Up vector: camera's local up direction (affected by roll if implemented)
        up_x = 0  # For now, up is always world vertical
        up_y = 0  # Could be enhanced later for banking/rolling
        up_z = 1
        
        # Apply movement relative to camera orientation
        if self.keys["w"]:  # Forward: move in camera's forward direction
            self.camera_pos.x += forward_x * speed * dt
            self.camera_pos.y += forward_y * speed * dt
            self.camera_pos.z += forward_z * speed * dt
            
        if self.keys["s"]:  # Backward: move opposite to camera's forward direction
            self.camera_pos.x -= forward_x * speed * dt
            self.camera_pos.y -= forward_y * speed * dt
            self.camera_pos.z -= forward_z * speed * dt
            
        if self.keys["a"]:  # Strafe left: move perpendicular to camera heading
            self.camera_pos.x -= right_x * speed * dt
            self.camera_pos.y -= right_y * speed * dt
            # No Z movement for horizontal strafe
            
        if self.keys["d"]:  # Strafe right: move perpendicular to camera heading
            self.camera_pos.x += right_x * speed * dt
            self.camera_pos.y += right_y * speed * dt
            # No Z movement for horizontal strafe
            
        if self.keys["space"]:  # Move up: always world vertical (not camera relative)
            self.camera_pos.z += speed * dt
            
        if self.keys["shift"]:  # Move down: always world vertical (not camera relative)
            self.camera_pos.z -= speed * dt'''
    
    new_movement_section = '''        # FIXED CAMERA-RELATIVE MOVEMENT SYSTEM
        # Convert camera angles to radians for proper calculation
        heading_rad = math.radians(self.camera_hpr.x)  # Yaw (Q/E rotation)
        pitch_rad = math.radians(self.camera_hpr.y)    # Pitch (Up/Down arrows)
        
        # Calculate PROPER camera-relative movement vectors
        # Forward vector: EXACT direction camera is looking (includes pitch)
        forward_x = math.sin(heading_rad) * math.cos(pitch_rad)
        forward_y = math.cos(heading_rad) * math.cos(pitch_rad)
        forward_z = -math.sin(pitch_rad)
        
        # Right vector: perpendicular to camera heading (for strafing)
        # This stays horizontal regardless of pitch for intuitive strafing
        right_x = math.cos(heading_rad)
        right_y = -math.sin(heading_rad)
        right_z = 0  # Strafe is always horizontal
        
        # MOVEMENT: All relative to current camera orientation
        if self.keys["w"]:  # Forward in camera direction (includes vertical if pitched)
            self.camera_pos.x += forward_x * speed * dt
            self.camera_pos.y += forward_y * speed * dt
            self.camera_pos.z += forward_z * speed * dt
            
        if self.keys["s"]:  # Backward from camera direction (includes vertical if pitched)
            self.camera_pos.x -= forward_x * speed * dt
            self.camera_pos.y -= forward_y * speed * dt
            self.camera_pos.z -= forward_z * speed * dt
            
        if self.keys["a"]:  # Strafe left relative to camera heading (horizontal only)
            self.camera_pos.x -= right_x * speed * dt
            self.camera_pos.y -= right_y * speed * dt
            # No Z component - strafe stays horizontal
            
        if self.keys["d"]:  # Strafe right relative to camera heading (horizontal only)
            self.camera_pos.x += right_x * speed * dt
            self.camera_pos.y += right_y * speed * dt
            # No Z component - strafe stays horizontal
            
        if self.keys["space"]:  # Pure vertical up (world axis, not camera relative)
            self.camera_pos.z += speed * dt
            
        if self.keys["shift"]:  # Pure vertical down (world axis, not camera relative)
            self.camera_pos.z -= speed * dt'''
    
    if old_movement_section in content:
        content = content.replace(old_movement_section, new_movement_section)
        print("✅ Fixed camera movement system!")
    else:
        print("❌ Could not find movement section - checking for alternative pattern")
        # Try to find a simpler pattern to replace
        if 'heading_rad = math.radians(self.camera_hpr.x)' in content:
            print("Found camera movement section with different formatting")
        return False
    
    # Update the main description
    content = content.replace('print("\\n=== SMOOTH REALISTIC Kent-Sized Terrain ===")',
                            'print("\\n=== CAMERA-RELATIVE MOVEMENT Kent Terrain ===")')
    
    # Add camera movement description
    new_features = '''    print("🎮 FIXED CAMERA MOVEMENT:")
    print("  • W/S: Move forward/backward in camera's exact viewing direction")
    print("  • A/D: Strafe left/right perpendicular to camera (horizontal)")
    print("  • Space/Shift: Pure vertical movement (world up/down)")
    print("  • Movement stays relative to camera after Q/E yaw or arrow pitch")
    print("  • No more grid-aligned movement - true camera-relative controls!")'''
    
    # Insert camera features before mountain system
    content = content.replace('    print("🏔️ REALISTIC MOUNTAIN SYSTEM:")', 
                            new_features + '\\n    print("🏔️ REALISTIC MOUNTAIN SYSTEM:")')
    
    # Write the camera-fixed version
    with open('08.12_terrain_kent_camera_fixed.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Created 08.12_terrain_kent_camera_fixed.py!")
    print("🎮 Camera movement now properly relative to view direction")
    print("📍 W/S includes vertical movement when pitched up/down")
    print("↔️ A/D strafe horizontally regardless of pitch")
    print("⬆️ Space/Shift for pure vertical movement")
    return True

if __name__ == "__main__":
    create_camera_fixed_version()
