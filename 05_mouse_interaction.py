"""
05_mouse_interaction.py - Mouse interaction example
Click and drag to rotate the camera around the scene
Scroll to zoom in/out
"""

from direct.showbase.ShowBase import ShowBase
from panda3d.core import Point3, Vec3
from direct.task import Task
from math import sin, cos, pi

class MouseInteraction(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        
        # Set window title
        from panda3d.core import WindowProperties
        props = WindowProperties()
        props.setTitle("Mouse Interaction")
        self.win.requestProperties(props)
        
        # Set background color
        self.setBackgroundColor(0.05, 0.05, 0.15, 1)
        
        # Create a scene with multiple objects
        self.objects = []
        
        # Create a grid of cubes
        for x in range(-2, 3):
            for y in range(-2, 3):
                cube = self.loader.loadModel("models/environment")
                cube.reparentTo(self.render)
                cube.setScale(0.3, 0.3, 0.3)
                cube.setPos(x * 2, y * 2, 0)
                
                # Color based on position
                r = (x + 2) / 4.0
                g = (y + 2) / 4.0
                b = 0.5
                cube.setColor(r, g, b, 1)
                
                self.objects.append(cube)
        
        # Camera control variables
        self.cameraDist = 20
        self.cameraHpr = Vec3(0, -30, 0)  # Heading, Pitch, Roll
        self.lastMousePos = None
        self.mouseDown = False
        
        # Set initial camera position
        self.updateCamera()
        
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
        
        # Set up mouse controls
        self.accept("mouse1", self.onMouseDown)
        self.accept("mouse1-up", self.onMouseUp)
        self.accept("wheel_up", self.zoomIn)
        self.accept("wheel_down", self.zoomOut)
        
        # Reset camera
        self.accept("r", self.resetCamera)
        
        # Escape to quit
        self.accept("escape", self.userExit)
        
        # Add tasks
        self.taskMgr.add(self.mouseTask, "MouseTask")
        self.taskMgr.add(self.animateObjects, "AnimateObjects")
        
        # Instructions
        from direct.gui.OnscreenText import OnscreenText
        self.instructions = OnscreenText(
            text="Mouse Controls:\nLeft Click + Drag - Rotate camera\n" +
                 "Scroll - Zoom in/out\nR - Reset camera | ESC - Exit",
            style=1, 
            fg=(1, 1, 1, 1),
            pos=(-0.95, 0.9), 
            scale=0.04,
            align=OnscreenText.A_left
        )
    
    def onMouseDown(self):
        self.mouseDown = True
        # Store the initial mouse position
        if self.mouseWatcherNode.hasMouse():
            self.lastMousePos = Vec3(self.mouseWatcherNode.getMouseX(), 
                                     self.mouseWatcherNode.getMouseY(), 0)
    
    def onMouseUp(self):
        self.mouseDown = False
        self.lastMousePos = None
    
    def zoomIn(self):
        self.cameraDist = max(5, self.cameraDist - 2)
        self.updateCamera()
    
    def zoomOut(self):
        self.cameraDist = min(50, self.cameraDist + 2)
        self.updateCamera()
    
    def resetCamera(self):
        self.cameraDist = 20
        self.cameraHpr = Vec3(0, -30, 0)
        self.updateCamera()
    
    def updateCamera(self):
        # Convert spherical coordinates to Cartesian
        heading = self.cameraHpr.x * pi / 180
        pitch = self.cameraHpr.y * pi / 180
        
        x = self.cameraDist * cos(pitch) * sin(heading)
        y = -self.cameraDist * cos(pitch) * cos(heading)
        z = self.cameraDist * sin(pitch)
        
        self.camera.setPos(x, y, z)
        self.camera.lookAt(0, 0, 0)
    
    def mouseTask(self, task):
        if self.mouseDown and self.mouseWatcherNode.hasMouse():
            # Get current mouse position
            currentPos = Vec3(self.mouseWatcherNode.getMouseX(),
                             self.mouseWatcherNode.getMouseY(), 0)
            
            if self.lastMousePos:
                # Calculate the difference
                diff = currentPos - self.lastMousePos
                
                # Update camera rotation based on mouse movement
                self.cameraHpr.x += diff.x * 100  # Heading
                self.cameraHpr.y = max(-89, min(89, self.cameraHpr.y - diff.y * 100))  # Pitch (clamped)
                
                self.updateCamera()
            
            self.lastMousePos = currentPos
        
        return Task.cont
    
    def animateObjects(self, task):
        # Animate the cubes
        for i, obj in enumerate(self.objects):
            # Gentle rotation
            obj.setH(task.time * 10 + i * 10)
            
            # Pulsing scale
            scale = 0.3 + sin(task.time * 2 + i * 0.2) * 0.05
            obj.setScale(scale, scale, scale)
        
        return Task.cont

# Run the application
if __name__ == "__main__":
    app = MouseInteraction()
    app.run()
