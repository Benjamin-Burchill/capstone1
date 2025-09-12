#!/usr/bin/env python3
"""
Create a realistic, traversable terrain with proper height constraints
"""

def create_realistic_terrain():
    # Read the base file
    with open('08.09_terrain_kent_advanced.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Update to realistic version
    content = content.replace('08.09_terrain_kent_advanced.py - ADVANCED Multi-Scale Kent-sized terrain',
                            '08.10_terrain_kent_realistic.py - REALISTIC TRAVERSABLE Kent-sized terrain')
    
    content = content.replace('class AdvancedKentTerrain(ShowBase):', 'class RealisticKentTerrain(ShowBase):')
    content = content.replace('app = AdvancedKentTerrain()', 'app = RealisticKentTerrain()')
    
    # Fix the terrain generation section with proper constraints
    old_section = '''                    # Multi-scale terrain generation
                    # Large scale mountains and valleys
                    large_scale = self.fractal_brownian_motion(wx, wy, octaves=6, frequency=0.00003, amplitude=300, seed=42)
                    
                    # Medium scale hills and ridges  
                    medium_scale = self.fractal_brownian_motion(wx, wy, octaves=5, frequency=0.0001, amplitude=150, seed=123)
                    
                    # Small scale detail
                    small_scale = self.fractal_brownian_motion(wx, wy, octaves=4, frequency=0.0005, amplitude=50, seed=456)
                    
                    # Combine scales
                    heightmap[j, i] = large_scale + medium_scale + small_scale'''
    
    new_section = '''                    # REALISTIC Multi-scale terrain with HEIGHT CONSTRAINTS
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
    
    content = content.replace(old_section, new_section)
    
    # Fix ocean depth constraints
    content = content.replace('ocean_depth = -150.0', 'ocean_depth = -200.0  # Realistic ocean depth')
    content = content.replace('depth_variation = self.fractal_brownian_motion(wx, wy, octaves=3, frequency=0.00001, amplitude=50, seed=789)',
                            'depth_variation = self.fractal_brownian_motion(wx, wy, octaves=3, frequency=0.00001, amplitude=80, seed=789)')
    content = content.replace('heightmap[j, i] = ocean_depth + depth_variation',
                            'heightmap[j, i] = min(-5, ocean_depth + depth_variation)  # Keep ocean below sea level')
    
    # Fix ridged mountain generation with constraints
    old_ridges = '''                    # Add ridged mountains
                    ridges = self.ridged_noise(wx, wy, octaves=4, frequency=0.00008, seed=999) * 200
                    heightmap[j, i] += ridges'''
    
    new_ridges = '''                    # Add CONSTRAINED ridged mountains
                    current_height = heightmap[j, i]
                    ridge_intensity = min(1.0, current_height / 800.0)  # More ridges at elevation
                    ridges = self.ridged_noise(wx, wy, octaves=3, frequency=0.00006, seed=999) * 400 * ridge_intensity
                    
                    # Apply ridges but maintain 4km height limit
                    new_height = current_height + ridges
                    heightmap[j, i] = max(0, min(4000, new_height))'''
    
    content = content.replace(old_ridges, new_ridges)
    
    # Update coloring for realistic heights
    old_colors = '''                elif h < 500:
                    r, g, b = 0.6, 0.55, 0.45  # Alpine regions
                else:
                    r, g, b = 0.95, 0.95, 1.0  # Snow peaks'''
    
    new_colors = '''                elif h < 1000:
                    r, g, b = 0.45, 0.4, 0.3   # Mid mountains
                elif h < 2000:
                    r, g, b = 0.55, 0.5, 0.4   # High mountains  
                elif h < 3000:
                    r, g, b = 0.7, 0.65, 0.55  # Alpine regions
                else:  # Above 3000m
                    r, g, b = 0.9, 0.9, 0.95   # Snow peaks'''
    
    content = content.replace(old_colors, new_colors)
    
    # Update main description
    content = content.replace('print("\\n=== ADVANCED Multi-Scale Kent-Sized Terrain ===")',
                            'print("\\n=== REALISTIC TRAVERSABLE Kent-Sized Terrain ===")')
    
    # Write the realistic file
    with open('08.10_terrain_kent_realistic.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Created realistic traversable terrain!")
    print("🌍 Key features:")
    print("  • Heights: 0m (sea level) to 4,000m maximum")
    print("  • 5 levels of detail for ground exploration")
    print("  • No terrain below ground plane")
    print("  • Realistic elevation distribution")
    print("  • Enhanced traversability")

if __name__ == "__main__":
    create_realistic_terrain()
