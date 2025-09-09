"""
07_terrain_simple.py - Simplest possible procedural terrain
Starting with basic sine waves to create rolling hills
"""

from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    WindowProperties, Point3, Vec3, Vec4,
    CardMaker, NodePath, Texture,
    GeomNode, GeomPoints, GeomTriangles, Geom,
    GeomVertexFormat, GeomVertexData, GeomVertexWriter,
    AmbientLight, DirectionalLight
)
from direct.task import Task
import math

class TerrainDemo(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        
        # Window setup
        props = WindowProperties()
        props.setTitle("Simple Terrain Generation - Step 1")
        self.win.requestProperties(props)
        
        # Sky color (overcast winter sky)
        self.setBackgroundColor(0.7, 0.75, 0.8, 1)
        
        # Create simple terrain using sine waves
        self.terrain = self.create_simple_terrain()
        
        # Camera position
        self.camera_pos = Point3(0, -30, 10)
        self.camera.setPos(self.camera_pos)
        self.camera.lookAt(0, 0, 0)
        
        # Movement
        self.keys = {"w": False, "s": False, "a": False, "d": False, 
                     "space": False, "shift": False}
        self.speed = 10.0
        
        # Key bindings
        for key in ["w", "s", "a", "d", "space", "shift"]:
            self.accept(key, self.set_key, [key, True])
            self.accept(f"{key}-up", self.set_key, [key, False])
        self.accept("escape", self.userExit)
        self.accept("r", self.reset_camera)
        
        # Movement task
        self.taskMgr.add(self.move_task, "move")
        
        # Lighting
        alight = AmbientLight('alight')
        alight.setColor((0.4, 0.4, 0.45, 1))
        alnp = self.render.attachNewNode(alight)
        self.render.setLight(alnp)
        
        dlight = DirectionalLight('dlight')
        dlight.setColor((0.6, 0.55, 0.5, 1))
        dlnp = self.render.attachNewNode(dlight)
        dlnp.setHpr(-30, -60, 0)
        self.render.setLight(dlnp)
        
        # Info text
        from direct.gui.OnscreenText import OnscreenText
        self.info = OnscreenText(
            text="Simple Terrain v1: Sine Wave Hills\nWASD+Space/Shift: Move | R: Reset",
            pos=(0, 0.95), scale=0.04, fg=(1, 1, 1, 1)
        )
    
    def create_simple_terrain(self):
        """Create terrain using simple mathematical rules"""
        
        # Terrain parameters
        width = 50  # X dimension
        depth = 50  # Y dimension
        resolution = 20  # Points per dimension
        
        # Create vertex data
        vformat = GeomVertexFormat.getV3n3()
        vdata = GeomVertexData('terrain', vformat, Geom.UHStatic)
        vdata.setNumRows(resolution * resolution)
        vertex = GeomVertexWriter(vdata, 'vertex')
        normal = GeomVertexWriter(vdata, 'normal')
        
        # Generate height map using simple rules
        heights = []
        for y in range(resolution):
            row = []
            for x in range(resolution):
                # Convert to world coordinates
                world_x = (x / (resolution - 1) - 0.5) * width
                world_y = (y / (resolution - 1) - 0.5) * depth
                
                # RULE 1: Primary rolling hills (sine waves)
                height = 3.0 * math.sin(world_x * 0.1) * math.cos(world_y * 0.1)
                
                # RULE 2: Secondary variation
                height += 1.5 * math.sin(world_x * 0.2 + 1) * math.sin(world_y * 0.15)
                
                # RULE 3: Small bumps
                height += 0.5 * math.sin(world_x * 0.5) * math.sin(world_y * 0.5)
                
                row.append(height)
                
                # Write vertex
                vertex.addData3(world_x, world_y, height)
                # Simple normal (pointing up for now)
                normal.addData3(0, 0, 1)
            
            heights.append(row)
        
        # Create geometry
        geom = Geom(vdata)
        
        # Create triangles
        for y in range(resolution - 1):
            for x in range(resolution - 1):
                # Get the four corners of this quad
                v0 = y * resolution + x
                v1 = v0 + 1
                v2 = v0 + resolution
                v3 = v2 + 1
                
                # Create two triangles
                prim = GeomTriangles(Geom.UHStatic)
                prim.addVertices(v0, v2, v1)
                prim.addVertices(v1, v2, v3)
                prim.closePrimitive()
                geom.addPrimitive(prim)
        
        # Create node and attach to scene
        node = GeomNode('terrain')
        node.addGeom(geom)
        terrain_np = self.render.attachNewNode(node)
        
        # Set color (snowy white with slight blue tint)
        terrain_np.setColor(0.9, 0.92, 0.95, 1)
        
        return terrain_np
    
    def set_key(self, key, value):
        self.keys[key] = value
    
    def reset_camera(self):
        self.camera_pos = Point3(0, -30, 10)
        self.camera.setPos(self.camera_pos)
        self.camera.lookAt(0, 0, 0)
    
    def move_task(self, task):
        dt = 0.016  # 60 FPS assumed
        
        # Update position based on keys
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
        
        self.camera.setPos(self.camera_pos)
        
        return Task.cont

if __name__ == "__main__":
    print("=== Simple Terrain Generation ===")
    print("Step 1: Basic sine wave hills")
    print("This is the foundation we'll build on")
    app = TerrainDemo()
    app.run()

