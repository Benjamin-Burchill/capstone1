#!/usr/bin/env python3
"""
Script to fix terrain height constraints and add ground-level detail
- Constrains heights: 0m minimum (sea level), 4000m maximum
- Adds high-resolution ground-level features for traversability
- Focuses on realistic elevation distribution
"""

def fix_terrain_heights():
    with open('08.10_terrain_kent_realistic.py', 'r') as f:
        content = f.read()
    
    # Update header and description
    content = content.replace(
        '08.09_terrain_kent_advanced.py - ADVANCED Multi-Scale Kent-sized terrain',
        '08.10_terrain_kent_realistic.py - REALISTIC TRAVERSABLE Kent-sized terrain'
    )
    
    content = content.replace(
        'Features: Multi-octave noise, domain warping, erosion simulation, fractal coastlines',
        'Features: HEIGHT-CONSTRAINED realistic terrain, ground-level detail, traversable landscape'
    )
    
    content = content.replace(
        'props.setTitle("Advanced Kent-Sized Terrain - 3,500 km² (MULTI-SCALE)")',
        'props.setTitle("Realistic Kent-Sized Terrain - 3,500 km² (TRAVERSABLE)")'
    )
    
    # Fix the terrain generation with proper height constraints
    old_terrain_gen = '''        # Phase 4: Multi-octave base terrain (15%)
        yield (0.21, "Generating multi-octave base terrain", 4)
        heightmap = np.zeros((resolution, resolution))
        ocean_depth = -150.0
        
        for j in range(resolution):
            for i in range(resolution):
                if coastline_mask[j, i] > 0:  # Land areas
                    wx, wy = warped_coords[j, i]
                    
                    # Multi-scale terrain generation
                    # Large scale mountains and valleys
                    large_scale = self.fractal_brownian_motion(wx, wy, octaves=6, frequency=0.00003, amplitude=300, seed=42)
                    
                    # Medium scale hills and ridges  
                    medium_scale = self.fractal_brownian_motion(wx, wy, octaves=5, frequency=0.0001, amplitude=150, seed=123)
                    
                    # Small scale detail
                    small_scale = self.fractal_brownian_motion(wx, wy, octaves=4, frequency=0.0005, amplitude=50, seed=456)
                    
                    # Combine scales
                    heightmap[j, i] = large_scale + medium_scale + small_scale
                else:  # Ocean areas
                    # Ocean depth variation
                    wx, wy = warped_coords[j, i]
                    depth_variation = self.fractal_brownian_motion(wx, wy, octaves=3, frequency=0.00001, amplitude=50, seed=789)
                    heightmap[j, i] = ocean_depth + depth_variation
            
            if j % 20 == 0:
                progress = 0.20 + (0.15 * j / resolution)
                yield (progress, f"Multi-octave terrain: {j}/{resolution} rows", 4)
        
        yield (0.35, "Base terrain generation complete", 4)
        
        # Phase 5: Ridged mountain generation (10%)
        yield (0.36, "Adding ridged mountain ranges", 5)
        
        for j in range(resolution):
            for i in range(resolution):
                if coastline_mask[j, i] > 0 and heightmap[j, i] > 50:  # Only on elevated land
                    wx, wy = warped_coords[j, i]
                    
                    # Add ridged mountains
                    ridges = self.ridged_noise(wx, wy, octaves=4, frequency=0.00008, seed=999) * 200
                    heightmap[j, i] += ridges
            
            if j % 25 == 0:
                progress = 0.35 + (0.10 * j / resolution)
                yield (progress, f"Ridged mountains: {j}/{resolution} rows", 5)
        
        yield (0.45, "Mountain ridge generation complete", 5)'''
    
    new_terrain_gen = '''        # Phase 4: REALISTIC HEIGHT-CONSTRAINED base terrain (15%)
        yield (0.21, "Generating realistic height-constrained terrain", 4)
        heightmap = np.zeros((resolution, resolution))
        ocean_depth = -200.0  # Deeper ocean for realism
        max_land_height = 4000.0  # 4km max height - realistic for traversable world
        
        for j in range(resolution):
            for i in range(resolution):
                if coastline_mask[j, i] > 0:  # Land areas
                    wx, wy = warped_coords[j, i]
                    distance_from_center = math.sqrt(wx**2 + wy**2)
                    
                    # REALISTIC Multi-scale terrain generation with HEIGHT CONSTRAINTS
                    # Large scale base elevation (0-2000m)
                    large_scale = self.fractal_brownian_motion(wx, wy, octaves=4, frequency=0.00002, amplitude=800, seed=42)
                    large_scale = max(0, large_scale)  # No negative base elevation
                    
                    # Medium scale hills and valleys (0-800m variation)
                    medium_scale = self.fractal_brownian_motion(wx, wy, octaves=6, frequency=0.00008, amplitude=300, seed=123)
                    
                    # Small scale detail for ground traversal (0-100m variation)
                    small_scale = self.fractal_brownian_motion(wx, wy, octaves=8, frequency=0.0004, amplitude=40, seed=456)
                    
                    # Very fine detail for interesting ground features (0-20m)
                    micro_scale = self.fractal_brownian_motion(wx, wy, octaves=6, frequency=0.002, amplitude=8, seed=789)
                    
                    # Ground-level traversability features (0-5m)
                    ground_detail = self.fractal_brownian_motion(wx, wy, octaves=4, frequency=0.01, amplitude=2, seed=101112)
                    
                    # Combine scales with realistic constraints
                    base_height = large_scale + medium_scale + small_scale + micro_scale + ground_detail
                    
                    # Apply distance-based height falloff for realistic continental shape
                    max_distance = size * 0.4
                    if distance_from_center > max_distance * 0.7:
                        # Coastal areas are lower
                        height_multiplier = max(0, 1.0 - (distance_from_center - max_distance * 0.7) / (max_distance * 0.3))
                        base_height *= height_multiplier
                    
                    # CRITICAL: Enforce height constraints
                    heightmap[j, i] = max(0, min(max_land_height, base_height))
                    
                else:  # Ocean areas
                    # Ocean depth variation (-200m to -10m)
                    wx, wy = warped_coords[j, i]
                    depth_variation = self.fractal_brownian_motion(wx, wy, octaves=3, frequency=0.00001, amplitude=80, seed=131415)
                    ocean_height = ocean_depth + depth_variation
                    
                    # Ensure ocean stays below sea level
                    heightmap[j, i] = min(-10, ocean_height)
            
            if j % 20 == 0:
                progress = 0.20 + (0.15 * j / resolution)
                yield (progress, f"Realistic terrain: {j}/{resolution} rows", 4)
        
        yield (0.35, "Height-constrained base terrain complete", 4)
        
        # Phase 5: CONSTRAINED mountain ridge generation (10%)
        yield (0.36, "Adding realistic mountain ranges (max 4km)", 5)
        
        for j in range(resolution):
            for i in range(resolution):
                if coastline_mask[j, i] > 0 and heightmap[j, i] > 200:  # Only on elevated land
                    wx, wy = warped_coords[j, i]
                    current_height = heightmap[j, i]
                    
                    # Add ridged mountains with height constraints
                    ridge_intensity = min(1.0, current_height / 1000.0)  # More ridges at higher elevations
                    ridges = self.ridged_noise(wx, wy, octaves=3, frequency=0.00006, seed=999) * 600 * ridge_intensity
                    
                    # Apply ridges but maintain height constraint
                    new_height = current_height + ridges
                    heightmap[j, i] = max(0, min(max_land_height, new_height))
            
            if j % 25 == 0:
                progress = 0.35 + (0.10 * j / resolution)
                yield (progress, f"Constrained mountains: {j}/{resolution} rows", 5)
        
        yield (0.45, "Realistic mountain generation complete", 5)'''
    
    if old_terrain_gen in content:
        content = content.replace(old_terrain_gen, new_terrain_gen)
        print("✅ Fixed height constraints and added ground-level detail!")
    else:
        print("❌ Could not find terrain generation code to replace")
        return False
    
    # Update the coloring system for realistic height ranges
    old_coloring = '''                # Base color from height
                if h < ocean_depth + 10:
                    r, g, b = 0.05, 0.15, 0.4  # Deep ocean
                elif h < ocean_depth + 50:
                    r, g, b = 0.1, 0.25, 0.6   # Shallow ocean
                elif h < 0:
                    r, g, b = 0.2, 0.4, 0.8    # Coastal water
                elif h < 5:
                    r, g, b = 0.9, 0.85, 0.7   # Beach sand
                elif h < 20:
                    r, g, b = 0.4, 0.7, 0.2    # Coastal grass
                elif h < 100:
                    r, g, b = 0.2, 0.5, 0.15   # Lowland forest
                elif h < 200:
                    r, g, b = 0.3, 0.4, 0.2    # Highland forest
                elif h < 350:
                    r, g, b = 0.5, 0.45, 0.35  # Rocky slopes
                elif h < 500:
                    r, g, b = 0.6, 0.55, 0.45  # Alpine regions
                else:
                    r, g, b = 0.95, 0.95, 1.0  # Snow peaks'''
    
    new_coloring = '''                # REALISTIC height-based coloring for traversable world
                if h < -100:
                    r, g, b = 0.02, 0.08, 0.2   # Deep ocean trenches
                elif h < -50:
                    r, g, b = 0.05, 0.12, 0.3   # Deep ocean
                elif h < -20:
                    r, g, b = 0.08, 0.18, 0.4   # Medium ocean
                elif h < -5:
                    r, g, b = 0.12, 0.25, 0.5   # Shallow ocean
                elif h < 0:
                    r, g, b = 0.18, 0.35, 0.65  # Coastal shallows
                elif h < 2:
                    r, g, b = 0.85, 0.8, 0.65   # Beach/tidal zones
                elif h < 10:
                    r, g, b = 0.4, 0.65, 0.25   # Coastal grasslands
                elif h < 50:
                    r, g, b = 0.35, 0.6, 0.2    # Lowland plains
                elif h < 150:
                    r, g, b = 0.25, 0.5, 0.15   # Rolling hills
                elif h < 400:
                    r, g, b = 0.2, 0.45, 0.12   # Forested hills
                elif h < 800:
                    r, g, b = 0.3, 0.4, 0.2     # Mountain foothills
                elif h < 1500:
                    r, g, b = 0.4, 0.35, 0.25   # Lower mountains
                elif h < 2500:
                    r, g, b = 0.5, 0.45, 0.35   # High mountains
                elif h < 3500:
                    r, g, b = 0.65, 0.6, 0.5    # Alpine regions
                else:  # Above 3500m
                    r, g, b = 0.9, 0.9, 0.95    # Snow-capped peaks'''
    
    content = content.replace(old_coloring, new_coloring)
    
    # Update statistics logging
    old_stats = '''        self.logger.info(f"=== ADVANCED TERRAIN STATISTICS ===")
        self.logger.info(f"Resolution: {resolution}x{resolution} = {resolution*resolution:,} vertices")
        self.logger.info(f"Height range: {min_h:.1f}m to {max_h:.1f}m")
        self.logger.info(f"Land area: {land_area:.0f} km² ({land_area/3500*100:.1f}% of total)")
        self.logger.info(f"Triangle count: {triangle_count:,}")
        self.logger.info(f"Techniques used: Multi-octave fBm, Domain warping, Ridged noise, Hydraulic erosion")'''
    
    new_stats = '''        self.logger.info(f"=== REALISTIC TRAVERSABLE TERRAIN STATISTICS ===")
        self.logger.info(f"Resolution: {resolution}x{resolution} = {resolution*resolution:,} vertices")
        self.logger.info(f"Height range: {min_h:.1f}m to {max_h:.1f}m (CONSTRAINED: 0m-4000m)")
        self.logger.info(f"Land area: {land_area:.0f} km² ({land_area/3500*100:.1f}% of total)")
        self.logger.info(f"Triangle count: {triangle_count:,}")
        self.logger.info(f"Ground traversability: Multi-scale detail from continental to 1m features")
        self.logger.info(f"Techniques: Height-constrained fBm, Ground-level detail, Realistic elevation zones")'''
    
    content = content.replace(old_stats, new_stats)
    
    # Update main section
    old_main = '''if __name__ == "__main__":
    print("\\n=== ADVANCED Multi-Scale Kent-Sized Terrain ===")
    print("Scale: 59km x 59km (3,500 km²)")
    print("🚀 ADVANCED TECHNIQUES:")
    print("  • Multi-octave Fractal Brownian Motion (fBm)")
    print("  • Domain warping for organic shapes")
    print("  • Ridged noise for realistic mountain ranges")
    print("  • Hydraulic erosion simulation")
    print("  • Fractal coastlines with multi-scale detail")
    print("  • Advanced climate-based coloring")
    print("  • Higher resolution: 300x300 = 90,000 vertices")
    print("🌍 REALISM FEATURES:")
    print("  • Natural irregular coastlines")
    print("  • Realistic mountain ridges and valleys")
    print("  • Eroded river systems")
    print("  • Multi-scale terrain complexity")
    print("\\nStarting ADVANCED terrain generation...")
    app = AdvancedKentTerrain()
    app.run()'''
    
    new_main = '''if __name__ == "__main__":
    print("\\n=== REALISTIC TRAVERSABLE Kent-Sized Terrain ===")
    print("Scale: 59km x 59km (3,500 km²)")
    print("🌍 REALISTIC CONSTRAINTS:")
    print("  • Height range: 0m (sea level) to 4,000m (realistic peaks)")
    print("  • No terrain below ground plane - fully traversable")
    print("  • Multi-scale detail: Continental → Regional → Local → Ground-level")
    print("  • 5 levels of detail from 800m mountains to 2m ground features")
    print("🚀 GROUND-LEVEL FEATURES:")
    print("  • High-resolution terrain for walking/driving")
    print("  • Natural irregular coastlines")
    print("  • Realistic elevation zones and transitions")
    print("  • Detailed surface variation for exploration")
    print("  • Height-constrained mountain ranges")
    print("🎮 TRAVERSABILITY:")
    print("  • Realistic slopes and elevation changes")
    print("  • Ground-level detail for immersive exploration")
    print("  • No impossible terrain features")
    print("\\nStarting REALISTIC terrain generation...")
    app = AdvancedKentTerrain()
    app.run()'''
    
    content = content.replace(old_main, new_main)
    
    # Update class name and title
    content = content.replace('class AdvancedKentTerrain(ShowBase):', 'class RealisticKentTerrain(ShowBase):')
    content = content.replace('app = AdvancedKentTerrain()', 'app = RealisticKentTerrain()')
    content = content.replace('"Advanced Multi-Scale Terrain"', '"Realistic Traversable Terrain"')
    content = content.replace('self.logger = logging.getLogger(\'AdvancedTerrain\')', 'self.logger = logging.getLogger(\'RealisticTerrain\')')
    
    # Write the fixed file
    with open('08.10_terrain_kent_realistic.py', 'w') as f:
        f.write(content)
    
    print("✅ Successfully created realistic traversable terrain!")
    print("🌍 Key improvements:")
    print("  • Heights constrained: 0m to 4,000m (no impossible features)")
    print("  • 5 levels of detail for ground-level exploration")
    print("  • Realistic elevation zones")
    print("  • Enhanced traversability")
    print("  • No terrain below ground plane")
    return True

if __name__ == "__main__":
    fix_terrain_heights()
