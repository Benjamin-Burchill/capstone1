"""
Panda3D Common Imports and Usage Reference
This file serves as a quick reference to avoid dependency errors
"""

# ============================================
# CORRECT IMPORT PATTERNS
# ============================================

# Core imports
from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    Point3, Vec3, Vec4,
    WindowProperties,
    TextNode,  # For text alignment constants
    NodePath,
    CardMaker,
    AmbientLight, DirectionalLight, PointLight, Spotlight
)

# GUI imports
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import *  # For buttons, frames, etc.

# Task system
from direct.task import Task

# ============================================
# BUILT-IN GLOBALS (DO NOT IMPORT)
# ============================================
# These are automatically available when you inherit from ShowBase:
# - self.globalClock (for getDt())
# - self.loader (for loadModel())
# - self.render (scene graph root)
# - self.camera (default camera)
# - self.taskMgr (task manager)
# - self.win (graphics window)
# - self.mouseWatcherNode (mouse input)
# - self.accept() (for keyboard/mouse events)

# ============================================
# COMMON USAGE PATTERNS
# ============================================

class ExampleApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        
        # Window title (correct way)
        props = WindowProperties()
        props.setTitle("My Game")
        self.win.requestProperties(props)
        
        # Text alignment constants (use TextNode, not OnscreenText)
        text = OnscreenText(
            text="Hello",
            align=TextNode.ALeft,    # NOT OnscreenText.A_left
            # Other options: TextNode.ACenter, TextNode.ARight
        )
        
        # Get delta time (use self.globalClock)
        dt = self.globalClock.getDt()  # NOT globalClock.getDt()
        
        # Load models (use self.loader)
        model = self.loader.loadModel("models/environment")
        
        # Attach to scene (use self.render)
        model.reparentTo(self.render)
        
        # Accept keyboard events (use self.accept)
        self.accept("escape", self.userExit)
        
        # Add tasks (use self.taskMgr)
        self.taskMgr.add(self.update, "update")
    
    def update(self, task):
        # Task should return Task.cont to continue
        return Task.cont

# ============================================
# COMMON ERRORS AND FIXES
# ============================================

"""
ERROR: AttributeError: 'GraphicsWindow' object has no attribute 'setWindowTitle'
FIX: Use WindowProperties instead:
    props = WindowProperties()
    props.setTitle("Title")
    self.win.requestProperties(props)

ERROR: ImportError: cannot import name 'globalClock'
FIX: Use self.globalClock (it's built-in)

ERROR: AttributeError: type object 'OnscreenText' has no attribute 'A_left'
FIX: Use TextNode.ALeft instead

ERROR: NameError: name 'render' is not defined
FIX: Use self.render (it's a member of ShowBase)

ERROR: Models not showing up
FIX: Check that you:
    1. Called reparentTo(self.render)
    2. Set appropriate scale and position
    3. Added lighting (objects need light to be visible)
"""

# ============================================
# TESTING IMPORTS
# ============================================

def test_imports():
    """Run this to verify all imports work"""
    try:
        from direct.showbase.ShowBase import ShowBase
        from panda3d.core import Point3, Vec3, WindowProperties, TextNode
        from direct.gui.OnscreenText import OnscreenText
        from direct.task import Task
        from panda3d.core import AmbientLight, DirectionalLight
        print("✓ All imports successful!")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

if __name__ == "__main__":
    test_imports()

