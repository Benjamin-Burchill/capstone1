#!/usr/bin/env python3
"""
Character Generator GUI - Professional 3D character customization interface
===========================================================================

This module provides a complete graphical user interface for the character
generation system, featuring real-time 3D visualization, parameter controls,
and export functionality.

Features:
---------
- Real-time 3D mesh visualization using matplotlib
- Organized parameter controls with tabbed interface
- Preset management system
- Export to standard 3D formats (OBJ, JSON)
- Wireframe/solid rendering modes
- Camera controls (rotation, zoom, reset)

Architecture:
------------
The GUI uses PyQt6 for the interface and matplotlib for 3D rendering:

1. **Main Window** (CharacterGeneratorGUI)
   - Menu bar with file/edit/view/help menus
   - Central 3D viewport
   - Parameter control panel
   - Info panel with mesh statistics

2. **Parameter Panel** (ParameterPanel)
   - Tabbed organization by body region
   - Custom slider widgets with reset functionality
   - Real-time parameter updates

3. **3D Viewport** (Viewport3D)
   - Matplotlib-based 3D rendering
   - Mouse controls for rotation and zoom
   - Wireframe toggle
   - Stable camera during parameter changes

Dependencies:
------------
- PyQt6: GUI framework
- matplotlib: 3D visualization
- numpy: Numerical operations
- trimesh: Mesh handling

Author: GUI Development Team
Version: 2.0
Date: 2024
"""

import sys
import numpy as np
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSlider, QLabel, QPushButton, QComboBox, QGroupBox, QScrollArea,
    QTabWidget, QFileDialog, QSpinBox, QDoubleSpinBox, QGridLayout,
    QMessageBox, QSplitter
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt6.QtGui import QFont, QPalette, QColor
import json
from pathlib import Path

# For 3D visualization
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

# Import our character generator (silently)
import logging
logging.basicConfig(level=logging.WARNING)  # Suppress info messages
try:
    # Try to use advanced generator first
    from character_generator_advanced import AdvancedCharacterGenerator as CharacterGenerator
    from character_generator import CharacterParameters, CharacterPreset
    print("Using Advanced Character Generator with fingers, toes, and muscle definitions!")
except ImportError:
    # Fallback to basic
    from character_generator import (
        CharacterGenerator, CharacterParameters, CharacterPreset
    )
    print("Using basic character generator")

class ParameterSlider(QWidget):
    """Custom slider widget for parameter control"""
    
    valueChanged = pyqtSignal(str, float)
    
    def __init__(self, name: str, display_name: str, 
                 min_val: float = -1.0, max_val: float = 1.0, 
                 default: float = 0.0):
        super().__init__()
        self.name = name
        self.display_name = display_name
        
        # Create layout
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 2, 5, 2)
        
        # Label
        self.label = QLabel(f"{display_name}:")
        self.label.setMinimumWidth(120)
        layout.addWidget(self.label)
        
        # Slider
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(int(min_val * 100))
        self.slider.setMaximum(int(max_val * 100))
        self.slider.setValue(int(default * 100))
        self.slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.slider.setTickInterval(50)
        self.slider.valueChanged.connect(self._on_slider_change)
        layout.addWidget(self.slider)
        
        # Value display
        self.value_label = QLabel(f"{default:.2f}")
        self.value_label.setMinimumWidth(50)
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.value_label)
        
        # Reset button
        self.reset_btn = QPushButton("↺")
        self.reset_btn.setMaximumWidth(30)
        self.reset_btn.clicked.connect(self.reset)
        layout.addWidget(self.reset_btn)
        
        self.setLayout(layout)
        self.default_value = default
    
    def _on_slider_change(self, value):
        """Handle slider value change"""
        float_val = value / 100.0
        self.value_label.setText(f"{float_val:.2f}")
        self.valueChanged.emit(self.name, float_val)
    
    def reset(self):
        """Reset to default value"""
        self.slider.setValue(int(self.default_value * 100))
    
    def set_value(self, value: float):
        """Set slider value programmatically"""
        self.slider.setValue(int(value * 100))


