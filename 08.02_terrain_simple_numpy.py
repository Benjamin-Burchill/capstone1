"""
08.02_terrain_simple_numpy.py - Simple NumPy enhancements to working terrain
Incremental improvements without scipy dependency
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

class SimpleNumpyTerrain(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        
        # Window setup
        props = WindowProperties()
        props.setTitle("Simple NumPy Terrain - Incremental Improvements")
        self.win.requestProperties(props)
        
        # Sky color
        self.setBackgroundColor(0.5, 0.6, 0.8, 1)
        
        # Generate terrain
        print("Generating terrain with simple NumPy enhancements...")
        self.terrain = self.create_simple_numpy_terrain()
        print("Terrain ready!")
        
        # Camera
        self.camera_pos = Point3(0, -40, 20)
        self.camera.setPos(self.camera_pos)
        self.camera.lookAt(0, 0, 5)
        
        # Movement controls
        self.keys = {"w": False, "s": False, "a": False, "d": False,
                     "space": False, "shift": False, "q": False, "e": False}
        self.speed = 15.0
        
        for key in self.keys:
            self.accept(key, self.set_key, [key, True])
            self.accept(f"{key}-up", self.set_key, [key, False])
        self.accept("escape", self.userExit)
        self.accept("r", self.reset_camera)
        
        self.taskMgr.add(self.move_task, "move")
        
        # Lighting
        alight = AmbientLight('alight')
        alight.setColor((0.45, 0.45, 0.5, 1))
        alnp = self.render.attachNewNode(alight)
        self.render.setLight(alnp)
        
        dlight = DirectionalLight('sun')
        dlight.setColor((0.6, 0.55, 0.5, 1))
        dlnp = self.render.attachNewNode(dlight)
        dlnp.setHpr(-45, -50, 0)
        self.render.setLight(dlnp)
        
        # UI Elements
        from direct.gui.OnscreenText import OnscreenText
        
        self.title = OnscreenText(
            text="Simple NumPy Terrain",
            pos=(0, 0.95), scale=0.05, fg=(1, 1, 1, 1)
        )
        
        self.controls = OnscreenText(
            text="WASD: Move | Q/E: Rotate | Space/Shift: Up/Down | R: Reset | ESC: Exit",
            pos=(0, 0.88), scale=0.04, fg=(0.9, 0.9, 0.9, 1)
        )
        
        self.pos_text = OnscreenText(
            text="Position: (0.0, -40.0, 20.0)",
            pos=(0, -0.95), scale=0.04,
            fg=(1, 1, 0, 1), mayChange=True
        )
        
        self.info_text = OnscreenText(
            text="Features: NumPy-based heights | Variable ridge spacing | Controlled randomness",
            pos=(0, -0.88), scale=0.035,
            fg=(0.8, 0.8, 0.8, 1)
        )
    
    def create_simple_numpy_terrain(self):
        """Create terrain using NumPy for better performance"""
        
        # Parameters
        size = 80
        resolution = 50
        
        # Set random seed
        np.random.seed(42)
        
        # Create coordinate arrays
        x = np.linspace(-size/2, size/2, resolution)
        y = np.linspace(-size/2, size/2, resolution)
        X, Y = np.meshgrid(x, y)
        
        # Initialize heightmap
        heightmap = np.ones((resolution, resolution)) * 3.0  # Base elevation
        
        # 1. PRIMARY RIDGES (Appalachian style)
        angle = np.radians(30)  # Northeast-southwest
        X_rot = X * np.cos(angle) - Y * np.sin(angle)
        Y_rot = X * np.sin(angle) + Y * np.cos(angle)
        
        # Simple variable ridge spacing (increases with distance)
        distance = np.sqrt(X**2 + Y**2)
        base_spacing = 15.0
        spacing_factor = 1.0 + (distance / (size/2)) * 0.5  # Spacing increases by up to 50%
        
        # Ridge pattern
        ridge_height = 8.0
        ridges = ridge_height * (0.5 + 0.5 * np.cos(X_rot / (base_spacing * spacing_factor) * 2 * np.pi))
        heightmap += ridges
        
        # 2. VALLEYS (simple carving)
        valley_mask = np.sin(X_rot / base_spacing * np.pi)
        valley_areas = valley_mask < -0.3
        heightmap[valley_areas] *= 0.5  # Make valleys 50% lower
        
        # 3. ALONG-RIDGE VARIATION
        variation = 2.0 * np.sin(Y_rot * 0.05) * np.cos(Y_rot * 0.03)
        heightmap += variation
        
        # 4. SIMPLE RANDOM NOISE
        # Add controlled random variation
        noise = np.random.randn(resolution, resolution) * 1.0
        
        # Smooth the noise (simple averaging)
        smoothed_noise = np.zeros_like(noise)
        for i in range(1, resolution-1):
            for j in range(1, resolution-1):
                smoothed_noise[i, j] = (
                    noise[i, j] * 0.4 +
                    noise[i-1, j] * 0.15 +
                    noise[i+1, j] * 0.15 +
                    noise[i, j-1] * 0.15 +
                    noise[i, j+1] * 0.15
                )
        heightmap += smoothed_noise
        
        # 5. SMALL TEXTURE
        texture = 0.3 * np.sin(X * 0.5) * np.sin(Y * 0.5)
        heightmap += texture
        
        # Get height range
        min_h = np.min(heightmap)
        max_h = np.max(heightmap)
        print(f"Height range: {min_h:.1f} to {max_h:.1f}")
        
        # CREATE MESH
        vformat = GeomVertexFormat.getV3n3c4()
        vdata = GeomVertexData('terrain', vformat, Geom.UHStatic)
        vdata.setNumRows(resolution * resolution)
        
        vertex = GeomVertexWriter(vdata, 'vertex')
        normal = GeomVertexWriter(vdata, 'normal')
        color = GeomVertexWriter(vdata, 'color')
        
        # First pass: write vertices
        for j in range(resolution):
            for i in range(resolution):
                # Position
                vertex.addData3(x[i], y[j], heightmap[j, i])
                
                # Placeholder normal
                normal.addData3(0, 0, 1)
                
                # Height-based color
                h_norm = (heightmap[j, i] - min_h) / (max_h - min_h + 0.001)
                
                if h_norm < 0.25:  # Valley - green
                    r, g, b = 0.1, 0.4, 0.1
                elif h_norm < 0.5:  # Lower slopes - yellow-green
                    t = (h_norm - 0.25) / 0.25
                    r = 0.1 + t * 0.3
                    g = 0.4 - t * 0.1
                    b = 0.1 + t * 0.1
                elif h_norm < 0.75:  # Upper slopes - brown
                    t = (h_norm - 0.5) / 0.25
                    r = 0.4 + t * 0.2
                    g = 0.3 - t * 0.05
                    b = 0.2 + t * 0.1
                else:  # Peak - white
                    t = (h_norm - 0.75) / 0.25
                    r = 0.6 + t * 0.4
                    g = 0.25 + t * 0.75
                    b = 0.3 + t * 0.7
                
                color.addData4(r, g, b, 1.0)
        
        # Second pass: calculate proper normals
        for j in range(resolution):
            for i in range(resolution):
                idx = j * resolution + i
                
                # Calculate normal from neighboring heights
                h_center = heightmap[j, i]
                h_left = heightmap[j, i-1] if i > 0 else h_center
                h_right = heightmap[j, i+1] if i < resolution-1 else h_center
                h_down = heightmap[j-1, i] if j > 0 else h_center
                h_up = heightmap[j+1, i] if j < resolution-1 else h_center
                
                # Gradient
                dx = (h_right - h_left) / (2.0 * size / resolution)
                dy = (h_up - h_down) / (2.0 * size / resolution)
                
                # Normal
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
    
    def reset_camera(self):
        self.camera_pos = Point3(0, -40, 20)
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
    print("\n=== Simple NumPy Terrain ===")
    print("Incremental improvements:")
    print("- NumPy arrays for efficiency")
    print("- Variable ridge spacing")
    print("- Simple smoothed noise")
    print("- No scipy dependency")
    app = SimpleNumpyTerrain()
    app.run()
