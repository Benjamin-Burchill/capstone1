"""
08.02_terrain_numpy_random.py - Enhanced terrain with NumPy randomness and controlled variation
Features: Increasing mountain spacing, partial randomness with limit ratios
"""

from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    WindowProperties, Point3,
    GeomNode, GeomTriangles, Geom,
    GeomVertexFormat, GeomVertexData, GeomVertexWriter,
    AmbientLight, DirectionalLight
)
from direct.task import Task
import numpy as np
import math

class NumpyRandomTerrain(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        
        # Window setup
        props = WindowProperties()
        props.setTitle("NumPy Random Terrain - Controlled Variation")
        self.win.requestProperties(props)
        
        # Sky color
        self.setBackgroundColor(0.45, 0.55, 0.75, 1)
        
        # Generate terrain
        print("Generating NumPy-enhanced terrain...")
        self.terrain = self.create_numpy_terrain()
        print("Terrain complete!")
        
        # Camera setup
        self.camera_pos = Point3(0, -50, 25)
        self.camera.setPos(self.camera_pos)
        self.camera.lookAt(0, 0, 5)
        
        # Movement
        self.keys = {"w": False, "s": False, "a": False, "d": False,
                     "space": False, "shift": False, "q": False, "e": False}
        self.speed = 20.0
        
        for key in self.keys:
            self.accept(key, self.set_key, [key, True])
            self.accept(f"{key}-up", self.set_key, [key, False])
        self.accept("escape", self.userExit)
        self.accept("r", self.reset_camera)
        
        self.taskMgr.add(self.move_task, "move")
        
        # Lighting
        alight = AmbientLight('ambient')
        alight.setColor((0.5, 0.5, 0.55, 1))
        alnp = self.render.attachNewNode(alight)
        self.render.setLight(alnp)
        
        sun = DirectionalLight('sun')
        sun.setColor((0.6, 0.55, 0.5, 1))
        sun_np = self.render.attachNewNode(sun)
        sun_np.setHpr(-45, -60, 0)
        self.render.setLight(sun_np)
        
        # UI
        from direct.gui.OnscreenText import OnscreenText
        
        self.title = OnscreenText(
            text="NumPy Random Terrain - Controlled Features",
            pos=(0, 0.95), scale=0.045, fg=(1, 1, 1, 1)
        )
        
        self.controls = OnscreenText(
            text="WASD: Move | Q/E: Rotate | Space/Shift: Up/Down | R: Reset | ESC: Exit",
            pos=(0, 0.89), scale=0.038, fg=(0.9, 0.9, 0.9, 1)
        )
        
        self.pos_text = OnscreenText(
            text="Position: (0.0, -50.0, 25.0)",
            pos=(0, -0.95), scale=0.04,
            fg=(1, 1, 0, 1), mayChange=True
        )
        
        self.info = OnscreenText(
            text="Features: Variable ridge spacing | Controlled randomness | Height limits",
            pos=(0, -0.89), scale=0.035, fg=(0.8, 0.8, 0.8, 1)
        )
    
    def create_numpy_terrain(self):
        """Create terrain with NumPy-based controlled randomness"""
        
        # Parameters
        size = 100
        resolution = 60
        
        # Feature control parameters (limit ratios)
        MIN_RIDGE_HEIGHT = 3.0
        MAX_RIDGE_HEIGHT = 12.0
        MIN_VALLEY_DEPTH = 0.2  # Ratio of ridge height
        MAX_VALLEY_DEPTH = 0.6
        MIN_RIDGE_SPACING = 10.0
        MAX_RIDGE_SPACING = 30.0
        NOISE_AMPLITUDE_RATIO = 0.3  # Max 30% of base height
        
        # Set random seed for reproducibility
        np.random.seed(42)
        
        # Create coordinate grids
        x = np.linspace(-size/2, size/2, resolution)
        y = np.linspace(-size/2, size/2, resolution)
        X, Y = np.meshgrid(x, y)
        
        # Initialize heightmap
        heightmap = np.zeros((resolution, resolution))
        
        # 1. PRIMARY RIDGES with increasing spacing
        # Ridge spacing increases as we move away from center
        distance_from_center = np.sqrt(X**2 + Y**2)
        ridge_spacing = MIN_RIDGE_SPACING + (distance_from_center / (size/2)) * (MAX_RIDGE_SPACING - MIN_RIDGE_SPACING)
        
        # Rotate for Appalachian orientation (30 degrees)
        angle = np.radians(30)
        X_rot = X * np.cos(angle) - Y * np.sin(angle)
        Y_rot = X * np.sin(angle) + Y * np.cos(angle)
        
        # Variable ridge heights
        ridge_height_variation = np.random.uniform(MIN_RIDGE_HEIGHT, MAX_RIDGE_HEIGHT, (resolution, resolution))
        
        # Create ridges with variable spacing
        ridge_pattern = np.zeros_like(X)
        for i in range(resolution):
            for j in range(resolution):
                local_spacing = ridge_spacing[i, j]
                ridge_pattern[i, j] = np.cos(X_rot[i, j] / local_spacing * 2 * np.pi)
        
        # Apply ridge pattern with height variation
        ridges = ridge_height_variation * (0.5 + 0.5 * ridge_pattern)
        heightmap += ridges
        
        # 2. VALLEYS with controlled depth
        valley_depth = np.random.uniform(MIN_VALLEY_DEPTH, MAX_VALLEY_DEPTH, (resolution, resolution))
        valley_mask = np.sin(X_rot / ridge_spacing * np.pi)
        valley_areas = valley_mask < -0.3
        heightmap[valley_areas] *= valley_depth[valley_areas]
        
        # 3. PERLIN-LIKE NOISE using NumPy
        # Generate multiple octaves of noise
        octaves = 4
        persistence = 0.5
        total_amplitude = 0
        
        for octave in range(octaves):
            frequency = 2 ** octave
            amplitude = persistence ** octave
            
            # Generate random gradients
            grid_size = int(resolution / (10 / frequency)) + 2
            gradients_x = np.random.randn(grid_size, grid_size)
            gradients_y = np.random.randn(grid_size, grid_size)
            
            # Interpolate to full resolution (simplified)
            from scipy.ndimage import zoom
            noise_x = zoom(gradients_x, resolution/grid_size, order=3)[:resolution, :resolution]
            noise_y = zoom(gradients_y, resolution/grid_size, order=3)[:resolution, :resolution]
            
            # Combine gradients
            noise = noise_x * np.cos(X * frequency * 0.1) + noise_y * np.sin(Y * frequency * 0.1)
            heightmap += noise * amplitude * 3
            total_amplitude += amplitude
        
        # Normalize noise contribution
        heightmap /= (1 + total_amplitude)
        
        # 4. SECONDARY FEATURES with limits
        # Cross-ridges (perpendicular variation)
        cross_ridges = 2.0 * np.sin(Y_rot * 0.05) * np.cos(Y_rot * 0.03)
        heightmap += cross_ridges
        
        # Small-scale bumps
        bumps = np.random.randn(resolution, resolution) * 0.5
        from scipy.ndimage import gaussian_filter
        bumps = gaussian_filter(bumps, sigma=1.0)
        heightmap += bumps
        
        # 5. EROSION SIMULATION (simple)
        # Smooth steep areas
        for _ in range(3):
            heightmap = gaussian_filter(heightmap, sigma=0.5)
        
        # 6. ENFORCE HEIGHT LIMITS
        # Clip to reasonable range
        heightmap = np.clip(heightmap, 0, MAX_RIDGE_HEIGHT * 1.2)
        
        # Add base elevation
        base_elevation = 2.0
        heightmap += base_elevation
        
        # Get final height range
        min_h = np.min(heightmap)
        max_h = np.max(heightmap)
        print(f"Final height range: {min_h:.1f} to {max_h:.1f}")
        print(f"Average ridge spacing: {np.mean(ridge_spacing):.1f}")
        
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
                # Position
                vertex.addData3(x[i], y[j], heightmap[j, i])
                
                # Normal calculation
                nx, ny, nz = 0, 0, 1
                if i > 0 and i < resolution-1 and j > 0 and j < resolution-1:
                    dzdx = (heightmap[j, i+1] - heightmap[j, i-1]) / (2.0 * size / resolution)
                    dzdy = (heightmap[j+1, i] - heightmap[j-1, i]) / (2.0 * size / resolution)
                    nx = -dzdx
                    ny = -dzdy
                    nz = 1.0
                    length = math.sqrt(nx*nx + ny*ny + nz*nz)
                    nx /= length
                    ny /= length
                    nz /= length
                normal.addData3(nx, ny, nz)
                
                # Height-based coloring with smooth transitions
                h_norm = (heightmap[j, i] - min_h) / (max_h - min_h + 0.001)
                
                # Color zones
                if h_norm < 0.15:  # Deep valley - dark green
                    r, g, b = 0.05, 0.2, 0.05
                elif h_norm < 0.3:  # Valley - green
                    t = (h_norm - 0.15) / 0.15
                    r = 0.05 + t * 0.1
                    g = 0.2 + t * 0.2
                    b = 0.05 + t * 0.05
                elif h_norm < 0.45:  # Lower slopes - yellow-green
                    t = (h_norm - 0.3) / 0.15
                    r = 0.15 + t * 0.25
                    g = 0.4 - t * 0.1
                    b = 0.1 + t * 0.1
                elif h_norm < 0.6:  # Mid slopes - brown
                    t = (h_norm - 0.45) / 0.15
                    r = 0.4 + t * 0.1
                    g = 0.3 - t * 0.05
                    b = 0.2
                elif h_norm < 0.75:  # Upper slopes - gray-brown
                    t = (h_norm - 0.6) / 0.15
                    r = 0.5 + t * 0.15
                    g = 0.25 + t * 0.25
                    b = 0.2 + t * 0.3
                elif h_norm < 0.9:  # High elevation - gray
                    t = (h_norm - 0.75) / 0.15
                    r = 0.65 + t * 0.15
                    g = 0.5 + t * 0.2
                    b = 0.5 + t * 0.2
                else:  # Snow cap - white
                    t = (h_norm - 0.9) / 0.1
                    r = 0.8 + t * 0.2
                    g = 0.7 + t * 0.3
                    b = 0.7 + t * 0.3
                
                # Add subtle noise to color
                color_noise = (np.random.random() - 0.5) * 0.05
                r = np.clip(r + color_noise, 0, 1)
                g = np.clip(g + color_noise, 0, 1)
                b = np.clip(b + color_noise, 0, 1)
                
                color.addData4(r, g, b, 1.0)
        
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
    
    def reset_camera(self):
        self.camera_pos = Point3(0, -50, 25)
        self.camera.setPos(self.camera_pos)
        self.camera.lookAt(0, 0, 5)
    
    def move_task(self, task):
        dt = 0.016
        
        if self.keys["w"]:
            self.camera_pos.y += self.speed * dt
        if self.keys["s"]:
            self.camera_pos.y -= self.speed * dt
        if self.keys["a"]:
            self.camera_pos.x -= self.speed * dt
        if self.keys["d"]:
            self.camera_pos.x += self.speed * dt
        if self.keys["space"]:
            self.camera_pos.z += self.speed * dt
        if self.keys["shift"]:
            self.camera_pos.z -= self.speed * dt
        
        if self.keys["q"]:
            h = self.camera.getH()
            self.camera.setH(h + 30 * dt)
        if self.keys["e"]:
            h = self.camera.getH()
            self.camera.setH(h - 30 * dt)
        
        self.camera.setPos(self.camera_pos)
        
        self.pos_text.setText(
            f"Position: ({self.camera_pos.x:.1f}, {self.camera_pos.y:.1f}, {self.camera_pos.z:.1f})"
        )
        
        return Task.cont

if __name__ == "__main__":
    print("\n=== NumPy Random Terrain Generation ===")
    print("Features:")
    print("- Ridge spacing increases with distance from center")
    print("- Controlled randomness with limit ratios")
    print("- Height limits: 3-12 units for ridges")
    print("- Valley depth: 20-60% of ridge height")
    print("- Noise amplitude: max 30% of base height")
    print("- 7 distinct color zones")
    app = NumpyRandomTerrain()
    app.run()