class ParameterPanel(QWidget):
    """Panel containing categorized parameter controls"""
    
    parametersChanged = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.sliders = {}
        self.init_ui()
    
    def init_ui(self):
        """Initialize the parameter panel UI"""
        # Main layout
        main_layout = QVBoxLayout()
        
        # Create tab widget for categories
        self.tabs = QTabWidget()
        
        # Define parameter categories
        categories = {
            "Global": [
                ("height", "Height", 0.5, 1.5, 1.0),
                ("build", "Build", -1.0, 1.0, 0.0),
                ("muscle_definition", "Muscle", -1.0, 1.0, 0.0),
            ],
            "Head": [
                ("head_size", "Head Size", -1.0, 1.0, 0.0),
                ("head_width", "Head Width", -1.0, 1.0, 0.0),
                ("head_depth", "Head Depth", -1.0, 1.0, 0.0),
            ],
            "Face": [
                ("jaw_width", "Jaw Width", -1.0, 1.0, 0.0),
                ("jaw_height", "Jaw Height", -1.0, 1.0, 0.0),
                ("chin_size", "Chin Size", -1.0, 1.0, 0.0),
                ("cheek_bones", "Cheek Bones", -1.0, 1.0, 0.0),
                ("brow_ridge", "Brow Ridge", -1.0, 1.0, 0.0),
                ("forehead_size", "Forehead", -1.0, 1.0, 0.0),
            ],
            "Features": [
                ("eye_size", "Eye Size", -1.0, 1.0, 0.0),
                ("eye_spacing", "Eye Spacing", -1.0, 1.0, 0.0),
                ("nose_width", "Nose Width", -1.0, 1.0, 0.0),
                ("nose_length", "Nose Length", -1.0, 1.0, 0.0),
                ("mouth_width", "Mouth Width", -1.0, 1.0, 0.0),
                ("ear_size", "Ear Size", -1.0, 1.0, 0.0),
                ("ear_point", "Ear Point", 0.0, 1.0, 0.0),
            ],
            "Body": [
                ("shoulder_width", "Shoulders", -1.0, 1.0, 0.0),
                ("chest_size", "Chest Size", -1.0, 1.0, 0.0),
                ("waist_size", "Waist Size", -1.0, 1.0, 0.0),
                ("hip_width", "Hip Width", -1.0, 1.0, 0.0),
                ("torso_length", "Torso Length", -1.0, 1.0, 0.0),
            ],
            "Limbs": [
                ("arm_length", "Arm Length", -1.0, 1.0, 0.0),
                ("upper_arm_size", "Upper Arm", -1.0, 1.0, 0.0),
                ("forearm_size", "Forearm", -1.0, 1.0, 0.0),
                ("hand_size", "Hand Size", -1.0, 1.0, 0.0),
                ("leg_length", "Leg Length", -1.0, 1.0, 0.0),
                ("thigh_size", "Thigh Size", -1.0, 1.0, 0.0),
                ("calf_size", "Calf Size", -1.0, 1.0, 0.0),
                ("foot_size", "Foot Size", -1.0, 1.0, 0.0),
            ],
            "Special": [
                ("horn_size", "Horn Size", 0.0, 1.0, 0.0),
                ("horn_position", "Horn Position", -1.0, 1.0, 0.0),
                ("tail_length", "Tail Length", 0.0, 1.0, 0.0),
                ("tail_thickness", "Tail Thick", 0.0, 1.0, 0.0),
            ]
        }
        
        # Create tabs with sliders
        for category, params in categories.items():
            tab = QWidget()
            layout = QVBoxLayout()
            
            for param_info in params:
                name, display, min_v, max_v, default = param_info
                slider = ParameterSlider(name, display, min_v, max_v, default)
                slider.valueChanged.connect(self._on_parameter_change)
                self.sliders[name] = slider
                layout.addWidget(slider)
            
            # Add stretch at bottom
            layout.addStretch()
            
            # Make scrollable
            scroll = QScrollArea()
            scroll_widget = QWidget()
            scroll_widget.setLayout(layout)
            scroll.setWidget(scroll_widget)
            scroll.setWidgetResizable(True)
            
            tab_layout = QVBoxLayout()
            tab_layout.addWidget(scroll)
            tab.setLayout(tab_layout)
            
            self.tabs.addTab(tab, category)
        
        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)
    
    def _on_parameter_change(self, name: str, value: float):
        """Handle parameter change"""
        all_params = self.get_all_parameters()
        self.parametersChanged.emit(all_params)
    
    def get_all_parameters(self) -> dict:
        """Get all current parameter values"""
        params = {}
        for name, slider in self.sliders.items():
            params[name] = slider.slider.value() / 100.0
        return params
    
    def set_parameters(self, params: dict):
        """Set all parameters from dictionary"""
        for name, value in params.items():
            if name in self.sliders:
                self.sliders[name].set_value(value)
    
    def reset_all(self):
        """Reset all parameters to default"""
        for slider in self.sliders.values():
            slider.reset()


