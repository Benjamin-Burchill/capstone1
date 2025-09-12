#!/usr/bin/env python3
"""
Implement the enhanced camera movement system from the expert response
"""

def implement_enhanced_camera():
    with open('08.12_terrain_kent_camera_fixed.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and replace the entire update_camera function with the enhanced version
    old_function_start = '    def update_camera(self, task):'
    old_function_end = '        return Task.cont'
    
    # Find the start and end of the function
    start_idx = content.find(old_function_start)
    if start_idx == -1:
        print("❌ Could not find update_camera function")
        return False
    
    # Find the end by looking for the next function or end of class
    end_idx = content.find('        return Task.cont', start_idx)
    if end_idx == -1:
        print("❌ Could not find end of update_camera function")
        return False
    
    end_idx = content.find('\n', end_idx) + 1  # Include the newline
    
    # Extract everything before and after the function
    before_function = content[:start_idx]
    after_function = content[end_idx:]
    
    # The new enhanced camera function
    new_function = '''    def update_camera(self, task):
        dt = globalClock.getDt()  # Use real delta time for smoother frame-rate independence
        target_speed = self.fast_speed if self.fast_mode else self.move_speed
        
        # Smooth speed transition for polished RPG feel (e.g., accelerating into a sprint across plains)
        self.current_speed = getattr(self, 'current_speed', target_speed)
        self.current_speed = self.lerp(self.current_speed, target_speed, 0.1)  # 10% lerp per frame
        
        # FIRST: Handle camera rotation (Q/E for yaw, arrows for pitch)
        if self.keys["q"]:
            self.camera_hpr.x += self.rotate_speed * dt
        if self.keys["e"]:
            self.camera_hpr.x -= self.rotate_speed * dt
        if self.keys["up"]:
            self.camera_hpr.y = max(-89, self.camera_hpr.y - self.rotate_speed * dt)  # Clamp to avoid flips
        if self.keys["down"]:
            self.camera_hpr.y = min(89, self.camera_hpr.y + self.rotate_speed * dt)
        
        # Get current camera orientation in radians
        heading_rad = math.radians(self.camera_hpr.x)  # Yaw: left/right rotation
        pitch_rad = math.radians(self.camera_hpr.y)    # Pitch: up/down tilt
        
        # Forward vector: Fully relative to camera direction (includes pitch for diving/soaring)
        forward_x = math.sin(heading_rad) * math.cos(pitch_rad)
        forward_y = math.cos(heading_rad) * math.cos(pitch_rad)
        forward_z = -math.sin(pitch_rad)  # Negative for forward being "into" the view
        
        # Enhanced right vector: Perpendicular to forward, but now tilts with pitch for less "grid" feel
        # (50% pitch influence keeps strafe mostly horizontal but follows camera plane for smoother banking)
        strafe_pitch_factor = 0.5  # Tune: 0.0 = pure horizontal (current), 1.0 = full pitch-relative
        right_x = math.cos(heading_rad) * math.cos(pitch_rad * strafe_pitch_factor)
        right_y = -math.sin(heading_rad) * math.cos(pitch_rad * strafe_pitch_factor)
        right_z = math.sin(pitch_rad * strafe_pitch_factor)  # Subtle Z for perspective-locked strafing
        
        # Normalize vectors to prevent speed scaling issues at extreme pitches
        forward_mag = math.sqrt(forward_x**2 + forward_y**2 + forward_z**2)
        if forward_mag > 0:
            forward_x /= forward_mag
            forward_y /= forward_mag
            forward_z /= forward_mag
        
        right_mag = math.sqrt(right_x**2 + right_y**2 + right_z**2)
        if right_mag > 0:
            right_x /= right_mag
            right_y /= right_mag
            right_z /= right_z
        
        # Apply movements: All relative to current camera state (updates every frame for yaw/pitch changes)
        if self.keys["w"]:  # Forward: Dive/soar in exact view direction—perfect for chasing aerial quests
            self.camera_pos.x += forward_x * self.current_speed * dt
            self.camera_pos.y += forward_y * self.current_speed * dt
            self.camera_pos.z += forward_z * self.current_speed * dt
            
        if self.keys["s"]:  # Backward: Opposite of forward, maintains relativity
            self.camera_pos.x -= forward_x * self.current_speed * dt
            self.camera_pos.y -= forward_y * self.current_speed * dt
            self.camera_pos.z -= forward_z * self.current_speed * dt
            
        if self.keys["a"]:  # Strafe left: Now follows pitched horizon for fluid valley skirting
            self.camera_pos.x -= right_x * self.current_speed * dt
            self.camera_pos.y -= right_y * self.current_speed * dt
            self.camera_pos.z -= right_z * self.current_speed * dt
            
        if self.keys["d"]:  # Strafe right: Mirrors left, enhances side-scrolling over ridges
            self.camera_pos.x += right_x * self.current_speed * dt
            self.camera_pos.y += right_y * self.current_speed * dt
            self.camera_pos.z += right_z * self.current_speed * dt
            
        # Vertical: World-relative (up/down ignores pitch for easy altitude control during scouting)
        if self.keys["space"]:
            self.camera_pos.z += self.current_speed * dt
        if self.keys["shift"]:
            self.camera_pos.z -= self.current_speed * dt
        
        # Apply to camera
        self.camera.setPos(self.camera_pos)
        self.camera.setHpr(self.camera_hpr)
        
        # UI Update: RPG-friendly stats (position in km for world-scale awareness)
        mode = "FAST" if self.fast_mode else "NORM"
        self.state_text.setText(
            f"Pos: ({self.camera_pos.x/1000:.1f}km, {self.camera_pos.y/1000:.1f}km, {self.camera_pos.z/1000:.1f}km) | "
            f"H: {self.camera_hpr.x:.0f}° P: {self.camera_hpr.y:.0f}° | Speed: {mode} ({self.current_speed:.0f}u/s)"
        )
        
        return Task.cont
    
    # Helper lerp function (add this to your class if not present—simple interpolation for smoothing)
    def lerp(self, a, b, t):
        \"\"\"Linear interpolation for smooth transitions (e.g., speed ramps in open-world traversal)\"\"\"
        return a + t * (b - a)'''
    
    # Add the lerp method after the update_camera function
    new_function_with_lerp = new_function + '''
    
    def lerp(self, a, b, t):
        """Linear interpolation for smooth transitions (e.g., speed ramps in open-world traversal)"""
        return a + t * (b - a)'''
    
    # Reconstruct the file
    new_content = before_function + new_function_with_lerp + after_function
    
    # Also need to import globalClock at the top
    if 'from direct.task import Task' in new_content:
        new_content = new_content.replace(
            'from direct.task import Task',
            'from direct.task import Task\nfrom direct.showbase.DirectObject import DirectObject'
        )
    
    # Add globalClock import
    if 'import time' in new_content:
        new_content = new_content.replace(
            'import time',
            'import time\nfrom panda3d.core import globalClock'
        )
    
    # Write the enhanced version
    with open('08.12_terrain_kent_camera_fixed.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Implemented enhanced camera movement system!")
    print("🎮 Key improvements:")
    print("  • Smooth speed transitions with lerp")
    print("  • Enhanced strafe that follows camera pitch plane")
    print("  • Normalized vectors prevent speed scaling issues")
    print("  • Real delta time for frame-rate independence")
    print("  • RPG-friendly movement feel")
    print("🔧 Features:")
    print("  • strafe_pitch_factor = 0.5 (tunable)")
    print("  • Vector normalization prevents speed issues")
    print("  • Smooth acceleration/deceleration")
    
    return True

if __name__ == "__main__":
    implement_enhanced_camera()
