"""
06_simple_movement_working.py - Fixed 3D movement with proper state management
This version correctly maintains position state so you can move continuously
"""

from direct.showbase.ShowBase import ShowBase
from panda3d.core import WindowProperties, Point3
from direct.task import Task

class SimpleMovement(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        
        # Set window title
        props = WindowProperties()
        props.setTitle("3D Movement - Working!")
        self.win.requestProperties(props)
        
        # Set background color
        self.setBackgroundColor(0.5, 0.8, 1, 1)
        
        # Create ground plane
        ground = self.loader.loadModel("models/environment")
        ground.reparentTo(self.render)
        ground.setScale(30, 30, 0.1)
        ground.setPos(0, 0, -2)
        ground.setColor(0.2, 0.7, 0.2, 1)
        
        # Add grid of reference objects
        for x in range(-10, 11, 5):
            for y in range(-10, 11, 5):
                if x == 0 and y == 0:
                    # Red pillar at origin
                    marker = self.loader.loadModel("models/environment")
                    marker.reparentTo(self.render)
                    marker.setScale(0.3, 0.3, 5)
                    marker.setPos(0, 0, 0)
                    marker.setColor(1, 0, 0, 1)
                else:
                    # Blue cubes as landmarks
                    cube = self.loader.loadModel("models/environment")
                    cube.reparentTo(self.render)
                    cube.setScale(1, 1, 2)
                    cube.setPos(x, y, 0)
                    # Color varies by position for easier navigation
                    cube.setColor(0.3 + abs(x)*0.02, 0.3 + abs(y)*0.02, 0.8, 1)
        
        # CRITICAL: Maintain our own position state
        # This is the fix - we track position ourselves
        self.camera_position = Point3(0, -5, 2)  # Starting position
        self.camera.setPos(self.camera_position)
        
        # Movement parameters
        self.move_speed = 5.0  # Units per second
        
        # Key state tracking
        self.keys_pressed = {
            "w": False,
            "s": False,
            "a": False,
            "d": False,
            "space": False,
            "shift": False,
        }
        
        # Set up keyboard input
        # Forward/Backward
        self.accept("w", self.update_key_state, ["w", True])
        self.accept("w-up", self.update_key_state, ["w", False])
        self.accept("s", self.update_key_state, ["s", True])
        self.accept("s-up", self.update_key_state, ["s", False])
        
        # Left/Right
        self.accept("a", self.update_key_state, ["a", True])
        self.accept("a-up", self.update_key_state, ["a", False])
        self.accept("d", self.update_key_state, ["d", True])
        self.accept("d-up", self.update_key_state, ["d", False])
        
        # Up/Down
        self.accept("space", self.update_key_state, ["space", True])
        self.accept("space-up", self.update_key_state, ["space", False])
        self.accept("shift", self.update_key_state, ["shift", True])
        self.accept("shift-up", self.update_key_state, ["shift", False])
        
        # Utility keys
        self.accept("r", self.reset_to_start)
        self.accept("escape", self.userExit)
        
        # Start the movement update task
        self.taskMgr.add(self.movement_update_task, "movement_task")
        
        # Add lighting for better visibility
        from panda3d.core import AmbientLight, DirectionalLight
        
        ambient = AmbientLight('ambient')
        ambient.setColor((0.4, 0.4, 0.4, 1))
        ambient_np = self.render.attachNewNode(ambient)
        self.render.setLight(ambient_np)
        
        directional = DirectionalLight('directional')
        directional.setColor((0.6, 0.6, 0.6, 1))
        directional_np = self.render.attachNewNode(directional)
        directional_np.setHpr(-45, -45, 0)
        self.render.setLight(directional_np)
        
        # UI Text
        from direct.gui.OnscreenText import OnscreenText
        
        self.title_text = OnscreenText(
            text="3D Movement with State Management",
            pos=(0, 0.95),
            scale=0.05,
            fg=(1, 1, 1, 1)
        )
        
        self.control_text = OnscreenText(
            text="WASD: Move | Space: Up | Shift: Down | R: Reset | ESC: Exit",
            pos=(0, 0.88),
            scale=0.04,
            fg=(0.9, 0.9, 0.9, 1)
        )
        
        self.position_text = OnscreenText(
            text="Position: (0.0, -5.0, 2.0)",
            pos=(0, -0.92),
            scale=0.045,
            fg=(1, 1, 0, 1),
            mayChange=True
        )
        
        print("Movement system ready! Use WASD + Space/Shift to move.")
        print("Your position is being tracked independently of the camera.")
    
    def update_key_state(self, key, is_pressed):
        """Update the state of a key"""
        self.keys_pressed[key] = is_pressed
    
    def reset_to_start(self):
        """Reset position to starting point"""
        self.camera_position = Point3(0, -5, 2)
        self.camera.setPos(self.camera_position)
        print("Position reset to start")
    
    def movement_update_task(self, task):
        """Update movement every frame - with proper state management"""
        
        # Use a fixed delta time for consistent movement
        # In a real game, you'd calculate actual frame time
        dt = 0.016  # Assuming 60 FPS
        
        # Calculate movement based on pressed keys
        movement_vector = Point3(0, 0, 0)
        
        # Horizontal movement
        if self.keys_pressed["w"]:
            movement_vector.y += self.move_speed * dt
        if self.keys_pressed["s"]:
            movement_vector.y -= self.move_speed * dt
        if self.keys_pressed["a"]:
            movement_vector.x -= self.move_speed * dt
        if self.keys_pressed["d"]:
            movement_vector.x += self.move_speed * dt
        
        # Vertical movement
        if self.keys_pressed["space"]:
            movement_vector.z += self.move_speed * dt
        if self.keys_pressed["shift"]:
            movement_vector.z -= self.move_speed * dt
        
        # CRITICAL: Update OUR position state
        # This is the key - we maintain position ourselves
        self.camera_position.x += movement_vector.x
        self.camera_position.y += movement_vector.y
        self.camera_position.z += movement_vector.z
        
        # Apply our position to the camera
        self.camera.setPos(self.camera_position)
        
        # Update position display
        self.position_text.setText(
            f"Position: ({self.camera_position.x:.1f}, "
            f"{self.camera_position.y:.1f}, "
            f"{self.camera_position.z:.1f})"
        )
        
        return Task.cont

if __name__ == "__main__":
    app = SimpleMovement()
    app.run()

