#!/usr/bin/env python3
"""
Debug camera movement vectors to understand why it only works at 0° and 180°
"""

def debug_camera_movement():
    with open('08.12_terrain_kent_camera_fixed.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the movement vector calculation and add debug output
    old_vector_calc = '''        # Forward vector: direction camera is NOW pointing (after rotation)
        forward_x = math.sin(heading_rad) * math.cos(pitch_rad)
        forward_y = math.cos(heading_rad) * math.cos(pitch_rad)
        forward_z = -math.sin(pitch_rad)
        
        # Right vector: perpendicular to current camera heading
        right_x = math.cos(heading_rad)
        right_y = -math.sin(heading_rad)'''
    
    new_vector_calc = '''        # DEBUG: Print current angles and calculated vectors
        if self.keys["w"] and hasattr(self, '_debug_timer'):
            self._debug_timer = getattr(self, '_debug_timer', 0) + dt
            if self._debug_timer > 1.0:  # Print every second
                print(f"\\n=== MOVEMENT DEBUG ===")
                print(f"Camera HPR: {self.camera_hpr.x:.1f}°, {self.camera_hpr.y:.1f}°, {self.camera_hpr.z:.1f}°")
                print(f"Heading rad: {heading_rad:.3f}, Pitch rad: {pitch_rad:.3f}")
                print(f"Forward vector: ({forward_x:.3f}, {forward_y:.3f}, {forward_z:.3f})")
                print(f"Right vector: ({right_x:.3f}, {right_y:.3f})")
                self._debug_timer = 0
        elif not self.keys["w"]:
            self._debug_timer = 0
        
        # ORIGINAL PANDA3D COORDINATE SYSTEM ATTEMPT
        # Forward vector: direction camera is NOW pointing (after rotation)  
        forward_x = math.sin(heading_rad) * math.cos(pitch_rad)
        forward_y = math.cos(heading_rad) * math.cos(pitch_rad)
        forward_z = -math.sin(pitch_rad)
        
        # Right vector: perpendicular to current camera heading
        right_x = math.cos(heading_rad)
        right_y = -math.sin(heading_rad)
        
        # ALTERNATIVE: Try different coordinate system
        # Panda3D might use Y-forward, X-right, Z-up differently
        # Let's also try the "corrected" version
        if hasattr(self, '_use_alt_vectors') and self._use_alt_vectors:
            # Alternative calculation - swap X and Y components
            forward_x_alt = math.cos(heading_rad) * math.cos(pitch_rad)  # X component
            forward_y_alt = math.sin(heading_rad) * math.cos(pitch_rad)  # Y component  
            forward_z_alt = -math.sin(pitch_rad)                        # Z component
            
            right_x_alt = -math.sin(heading_rad)  # X component for right vector
            right_y_alt = math.cos(heading_rad)   # Y component for right vector
            
            # Use alternative vectors
            forward_x, forward_y, forward_z = forward_x_alt, forward_y_alt, forward_z_alt
            right_x, right_y = right_x_alt, right_y_alt'''
    
    if old_vector_calc in content:
        content = content.replace(old_vector_calc, new_vector_calc)
        print("✅ Added movement vector debugging!")
    else:
        print("❌ Could not find vector calculation section")
        return False
    
    # Add a key to toggle between vector calculation methods
    old_key_bindings = '''        self.accept("r", self.reset_camera)
        self.accept("o", self.overview_camera)  # O key for overview'''
    
    new_key_bindings = '''        self.accept("r", self.reset_camera)
        self.accept("o", self.overview_camera)  # O key for overview
        self.accept("v", self.toggle_vector_calc)  # V key to toggle vector calculation'''
    
    content = content.replace(old_key_bindings, new_key_bindings)
    
    # Add the toggle function
    toggle_function = '''    
    def toggle_vector_calc(self):
        """Toggle between original and alternative vector calculations"""
        if not hasattr(self, '_use_alt_vectors'):
            self._use_alt_vectors = False
        
        self._use_alt_vectors = not self._use_alt_vectors
        method = "ALTERNATIVE (swapped X/Y)" if self._use_alt_vectors else "ORIGINAL"
        print(f"Switched to {method} vector calculation")
        self.logger.info(f"Vector calculation method: {method}")'''
    
    # Insert after overview_camera function
    content = content.replace('        print("OVERVIEW MODE: 25km altitude - Full 59km x 59km map visible")',
                            'print("OVERVIEW MODE: 25km altitude - Full 59km x 59km map visible")' + toggle_function)
    
    # Update controls text
    content = content.replace('R: Reset | O: Overview",', 'R: Reset | O: Overview | V: Toggle Vectors",')
    
    # Write the debug version
    with open('08.12_terrain_kent_camera_fixed.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("🐛 Added debugging features:")
    print("  • Movement vector values printed when holding W")
    print("  • 'V' key to toggle between vector calculation methods")
    print("  • Debug output shows angles and calculated vectors")
    print("\\nNow you can:")
    print("  1. Run the terrain and move around")
    print("  2. Hold W and see what vectors are calculated at different angles")
    print("  3. Press V to try alternative vector calculation")
    print("  4. Test if the alternative works better at 90° angles")
    
    return True

if __name__ == "__main__":
    debug_camera_movement()
