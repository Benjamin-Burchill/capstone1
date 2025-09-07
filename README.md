# Panda3D Simple Examples

This repository contains simple Panda3D examples to help you get started with 3D graphics programming in Python.

## Setup

1. Make sure you have Python installed (Python 3.8 or higher recommended)

2. Activate the virtual environment:
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

3. Install dependencies (if not already installed):
   ```bash
   pip install -r requirements.txt
   ```

## Examples

### 01_hello_window.py
The simplest possible Panda3D application. Creates a window with text that you can close with ESC.

```bash
python 01_hello_window.py
```

### 02_spinning_cube.py
Shows a rotating cube with basic lighting. Demonstrates:
- Loading 3D models
- Basic animation using tasks
- Simple lighting setup

```bash
python 02_spinning_cube.py
```

### 03_colored_shapes.py
Multiple colored cubes with different animations. Demonstrates:
- Creating multiple objects
- Applying colors to objects
- Different animation patterns

```bash
python 03_colored_shapes.py
```

### 04_keyboard_control.py
Interactive keyboard controls to move a cube. Demonstrates:
- Keyboard input handling
- Real-time object movement
- Position tracking

Controls:
- Arrow keys or WASD: Move horizontally
- Space: Move up
- Shift: Move down
- R: Reset position
- ESC: Exit

```bash
python 04_keyboard_control.py
```

### 05_mouse_interaction.py
Mouse-controlled camera rotation and zoom. Demonstrates:
- Mouse input handling
- Camera manipulation
- Creating a grid of objects

Controls:
- Left click + drag: Rotate camera
- Scroll wheel: Zoom in/out
- R: Reset camera
- ESC: Exit

```bash
python 05_mouse_interaction.py
```

## Common Panda3D Concepts

### ShowBase
The main application class that handles window creation, rendering, and the main loop.

### Task Manager
Handles recurring tasks and animations. Tasks are functions that run every frame.

### Scene Graph
Panda3D uses a tree structure for organizing 3D objects. The root is `render`, and all visible objects must be attached to it.

### Coordinate System
Panda3D uses a right-handed coordinate system:
- X: Right/Left
- Y: Forward/Backward  
- Z: Up/Down

### Lighting
Basic lighting types:
- **AmbientLight**: Provides overall illumination
- **DirectionalLight**: Simulates distant light sources like the sun
- **PointLight**: Light that emanates from a single point
- **Spotlight**: Cone-shaped light beam

## Next Steps

Once you're comfortable with these examples, you can:
1. Combine concepts from different examples
2. Load custom 3D models (.egg, .bam, .glb formats)
3. Add physics with Panda3D's built-in physics engine
4. Create more complex animations and interactions
5. Add textures and materials to objects
6. Implement collision detection
7. Add sound effects and music

## Resources

- [Panda3D Manual](https://docs.panda3d.org/1.10/python/index)
- [Panda3D API Reference](https://docs.panda3d.org/1.10/python/reference/index)
- [Panda3D Forums](https://discourse.panda3d.org/)
- [Panda3D GitHub](https://github.com/panda3d/panda3d)
