"""
06_simple_movement_debug.py - Debug version to understand movement issues
"""

from direct.showbase.ShowBase import ShowBase
from panda3d.core import WindowProperties
from direct.task import Task

class SimpleMovement(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        
        # Set window title
        props = WindowProperties()
        props.setTitle("Simple 3D Movement - DEBUG")
        self.win.requestProperties(props)
        
        # Set background color (sky blue)
        self.setBackgroundColor(0.5, 0.8, 1, 1)
        
        # Create a simple "ground"
        ground = self.loader.loadModel("models/environment")
        ground.reparentTo(self.render)
        ground.setScale(20, 20, 0.1)
        ground.setPos(0, 0, -2)
        ground.setColor(0.2, 0.8, 0.2, 1)
        
        # Add reference cubes
        positions = [(5, 5, 0), (-5, 5, 0), (5, -5, 0), (-5, -5, 0), (0, 10, 0)]
        for x, y, z in positions:
            cube = self.loader.loadModel("models/environment")
            cube.reparentTo(self.render)
            cube.setScale(1, 1, 2)
            cube.setPos(x, y, z)
            cube.setColor(0.5, 0.5, 0.8, 1)
        
        # Camera starting position
        self.camera.setPos(0, 0, 1)
        
        # Movement speed - let's make it bigger to see if that helps
        self.move_speed = 0.5  # Increased from 0.1
        
        # Movement state
        self.keys = {
            "forward": False,
            "backward": False,
            "left": False,
            "right": False,
            "up": False,
            "down": False,
        }
        
        # Debug counter
        self.frame_count = 0
        self.move_count = 0
        
        # Set up key bindings with debug output
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
        
        # Add lighting
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
        
        # Debug text
        from direct.gui.OnscreenText import OnscreenText
        self.instructions = OnscreenText(
            text="DEBUG MODE - Press keys and watch console",
            pos=(0, 0.9), 
            scale=0.05,
            fg=(1, 1, 1, 1),
            mayChange=True
        )
        
        self.pos_text = OnscreenText(
            text="Pos: (0, 0, 1)",
            pos=(0, -0.9),
            scale=0.05,
            fg=(1, 1, 0, 1),
            mayChange=True
        )
        
        self.debug_text = OnscreenText(
            text="Frames: 0 | Moves: 0",
            pos=(0, -0.8),
            scale=0.04,
            fg=(1, 0, 0, 1),
            mayChange=True
        )
    
    def setKey(self, key, value):
        print(f"Key event: {key} = {value}")
        self.keys[key] = value
    
    def moveTask(self, task):
        self.frame_count += 1
        
        # Get current camera position
        pos = self.camera.getPos()
        old_pos = pos.copy()  # Save old position
        
        # Check which keys are pressed
        moving = False
        if self.keys["forward"]:
            pos.y += self.move_speed
            moving = True
        if self.keys["backward"]:
            pos.y -= self.move_speed
            moving = True
        if self.keys["left"]:
            pos.x -= self.move_speed
            moving = True
        if self.keys["right"]:
            pos.x += self.move_speed
            moving = True
        if self.keys["up"]:
            pos.z += self.move_speed
            moving = True
        if self.keys["down"]:
            pos.z -= self.move_speed
            moving = True
        
        # Apply the new position
        self.camera.setPos(pos)
        
        # Debug: did we actually move?
        if moving:
            self.move_count += 1
            print(f"Frame {self.frame_count}: Moved from {old_pos} to {pos}")
        
        # Update displays
        self.pos_text.setText(f"Pos: ({pos.x:.2f}, {pos.y:.2f}, {pos.z:.2f})")
        self.debug_text.setText(f"Frames: {self.frame_count} | Moves: {self.move_count} | Keys: {sum(self.keys.values())} pressed")
        
        # Continue the task
        return Task.cont

# Run the application
if __name__ == "__main__":
    print("Starting debug version...")
    print("Watch this console for key events and movement logs")
    app = SimpleMovement()
    app.run()

