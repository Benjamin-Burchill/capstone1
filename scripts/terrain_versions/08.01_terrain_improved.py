"""
10_terrain_improved.py - Improved version of terrain_ridges with small enhancements
Building on the working ridge terrain with better colors and UI
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

class ImprovedTerrain(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        
        # Window setup
        props = WindowProperties()
        props.setTitle("Improved Appalachian Terrain")
        self.win.requestProperties(props)
        
        # Sky color (clearer day)
        self.setBackgroundColor(0.5, 0.6, 0.8, 1)
        
        # Generate terrain
        print("Generating improved terrain...")
        self.terrain = self.create_improved_terrain()
        print("Terrain ready!")
        
        # Camera with position tracking
        self.camera_pos = Point3(0, -40, 20)
        self.camera.setPos(self.camera_pos)
        self.camera.lookAt(0, 0, 5)
        
        # Movement controls
        self.keys = {"w": False, "s": False, "a": False, "d": False,
                     "space": False, "shift": False, "q": False, "e": False}
        self.speed = 15.0
        
        # Key bindings
        for key in self.keys:
            self.accept(key, self.set_key, [key, True])
            self.accept(f"{key}-up", self.set_key, [key, False])
        self.accept("escape", self.userExit)
        self.accept("r", self.reset_camera)
        
        self.taskMgr.add(self.move_task, "move")
        
        # Improved lighting
        alight = AmbientLight('alight')
        alight.setColor((0.45, 0.45, 0.5, 1))  # Slightly brighter
        alnp = self.render.attachNewNode(alight)
        self.render.setLight(alnp)
        
        dlight = DirectionalLight('sun')
        dlight.setColor((0.6, 0.55, 0.5, 1))
        dlnp = self.render.attachNewNode(dlight)
        dlnp.setHpr(-45, -50, 0)
        self.render.setLight(dlnp)
        
        # UI Elements
        from direct.gui.OnscreenText import OnscreenText
        
        # Title
        self.title = OnscreenText(
            text="Improved Appalachian Terrain",
            pos=(0, 0.95), scale=0.05, fg=(1, 1, 1, 1)
        )
        
        # Controls
        self.controls = OnscreenText(
            text="WASD: Move | Q/E: Rotate | Space/Shift: Up/Down | R: Reset | ESC: Exit",
            pos=(0, 0.88), scale=0.04, fg=(0.9, 0.9, 0.9, 1)
        )
        
        # Position display
        self.pos_text = OnscreenText(
            text="Position: (0.0, -40.0, 20.0)",
            pos=(0, -0.95), scale=0.04, 
            fg=(1, 1, 0, 1), mayChange=True
        )
        
        # Terrain info
        self.info_text = OnscreenText(
            text="Features: Ridges, Valleys, Height-based colors, Random variation",
            pos=(0, -0.88), scale=0.035,
            fg=(0.8, 0.8, 0.8, 1)
        )
    
    def height_at_point(self, x, y):
        """
        Calculate height using improved Appalachian-style rules
        """
        # Initialize random seed based on position for consistency
        random.seed(int(x * 100 + y * 100))
        
        # RULE 1: Primary ridges (northeast-southwest orientation)
        angle = math.radians(30)
        rx = x * math.cos(angle) - y * math.sin(angle)
        ry = x * math.sin(angle) + y * math.cos(angle)
        
        # Main ridge pattern
        ridge_spacing = 15.0
        ridge_height = 8.0
        ridge = ridge_height * (0.5 + 0.5 * math.cos(rx / ridge_spacing * 2 * math.pi))
        
        # RULE 2: Valley carving
        valley_depth = 0.4
        valley_width = 0.3
        valley_factor = abs(math.sin(rx / ridge_spacing * math.pi))
        if valley_factor < valley_width:
            ridge *= valley_depth
        
        # RULE 3: Along-ridge variation
        variation = 2.0 * math.sin(ry * 0.05) * math.cos(ry * 0.03)
        
        # RULE 4: Add some random noise for realism
        noise = (random.random() - 0.5) * 1.5
        
        # RULE 5: Erosion (smooth/round the peaks)
        erosion = 0.8
        height = ridge * erosion + variation + noise
        
        # RULE 6: Small-scale texture
        texture = 0.3 * math.sin(x * 0.5) * math.sin(y * 0.5)
        height += texture
        
        # RULE 7: Base elevation
        base_elevation = 3.0
        height += base_elevation
        
        return height
    
    def create_improved_terrain(self):
        """Create terrain mesh with improved features"""
        
        # Terrain parameters
        size = 80
        resolution = 50  # Good balance of detail and performance
        
        # Create vertex data with colors
        vformat = GeomVertexFormat.getV3n3c4()
        vdata = GeomVertexData('terrain', vformat, Geom.UHStatic)
        vdata.setNumRows(resolution * resolution)
        
        vertex = GeomVertexWriter(vdata, 'vertex')
        normal = GeomVertexWriter(vdata, 'normal')
        color = GeomVertexWriter(vdata, 'color')
        
        # Generate vertices and store heights
        heights = []
        min_h = float('inf')
        max_h = float('-inf')
        
        for j in range(resolution):
            row = []
            for i in range(resolution):
                # World coordinates
                x = (i / (resolution - 1) - 0.5) * size
                y = (j / (resolution - 1) - 0.5) * size
                
                # Get height from rules
                h = self.height_at_point(x, y)
                row.append(h)
                
                # Track min/max
                min_h = min(min_h, h)
                max_h = max(max_h, h)
                
                # Write vertex
                vertex.addData3(x, y, h)
                
                # Placeholder normal
                normal.addData3(0, 0, 1)
            
            heights.append(row)
        
        print(f"Height range: {min_h:.1f} to {max_h:.1f}")
        
        # Second pass: colors and normals
        for j in range(resolution):
            for i in range(resolution):
                idx = j * resolution + i
                h = heights[j][i]
                
                # Calculate proper normal
                nx, ny, nz = 0, 0, 1
                if i > 0 and i < resolution-1 and j > 0 and j < resolution-1:
                    dzdx = (heights[j][i+1] - heights[j][i-1]) / (2.0 * size / resolution)
                    dzdy = (heights[j+1][i] - heights[j-1][i]) / (2.0 * size / resolution)
                    nx = -dzdx
                    ny = -dzdy
                    nz = 1.0
                    length = math.sqrt(nx*nx + ny*ny + nz*nz)
                    nx /= length
                    ny /= length
                    nz /= length
                
                # Update normal
                normal.setRow(idx)
                normal.setData3(nx, ny, nz)
                
                # Improved color based on height
                h_norm = (h - min_h) / (max_h - min_h + 0.001)
                
                # More gradual color transitions
                if h_norm < 0.2:  # Deep valley - dark green
                    r, g, b = 0.05, 0.25, 0.05
                elif h_norm < 0.35:  # Valley - green
                    t = (h_norm - 0.2) / 0.15
                    r = 0.05 + t * 0.15
                    g = 0.25 + t * 0.15
                    b = 0.05 + t * 0.05
                elif h_norm < 0.5:  # Lower slopes - yellow-green
                    t = (h_norm - 0.35) / 0.15
                    r = 0.2 + t * 0.2
                    g = 0.4 - t * 0.1
                    b = 0.1 + t * 0.1
                elif h_norm < 0.65:  # Mid slopes - brown
                    t = (h_norm - 0.5) / 0.15
                    r = 0.4 + t * 0.1
                    g = 0.3
                    b = 0.2 + t * 0.05
                elif h_norm < 0.8:  # Upper slopes - gray-brown
                    t = (h_norm - 0.65) / 0.15
                    r = 0.5 + t * 0.2
                    g = 0.3 + t * 0.2
                    b = 0.25 + t * 0.25
                else:  # Snow line - white
                    t = (h_norm - 0.8) / 0.2
                    r = 0.7 + t * 0.3
                    g = 0.5 + t * 0.5
                    b = 0.5 + t * 0.5
                
                # Add slight color variation based on slope
                slope = math.sqrt(dzdx*dzdx + dzdy*dzdy) if 'dzdx' in locals() else 0
                if slope > 1.0:  # Steep areas slightly darker
                    r *= 0.9
                    g *= 0.9
                    b *= 0.9
                
                color.setRow(idx)
                color.setData4(r, g, b, 1.0)
        
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
        
        # Enable two-sided rendering
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
        self.pos_text.setText(
            f"Position: ({self.camera_pos.x:.1f}, {self.camera_pos.y:.1f}, {self.camera_pos.z:.1f})"
        )
        
        return Task.cont

if __name__ == "__main__":
    print("=== Improved Terrain Generation ===")
    print("Based on working ridge terrain with enhancements:")
    print("- Better color gradients")
    print("- UI elements (position, controls)")
    print("- Random variation for realism")
    print("- Slope-based color adjustment")
    app = ImprovedTerrain()
    app.run()
