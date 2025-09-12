"""
09_terrain_advanced.py - Advanced terrain with noise, erosion, and realistic coloring
Using NumPy for efficient array operations and custom noise generation
"""

from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    WindowProperties, Point3,
    GeomNode, GeomTriangles, Geom,
    GeomVertexFormat, GeomVertexData, GeomVertexWriter,
    AmbientLight, DirectionalLight, Vec4
)
from direct.task import Task
import numpy as np
import math

class AdvancedTerrain(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        
        # Window setup
        props = WindowProperties()
        props.setTitle("Advanced Terrain - Noise, Erosion & Colors")
        self.win.requestProperties(props)
        
        # Sky color
        self.setBackgroundColor(0.5, 0.6, 0.8, 1)
        
        # Generate advanced terrain
        print("Generating terrain...")
        self.terrain = self.create_advanced_terrain()
        print("Terrain generated!")
        
        # Camera
        self.camera_pos = Point3(0, -60, 30)
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
        alight = AmbientLight('alight')
        alight.setColor((0.3, 0.3, 0.35, 1))
        alnp = self.render.attachNewNode(alight)
        self.render.setLight(alnp)
        
        sun = DirectionalLight('sun')
        sun.setColor((0.8, 0.75, 0.7, 1))
        sun_np = self.render.attachNewNode(sun)
        sun_np.setHpr(-45, -60, 0)
        self.render.setLight(sun_np)
        
        # Info
        from direct.gui.OnscreenText import OnscreenText
        self.info = OnscreenText(
            text="Advanced Terrain with NumPy\nNoise + Erosion + Realistic Colors",
            pos=(0, 0.93), scale=0.04, fg=(1, 1, 1, 1)
        )
    
    def generate_perlin_noise(self, width, height, scale=20.0, octaves=4, persistence=0.5, seed=42):
        """Generate Perlin-like noise using NumPy"""
        np.random.seed(seed)
        
        # Create base random gradients
        gradient_width = int(width / scale) + 2
        gradient_height = int(height / scale) + 2
        
        noise_map = np.zeros((height, width))
        
        amplitude = 1.0
        frequency = 1.0
        max_value = 0.0
        
        for octave in range(octaves):
            # Generate random gradients for this octave
            gradients = np.random.randn(gradient_height, gradient_width, 2)
            
            # Normalize gradients
            grad_norm = np.sqrt(gradients[:,:,0]**2 + gradients[:,:,1]**2)
            gradients[:,:,0] /= grad_norm + 1e-10
            gradients[:,:,1] /= grad_norm + 1e-10
            
            # Generate coordinates
            x_coords = np.arange(width) * frequency / scale
            y_coords = np.arange(height) * frequency / scale
            
            # Interpolate (simplified bilinear)
            for y in range(height):
                for x in range(width):
                    # Grid coordinates
                    x_scaled = x * frequency / scale
                    y_scaled = y * frequency / scale
                    
                    # Grid cell
                    x0 = int(x_scaled)
                    y0 = int(y_scaled)
                    x1 = x0 + 1
                    y1 = y0 + 1
                    
                    # Interpolation weights
                    sx = x_scaled - x0
                    sy = y_scaled - y0
                    
                    # Smooth the weights
                    sx = sx * sx * (3 - 2 * sx)
                    sy = sy * sy * (3 - 2 * sy)
                    
                    # Simple interpolation
                    n0 = (1 - sx) * (1 - sy)
                    n1 = sx * (1 - sy)
                    n2 = (1 - sx) * sy
                    n3 = sx * sy
                    
                    # Combine
                    value = n0 + n1 + n2 + n3
                    noise_map[y, x] += value * amplitude
            
            max_value += amplitude
            amplitude *= persistence
            frequency *= 2
        
        # Normalize to 0-1
        noise_map = (noise_map + max_value) / (2 * max_value)
        return noise_map
    
    def apply_erosion(self, heightmap, iterations=5, strength=0.1):
        """Simple thermal erosion simulation"""
        h, w = heightmap.shape
        
        for _ in range(iterations):
            # Calculate gradients
            grad_x = np.zeros_like(heightmap)
            grad_y = np.zeros_like(heightmap)
            
            grad_x[:-1, :] = heightmap[1:, :] - heightmap[:-1, :]
            grad_y[:, :-1] = heightmap[:, 1:] - heightmap[:, :-1]
            
            # Calculate slope
            slope = np.sqrt(grad_x**2 + grad_y**2)
            
            # Thermal erosion: move material from steep slopes
            erosion = np.where(slope > 0.5, slope * strength, 0)
            
            # Apply erosion (simplified - just lower steep areas)
            heightmap -= erosion
            
            # Smooth slightly (deposit material)
            kernel = np.array([[0.05, 0.1, 0.05],
                              [0.1, 0.4, 0.1],
                              [0.05, 0.1, 0.05]])
            
            # Simple convolution (edges handled roughly)
            new_heightmap = np.copy(heightmap)
            for i in range(1, h-1):
                for j in range(1, w-1):
                    new_heightmap[i, j] = np.sum(
                        heightmap[i-1:i+2, j-1:j+2] * kernel
                    )
            
            heightmap = new_heightmap
        
        return heightmap
    
    def height_to_color(self, height, min_h, max_h):
        """Map height to realistic terrain colors"""
        # Normalize height to 0-1
        h_norm = (height - min_h) / (max_h - min_h + 1e-10)
        
        # Define color zones
        if h_norm < 0.2:  # Deep valley - dark green
            return Vec4(0.1, 0.3, 0.1, 1)
        elif h_norm < 0.35:  # Valley floor - green
            t = (h_norm - 0.2) / 0.15
            return Vec4(0.1 + t*0.2, 0.3 + t*0.2, 0.1, 1)
        elif h_norm < 0.5:  # Lower slopes - brown-green
            t = (h_norm - 0.35) / 0.15
            return Vec4(0.3 + t*0.2, 0.5 - t*0.1, 0.1 + t*0.1, 1)
        elif h_norm < 0.7:  # Upper slopes - brown/rock
            t = (h_norm - 0.5) / 0.2
            return Vec4(0.5 + t*0.1, 0.4 + t*0.1, 0.2 + t*0.1, 1)
        elif h_norm < 0.85:  # High elevation - gray rock
            t = (h_norm - 0.7) / 0.15
            return Vec4(0.6 + t*0.2, 0.5 + t*0.2, 0.3 + t*0.3, 1)
        else:  # Snow line - white
            t = (h_norm - 0.85) / 0.15
            return Vec4(0.8 + t*0.2, 0.7 + t*0.3, 0.6 + t*0.4, 1)
    
    def create_advanced_terrain(self):
        """Create terrain with noise, erosion, and colors"""
        
        # Parameters
        size = 100
        resolution = 80
        
        # Generate base heightmap with multiple noise layers
        print("  Generating noise layers...")
        
        # Large-scale features (mountains/valleys)
        base_noise = self.generate_perlin_noise(resolution, resolution, scale=30, octaves=3, persistence=0.6)
        
        # Medium features (ridges)
        ridge_noise = self.generate_perlin_noise(resolution, resolution, scale=15, octaves=4, persistence=0.4, seed=123)
        
        # Small details
        detail_noise = self.generate_perlin_noise(resolution, resolution, scale=5, octaves=2, persistence=0.3, seed=456)
        
        # Combine noise layers
        heightmap = base_noise * 15  # Base elevation
        heightmap += ridge_noise * 8  # Ridges
        heightmap += detail_noise * 2  # Details
        
        # Add some Appalachian-style ridges
        x = np.linspace(-np.pi*2, np.pi*2, resolution)
        y = np.linspace(-np.pi*2, np.pi*2, resolution)
        X, Y = np.meshgrid(x, y)
        
        # Rotated ridges
        angle = np.radians(30)
        X_rot = X * np.cos(angle) - Y * np.sin(angle)
        ridge_pattern = np.sin(X_rot * 0.5) * 3
        heightmap += ridge_pattern
        
        # Apply erosion
        print("  Applying erosion...")
        heightmap = self.apply_erosion(heightmap, iterations=3, strength=0.05)
        
        # Create valleys by inverting and combining
        valley_mask = 1 - (ridge_noise * 0.5 + 0.5)
        heightmap *= (0.5 + valley_mask * 0.5)
        
        # Get height range for coloring
        min_height = np.min(heightmap)
        max_height = np.max(heightmap)
        
        print("  Building mesh...")
        
        # Create vertex data
        vformat = GeomVertexFormat.getV3n3c4()
        vdata = GeomVertexData('terrain', vformat, Geom.UHStatic)
        vdata.setNumRows(resolution * resolution)
        
        vertex = GeomVertexWriter(vdata, 'vertex')
        normal = GeomVertexWriter(vdata, 'normal')
        color = GeomVertexWriter(vdata, 'color')
        
        # Generate vertices
        for j in range(resolution):
            for i in range(resolution):
                # World position
                x = (i / (resolution - 1) - 0.5) * size
                y = (j / (resolution - 1) - 0.5) * size
                z = heightmap[j, i]
                
                vertex.addData3(x, y, z)
                
                # Color based on height
                c = self.height_to_color(z, min_height, max_height)
                color.addData4(c)
                
                # Calculate normal
                dzdx = 0
                dzdy = 0
                if i > 0 and i < resolution - 1:
                    dzdx = (heightmap[j, i+1] - heightmap[j, i-1]) / (2 * size / resolution)
                if j > 0 and j < resolution - 1:
                    dzdy = (heightmap[j+1, i] - heightmap[j-1, i]) / (2 * size / resolution)
                
                # Normal vector
                nx = -dzdx
                ny = -dzdy
                nz = 1
                length = math.sqrt(nx*nx + ny*ny + nz*nz)
                normal.addData3(nx/length, ny/length, nz/length)
        
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
        
        return terrain_np
    
    def set_key(self, key, value):
        self.keys[key] = value
    
    def reset_camera(self):
        self.camera_pos = Point3(0, -60, 30)
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
        return Task.cont

if __name__ == "__main__":
    print("=== Advanced Terrain Generation ===")
    print("Features: Perlin-like noise, erosion, height-based coloring")
    print("This may take a moment to generate...")
    app = AdvancedTerrain()
    app.run()

