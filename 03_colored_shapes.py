"""
03_colored_shapes.py - Creating simple colored 3D shapes
Shows how to create basic geometric shapes with colors
"""

from direct.showbase.ShowBase import ShowBase
from panda3d.core import CardMaker, NodePath
from panda3d.core import Point3, Vec3, Vec4
from direct.task import Task
from math import sin

class ColoredShapes(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        
        # Set window title
        from panda3d.core import WindowProperties
        props = WindowProperties()
        props.setTitle("Colored Shapes")
        self.win.requestProperties(props)
        
        # Set background color
        self.setBackgroundColor(0.1, 0.1, 0.2, 1)
        
        # Create multiple colored cubes at different positions
        self.shapes = []
        
        # Load and position multiple cubes with different colors
        positions = [
            (-3, 0, 0, (1, 0, 0, 1)),  # Red cube on left
            (0, 0, 0, (0, 1, 0, 1)),   # Green cube in center
            (3, 0, 0, (0, 0, 1, 1)),   # Blue cube on right
        ]
        
        for x, y, z, color in positions:
            cube = self.loader.loadModel("models/environment")
            cube.reparentTo(self.render)
            cube.setScale(0.5, 0.5, 0.5)
            cube.setPos(x, y, z)
            cube.setColor(color)
            self.shapes.append(cube)
        
        # Set up the camera
        self.camera.setPos(0, -15, 5)
        self.camera.lookAt(0, 0, 0)
        
        # Add lighting
        from panda3d.core import DirectionalLight, AmbientLight
        
        # Ambient light
        alight = AmbientLight('alight')
        alight.setColor((0.3, 0.3, 0.3, 1))
        alnp = self.render.attachNewNode(alight)
        self.render.setLight(alnp)
        
        # Directional light
        dlight = DirectionalLight('dlight')
        dlight.setColor((0.7, 0.7, 0.7, 1))
        dlnp = self.render.attachNewNode(dlight)
        dlnp.setHpr(-45, -45, 0)
        self.render.setLight(dlnp)
        
        # Add animation task
        self.taskMgr.add(self.animateShapes, "AnimateShapes")
        
        # Instructions
        from direct.gui.OnscreenText import OnscreenText
        self.title = OnscreenText(
            text="Colored Shapes - RGB Cubes\nPress ESC to exit",
            style=1, 
            fg=(1, 1, 1, 1),
            pos=(0, 0.9), 
            scale=0.05
        )
        
        # Accept the escape key to quit
        self.accept("escape", self.userExit)
    
    def animateShapes(self, task):
        # Animate each shape differently
        for i, shape in enumerate(self.shapes):
            # Different rotation speeds for each shape
            speed = 20 * (i + 1)
            shape.setH(task.time * speed)
            
            # Gentle up and down motion
            shape.setZ(sin(task.time * 2 + i) * 0.5)
        
        return Task.cont

# Run the application
if __name__ == "__main__":
    app = ColoredShapes()
    app.run()
