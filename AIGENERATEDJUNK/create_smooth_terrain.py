#!/usr/bin/env python3
"""
Create smooth, realistic terrain with gentle slopes and overview camera
"""

def create_smooth_terrain():
    with open('08.11_terrain_kent_smooth.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Update header
    content = content.replace('08.10_terrain_kent_realistic.py - REALISTIC TRAVERSABLE Kent-sized terrain',
                            '08.11_terrain_kent_smooth.py - SMOOTH REALISTIC Kent-sized terrain')
    
    content = content.replace('class RealisticKentTerrain(ShowBase):', 'class SmoothKentTerrain(ShowBase):')
    content = content.replace('app = RealisticKentTerrain()', 'app = SmoothKentTerrain()')
    
    # Add overview camera function after reset_camera
    overview_camera_code = '''    
    def overview_camera(self):
        """Move camera to high overview position to see entire map"""
        # Calculate height needed to see entire 59km map
        map_size = 59000
        # Position camera at center, very high up, looking down
        self.camera_pos = Point3(0, 0, 25000)  # 25km high for full overview
        self.camera_hpr = Vec3(0, -89, 0)  # Looking straight down
        self.camera.setPos(self.camera_pos)
        self.camera.setHpr(self.camera_hpr)
        self.logger.info("Camera moved to overview position - 25km high, full map view")
        print("OVERVIEW MODE: 25km altitude - Full 59km x 59km map visible")'''
    
    # Insert after reset_camera function
    content = content.replace('        print("Camera reset to overview position")',
                            'print("Camera reset to overview position")' + overview_camera_code)
    
    # Add overview key binding
    content = content.replace('        self.accept("r", self.reset_camera)',
                            '''        self.accept("r", self.reset_camera)
        self.accept("o", self.overview_camera)  # 'O' key for overview''')
    
    # Update controls text to include overview key
    content = content.replace('text="WASD: Move | Q/E: Yaw | Arrows: Pitch | Space/Shift: Up/Down | F: Fast mode | R: Reset",',
                            'text="WASD: Move | Q/E: Yaw | Arrows: Pitch | Space/Shift: Up/Down | F: Fast mode | R: Reset | O: Overview",')
    
    # Now fix the terrain generation for smooth, realistic mountains
    # First, replace the terrain generation section with smoother algorithm
    old_terrain_section = '''                    # REALISTIC Multi-scale terrain with HEIGHT CONSTRAINTS
                    distance_from_center = math.sqrt(wx**2 + wy**2)
                    
                    # Large scale base elevation (0-1500m)
                    large_scale = self.fractal_brownian_motion(wx, wy, octaves=4, frequency=0.00002, amplitude=600, seed=42)
                    large_scale = max(0, large_scale)  # No negative base elevation
                    
                    # Medium scale hills (0-400m variation)
                    medium_scale = self.fractal_brownian_motion(wx, wy, octaves=6, frequency=0.00008, amplitude=200, seed=123)
                    
                    # Small scale detail for traversal (0-80m)
                    small_scale = self.fractal_brownian_motion(wx, wy, octaves=8, frequency=0.0004, amplitude=30, seed=456)
                    
                    # Ground-level detail (0-15m)
                    ground_detail = self.fractal_brownian_motion(wx, wy, octaves=6, frequency=0.002, amplitude=6, seed=789)
                    
                    # Micro features (0-3m)
                    micro_detail = self.fractal_brownian_motion(wx, wy, octaves=4, frequency=0.01, amplitude=1.5, seed=101112)
                    
                    # Combine with distance falloff
                    base_height = large_scale + medium_scale + small_scale + ground_detail + micro_detail
                    
                    # Apply coastal height reduction
                    max_distance = size * 0.4
                    if distance_from_center > max_distance * 0.6:
                        falloff = max(0, 1.0 - (distance_from_center - max_distance * 0.6) / (max_distance * 0.4))
                        base_height *= falloff
                    
                    # ENFORCE HEIGHT CONSTRAINTS: 0m to 4000m
                    heightmap[j, i] = max(0, min(4000, base_height))'''
    
    new_terrain_section = '''                    # SMOOTH REALISTIC terrain with gentle slopes
                    distance_from_center = math.sqrt(wx**2 + wy**2)
                    
                    # Base continental elevation (0-800m) - much gentler
                    continental_base = self.fractal_brownian_motion(wx, wy, octaves=3, frequency=0.00001, amplitude=400, seed=42)
                    continental_base = max(0, continental_base * 0.7)  # Reduce amplitude, no negatives
                    
                    # Regional hills (0-300m) - gentle rolling terrain
                    regional_hills = self.fractal_brownian_motion(wx, wy, octaves=4, frequency=0.00005, amplitude=150, seed=123)
                    
                    # Local terrain variation (0-80m) - subtle undulation
                    local_terrain = self.fractal_brownian_motion(wx, wy, octaves=5, frequency=0.0002, amplitude=40, seed=456)
                    
                    # Fine detail (0-20m) - surface variation
                    fine_detail = self.fractal_brownian_motion(wx, wy, octaves=4, frequency=0.001, amplitude=10, seed=789)
                    
                    # Ground micro-detail (0-5m)
                    micro_detail = self.fractal_brownian_motion(wx, wy, octaves=3, frequency=0.005, amplitude=2.5, seed=101112)
                    
                    # Combine scales
                    base_height = continental_base + regional_hills + local_terrain + fine_detail + micro_detail
                    
                    # Apply distance-based height reduction for realistic continental shape
                    max_distance = size * 0.4
                    if distance_from_center > max_distance * 0.5:
                        # Gentler falloff to coast
                        falloff_distance = distance_from_center - max_distance * 0.5
                        max_falloff = max_distance * 0.5
                        falloff = max(0, 1.0 - (falloff_distance / max_falloff) ** 1.5)
                        base_height *= falloff
                    
                    # ENFORCE REALISTIC HEIGHT CONSTRAINTS: 0m to 2000m (much lower!)
                    base_height = max(0, min(2000, base_height))
                    
                    # RARE PEAK GENERATION: Only 1-2 points should reach 2000m
                    # Create very rare, isolated peaks
                    peak_probability = self.fractal_brownian_motion(wx, wy, octaves=2, frequency=0.000005, amplitude=1, seed=999)
                    if peak_probability > 0.95 and base_height > 800:  # Very rare condition
                        # Add extra height for rare peaks
                        peak_bonus = (peak_probability - 0.95) * 20 * 400  # Up to 400m bonus
                        base_height = min(2000, base_height + peak_bonus)
                    
                    heightmap[j, i] = base_height'''
    
    content = content.replace(old_terrain_section, new_terrain_section)
    
    # Remove the ridged mountain generation entirely - it creates too many cliffs
    old_ridged_section = '''        # Phase 5: CONSTRAINED mountain ridge generation (10%)
        yield (0.36, "Adding realistic mountain ranges (max 4km)", 5)
        
        for j in range(resolution):
            for i in range(resolution):
                if coastline_mask[j, i] > 0 and heightmap[j, i] > 200:  # Only on elevated land
                    wx, wy = warped_coords[j, i]
                    current_height = heightmap[j, i]
                    
                    # Add CONSTRAINED ridged mountains
                    current_height = heightmap[j, i]
                    ridge_intensity = min(1.0, current_height / 800.0)  # More ridges at elevation
                    ridges = self.ridged_noise(wx, wy, octaves=3, frequency=0.00006, seed=999) * 400 * ridge_intensity
                    
                    # Apply ridges but maintain 4km height limit
                    new_height = current_height + ridges
                    heightmap[j, i] = max(0, min(4000, new_height))
            
            if j % 25 == 0:
                progress = 0.35 + (0.10 * j / resolution)
                yield (progress, f"Constrained mountains: {j}/{resolution} rows", 5)
        
        yield (0.45, "Realistic mountain generation complete", 5)'''
    
    new_smooth_section = '''        # Phase 5: SMOOTH terrain post-processing (10%)
        yield (0.36, "Applying terrain smoothing for gentle slopes", 5)
        
        # Apply smoothing filter to eliminate sharp transitions
        smoothed_heightmap = heightmap.copy()
        smooth_radius = 2  # Smooth over 2-pixel radius
        
        for j in range(smooth_radius, resolution - smooth_radius):
            for i in range(smooth_radius, resolution - smooth_radius):
                if coastline_mask[j, i] > 0:  # Only smooth land areas
                    # Calculate average height of surrounding area
                    total_height = 0
                    count = 0
                    for dj in range(-smooth_radius, smooth_radius + 1):
                        for di in range(-smooth_radius, smooth_radius + 1):
                            nj, ni = j + dj, i + di
                            if coastline_mask[nj, ni] > 0:  # Only include land points
                                weight = 1.0 / (1.0 + math.sqrt(dj*dj + di*di))  # Distance-weighted
                                total_height += heightmap[nj, ni] * weight
                                count += weight
                    
                    if count > 0:
                        # Blend original height with smoothed average (80% original, 20% smoothed)
                        smoothed_height = total_height / count
                        smoothed_heightmap[j, i] = heightmap[j, i] * 0.8 + smoothed_height * 0.2
            
            if j % 30 == 0:
                progress = 0.35 + (0.10 * j / resolution)
                yield (progress, f"Smoothing terrain: {j}/{resolution} rows", 5)
        
        heightmap = smoothed_heightmap
        yield (0.45, "Gentle slope terrain smoothing complete", 5)'''
    
    content = content.replace(old_ridged_section, new_smooth_section)
    
    # Update height constraints in coloring
    content = content.replace('elif h < 1000:', 'elif h < 600:')
    content = content.replace('elif h < 2000:', 'elif h < 1200:')
    content = content.replace('elif h < 3000:', 'elif h < 1800:')
    content = content.replace('else:  # Above 3000m', 'else:  # Above 1800m (rare peaks)')
    
    # Update statistics
    content = content.replace('Height range: {min_h:.1f}m to {max_h:.1f}m (CONSTRAINED: 0m-4000m)',
                            'Height range: {min_h:.1f}m to {max_h:.1f}m (SMOOTH: 0m-2000m, rare peaks)')
    
    # Update main description
    content = content.replace('print("\\n=== REALISTIC TRAVERSABLE Kent-Sized Terrain ===")',
                            'print("\\n=== SMOOTH REALISTIC Kent-Sized Terrain ===")')
    
    # Add new feature descriptions
    new_features = '''    print("🏔️ REALISTIC MOUNTAIN SYSTEM:")
    print("  • Maximum height: 2,000m (only 1-2 rare peaks)")
    print("  • Gentle slopes - no pseudo sheer cliffs")
    print("  • Terrain smoothing for realistic transitions")
    print("  • Probabilistic peak generation")
    print("  • Rolling hills and valleys")
    print("📷 CAMERA CONTROLS:")
    print("  • 'O' key: Overview mode (25km altitude)")
    print("  • 'R' key: Reset to standard view")
    print("  • Full 59km x 59km map visible from overview")'''
    
    # Insert before the starting message
    content = content.replace('print("\\nStarting ADVANCED terrain generation...")',
                            new_features + '\\n    print("\\nStarting SMOOTH terrain generation...")')
    
    # Write the smooth terrain file
    with open('08.11_terrain_kent_smooth.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Created smooth realistic terrain!")
    print("📷 Added 'O' key for overview camera (25km altitude)")
    print("🏔️ Reduced max height to 2km with rare peaks only")
    print("🌄 Added terrain smoothing for gentle slopes")
    print("🚫 Eliminated cliff-generating ridged noise")

if __name__ == "__main__":
    create_smooth_terrain()
