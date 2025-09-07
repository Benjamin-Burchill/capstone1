"""
04_keyboard_control.py - Interactive keyboard controls
Use arrow keys or WASD to move a cube around
"""

from direct.showbase.ShowBase import ShowBase
from panda3d.core import Point3, Vec3
from direct.showbase.ShowBase import globalClock

class KeyboardControl(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        
        # Set window title
        from panda3d.core import WindowProperties
        props = WindowProperties()
        props.setTitle("Keyboard Control")
        self.win.requestProperties(props)
        
        # Set background color
        self.setBackgroundColor(0.1, 0.1, 0.1, 1)
        
        # Load the cube model
        self.cube = self.loader.loadModel("models/environment")
        self.cube.reparentTo(self.render)
        self.cube.setScale(0.5, 0.5, 0.5)
        self.cube.setPos(0, 0, 0)
        self.cube.setColor(0.5, 0.8, 1, 1)  # Light blue
        
        # Movement speed
        self.speed = 5.0
        
        # Set up the camera
        self.camera.setPos(0, -20, 10)
        self.camera.lookAt(0, 0, 0)
        
        # Add lighting
        from panda3d.core import DirectionalLight, AmbientLight
        
        alight = AmbientLight('alight')
        alight.setColor((0.3, 0.3, 0.3, 1))
        alnp = self.render.attachNewNode(alight)
        self.render.setLight(alnp)
        
        dlight = DirectionalLight('dlight')
        dlight.setColor((0.7, 0.7, 0.7, 1))
        dlnp = self.render.attachNewNode(dlight)
        dlnp.setHpr(-45, -45, 0)
        self.render.setLight(dlnp)
        
        # Set up keyboard controls
        self.keys = {
            "left": False,
            "right": False,
            "up": False,
            "down": False,
            "space": False,
            "shift": False
        }
        
        # Accept keyboard events
        self.accept("arrow_left", self.setKey, ["left", True])
        self.accept("arrow_left-up", self.setKey, ["left", False])
        self.accept("arrow_right", self.setKey, ["right", True])
        self.accept("arrow_right-up", self.setKey, ["right", False])
        self.accept("arrow_up", self.setKey, ["up", True])
        self.accept("arrow_up-up", self.setKey, ["up", False])
        self.accept("arrow_down", self.setKey, ["down", True])
        self.accept("arrow_down-up", self.setKey, ["down", False])
        
        # WASD controls
        self.accept("a", self.setKey, ["left", True])
        self.accept("a-up", self.setKey, ["left", False])
        self.accept("d", self.setKey, ["right", True])
        self.accept("d-up", self.setKey, ["right", False])
        self.accept("w", self.setKey, ["up", True])
        self.accept("w-up", self.setKey, ["up", False])
        self.accept("s", self.setKey, ["down", True])
        self.accept("s-up", self.setKey, ["down", False])
        
        # Vertical movement
        self.accept("space", self.setKey, ["space", True])
        self.accept("space-up", self.setKey, ["space", False])
        self.accept("shift", self.setKey, ["shift", True])
        self.accept("shift-up", self.setKey, ["shift", False])
        
        # Reset position
        self.accept("r", self.resetPosition)
        
        # Escape to quit
        self.accept("escape", self.userExit)
        
        # Add the movement task
        self.taskMgr.add(self.moveTask, "MoveTask")
        
        # Instructions
        from direct.gui.OnscreenText import OnscreenText
        self.instructions = OnscreenText(
            text="Keyboard Controls:\nArrow Keys or WASD - Move horizontally\n" +
                 "Space - Move up | Shift - Move down\nR - Reset position | ESC - Exit",
            style=1, 
            fg=(1, 1, 1, 1),
            pos=(-0.95, 0.9), 
            scale=0.04,
            align=OnscreenText.A_left
        )
        
        # Position display
        self.posText = OnscreenText(
            text="Position: (0.0, 0.0, 0.0)",
            style=1,
            fg=(1, 1, 0.5, 1),
            pos=(-0.95, -0.9),
            scale=0.04,
            align=OnscreenText.A_left
        )
    
    def setKey(self, key, value):
        self.keys[key] = value
    
    def resetPosition(self):
        self.cube.setPos(0, 0, 0)
    
    def moveTask(self, task):
        dt = globalClock.getDt()
        pos = self.cube.getPos()
        
        # Calculate movement based on pressed keys
        if self.keys["left"]:
            pos.x -= self.speed * dt
        if self.keys["right"]:
            pos.x += self.speed * dt
        if self.keys["up"]:
            pos.y += self.speed * dt
        if self.keys["down"]:
            pos.y -= self.speed * dt
        if self.keys["space"]:
            pos.z += self.speed * dt
        if self.keys["shift"]:
            pos.z -= self.speed * dt
        
        # Apply the new position
        self.cube.setPos(pos)
        
        # Update position display
        self.posText.setText(f"Position: ({pos.x:.1f}, {pos.y:.1f}, {pos.z:.1f})")
        
        # Rotate the cube slowly for visual effect
        self.cube.setH(self.cube.getH() + dt * 30)
        
        return task.cont

# Run the application
if __name__ == "__main__":
    app = KeyboardControl()
    app.run()
