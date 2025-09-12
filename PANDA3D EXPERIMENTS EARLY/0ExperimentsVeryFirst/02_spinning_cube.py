"""
02_spinning_cube.py - A simple rotating cube
Shows basic 3D object loading and animation
"""

from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from math import sin, cos
from panda3d.core import Point3

class SpinningCube(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        
        # Set window title
        from panda3d.core import WindowProperties
        props = WindowProperties()
        props.setTitle("Spinning Cube")
        self.win.requestProperties(props)
        
        # Load the environment model (a simple cube)
        # Panda3D comes with some built-in models
        self.cube = self.loader.loadModel("models/environment")
        
        # Reparent the model to render
        self.cube.reparentTo(self.render)
        
        # Apply scale and initial position
        self.cube.setScale(0.25, 0.25, 0.25)
        self.cube.setPos(0, 0, 0)
        
        # Set up the camera
        self.camera.setPos(0, -20, 3)
        self.camera.lookAt(0, 0, 0)
        
        # Add a light
        from panda3d.core import DirectionalLight, AmbientLight
        
        # Create ambient light
        alight = AmbientLight('alight')
        alight.setColor((0.2, 0.2, 0.2, 1))
        alnp = self.render.attachNewNode(alight)
        self.render.setLight(alnp)
        
        # Create directional light
        dlight = DirectionalLight('dlight')
        dlight.setColor((0.8, 0.8, 0.8, 1))
        dlnp = self.render.attachNewNode(dlight)
        dlnp.setHpr(-45, -45, 0)
        self.render.setLight(dlnp)
        
        # Add the spin task
        self.taskMgr.add(self.spinCubeTask, "SpinCubeTask")
        
        # Instructions
        from direct.gui.OnscreenText import OnscreenText
        self.title = OnscreenText(
            text="Spinning Cube\nPress ESC to exit",
            style=1, 
            fg=(1, 1, 1, 1),
            pos=(0, 0.9), 
            scale=0.05
        )
        
        # Accept the escape key to quit
        self.accept("escape", self.userExit)
    
    def spinCubeTask(self, task):
        # Calculate the new orientation
        angleDegrees = task.time * 30.0  # 30 degrees per second
        self.cube.setHpr(angleDegrees, angleDegrees * 0.5, angleDegrees * 0.3)
        
        # Continue the task
        return Task.cont

# Run the application
if __name__ == "__main__":
    app = SpinningCube()
    app.run()
