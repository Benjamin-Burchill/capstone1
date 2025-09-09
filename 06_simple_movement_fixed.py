"""
06_simple_movement_fixed.py - Simple 3D movement with minimal dependencies
Move around in a basic 3D environment - the foundation for any 3D game
"""

from direct.showbase.ShowBase import ShowBase
from panda3d.core import WindowProperties

class SimpleMovement(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        
        # Set window title
        props = WindowProperties()
        props.setTitle("Simple 3D Movement")
        self.win.requestProperties(props)
        
        # Set background color (sky blue)
        self.setBackgroundColor(0.5, 0.8, 1, 1)
        
        # Create a simple "ground" - just a flat green square
        ground = self.loader.loadModel("models/environment")
        ground.reparentTo(self.render)
        ground.setScale(20, 20, 0.1)  # Make it wide and flat
        ground.setPos(0, 0, -2)  # Position it below us
        ground.setColor(0.2, 0.8, 0.2, 1)  # Green color
        
        # Add some reference cubes so we can see movement
        positions = [
            (5, 5, 0),
            (-5, 5, 0),
            (5, -5, 0),
            (-5, -5, 0),
            (0, 10, 0),
        ]
        
        for x, y, z in positions:
            cube = self.loader.loadModel("models/environment")
            cube.reparentTo(self.render)
            cube.setScale(1, 1, 2)  # Make them tall
            cube.setPos(x, y, z)
            cube.setColor(0.5, 0.5, 0.8, 1)  # Blue-ish color
        
        # Camera starting position
        self.camera.setPos(0, 0, 1)  # Start at eye level
        
        # Movement speed
        self.move_speed = 0.1  # Units per frame (simpler than delta time)
        
        # Movement state
        self.keys = {
            "forward": False,
            "backward": False,
            "left": False,
            "right": False,
            "up": False,
            "down": False,
        }
        
        # Set up key bindings
        self.accept("w", self.setKey, ["forward", True])
        self.accept("w-up", self.setKey, ["forward", False])
        self.accept("s", self.setKey, ["backward", True])
        self.accept("s-up", self.setKey, ["backward", False])
        self.accept("a", self.setKey, ["left", True])
        self.accept("a-up", self.setKey, ["left", False])
        self.accept("d", self.setKey, ["right", True])
        self.accept("d-up", self.setKey, ["right", False])
        self.accept("space", self.setKey, ["up", True])
        self.accept("space-up", self.setKey, ["up", False])
        self.accept("shift", self.setKey, ["down", True])
        self.accept("shift-up", self.setKey, ["down", False])
        self.accept("escape", self.userExit)
        
        # Start the movement task
        self.taskMgr.add(self.moveTask, "MoveTask")
        
        # Add basic lighting
        from panda3d.core import AmbientLight, DirectionalLight
        
        alight = AmbientLight('alight')
        alight.setColor((0.5, 0.5, 0.5, 1))
        alnp = self.render.attachNewNode(alight)
        self.render.setLight(alnp)
        
        dlight = DirectionalLight('dlight')
        dlight.setColor((0.5, 0.5, 0.5, 1))
        dlnp = self.render.attachNewNode(dlight)
        dlnp.setHpr(-45, -45, 0)
        self.render.setLight(dlnp)
        
        # Simple text instructions (without alignment issues)
        from direct.gui.OnscreenText import OnscreenText
        self.instructions = OnscreenText(
            text="WASD: Move | Space/Shift: Up/Down | ESC: Exit",
            pos=(0, 0.9), 
            scale=0.05,
            fg=(1, 1, 1, 1),
            mayChange=True
        )
        
        # Position display
        self.pos_text = OnscreenText(
            text="Pos: (0, 0, 1)",
            pos=(0, -0.9),
            scale=0.05,
            fg=(1, 1, 0, 1),
            mayChange=True
        )
    
    def setKey(self, key, value):
        self.keys[key] = value
    
    def moveTask(self, task):
        # Get current camera position
        pos = self.camera.getPos()
        
        # Simple movement without delta time (frame-based)
        if self.keys["forward"]:
            pos.y += self.move_speed
        if self.keys["backward"]:
            pos.y -= self.move_speed
        if self.keys["left"]:
            pos.x -= self.move_speed
        if self.keys["right"]:
            pos.x += self.move_speed
        if self.keys["up"]:
            pos.z += self.move_speed
        if self.keys["down"]:
            pos.z -= self.move_speed
        
        # Apply the new position
        self.camera.setPos(pos)
        
        # Update position display
        self.pos_text.setText(f"Pos: ({pos.x:.1f}, {pos.y:.1f}, {pos.z:.1f})")
        
        # Continue the task
        from direct.task import Task
        return Task.cont

# Run the application
if __name__ == "__main__":
    app = SimpleMovement()
    app.run()

