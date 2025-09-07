"""
08.03_terrain_fixed_rotation.py - Fixed state management for both position AND rotation
Based on working terrain with proper camera state tracking
"""

from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    WindowProperties, Point3, Vec3,
    GeomNode, GeomTriangles, Geom,
    GeomVertexFormat, GeomVertexData, GeomVertexWriter,
    AmbientLight, DirectionalLight
)
from direct.task import Task
import numpy as np
import math

class FixedStateTerrain(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        
        # Window setup
        props = WindowProperties()
        props.setTitle("Terrain with Fixed Camera State Management")
        self.win.requestProperties(props)
        
        # Sky color
        self.setBackgroundColor(0.5, 0.6, 0.8, 1)
        
        # Generate terrain
        print("Generating terrain...")
        self.terrain = self.create_terrain()
        print("Terrain ready!")
        
        # CRITICAL: Camera state management - track BOTH position and rotation
        self.camera_pos = Point3(0, -40, 20)
        self.camera_hpr = Vec3(0, 0, 0)  # Heading, Pitch, Roll
        
        # Apply initial camera state
        self.camera.setPos(self.camera_pos)
        self.camera.setHpr(self.camera_hpr)
        self.camera.lookAt(0, 0, 5)
        # Store the initial HPR after lookAt
        self.camera_hpr = self.camera.getHpr()
        
        # Movement controls
        self.keys = {
            "w": False, "s": False, "a": False, "d": False,
            "space": False, "shift": False, "q": False, "e": False
        }
        self.move_speed = 15.0
        self.rotate_speed = 45.0  # degrees per second
        
        # Key bindings
        for key in self.keys:
            self.accept(key, self.set_key, [key, True])
            self.accept(f"{key}-up", self.set_key, [key, False])
        self.accept("escape", self.userExit)
        self.accept("r", self.reset_camera)
        
        self.taskMgr.add(self.update_camera, "update_camera")
        
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
            text="Fixed Camera State Management",
            pos=(0, 0.95), scale=0.05, fg=(1, 1, 1, 1)
        )
        
        self.controls = OnscreenText(
            text="WASD: Move | Q/E: Rotate | Space/Shift: Up/Down | R: Reset | ESC: Exit",
            pos=(0, 0.88), scale=0.04, fg=(0.9, 0.9, 0.9, 1)
        )
        
        self.state_text = OnscreenText(
            text="",
            pos=(0, -0.95), scale=0.04,
            fg=(1, 1, 0, 1), mayChange=True
        )
        
        self.info_text = OnscreenText(
            text="Position and rotation are now properly tracked",
            pos=(0, -0.88), scale=0.035,
            fg=(0.8, 0.8, 0.8, 1)
        )
    
    def create_terrain(self):
        """Create simple terrain with NumPy"""
        
        # Parameters
        size = 80
        resolution = 40  # Lower for better performance
        
        # Set random seed
        np.random.seed(42)
        
        # Create coordinate arrays
        x = np.linspace(-size/2, size/2, resolution)
        y = np.linspace(-size/2, size/2, resolution)
        X, Y = np.meshgrid(x, y)
        
        # Create heightmap
        heightmap = np.ones((resolution, resolution)) * 3.0
        
        # Appalachian-style ridges
        angle = np.radians(30)
        X_rot = X * np.cos(angle) - Y * np.sin(angle)
        Y_rot = X * np.sin(angle) + Y * np.cos(angle)
        
        # Ridge pattern
        ridge_spacing = 15.0
        ridge_height = 8.0
        ridges = ridge_height * (0.5 + 0.5 * np.cos(X_rot / ridge_spacing * 2 * np.pi))
        heightmap += ridges
        
        # Valleys
        valley_mask = np.sin(X_rot / ridge_spacing * np.pi)
        valley_areas = valley_mask < -0.3
        heightmap[valley_areas] *= 0.5
        
        # Variation
        variation = 2.0 * np.sin(Y_rot * 0.05) * np.cos(Y_rot * 0.03)
        heightmap += variation
        
        # Simple noise
        noise = np.random.randn(resolution, resolution) * 0.5
        heightmap += noise
        
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
        
        # Generate vertices
        for j in range(resolution):
            for i in range(resolution):
                # Position
                vertex.addData3(x[i], y[j], heightmap[j, i])
                
                # Simple normal
                normal.addData3(0, 0, 1)
                
                # Height-based color
                h_norm = (heightmap[j, i] - min_h) / (max_h - min_h + 0.001)
                
                if h_norm < 0.3:  # Valley - green
                    r, g, b = 0.1, 0.4, 0.1
                elif h_norm < 0.6:  # Slopes - brown
                    t = (h_norm - 0.3) / 0.3
                    r = 0.1 + t * 0.4
                    g = 0.4 - t * 0.15
                    b = 0.1 + t * 0.1
                else:  # Peak - white
                    t = (h_norm - 0.6) / 0.4
                    r = 0.5 + t * 0.5
                    g = 0.25 + t * 0.75
                    b = 0.2 + t * 0.8
                
                color.addData4(r, g, b, 1.0)
        
        # Calculate proper normals
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
    
    def reset_camera(self):
        """Reset camera position AND rotation"""
        self.camera_pos = Point3(0, -40, 20)
        self.camera_hpr = Vec3(0, 0, 0)
        
        # Apply the reset
        self.camera.setPos(self.camera_pos)
        self.camera.setHpr(self.camera_hpr)
        self.camera.lookAt(0, 0, 5)
        # Store the HPR after lookAt
        self.camera_hpr = self.camera.getHpr()
        
        print("Camera reset to start position and rotation")
    
    def update_camera(self, task):
        """Update camera with proper state management"""
        dt = 0.016  # 60 FPS
        
        # POSITION UPDATES
        if self.keys["w"]:
            self.camera_pos.y += self.move_speed * dt
        if self.keys["s"]:
            self.camera_pos.y -= self.move_speed * dt
        if self.keys["a"]:
            self.camera_pos.x -= self.move_speed * dt
        if self.keys["d"]:
            self.camera_pos.x += self.move_speed * dt
        if self.keys["space"]:
            self.camera_pos.z += self.move_speed * dt
        if self.keys["shift"]:
            self.camera_pos.z -= self.move_speed * dt
        
        # ROTATION UPDATES - Update our stored rotation
        if self.keys["q"]:
            self.camera_hpr.x += self.rotate_speed * dt  # Heading (yaw)
        if self.keys["e"]:
            self.camera_hpr.x -= self.rotate_speed * dt
        
        # Apply the stored states to the camera
        self.camera.setPos(self.camera_pos)
        self.camera.setHpr(self.camera_hpr)
        
        # Update display with both position and rotation
        self.state_text.setText(
            f"Pos: ({self.camera_pos.x:.1f}, {self.camera_pos.y:.1f}, {self.camera_pos.z:.1f}) | "
            f"Rot: H={self.camera_hpr.x:.1f}°"
        )
        
        return Task.cont

if __name__ == "__main__":
    print("\n=== Fixed Camera State Management ===")
    print("Both position AND rotation are now properly tracked")
    print("Camera rotation will persist when you stop pressing Q/E")
    app = FixedStateTerrain()
    app.run()
