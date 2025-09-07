"""
06_movement_diagnostic.py - Diagnose why position resets
"""

from direct.showbase.ShowBase import ShowBase
from panda3d.core import WindowProperties, Point3
from direct.task import Task

class SimpleMovement(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        
        # Set window title
        props = WindowProperties()
        props.setTitle("Movement Diagnostic")
        self.win.requestProperties(props)
        
        # Set background color
        self.setBackgroundColor(0.5, 0.8, 1, 1)
        
        # Create ground
        ground = self.loader.loadModel("models/environment")
        ground.reparentTo(self.render)
        ground.setScale(20, 20, 0.1)
        ground.setPos(0, 0, -2)
        ground.setColor(0.2, 0.8, 0.2, 1)
        
        # Add reference cube at origin
        origin_marker = self.loader.loadModel("models/environment")
        origin_marker.reparentTo(self.render)
        origin_marker.setScale(0.2, 0.2, 5)
        origin_marker.setPos(0, 0, 0)
        origin_marker.setColor(1, 0, 0, 1)  # Red marker at origin
        
        # Add other reference cubes
        for x in [-5, 5]:
            for y in [-5, 5]:
                cube = self.loader.loadModel("models/environment")
                cube.reparentTo(self.render)
                cube.setScale(0.5, 0.5, 2)
                cube.setPos(x, y, 0)
                cube.setColor(0.5, 0.5, 0.8, 1)
        
        # IMPORTANT: Store our own position
        self.my_position = Point3(0, -3, 1)
        self.camera.setPos(self.my_position)
        
        # Movement speed
        self.speed = 3.0
        
        # Key states
        self.key_map = {
            "forward": False,
            "backward": False,
            "left": False,
            "right": False,
            "up": False,
            "down": False,
        }
        
        # Frame counter
        self.frame = 0
        
        # Bind keys
        self.accept("w", self.set_key, ["forward", True])
        self.accept("w-up", self.set_key, ["forward", False])
        self.accept("s", self.set_key, ["backward", True])
        self.accept("s-up", self.set_key, ["backward", False])
        self.accept("a", self.set_key, ["left", True])
        self.accept("a-up", self.set_key, ["left", False])
        self.accept("d", self.set_key, ["right", True])
        self.accept("d-up", self.set_key, ["right", False])
        self.accept("space", self.set_key, ["up", True])
        self.accept("space-up", self.set_key, ["up", False])
        self.accept("shift", self.set_key, ["down", True])
        self.accept("shift-up", self.set_key, ["down", False])
        
        self.accept("r", self.reset_position)
        self.accept("escape", self.userExit)
        
        # Start movement task
        self.taskMgr.add(self.update_movement, "update_movement")
        
        # Lighting
        from panda3d.core import AmbientLight, DirectionalLight
        alight = AmbientLight('alight')
        alight.setColor((0.6, 0.6, 0.6, 1))
        alnp = self.render.attachNewNode(alight)
        self.render.setLight(alnp)
        
        # UI Text
        from direct.gui.OnscreenText import OnscreenText
        
        self.instructions = OnscreenText(
            text="DIAGNOSTIC: Watch position values",
            pos=(0, 0.95),
            scale=0.04,
            fg=(1, 1, 1, 1)
        )
        
        self.pos_display = OnscreenText(
            text="",
            pos=(0, -0.85),
            scale=0.035,
            fg=(1, 1, 0, 1),
            mayChange=True
        )
        
        self.debug_display = OnscreenText(
            text="",
            pos=(0, -0.95),
            scale=0.035,
            fg=(1, 0.5, 0, 1),
            mayChange=True
        )
    
    def set_key(self, key, value):
        self.key_map[key] = value
        print(f"Key {key}: {value}")
    
    def reset_position(self):
        self.my_position = Point3(0, -3, 1)
        self.camera.setPos(self.my_position)
        print("Reset position to:", self.my_position)
    
    def update_movement(self, task):
        self.frame += 1
        dt = 0.016  # 60 FPS
        
        # Calculate velocity
        vel_x = 0
        vel_y = 0
        vel_z = 0
        
        if self.key_map["forward"]:
            vel_y = self.speed
        if self.key_map["backward"]:
            vel_y = -self.speed
        if self.key_map["left"]:
            vel_x = -self.speed
        if self.key_map["right"]:
            vel_x = self.speed
        if self.key_map["up"]:
            vel_z = self.speed
        if self.key_map["down"]:
            vel_z = -self.speed
        
        # METHOD 1: Update our stored position
        self.my_position.x += vel_x * dt
        self.my_position.y += vel_y * dt
        self.my_position.z += vel_z * dt
        
        # Set camera to our stored position
        self.camera.setPos(self.my_position)
        
        # Get camera position to verify
        actual_pos = self.camera.getPos()
        
        # Display both positions
        self.pos_display.setText(
            f"Stored Pos: ({self.my_position.x:.2f}, {self.my_position.y:.2f}, {self.my_position.z:.2f})\n" +
            f"Camera Pos: ({actual_pos.x:.2f}, {actual_pos.y:.2f}, {actual_pos.z:.2f})"
        )
        
        # Show velocity
        self.debug_display.setText(
            f"Frame: {self.frame} | Velocity: ({vel_x:.1f}, {vel_y:.1f}, {vel_z:.1f})"
        )
        
        # Log if there's a discrepancy
        if self.frame % 60 == 0:  # Every second
            if abs(actual_pos.x - self.my_position.x) > 0.01:
                print(f"WARNING: Position mismatch! Stored: {self.my_position}, Actual: {actual_pos}")
        
        return Task.cont

if __name__ == "__main__":
    print("=== DIAGNOSTIC MODE ===")
    print("Red pillar marks the origin (0,0)")
    print("Watch console for position mismatches")
    app = SimpleMovement()
    app.run()
