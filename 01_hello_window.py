"""
01_hello_window.py - The absolute simplest Panda3D application
Creates a window with a gray background that you can close with ESC or the X button
"""

from direct.showbase.ShowBase import ShowBase

class HelloWindow(ShowBase):
    def __init__(self):
        # Initialize the ShowBase parent class
        ShowBase.__init__(self)
        
        # Set window title using properties
        from panda3d.core import WindowProperties
        props = WindowProperties()
        props.setTitle("Hello Panda3D!")
        self.win.requestProperties(props)
        
        # Add instruction text in the window
        from direct.gui.OnscreenText import OnscreenText
        self.title = OnscreenText(
            text="Hello Panda3D!\nPress ESC to exit",
            style=1, 
            fg=(1, 1, 1, 1),
            pos=(0, 0.8), 
            scale=0.07
        )
        
        # Accept the escape key to quit
        self.accept("escape", self.userExit)

# Run the application
if __name__ == "__main__":
    app = HelloWindow()
    app.run()
