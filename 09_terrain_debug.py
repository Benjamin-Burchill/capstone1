"""
09_terrain_debug.py - Debug version to fix the blue terrain issue
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

class DebugTerrain(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        
        # Window setup
        props = WindowProperties()
        props.setTitle("Terrain Debug - Fixing Colors")
        self.win.requestProperties(props)
        
        # Sky color
        self.setBackgroundColor(0.5, 0.6, 0.8, 1)
        
        # Generate simple test terrain
        print("Generating debug terrain...")
        self.terrain = self.create_debug_terrain()
        print("Terrain generated!")
        
        # Camera
        self.camera_pos = Point3(0, -40, 20)
        self.camera.setPos(self.camera_pos)
        self.camera.lookAt(0, 0, 0)
        
        # Simple movement
        self.keys = {"w": False, "s": False, "a": False, "d": False,
                     "space": False, "shift": False}
        self.speed = 15.0
        
        for key in self.keys:
            self.accept(key, self.set_key, [key, True])
            self.accept(f"{key}-up", self.set_key, [key, False])
        self.accept("escape", self.userExit)
        self.accept("r", self.reset_camera)
        
        self.taskMgr.add(self.move_task, "move")
        
        # Lighting - IMPORTANT: Need good lighting to see vertex colors
        alight = AmbientLight('alight')
        alight.setColor((0.5, 0.5, 0.5, 1))  # Brighter ambient
        alnp = self.render.attachNewNode(alight)
        self.render.setLight(alnp)
        
        sun = DirectionalLight('sun')
        sun.setColor((1.0, 1.0, 1.0, 1))  # White light
        sun_np = self.render.attachNewNode(sun)
        sun_np.setHpr(-45, -60, 0)
        self.render.setLight(sun_np)
        
        # Info
        from direct.gui.OnscreenText import OnscreenText
        self.info = OnscreenText(
            text="Debug Terrain - Testing Colors\nHeight zones should show: Green(low) -> Brown -> White(high)",
            pos=(0, 0.93), scale=0.04, fg=(1, 1, 1, 1)
        )
        
        self.debug_text = OnscreenText(
            text="",
            pos=(0, -0.93), scale=0.04, fg=(1, 1, 0, 1),
            mayChange=True
        )
    
    def create_debug_terrain(self):
        """Create simple terrain with clear height-based colors"""
        
        # Small terrain for testing
        size = 50
        resolution = 30
        
        # Create simple height pattern for testing
        heightmap = np.zeros((resolution, resolution))
        
        # Create a gradient from left to right for testing colors
        for j in range(resolution):
            for i in range(resolution):
                # Simple gradient + some waves
                x = (i / (resolution - 1) - 0.5) * 2
                y = (j / (resolution - 1) - 0.5) * 2
                
                # Height increases from left to right
                height = i / (resolution - 1) * 10  # 0 to 10
                
                # Add some variation
                height += math.sin(x * 5) * 1
                height += math.sin(y * 5) * 1
                
                heightmap[j, i] = height
        
        # Get height range
        min_height = np.min(heightmap)
        max_height = np.max(heightmap)
        print(f"Height range: {min_height:.2f} to {max_height:.2f}")
        
        # Create vertex data - using V3c4 format (position + color, no normals for now)
        vformat = GeomVertexFormat.getV3c4()
        vdata = GeomVertexData('terrain', vformat, Geom.UHStatic)
        vdata.setNumRows(resolution * resolution)
        
        vertex = GeomVertexWriter(vdata, 'vertex')
        color = GeomVertexWriter(vdata, 'color')
        
        # Track color distribution
        color_counts = {"green": 0, "brown": 0, "white": 0, "other": 0}
        
        # Generate vertices with debug colors
        for j in range(resolution):
            for i in range(resolution):
                # World position
                x = (i / (resolution - 1) - 0.5) * size
                y = (j / (resolution - 1) - 0.5) * size
                z = heightmap[j, i]
                
                vertex.addData3(x, y, z)
                
                # Simple height-based coloring for debugging
                h_norm = (z - min_height) / (max_height - min_height + 0.001)
                
                if h_norm < 0.33:  # Low - green
                    color.addData4(0, 1, 0, 1)  # Pure green
                    color_counts["green"] += 1
                elif h_norm < 0.66:  # Mid - brown
                    color.addData4(0.6, 0.3, 0, 1)  # Brown
                    color_counts["brown"] += 1
                else:  # High - white
                    color.addData4(1, 1, 1, 1)  # White
                    color_counts["white"] += 1
        
        print(f"Color distribution: {color_counts}")
        
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
        
        # IMPORTANT: Enable vertex colors
        terrain_np.setRenderModeWireframe()  # Try wireframe first
        
        # After 2 seconds, switch to solid with vertex colors
        def enable_vertex_colors(task):
            terrain_np.clearRenderMode()  # Clear wireframe
            terrain_np.setColorScale(1, 1, 1, 1)  # Ensure no color scaling
            terrain_np.setLightOff()  # Turn off lighting to see pure vertex colors
            self.debug_text.setText("Vertex colors enabled, lighting off")
            return Task.done
        
        self.taskMgr.doMethodLater(2.0, enable_vertex_colors, 'enable_colors')
        
        # After 4 seconds, turn lighting back on
        def enable_lighting(task):
            terrain_np.clearLight()  # Clear light off
            self.debug_text.setText("Lighting re-enabled with vertex colors")
            return Task.done
        
        self.taskMgr.doMethodLater(4.0, enable_lighting, 'enable_lighting')
        
        return terrain_np
    
    def set_key(self, key, value):
        self.keys[key] = value
    
    def reset_camera(self):
        self.camera_pos = Point3(0, -40, 20)
        self.camera.setPos(self.camera_pos)
        self.camera.lookAt(0, 0, 0)
    
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
        
        self.camera.setPos(self.camera_pos)
        return Task.cont

if __name__ == "__main__":
    print("=== Terrain Color Debug ===")
    print("Testing vertex color rendering")
    print("Should show: Wireframe -> Vertex colors (no light) -> Vertex colors (with light)")
    app = DebugTerrain()
    app.run()
