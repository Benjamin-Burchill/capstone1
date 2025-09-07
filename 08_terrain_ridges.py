"""
08_terrain_ridges.py - Appalachian-style ridge and valley terrain
Adding rules for ridge lines and valleys characteristic of the Appalachians
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

class AppalachianTerrain(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        
        # Window setup
        props = WindowProperties()
        props.setTitle("Appalachian Terrain - Ridge & Valley")
        self.win.requestProperties(props)
        
        # Sky color (winter overcast)
        self.setBackgroundColor(0.65, 0.7, 0.75, 1)
        
        # Generate terrain
        self.terrain = self.create_appalachian_terrain()
        
        # Camera
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
        
        # Lighting (softer, winter light)
        alight = AmbientLight('alight')
        alight.setColor((0.35, 0.35, 0.4, 1))
        alnp = self.render.attachNewNode(alight)
        self.render.setLight(alnp)
        
        dlight = DirectionalLight('sun')
        dlight.setColor((0.7, 0.65, 0.6, 1))
        dlnp = self.render.attachNewNode(dlight)
        dlnp.setHpr(-45, -50, 0)
        self.render.setLight(dlnp)
        
        # Info
        from direct.gui.OnscreenText import OnscreenText
        self.info = OnscreenText(
            text="Appalachian Terrain: Ridge & Valley Pattern\n" +
                 "WASD: Move | Q/E: Rotate | Space/Shift: Up/Down | R: Reset",
            pos=(0, 0.93), scale=0.04, fg=(1, 1, 1, 1)
        )
        
        self.pos_text = OnscreenText(
            text="", pos=(0, -0.95), scale=0.04, 
            fg=(1, 1, 0, 1), mayChange=True
        )
    
    def height_at_point(self, x, y):
        """
        Calculate height using Appalachian-style rules
        Returns height and terrain type
        """
        # RULE 1: Primary ridges (northeast-southwest orientation)
        # Rotate coordinates to align with Appalachian ridge direction
        angle = math.radians(30)  # 30 degrees from north
        rx = x * math.cos(angle) - y * math.sin(angle)
        ry = x * math.sin(angle) + y * math.cos(angle)
        
        # Main ridge pattern
        ridge_spacing = 15.0  # Distance between ridges
        ridge_height = 8.0    # Maximum ridge height
        ridge = ridge_height * (0.5 + 0.5 * math.cos(rx / ridge_spacing * 2 * math.pi))
        
        # RULE 2: Valley carving
        valley_depth = 0.4  # How deep valleys cut
        valley_width = 0.3  # Width of valley floor
        valley_factor = abs(math.sin(rx / ridge_spacing * math.pi))
        if valley_factor < valley_width:
            ridge *= valley_depth
        
        # RULE 3: Along-ridge variation (make ridges not perfectly straight)
        variation = 2.0 * math.sin(ry * 0.05) * math.cos(ry * 0.03)
        
        # RULE 4: Erosion (smooth/round the peaks)
        erosion = 0.8  # Erosion factor (0=sharp, 1=very rounded)
        height = ridge * erosion + variation
        
        # RULE 5: Small-scale texture
        texture = 0.3 * math.sin(x * 0.5) * math.sin(y * 0.5)
        height += texture
        
        # RULE 6: Base elevation
        base_elevation = 2.0
        height += base_elevation
        
        return height
    
    def create_appalachian_terrain(self):
        """Create terrain mesh with Appalachian characteristics"""
        
        # Terrain parameters
        size = 80  # Total size
        resolution = 50  # Grid resolution
        
        # Create vertex data
        vformat = GeomVertexFormat.getV3n3c4()  # Position, normal, color
        vdata = GeomVertexData('terrain', vformat, Geom.UHStatic)
        vdata.setNumRows(resolution * resolution)
        
        vertex = GeomVertexWriter(vdata, 'vertex')
        normal = GeomVertexWriter(vdata, 'normal')
        color = GeomVertexWriter(vdata, 'color')
        
        # Generate vertices
        heights = []
        for j in range(resolution):
            row = []
            for i in range(resolution):
                # World coordinates
                x = (i / (resolution - 1) - 0.5) * size
                y = (j / (resolution - 1) - 0.5) * size
                
                # Get height from rules
                h = self.height_at_point(x, y)
                row.append(h)
                
                # Write vertex
                vertex.addData3(x, y, h)
                
                # Calculate color based on height (snow line effect)
                if h > 7:  # High elevation - snow
                    color.addData4(0.95, 0.95, 1.0, 1)
                elif h > 5:  # Mid elevation - mixed
                    blend = (h - 5) / 2
                    color.addData4(
                        0.6 + blend * 0.35,
                        0.65 + blend * 0.3,
                        0.6 + blend * 0.4,
                        1
                    )
                else:  # Low elevation - earth/vegetation
                    color.addData4(0.6, 0.65, 0.6, 1)
                
                # Placeholder normal (pointing up)
                normal.addData3(0, 0, 1)
            
            heights.append(row)
        
        # Calculate proper normals
        for j in range(resolution):
            for i in range(resolution):
                # Get neighboring heights for normal calculation
                h_center = heights[j][i]
                h_left = heights[j][i-1] if i > 0 else h_center
                h_right = heights[j][i+1] if i < resolution-1 else h_center
                h_down = heights[j-1][i] if j > 0 else h_center
                h_up = heights[j+1][i] if j < resolution-1 else h_center
                
                # Calculate normal (simplified)
                dx = (h_right - h_left) / (size / resolution)
                dy = (h_up - h_down) / (size / resolution)
                
                # Normalize (approximately)
                length = math.sqrt(dx*dx + dy*dy + 1)
                nx = -dx / length
                ny = -dy / length
                nz = 1 / length
                
                # Update normal
                idx = j * resolution + i
                normal.setRow(idx)
                normal.setData3(nx, ny, nz)
        
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
            f"Pos: ({self.camera_pos.x:.1f}, {self.camera_pos.y:.1f}, {self.camera_pos.z:.1f})"
        )
        
        return Task.cont

if __name__ == "__main__":
    print("=== Appalachian Terrain Generation ===")
    print("Ridge and valley patterns with snow line")
    print("Notice the northeast-southwest ridge orientation")
    app = AppalachianTerrain()
    app.run()
