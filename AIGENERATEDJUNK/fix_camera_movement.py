#!/usr/bin/env python3
"""
Fix camera movement to be properly relative to camera orientation
"""

def fix_camera_movement():
    with open('08.11_terrain_kent_smooth.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the camera movement section and replace it with improved version
    old_camera_section = '''        heading_rad = math.radians(self.camera_hpr.x)
        pitch_rad = math.radians(self.camera_hpr.y)
        
        # CAMERA-RELATIVE MOVEMENT VECTORS
        # Forward vector: direction camera is pointing (includes pitch)
        forward_x = math.sin(heading_rad) * math.cos(pitch_rad)
        forward_y = math.cos(heading_rad) * math.cos(pitch_rad)
        forward_z = -math.sin(pitch_rad)
        
        # Right vector: perpendicular to camera heading (for strafing)
        right_x = math.cos(heading_rad)
        right_y = -math.sin(heading_rad)
        
        if self.keys["w"]:  # Forward relative to camera direction
            self.camera_pos.x += forward_x * speed * dt
            self.camera_pos.y += forward_y * speed * dt
            self.camera_pos.z += forward_z * speed * dt
        if self.keys["s"]:  # Backward relative to camera direction
            self.camera_pos.x -= forward_x * speed * dt
            self.camera_pos.y -= forward_y * speed * dt
            self.camera_pos.z -= forward_z * speed * dt
        if self.keys["a"]:  # Strafe left relative to camera
            self.camera_pos.x -= right_x * speed * dt
            self.camera_pos.y -= right_y * speed * dt
        if self.keys["d"]:  # Strafe right relative to camera
            self.camera_pos.x += right_x * speed * dt
            self.camera_pos.y += right_y * speed * dt
        if self.keys["space"]:  # Move up (world vertical)
            self.camera_pos.z += speed * dt
        if self.keys["shift"]:  # Move down (world vertical)
            self.camera_pos.z -= speed * dt'''
    
    new_camera_section = '''        # Convert camera angles to radians
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
    
    if old_camera_section in content:
        content = content.replace(old_camera_section, new_camera_section)
        print("✅ Enhanced camera-relative movement system!")
    else:
        print("❌ Could not find camera movement section to replace")
        return False
    
    # Write the updated file
    with open('08.11_terrain_kent_smooth.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("🎮 Camera movement improvements:")
    print("  • W/S: Move forward/backward in camera's exact viewing direction")
    print("  • A/D: Strafe left/right perpendicular to camera heading")
    print("  • Space/Shift: Move up/down in world vertical (not camera relative)")
    print("  • Movement works correctly regardless of yaw (Q/E) or pitch (arrows)")
    return True

if __name__ == "__main__":
    fix_camera_movement()