class Viewport3D(QWidget):
    """3D viewport for character preview using matplotlib"""
    
    def __init__(self):
        super().__init__()
        self.mesh = None
        self.rotation = [30, 45]  # Initial rotation angles
        self.zoom = 1.0
        self.wireframe = False
        self.init_ui()
    
    def init_ui(self):
        """Initialize 3D viewport with matplotlib"""
        layout = QVBoxLayout()
        
        # Create matplotlib figure
        self.figure = Figure(figsize=(8, 6), facecolor='#1a1a1a')
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet("background-color: #1a1a1a;")
        
        # Create 3D axes
        self.ax = self.figure.add_subplot(111, projection='3d')
        self.ax.set_facecolor('#1a1a1a')
        self.ax.grid(True, alpha=0.2)
        
        # Set initial view
        self.ax.view_init(elev=self.rotation[0], azim=self.rotation[1])
        
        # Style the axes
        self.ax.xaxis.pane.fill = False
        self.ax.yaxis.pane.fill = False
        self.ax.zaxis.pane.fill = False
        self.ax.xaxis.pane.set_edgecolor('w')
        self.ax.yaxis.pane.set_edgecolor('w')
        self.ax.zaxis.pane.set_edgecolor('w')
        
        layout.addWidget(self.canvas)
        
        # Add controls
        controls_layout = QHBoxLayout()
        
        self.wireframe_btn = QPushButton("Wireframe")
        self.wireframe_btn.setCheckable(True)
        self.wireframe_btn.clicked.connect(self.toggle_wireframe)
        controls_layout.addWidget(self.wireframe_btn)
        
        self.reset_view_btn = QPushButton("Reset View")
        self.reset_view_btn.clicked.connect(self.reset_view)
        controls_layout.addWidget(self.reset_view_btn)
        
        layout.addLayout(controls_layout)
        
        self.setLayout(layout)
        
        # Connect mouse events for rotation
        self.canvas.mpl_connect('button_press_event', self.on_mouse_press)
        self.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
        self.canvas.mpl_connect('scroll_event', self.on_mouse_wheel)
    
    def update_mesh(self, mesh):
        """Update displayed mesh"""
        self.mesh = mesh
        self.draw_mesh()
    
    def draw_mesh(self):
        """Draw the mesh in the viewport"""
        if self.mesh is None:
            print("Warning: No mesh to draw")
            return
        
        print(f"Drawing mesh with {len(self.mesh.vertices)} vertices")
        
        # Save current view limits if they exist
        if hasattr(self, 'saved_xlim'):
            saved_xlim = self.ax.get_xlim()
            saved_ylim = self.ax.get_ylim()
            saved_zlim = self.ax.get_zlim()
            preserve_zoom = True
        else:
            preserve_zoom = False
        
        # Clear the axes
        self.ax.clear()
        
        # Get mesh data
        vertices = self.mesh.vertices
        faces = self.mesh.faces
        
        # Draw the mesh
        if self.wireframe:
            # Wireframe mode
            for face in faces:
                triangle = vertices[face]
                triangle = np.vstack([triangle, triangle[0]])  # Close the triangle
                self.ax.plot3D(triangle[:, 0], triangle[:, 2], triangle[:, 1], 
                             'cyan', linewidth=0.3)
        else:
            # Solid mode with simple shading
            from mpl_toolkits.mplot3d.art3d import Poly3DCollection
            
            # Create triangles
            triangles = vertices[faces]
            
            # Create polygon collection
            poly = Poly3DCollection(triangles[:, :, [0, 2, 1]],  # Swap Y and Z for better view
                                   alpha=0.9,
                                   facecolor='lightblue',
                                   edgecolor='darkblue',
                                   linewidth=0.1)
            
            self.ax.add_collection3d(poly)
        
        # Set labels and limits
        self.ax.set_xlabel('X', color='white')
        self.ax.set_ylabel('Z', color='white')
        self.ax.set_zlabel('Y', color='white')
        
        # Set aspect ratio - either preserve existing or calculate new
        if preserve_zoom:
            # Restore saved view limits
            self.ax.set_xlim(saved_xlim)
            self.ax.set_ylim(saved_ylim)
            self.ax.set_zlim(saved_zlim)
        else:
            # Calculate initial view limits (only on first draw or reset)
            if len(vertices) > 0:
                # Use fixed range for consistent view
                max_range = 1.2  # Fixed range for human-scale viewing
                
                # Center on origin with slight offset for better view
                mid_x = 0
                mid_y = 0.5  # Slight upward offset
                mid_z = 0
                
                self.ax.set_xlim(mid_x - max_range, mid_x + max_range)
                self.ax.set_ylim(mid_z - max_range, mid_z + max_range)
                self.ax.set_zlim(mid_y - max_range, mid_y + max_range)
                
                # Save these as default limits
                self.saved_xlim = self.ax.get_xlim()
                self.saved_ylim = self.ax.get_ylim()
                self.saved_zlim = self.ax.get_zlim()
        
        # Style
        self.ax.tick_params(colors='white')
        self.ax.xaxis.label.set_color('white')
        self.ax.yaxis.label.set_color('white')
        self.ax.zaxis.label.set_color('white')
        
        # Update view
        self.ax.view_init(elev=self.rotation[0], azim=self.rotation[1])
        
        # Redraw
        self.canvas.draw()
    
    def on_mouse_press(self, event):
        """Handle mouse press for rotation"""
        if event.inaxes == self.ax:
            self.last_mouse_pos = (event.xdata, event.ydata)
    
    def on_mouse_move(self, event):
        """Handle mouse drag for rotation"""
        if event.inaxes == self.ax and event.button == 1:
            if hasattr(self, 'last_mouse_pos') and self.last_mouse_pos:
                # Calculate rotation delta
                dx = event.xdata - self.last_mouse_pos[0] if event.xdata else 0
                dy = event.ydata - self.last_mouse_pos[1] if event.ydata else 0
                
                # Update rotation
                self.rotation[1] += dx * 100  # Azimuth
                self.rotation[0] += dy * 100  # Elevation
                
                # Clamp elevation
                self.rotation[0] = max(-90, min(90, self.rotation[0]))
                
                # Update view
                self.ax.view_init(elev=self.rotation[0], azim=self.rotation[1])
                self.canvas.draw()
                
                self.last_mouse_pos = (event.xdata, event.ydata)
    
    def on_mouse_wheel(self, event):
        """Handle mouse wheel for zoom"""
        if event.inaxes == self.ax:
            # Zoom in/out
            scale_factor = 1.1 if event.button == 'up' else 0.9
            
            # Get current limits
            xlim = self.ax.get_xlim()
            ylim = self.ax.get_ylim()
            zlim = self.ax.get_zlim()
            
            # Calculate new limits
            x_center = (xlim[0] + xlim[1]) / 2
            y_center = (ylim[0] + ylim[1]) / 2
            z_center = (zlim[0] + zlim[1]) / 2
            
            x_range = (xlim[1] - xlim[0]) * scale_factor / 2
            y_range = (ylim[1] - ylim[0]) * scale_factor / 2
            z_range = (zlim[1] - zlim[0]) * scale_factor / 2
            
            # Set new limits
            self.ax.set_xlim(x_center - x_range, x_center + x_range)
            self.ax.set_ylim(y_center - y_range, y_center + y_range)
            self.ax.set_zlim(z_center - z_range, z_center + z_range)
            
            self.canvas.draw()
    
    def toggle_wireframe(self):
        """Toggle wireframe display"""
        self.wireframe = self.wireframe_btn.isChecked()
        self.draw_mesh()
    
    def reset_view(self):
        """Reset viewport camera"""
        self.rotation = [30, 45]
        self.zoom = 1.0
        # Clear saved limits to force recalculation
        if hasattr(self, 'saved_xlim'):
            del self.saved_xlim
            del self.saved_ylim
            del self.saved_zlim
        if self.mesh:
            self.draw_mesh()


