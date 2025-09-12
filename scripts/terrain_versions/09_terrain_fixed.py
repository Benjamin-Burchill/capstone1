"""
09_terrain_fixed.py - Fixed terrain with proper vertex colors
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

class FixedTerrain(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        
        # Window setup
        props = WindowProperties()
        props.setTitle("Advanced Terrain - Fixed Colors")
        self.win.requestProperties(props)
        
        # Sky color
        self.setBackgroundColor(0.4, 0.5, 0.7, 1)
        
        # Generate terrain
        print("Generating terrain with proper colors...")
        self.terrain = self.create_fixed_terrain()
        print("Terrain ready!")
        
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
        
        # Lighting setup - balanced for vertex colors
        alight = AmbientLight('alight')
        alight.setColor((0.4, 0.4, 0.4, 1))
        alnp = self.render.attachNewNode(alight)
        self.render.setLight(alnp)
        
        sun = DirectionalLight('sun')
        sun.setColor((0.6, 0.6, 0.5, 1))
        sun_np = self.render.attachNewNode(sun)
        sun_np.setHpr(-45, -60, 0)
        self.render.setLight(sun_np)
        
        # Info
        from direct.gui.OnscreenText import OnscreenText
        self.info = OnscreenText(
            text="Advanced Terrain - Appalachian Style\nGreen valleys -> Brown hills -> White peaks",
            pos=(0, 0.93), scale=0.04, fg=(1, 1, 1, 1)
        )
    
    def simple_noise(self, x, y, scale=1.0, seed=0):
        """Simple pseudo-random noise function"""
        # Use sine waves with prime numbers for pseudo-randomness
        value = math.sin(x * scale * 0.1373 + seed) * 43758.5453
        value += math.sin(y * scale * 0.1171 + seed * 1.337) * 12345.6789
        value = math.sin(value) * 0.5 + 0.5
        return value
    
    def create_fixed_terrain(self):
        """Create terrain with working vertex colors"""
        
        # Parameters
        size = 100
        resolution = 60  # Lower for better performance
        
        # Generate heightmap
        heightmap = np.zeros((resolution, resolution))
        
        for j in range(resolution):
            for i in range(resolution):
                x = (i / (resolution - 1) - 0.5) * size
                y = (j / (resolution - 1) - 0.5) * size
                
                # Base terrain - rolling hills
                height = 5.0
                
                # Large scale features
                height += self.simple_noise(x, y, 0.05) * 8
                height += self.simple_noise(x, y, 0.1, 100) * 4
                
                # Ridge pattern (Appalachian style)
                ridge = math.sin((x * 0.7 - y * 0.3) * 0.1) * 3
                height += max(0, ridge)  # Only positive ridges
                
                # Valley carving
                valley = math.sin((x * 0.3 + y * 0.7) * 0.08) 
                if valley < -0.3:
                    height *= 0.5  # Deep valleys
                
                # Small details
                height += self.simple_noise(x, y, 0.3, 200) * 1
                
                heightmap[j, i] = height
        
        # Simple erosion pass
        for _ in range(2):
            new_heightmap = heightmap.copy()
            for j in range(1, resolution-1):
                for i in range(1, resolution-1):
                    # Average with neighbors (simple smoothing)
                    avg = (heightmap[j-1, i] + heightmap[j+1, i] + 
                          heightmap[j, i-1] + heightmap[j, i+1]) / 4
                    new_heightmap[j, i] = heightmap[j, i] * 0.7 + avg * 0.3
            heightmap = new_heightmap
        
        # Get height range
        min_h = np.min(heightmap)
        max_h = np.max(heightmap)
        height_range = max_h - min_h
        print(f"Terrain height: {min_h:.1f} to {max_h:.1f}")
        
        # Create vertex format with color
        vformat = GeomVertexFormat.getV3n3c4()  # position, normal, color
        vdata = GeomVertexData('terrain', vformat, Geom.UHStatic)
        vdata.setNumRows(resolution * resolution)
        
        vertex = GeomVertexWriter(vdata, 'vertex')
        normal = GeomVertexWriter(vdata, 'normal')
        color = GeomVertexWriter(vdata, 'color')
        
        # Generate vertices
        for j in range(resolution):
            for i in range(resolution):
                # Position
                x = (i / (resolution - 1) - 0.5) * size
                y = (j / (resolution - 1) - 0.5) * size
                z = heightmap[j, i]
                vertex.addData3(x, y, z)
                
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
                
                # Height-based coloring
                h_normalized = (z - min_h) / (height_range + 0.001)
                
                # Color based on elevation
                if h_normalized < 0.25:  # Deep valleys - dark green
                    r, g, b = 0.1, 0.25, 0.05
                elif h_normalized < 0.4:  # Valley floor - green
                    t = (h_normalized - 0.25) / 0.15
                    r = 0.1 + t * 0.15
                    g = 0.25 + t * 0.1
                    b = 0.05 + t * 0.05
                elif h_normalized < 0.55:  # Lower slopes - yellow-green
                    t = (h_normalized - 0.4) / 0.15
                    r = 0.25 + t * 0.2
                    g = 0.35 - t * 0.05
                    b = 0.1 + t * 0.1
                elif h_normalized < 0.7:  # Mid slopes - brown
                    t = (h_normalized - 0.55) / 0.15
                    r = 0.45 + t * 0.1
                    g = 0.3
                    b = 0.2
                elif h_normalized < 0.85:  # Upper slopes - gray-brown
                    t = (h_normalized - 0.7) / 0.15
                    r = 0.55 + t * 0.15
                    g = 0.3 + t * 0.2
                    b = 0.2 + t * 0.25
                else:  # Snow cap - white
                    t = (h_normalized - 0.85) / 0.15
                    r = 0.7 + t * 0.3
                    g = 0.5 + t * 0.5
                    b = 0.45 + t * 0.55
                
                # Add slight variation based on position
                variation = self.simple_noise(x, y, 0.5, 300) * 0.1 - 0.05
                r = max(0, min(1, r + variation))
                g = max(0, min(1, g + variation))
                b = max(0, min(1, b + variation))
                
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
        
        # Set two-sided rendering for terrain (optional, helps with viewing from below)
        terrain_np.setTwoSided(True)
        
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
    print("=== Fixed Advanced Terrain ===")
    print("Proper vertex colors with Appalachian-style features")
    app = FixedTerrain()
    app.run()
