#!/usr/bin/env python3
"""
Fix the camera movement vectors to actually work with Panda3D's coordinate system
"""

def fix_camera_vectors():
    with open('08.12_terrain_kent_camera_fixed.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and replace the camera movement section with a corrected version
    old_movement = '''        # FIXED CAMERA-RELATIVE MOVEMENT SYSTEM
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
    
    new_movement = '''        # CORRECTED CAMERA-RELATIVE MOVEMENT FOR PANDA3D
        # Get current camera angles in radians
        heading_rad = math.radians(self.camera_hpr.x)  # Yaw rotation (Q/E keys)
        pitch_rad = math.radians(self.camera_hpr.y)    # Pitch rotation (Up/Down arrows)
        
        # DEBUG: Print angles to verify they're changing
        if self.keys["w"] or self.keys["s"] or self.keys["a"] or self.keys["d"]:
            if hasattr(self, '_debug_counter'):
                self._debug_counter += 1
            else:
                self._debug_counter = 0
            
            if self._debug_counter % 60 == 0:  # Print every 60 frames (1 second)
                print(f"Camera angles - Heading: {self.camera_hpr.x:.1f}°, Pitch: {self.camera_hpr.y:.1f}°")
        
        # CORRECTED MOVEMENT VECTORS for Panda3D coordinate system
        # In Panda3D: +X is right, +Y is forward, +Z is up
        
        # Forward vector (direction camera is pointing)
        # Need to account for Panda3D's coordinate system
        forward_x = math.sin(heading_rad) * math.cos(pitch_rad)
        forward_y = math.cos(heading_rad) * math.cos(pitch_rad)
        forward_z = -math.sin(pitch_rad)
        
        # Right vector (perpendicular to forward, for strafing)
        # 90 degrees to the right of forward direction
        right_x = math.cos(heading_rad)
        right_y = -math.sin(heading_rad)
        right_z = 0  # Keep strafe horizontal
        
        # Apply movement based on current camera orientation
        if self.keys["w"]:  # Move FORWARD relative to camera direction
            self.camera_pos.x += forward_x * speed * dt
            self.camera_pos.y += forward_y * speed * dt
            self.camera_pos.z += forward_z * speed * dt
            
        if self.keys["s"]:  # Move BACKWARD relative to camera direction  
            self.camera_pos.x -= forward_x * speed * dt
            self.camera_pos.y -= forward_y * speed * dt
            self.camera_pos.z -= forward_z * speed * dt
            
        if self.keys["a"]:  # Strafe LEFT relative to camera
            self.camera_pos.x -= right_x * speed * dt
            self.camera_pos.y -= right_y * speed * dt
            
        if self.keys["d"]:  # Strafe RIGHT relative to camera
            self.camera_pos.x += right_x * speed * dt
            self.camera_pos.y += right_y * speed * dt
            
        if self.keys["space"]:  # Move UP (world vertical)
            self.camera_pos.z += speed * dt
            
        if self.keys["shift"]:  # Move DOWN (world vertical)
            self.camera_pos.z -= speed * dt'''
    
    if old_movement in content:
        content = content.replace(old_movement, new_movement)
        print("✅ Fixed camera movement vectors!")
    else:
        print("❌ Could not find movement section to replace")
        print("Let me check what's actually in the file...")
        # Let's see what's actually there
        lines = content.split('\n')
        for i, line in enumerate(lines[735:745], 735):
            print(f"Line {i}: {line}")
        return False
    
    # Write the corrected file
    with open('08.12_terrain_kent_camera_fixed.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("🎮 Movement should now be truly camera-relative!")
    print("📐 Added debug output to verify angles are changing")
    print("🔧 Corrected for Panda3D coordinate system")
    return True

if __name__ == "__main__":
    fix_camera_vectors()
