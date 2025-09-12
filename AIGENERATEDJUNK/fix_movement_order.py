#!/usr/bin/env python3
"""
Fix the order of camera updates so rotation happens BEFORE movement calculation
"""

def fix_movement_order():
    with open('08.12_terrain_kent_camera_fixed.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the entire update_camera function and replace it
    old_function = '''    def update_camera(self, task):
        dt = 0.016
        speed = self.fast_speed if self.fast_mode else self.move_speed
        
        # CORRECTED CAMERA-RELATIVE MOVEMENT FOR PANDA3D
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
            self.camera_pos.z -= speed * dt
        
        if self.keys["q"]:
            self.camera_hpr.x += self.rotate_speed * dt
        if self.keys["e"]:
            self.camera_hpr.x -= self.rotate_speed * dt
        if self.keys["up"]:
            self.camera_hpr.y = max(-89, self.camera_hpr.y - self.rotate_speed * dt)
        if self.keys["down"]:
            self.camera_hpr.y = min(89, self.camera_hpr.y + self.rotate_speed * dt)
        
        self.camera.setPos(self.camera_pos)
        self.camera.setHpr(self.camera_hpr)
        
        mode = "FAST" if self.fast_mode else "NORM"
        self.state_text.setText(
            f"Pos: ({self.camera_pos.x/1000:.1f}km, {self.camera_pos.y/1000:.1f}km, {self.camera_pos.z/1000:.1f}km) | "
            f"H: {self.camera_hpr.x:.0f}° P: {self.camera_hpr.y:.0f}° | Mode: {mode}"
        )
        
        return Task.cont'''
    
    new_function = '''    def update_camera(self, task):
        dt = 0.016
        speed = self.fast_speed if self.fast_mode else self.move_speed
        
        # FIRST: Handle camera rotation (Q/E for yaw, arrows for pitch)
        # This must happen BEFORE calculating movement vectors!
        if self.keys["q"]:
            self.camera_hpr.x += self.rotate_speed * dt
        if self.keys["e"]:
            self.camera_hpr.x -= self.rotate_speed * dt
        if self.keys["up"]:
            self.camera_hpr.y = max(-89, self.camera_hpr.y - self.rotate_speed * dt)
        if self.keys["down"]:
            self.camera_hpr.y = min(89, self.camera_hpr.y + self.rotate_speed * dt)
        
        # SECOND: Calculate movement vectors using UPDATED camera angles
        heading_rad = math.radians(self.camera_hpr.x)  # Current yaw after Q/E input
        pitch_rad = math.radians(self.camera_hpr.y)    # Current pitch after arrow input
        
        # Forward vector: direction camera is NOW pointing (after rotation)
        forward_x = math.sin(heading_rad) * math.cos(pitch_rad)
        forward_y = math.cos(heading_rad) * math.cos(pitch_rad)
        forward_z = -math.sin(pitch_rad)
        
        # Right vector: perpendicular to current camera heading
        right_x = math.cos(heading_rad)
        right_y = -math.sin(heading_rad)
        
        # THIRD: Apply movement using the updated vectors
        if self.keys["w"]:  # Forward in current camera direction
            self.camera_pos.x += forward_x * speed * dt
            self.camera_pos.y += forward_y * speed * dt
            self.camera_pos.z += forward_z * speed * dt
            
        if self.keys["s"]:  # Backward from current camera direction
            self.camera_pos.x -= forward_x * speed * dt
            self.camera_pos.y -= forward_y * speed * dt
            self.camera_pos.z -= forward_z * speed * dt
            
        if self.keys["a"]:  # Strafe left relative to current camera heading
            self.camera_pos.x -= right_x * speed * dt
            self.camera_pos.y -= right_y * speed * dt
            
        if self.keys["d"]:  # Strafe right relative to current camera heading
            self.camera_pos.x += right_x * speed * dt
            self.camera_pos.y += right_y * speed * dt
            
        if self.keys["space"]:  # Move up (world vertical)
            self.camera_pos.z += speed * dt
            
        if self.keys["shift"]:  # Move down (world vertical)
            self.camera_pos.z -= speed * dt
        
        # FOURTH: Update Panda3D camera with new position and orientation
        self.camera.setPos(self.camera_pos)
        self.camera.setHpr(self.camera_hpr)
        
        # Update status display
        mode = "FAST" if self.fast_mode else "NORM"
        self.state_text.setText(
            f"Pos: ({self.camera_pos.x/1000:.1f}km, {self.camera_pos.y/1000:.1f}km, {self.camera_pos.z/1000:.1f}km) | "
            f"H: {self.camera_hpr.x:.0f}° P: {self.camera_hpr.y:.0f}° | Mode: {mode}"
        )
        
        return Task.cont'''
    
    if old_function in content:
        content = content.replace(old_function, new_function)
        print("✅ Fixed camera update order!")
        print("🔄 Rotation now happens BEFORE movement calculation")
        print("🎮 WASD should now use current camera angles, not previous frame's angles")
    else:
        print("❌ Could not find exact function to replace")
        return False
    
    # Write the corrected file
    with open('08.12_terrain_kent_camera_fixed.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

if __name__ == "__main__":
    fix_movement_order()
