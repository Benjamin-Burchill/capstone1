"""
08.04_terrain_island.py - Massive island terrain with ocean, bays, and varied geography
20x larger scale with diverse landscape features
"""

from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    WindowProperties, Point3, Vec3,
    GeomNode, GeomTriangles, Geom,
    GeomVertexFormat, GeomVertexData, GeomVertexWriter,
    AmbientLight, DirectionalLight, Fog
)
from direct.task import Task
import numpy as np
import math

class IslandTerrain(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        
        # Window setup
        props = WindowProperties()
        props.setTitle("Massive Island Terrain - 20x Scale")
        self.win.requestProperties(props)
        
        # Sky color (ocean atmosphere)
        self.setBackgroundColor(0.4, 0.5, 0.7, 1)
        
        # Generate massive terrain
        print("Generating massive island terrain...")
        print("This may take a moment due to the large scale...")
        self.terrain = self.create_island_terrain()
        print("Island terrain ready!")
        
        # Camera state management
        self.camera_pos = Point3(0, -200, 100)  # Start high up to see the island
        self.camera_hpr = Vec3(0, -20, 0)  # Look down slightly
        
        # Apply initial camera state
        self.camera.setPos(self.camera_pos)
        self.camera.setHpr(self.camera_hpr)
        
        # Movement controls (faster for large terrain)
        self.keys = {
            "w": False, "s": False, "a": False, "d": False,
            "space": False, "shift": False, "q": False, "e": False,
            "up": False, "down": False
        }
        self.move_speed = 50.0  # Much faster for large terrain
        self.fast_speed = 200.0  # Hold shift for fast movement
        self.rotate_speed = 45.0
        
        # Key bindings
        for key in self.keys:
            self.accept(key, self.set_key, [key, True])
            self.accept(f"{key}-up", self.set_key, [key, False])
        
        # Arrow keys for pitch control
        self.accept("arrow_up", self.set_key, ["up", True])
        self.accept("arrow_up-up", self.set_key, ["up", False])
        self.accept("arrow_down", self.set_key, ["down", True])
        self.accept("arrow_down-up", self.set_key, ["down", False])
        
        self.accept("escape", self.userExit)
        self.accept("r", self.reset_camera)
        self.accept("f", self.toggle_fast_mode)
        
        self.fast_mode = False
        
        self.taskMgr.add(self.update_camera, "update_camera")
        
        # Lighting for ocean scene
        alight = AmbientLight('alight')
        alight.setColor((0.4, 0.45, 0.5, 1))
        alnp = self.render.attachNewNode(alight)
        self.render.setLight(alnp)
        
        sun = DirectionalLight('sun')
        sun.setColor((0.7, 0.65, 0.6, 1))
        sun_np = self.render.attachNewNode(sun)
        sun_np.setHpr(-45, -60, 0)
        self.render.setLight(sun_np)
        
        # Add fog for distance effect
        fog = Fog("fog")
        fog.setColor(0.6, 0.7, 0.8)
        fog.setExpDensity(0.0008)  # Very light fog for distance
        self.render.setFog(fog)
        
        # UI Elements
        from direct.gui.OnscreenText import OnscreenText
        
        self.title = OnscreenText(
            text="Massive Island Terrain (20x Scale)",
            pos=(0, 0.95), scale=0.045, fg=(1, 1, 1, 1)
        )
        
        self.controls = OnscreenText(
            text="WASD: Move | Q/E: Yaw | Arrows: Pitch | Space/Shift: Up/Down | F: Fast mode | R: Reset",
            pos=(0, 0.89), scale=0.038, fg=(0.9, 0.9, 0.9, 1)
        )
        
        self.state_text = OnscreenText(
            text="",
            pos=(0, -0.95), scale=0.04,
            fg=(1, 1, 0, 1), mayChange=True
        )
        
        self.info_text = OnscreenText(
            text="Features: Ocean, Island, Mountains, Flatlands, Bays, Beaches",
            pos=(0, -0.89), scale=0.035,
            fg=(0.8, 0.8, 0.8, 1)
        )
    
    def create_island_terrain(self):
        """Create massive island terrain with ocean"""
        
        # MASSIVE scale parameters
        size = 1600  # 20x larger (was 80)
        resolution = 120  # Higher resolution for detail
        
        # Set random seed
        np.random.seed(42)
        
        # Create coordinate arrays
        x = np.linspace(-size/2, size/2, resolution)
        y = np.linspace(-size/2, size/2, resolution)
        X, Y = np.meshgrid(x, y)
        
        # Distance from center
        distance_from_center = np.sqrt(X**2 + Y**2)
        max_distance = size / 2
        
        # 1. ISLAND SHAPE (using multiple methods for interesting coastline)
        # Main island body (elliptical with noise)
        island_radius_x = size * 0.35  # Island takes up ~70% of map width
        island_radius_y = size * 0.25  # Slightly elongated
        
        # Rotate island slightly
        angle = np.radians(20)
        X_rot = X * np.cos(angle) - Y * np.sin(angle)
        Y_rot = X * np.sin(angle) + Y * np.cos(angle)
        
        # Island mask with irregular coastline
        island_base = 1.0 - np.sqrt((X_rot/island_radius_x)**2 + (Y_rot/island_radius_y)**2)
        
        # Add coastal variation for bays and peninsulas
        coastal_noise = (
            np.sin(np.arctan2(Y, X) * 5) * 0.15 +  # Major bays
            np.sin(np.arctan2(Y, X) * 11) * 0.08 +  # Smaller inlets
            np.sin(np.arctan2(Y, X) * 23) * 0.04    # Fine detail
        )
        
        island_mask = island_base + coastal_noise
        island_mask = np.clip(island_mask, 0, 1)
        
        # Smooth transition from ocean to land
        island_mask = np.power(island_mask, 0.5)  # Sharper coastline
        
        # 2. BASE ELEVATION
        # Ocean depth
        ocean_depth = -20.0
        heightmap = np.ones((resolution, resolution)) * ocean_depth
        
        # Island elevation based on distance from edge
        island_elevation = island_mask * 40  # Max elevation 40 units
        
        # 3. TERRAIN FEATURES
        
        # Central mountains (higher in center of island)
        mountain_mask = np.maximum(0, island_mask - 0.3) / 0.7
        mountains = mountain_mask * 60 * (1 - distance_from_center / max_distance)
        
        # Ridge system (Appalachian style but adapted for island)
        ridge_spacing = 80.0
        ridges = 15 * np.sin(X_rot / ridge_spacing * 2 * np.pi) * mountain_mask
        ridges += 10 * np.cos(Y_rot / (ridge_spacing * 1.5) * 2 * np.pi) * mountain_mask
        
        # Flatlands (plateaus)
        flatland_areas = (np.sin(X * 0.003) * np.sin(Y * 0.003) > 0.3) & (island_mask > 0.5)
        
        # Valleys
        valley_pattern = np.sin(X_rot / 60) * np.cos(Y_rot / 60)
        valleys = valley_pattern * 10 * island_mask
        
        # 4. COMBINE FEATURES
        heightmap = ocean_depth * (1 - island_mask) + island_elevation
        heightmap += mountains
        heightmap += ridges
        heightmap += valleys
        
        # Apply flatlands (smooth out certain areas)
        heightmap[flatland_areas] = np.mean(heightmap[flatland_areas])
        
        # 5. BEACHES AND COASTAL FEATURES
        # Create beach zones (low elevation near water)
        beach_zone = (island_mask > 0.05) & (island_mask < 0.3)
        heightmap[beach_zone] = ocean_depth + (heightmap[beach_zone] - ocean_depth) * 0.2
        
        # 6. ADD DETAIL NOISE
        # Large scale features
        noise_large = np.random.randn(resolution, resolution) * 3
        # Smooth it
        from scipy.ndimage import gaussian_filter
        try:
            noise_large = gaussian_filter(noise_large, sigma=2)
        except ImportError:
            # Simple smoothing if scipy not available
            for _ in range(3):
                noise_smooth = np.zeros_like(noise_large)
                noise_smooth[1:-1, 1:-1] = (
                    noise_large[1:-1, 1:-1] * 0.4 +
                    noise_large[:-2, 1:-1] * 0.15 +
                    noise_large[2:, 1:-1] * 0.15 +
                    noise_large[1:-1, :-2] * 0.15 +
                    noise_large[1:-1, 2:] * 0.15
                )
                noise_large = noise_smooth
        
        heightmap += noise_large * island_mask
        
        # Small scale texture
        noise_small = np.random.randn(resolution, resolution) * 0.5
        heightmap += noise_small * island_mask
        
        # 7. ENSURE OCEAN IS FLAT FAR FROM ISLAND
        far_ocean = distance_from_center > size * 0.45
        heightmap[far_ocean] = ocean_depth
        
        # Get height range
        min_h = np.min(heightmap)
        max_h = np.max(heightmap)
        print(f"Height range: {min_h:.1f} to {max_h:.1f}")
        print(f"Island size: ~{int(island_radius_x*2)}x{int(island_radius_y*2)} units")
        
        # CREATE MESH
        vformat = GeomVertexFormat.getV3n3c4()
        vdata = GeomVertexData('terrain', vformat, Geom.UHStatic)
        vdata.setNumRows(resolution * resolution)
        
        vertex = GeomVertexWriter(vdata, 'vertex')
        normal = GeomVertexWriter(vdata, 'normal')
        color = GeomVertexWriter(vdata, 'color')
        
        # Generate vertices
        for j in range(resolution):
            for i in range(resolution):
                h = heightmap[j, i]
                
                # Position
                vertex.addData3(x[i], y[j], h)
                
                # Simple normal (will update later)
                normal.addData3(0, 0, 1)
                
                # Color based on height and terrain type
                if h < ocean_depth + 1:  # Deep ocean
                    r, g, b = 0.1, 0.2, 0.4
                elif h < ocean_depth + 3:  # Shallow ocean
                    r, g, b = 0.15, 0.3, 0.5
                elif h < 0:  # Very shallow water/beach
                    r, g, b = 0.2, 0.4, 0.6
                elif h < 2:  # Beach sand
                    r, g, b = 0.8, 0.7, 0.5
                elif h < 5:  # Coastal grass
                    r, g, b = 0.3, 0.5, 0.2
                elif h < 15:  # Lowland forest
                    r, g, b = 0.2, 0.4, 0.15
                elif h < 25:  # Highland forest
                    r, g, b = 0.25, 0.35, 0.15
                elif h < 35:  # Mountain slopes
                    r, g, b = 0.4, 0.35, 0.3
                elif h < 45:  # High mountain
                    r, g, b = 0.5, 0.45, 0.4
                else:  # Snow cap
                    r, g, b = 0.9, 0.9, 0.95
                
                # Add variation
                variation = (np.random.random() - 0.5) * 0.05
                r = np.clip(r + variation, 0, 1)
                g = np.clip(g + variation, 0, 1)
                b = np.clip(b + variation, 0, 1)
                
                color.addData4(r, g, b, 1.0)
        
        # Calculate normals
        for j in range(resolution):
            for i in range(resolution):
                idx = j * resolution + i
                
                if i > 0 and i < resolution-1 and j > 0 and j < resolution-1:
                    h_center = heightmap[j, i]
                    h_left = heightmap[j, i-1]
                    h_right = heightmap[j, i+1]
                    h_down = heightmap[j-1, i]
                    h_up = heightmap[j+1, i]
                    
                    dx = (h_right - h_left) / (2.0 * size / resolution)
                    dy = (h_up - h_down) / (2.0 * size / resolution)
                    
                    nx = -dx
                    ny = -dy
                    nz = 1.0
                    length = math.sqrt(nx*nx + ny*ny + nz*nz)
                    
                    normal.setRow(idx)
                    normal.setData3(nx/length, ny/length, nz/length)
        
        # Create geometry
        geom = Geom(vdata)
        
        # Create triangles
        for j in range(resolution - 1):
            for i in range(resolution - 1):
                v0 = j * resolution + i
                v1 = v0 + 1
                v2 = v0 + resolution
                v3 = v2 + 1
                
                prim = GeomTriangles(Geom.UHStatic)
                prim.addVertices(v0, v2, v1)
                prim.addVertices(v1, v2, v3)
                prim.closePrimitive()
                geom.addPrimitive(prim)
        
        # Create node
        node = GeomNode('terrain')
        node.addGeom(geom)
        terrain_np = self.render.attachNewNode(node)
        terrain_np.setTwoSided(True)
        
        return terrain_np
    
    def set_key(self, key, value):
        self.keys[key] = value
    
    def toggle_fast_mode(self):
        self.fast_mode = not self.fast_mode
        speed_text = "FAST" if self.fast_mode else "NORMAL"
        print(f"Movement speed: {speed_text}")
    
    def reset_camera(self):
        self.camera_pos = Point3(0, -200, 100)
        self.camera_hpr = Vec3(0, -20, 0)
        self.camera.setPos(self.camera_pos)
        self.camera.setHpr(self.camera_hpr)
        print("Camera reset to overview position")
    
    def update_camera(self, task):
        dt = 0.016
        
        # Choose speed based on mode
        speed = self.fast_speed if self.fast_mode else self.move_speed
        
        # Get camera forward direction
        heading_rad = math.radians(self.camera_hpr.x)
        pitch_rad = math.radians(self.camera_hpr.y)
        
        # Calculate forward vector
        forward_x = math.sin(heading_rad) * math.cos(pitch_rad)
        forward_y = math.cos(heading_rad) * math.cos(pitch_rad)
        forward_z = -math.sin(pitch_rad)
        
        # Calculate right vector
        right_x = math.cos(heading_rad)
        right_y = -math.sin(heading_rad)
        
        # POSITION UPDATES (relative to camera orientation)
        if self.keys["w"]:  # Forward
            self.camera_pos.x += forward_x * speed * dt
            self.camera_pos.y += forward_y * speed * dt
            self.camera_pos.z += forward_z * speed * dt
        if self.keys["s"]:  # Backward
            self.camera_pos.x -= forward_x * speed * dt
            self.camera_pos.y -= forward_y * speed * dt
            self.camera_pos.z -= forward_z * speed * dt
        if self.keys["a"]:  # Strafe left
            self.camera_pos.x -= right_x * speed * dt
            self.camera_pos.y -= right_y * speed * dt
        if self.keys["d"]:  # Strafe right
            self.camera_pos.x += right_x * speed * dt
            self.camera_pos.y += right_y * speed * dt
        if self.keys["space"]:  # Up
            self.camera_pos.z += speed * dt
        if self.keys["shift"]:  # Down
            self.camera_pos.z -= speed * dt
        
        # ROTATION UPDATES
        if self.keys["q"]:
            self.camera_hpr.x += self.rotate_speed * dt
        if self.keys["e"]:
            self.camera_hpr.x -= self.rotate_speed * dt
        if self.keys["up"]:
            self.camera_hpr.y = max(-89, self.camera_hpr.y - self.rotate_speed * dt)
        if self.keys["down"]:
            self.camera_hpr.y = min(89, self.camera_hpr.y + self.rotate_speed * dt)
        
        # Apply states
        self.camera.setPos(self.camera_pos)
        self.camera.setHpr(self.camera_hpr)
        
        # Update display
        mode = "FAST" if self.fast_mode else "NORM"
        self.state_text.setText(
            f"Pos: ({self.camera_pos.x:.0f}, {self.camera_pos.y:.0f}, {self.camera_pos.z:.0f}) | "
            f"H: {self.camera_hpr.x:.0f}° P: {self.camera_hpr.y:.0f}° | Mode: {mode}"
        )
        
        return Task.cont

if __name__ == "__main__":
    print("\n=== Massive Island Terrain ===")
    print("Scale: 1600x1600 units (20x larger)")
    print("Features:")
    print("- Large central island with irregular coastline")
    print("- Ocean surrounding the island")
    print("- Mountains in island center")
    print("- Flatlands and plateaus")
    print("- Bays and beaches")
    print("- Multiple elevation zones with distinct colors")
    print("\nControls:")
    print("- F: Toggle fast movement mode")
    print("- Arrow keys: Control camera pitch")
    app = IslandTerrain()
    app.run()

