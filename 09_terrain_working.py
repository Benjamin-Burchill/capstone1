"""
09_terrain_working.py - Working terrain with visible colors and UI
Simplified approach to ensure colors are visible
"""

from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    WindowProperties, Point3,
    GeomNode, GeomTriangles, Geom,
    GeomVertexFormat, GeomVertexData, GeomVertexWriter,
    AmbientLight, DirectionalLight
)
from direct.task import Task
import math
import random

class WorkingTerrain(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        
        # Window setup
        props = WindowProperties()
        props.setTitle("Terrain with Colors - Working Version")
        self.win.requestProperties(props)
        
        # Sky color
        self.setBackgroundColor(0.5, 0.6, 0.8, 1)
        
        # Generate terrain
        print("Generating colored terrain...")
        self.terrain = self.create_working_terrain()
        print("Terrain ready!")
        
        # Camera position tracking
        self.camera_pos = Point3(0, -50, 25)
        self.camera.setPos(self.camera_pos)
        self.camera.lookAt(0, 0, 5)
        
        # Movement controls
        self.keys = {
            "w": False, "s": False, "a": False, "d": False,
            "space": False, "shift": False, "q": False, "e": False
        }
        self.speed = 20.0
        
        # Key bindings
        for key in self.keys:
            self.accept(key, self.set_key, [key, True])
            self.accept(f"{key}-up", self.set_key, [key, False])
        self.accept("escape", self.userExit)
        self.accept("r", self.reset_camera)
        
        self.taskMgr.add(self.move_task, "move")
        
        # Lighting - important for seeing vertex colors
        alight = AmbientLight('ambient')
        alight.setColor((0.6, 0.6, 0.6, 1))  # Bright ambient to see colors
        alnp = self.render.attachNewNode(alight)
        self.render.setLight(alnp)
        
        sun = DirectionalLight('sun')
        sun.setColor((0.4, 0.4, 0.3, 1))  # Dimmer directional
        sun_np = self.render.attachNewNode(sun)
        sun_np.setHpr(-45, -60, 0)
        self.render.setLight(sun_np)
        
        # UI Elements - Instructions and Position
        from direct.gui.OnscreenText import OnscreenText
        
        # Title
        self.title = OnscreenText(
            text="Colored Terrain - Appalachian Style",
            pos=(0, 0.95), scale=0.05, fg=(1, 1, 1, 1)
        )
        
        # Instructions
        self.instructions = OnscreenText(
            text="Controls: WASD - Move | Space/Shift - Up/Down | Q/E - Rotate | R - Reset | ESC - Exit",
            pos=(0, 0.88), scale=0.04, fg=(0.9, 0.9, 0.9, 1)
        )
        
        # Position display
        self.pos_display = OnscreenText(
            text="Position: (0.0, -50.0, 25.0)",
            pos=(0, -0.95), scale=0.04, fg=(1, 1, 0, 1),
            mayChange=True
        )
        
        # Height zones legend
        self.legend = OnscreenText(
            text="Height Zones: Green (valleys) -> Brown (hills) -> White (peaks)",
            pos=(0, -0.88), scale=0.035, fg=(0.8, 0.8, 0.8, 1)
        )
    
    def create_working_terrain(self):
        """Create terrain with guaranteed visible colors"""
        
        # Smaller terrain for testing
        size = 60
        resolution = 40
        
        # Initialize random seed for reproducibility
        random.seed(42)
        
        # Generate simple heightmap
        heights = []
        for j in range(resolution):
            row = []
            for i in range(resolution):
                x = (i / (resolution - 1) - 0.5) * 2
                y = (j / (resolution - 1) - 0.5) * 2
                
                # Base height
                h = 5.0
                
                # Add some hills using sine waves
                h += math.sin(x * 3) * 2
                h += math.cos(y * 3) * 2
                h += math.sin(x * 5 + y * 5) * 1
                
                # Add some randomness
                h += random.random() * 2 - 1
                
                # Create a valley in the middle
                dist_from_center = math.sqrt(x*x + y*y)
                if dist_from_center < 0.3:
                    h *= 0.5  # Lower the center
                
                row.append(h)
            heights.append(row)
        
        # Smooth the heightmap
        for _ in range(2):
            new_heights = []
            for j in range(resolution):
                row = []
                for i in range(resolution):
                    total = heights[j][i] * 4
                    count = 4
                    if j > 0:
                        total += heights[j-1][i]
                        count += 1
                    if j < resolution - 1:
                        total += heights[j+1][i]
                        count += 1
                    if i > 0:
                        total += heights[j][i-1]
                        count += 1
                    if i < resolution - 1:
                        total += heights[j][i+1]
                        count += 1
                    row.append(total / count)
                new_heights.append(row)
            heights = new_heights
        
        # Find min/max for color mapping
        min_h = min(min(row) for row in heights)
        max_h = max(max(row) for row in heights)
        height_range = max_h - min_h
        print(f"Height range: {min_h:.1f} to {max_h:.1f}")
        
        # Create vertex format - IMPORTANT: Use the right format
        vformat = GeomVertexFormat.getV3n3c4()  # position, normal, color
        vdata = GeomVertexData('terrain', vformat, Geom.UHStatic)
        vdata.setNumRows(resolution * resolution)
        
        vertex = GeomVertexWriter(vdata, 'vertex')
        normal = GeomVertexWriter(vdata, 'normal')
        color = GeomVertexWriter(vdata, 'color')
        
        # Generate vertices with colors
        for j in range(resolution):
            for i in range(resolution):
                # Position
                x = (i / (resolution - 1) - 0.5) * size
                y = (j / (resolution - 1) - 0.5) * size
                z = heights[j][i]
                vertex.addData3(x, y, z)
                
                # Simple normal (pointing up)
                normal.addData3(0, 0, 1)
                
                # Color based on height - CLEAR ZONES
                h_norm = (z - min_h) / (height_range + 0.001)
                
                if h_norm < 0.3:  # Low - GREEN
                    r, g, b = 0.1, 0.6, 0.1
                elif h_norm < 0.6:  # Mid - BROWN
                    t = (h_norm - 0.3) / 0.3
                    r = 0.1 + t * 0.4
                    g = 0.6 - t * 0.3
                    b = 0.1
                else:  # High - WHITE
                    t = (h_norm - 0.6) / 0.4
                    r = 0.5 + t * 0.5
                    g = 0.3 + t * 0.7
                    b = 0.1 + t * 0.9
                
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
        
        # IMPORTANT: Make sure vertex colors are used
        terrain_np.setColorScale(1, 1, 1, 1)  # No color scaling
        terrain_np.setTwoSided(True)  # See both sides
        
        # Try without lighting first to see pure vertex colors
        # terrain_np.setLightOff()  # Uncomment to debug colors
        
        return terrain_np
    
    def set_key(self, key, value):
        self.keys[key] = value
    
    def reset_camera(self):
        self.camera_pos = Point3(0, -50, 25)
        self.camera.setPos(self.camera_pos)
        self.camera.lookAt(0, 0, 5)
    
    def move_task(self, task):
        dt = 0.016  # 60 FPS
        
        # Movement
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
        
        # Rotation
        if self.keys["q"]:
            h = self.camera.getH()
            self.camera.setH(h + 30 * dt)
        if self.keys["e"]:
            h = self.camera.getH()
            self.camera.setH(h - 30 * dt)
        
        self.camera.setPos(self.camera_pos)
        
        # Update position display
        self.pos_display.setText(
            f"Position: ({self.camera_pos.x:.1f}, {self.camera_pos.y:.1f}, {self.camera_pos.z:.1f})"
        )
        
        return Task.cont

if __name__ == "__main__":
    print("=== Working Colored Terrain ===")
    print("This version should show green valleys, brown hills, and white peaks")
    print("All UI elements included")
    app = WorkingTerrain()
    app.run()