class CharacterGeneratorGUI(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.generator = CharacterGenerator()
        self.init_ui()
        self.setup_connections()
        
    def init_ui(self):
        """Initialize the main UI"""
        self.setWindowTitle("Character Generator - MMORPG Character Creator")
        self.setGeometry(100, 100, 1400, 900)
        
        # Set dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
            }
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QGroupBox {
                border: 2px solid #555;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QSlider::groove:horizontal {
                height: 6px;
                background: #555;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #888;
                border: 1px solid #555;
                width: 14px;
                margin: -4px 0;
                border-radius: 7px;
            }
            QSlider::handle:horizontal:hover {
                background: #aaa;
            }
            QPushButton {
                background-color: #555;
                border: 1px solid #666;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #666;
            }
            QTabWidget::pane {
                border: 1px solid #555;
                background-color: #2b2b2b;
            }
            QTabBar::tab {
                background-color: #3b3b3b;
                padding: 5px 10px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #555;
            }
        """)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout()
        
        # Left panel - Controls
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        
        # Preset controls
        preset_group = QGroupBox("Presets")
        preset_layout = QHBoxLayout()
        
        self.preset_combo = QComboBox()
        self.preset_combo.addItems(["Human", "Dwarf", "Elf", "Orc", "Goblin"])
        self.preset_combo.currentTextChanged.connect(self.load_preset)
        preset_layout.addWidget(self.preset_combo)
        
        self.save_preset_btn = QPushButton("Save Preset")
        self.save_preset_btn.clicked.connect(self.save_preset)
        preset_layout.addWidget(self.save_preset_btn)
        
        preset_group.setLayout(preset_layout)
        left_layout.addWidget(preset_group)
        
        # Parameter panel
        self.param_panel = ParameterPanel()
        self.param_panel.parametersChanged.connect(self.update_character)
        left_layout.addWidget(self.param_panel)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.randomize_btn = QPushButton("🎲 Randomize")
        self.randomize_btn.clicked.connect(self.randomize_character)
        button_layout.addWidget(self.randomize_btn)
        
        self.reset_btn = QPushButton("↺ Reset All")
        self.reset_btn.clicked.connect(self.reset_character)
        button_layout.addWidget(self.reset_btn)
        
        self.export_btn = QPushButton("💾 Export")
        self.export_btn.clicked.connect(self.export_character)
        button_layout.addWidget(self.export_btn)
        
        left_layout.addLayout(button_layout)
        
        left_panel.setLayout(left_layout)
        left_panel.setMaximumWidth(400)
        
        # Center - 3D Viewport
        self.viewport = Viewport3D()
        
        # Right panel - Info/Stats
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        
        info_group = QGroupBox("Character Info")
        info_layout = QVBoxLayout()
        
        self.info_label = QLabel("Vertices: 0\nFaces: 0\nParameters: 0")
        self.info_label.setFont(QFont("Courier", 10))
        info_layout.addWidget(self.info_label)
        
        info_group.setLayout(info_layout)
        right_layout.addWidget(info_group)
        right_layout.addStretch()
        
        right_panel.setLayout(right_layout)
        right_panel.setMaximumWidth(200)
        
        # Add to main layout
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(self.viewport)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setStretchFactor(2, 0)
        
        main_layout.addWidget(splitter)
        central_widget.setLayout(main_layout)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Initialize with default character
        self.update_character({})
    
    def create_menu_bar(self):
        """Create application menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        file_menu.addAction("New Character", self.new_character)
        file_menu.addAction("Load Character", self.load_character)
        file_menu.addAction("Save Character", self.save_character)
        file_menu.addSeparator()
        file_menu.addAction("Export OBJ", self.export_obj_only)
        file_menu.addSeparator()
        file_menu.addAction("Exit", self.close)
        
        # Edit menu
        edit_menu = menubar.addMenu("Edit")
        edit_menu.addAction("Reset All", self.reset_character)
        
        # View menu
        view_menu = menubar.addMenu("View")
        view_menu.addAction("Reset Camera", self.reset_camera)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        help_menu.addAction("About", self.show_about)
    
    def setup_connections(self):
        """Setup signal connections"""
        pass  # Connections already set up in init_ui
    
    def update_character(self, params: dict):
        """Update character based on parameter changes"""
        for name, value in params.items():
            self.generator.set_parameter(name, value)
        
        # Update mesh display
        if self.generator.mesh.base_mesh:
            mesh = self.generator.mesh.base_mesh
            self.viewport.update_mesh(mesh)
            
            # Update info display
            self.info_label.setText(
                f"Vertices: {len(mesh.vertices)}\n"
                f"Faces: {len(mesh.faces)}\n"
                f"Parameters: {len(params)}"
            )
    
    def load_preset(self, preset_name: str):
        """Load a character preset"""
        self.generator.load_preset(preset_name.lower())
        
        # Update UI
        params = self.generator.parameters.to_dict()
        self.param_panel.set_parameters(params)
        
        # Update mesh
        self.update_character(params)
    
    def save_preset(self):
        """Save current as preset"""
        from PyQt6.QtWidgets import QInputDialog
        name, ok = QInputDialog.getText(self, "Save Preset", "Preset name:")
        if ok and name:
            self.generator.preset_manager.save_preset(name, self.generator.parameters)
            self.preset_combo.addItem(name.title())
    
    def randomize_character(self):
        """Generate random character"""
        self.generator.randomize(variation=0.4)
        params = self.generator.parameters.to_dict()
        self.param_panel.set_parameters(params)
        self.update_character(params)
    
    def reset_character(self):
        """Reset to default character"""
        self.generator.reset()
        self.param_panel.reset_all()
        self.update_character({})
    
    def export_character(self):
        """Export character to file"""
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Export Character", "", "Character Files (*.json);;OBJ Files (*.obj)"
        )
        if filepath:
            if filepath.endswith('.obj'):
                self.generator.mesh.export_mesh(filepath, format='obj')
                QMessageBox.information(self, "Export", f"Mesh exported to {filepath}")
            else:
                self.generator.save_character(filepath)
                QMessageBox.information(self, "Export", f"Character exported to {filepath}")
    
    def export_obj_only(self):
        """Export only OBJ file"""
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Export OBJ", "", "OBJ Files (*.obj)"
        )
        if filepath:
            self.generator.mesh.export_mesh(filepath, format='obj')
            QMessageBox.information(self, "Export", f"Mesh exported to {filepath}")
    
    def new_character(self):
        """Create new character"""
        self.reset_character()
    
    def load_character(self):
        """Load character from file"""
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Load Character", "", "Character Files (*.json)"
        )
        if filepath:
            with open(filepath, 'r') as f:
                data = json.load(f)
            params = CharacterParameters.from_dict(data['parameters'])
            self.generator.set_parameters(params)
            self.param_panel.set_parameters(data['parameters'])
            self.update_character(data['parameters'])
    
    def save_character(self):
        """Save current character"""
        self.export_character()
    
    def reset_camera(self):
        """Reset viewport camera"""
        self.viewport.reset_view()
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(self, "About Character Generator",
            "Character Generator v1.0\n\n"
            "A parametric character creation tool for MMORPGs\n"
            "Built with Python, PyQt6, and Trimesh\n\n"
            "Export characters as OBJ files for use in game engines")


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("Character Generator")
    
    # Set application style
    app.setStyle("Fusion")
    
    # Create and show main window
    window = CharacterGeneratorGUI()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
