#!/usr/bin/env python3
"""
Character Generator Documentation Web App
==========================================

A locally-hosted web application providing comprehensive documentation
for the Character Generator system.

Features:
- Interactive API documentation
- Architecture overview
- Visual examples
- Code snippets
- Parameter reference
- Tutorial guides

Author: Documentation Team
Version: 1.0
Date: 2024
"""

from flask import Flask, render_template, jsonify, send_file
import os
from pathlib import Path
import markdown
import json
from typing import Dict, List
import inspect
import sys

# Add character_generator to path
sys.path.insert(0, str(Path(__file__).parent))

# Import modules for documentation
try:
    from character_generator_advanced import AdvancedCharacterGenerator, AdvancedCharacterMesh
    from character_generator import CharacterParameters
    from humanoid_builder_symmetric import SymmetricHumanoidBuilder
    from morphing_system import AdvancedMorphingSystem
    MODULES_LOADED = True
except ImportError as e:
    print(f"Warning: Some modules couldn't be loaded: {e}")
    MODULES_LOADED = False

app = Flask(__name__)
app.config['SECRET_KEY'] = 'character-generator-docs-2024'

# Documentation data structure
DOCUMENTATION = {
    'overview': {
        'title': 'Character Generator System',
        'description': 'Professional parametric 3D character creation system',
        'version': '2.0',
        'features': [
            'Perfect bilateral symmetry through half-mesh mirroring',
            'Advanced morphing with RBF interpolation',
            'Anatomically correct muscle groups',
            'Multiple quality levels (low/medium/high)',
            'Comprehensive GUI with real-time preview',
            '48+ adjustable parameters',
            'Preset management system',
            'Export to standard 3D formats'
        ]
    },
    'modules': [
        {
            'name': 'humanoid_builder_symmetric',
            'title': 'Symmetric Mesh Builder',
            'description': 'Creates perfectly symmetric humanoid meshes using half-mesh mirroring',
            'key_features': [
                'Generates only right half + center line',
                'Mirrors for perfect bilateral symmetry',
                'Industry-standard approach',
                'Reduces code complexity by 50%'
            ]
        },
        {
            'name': 'morphing_system',
            'title': 'Advanced Morphing System',
            'description': 'Sophisticated deformation algorithms for character customization',
            'key_features': [
                'Blend shapes with linear interpolation',
                'RBF morphing with Gaussian functions',
                'Regional influence maps',
                'Anatomical muscle deformations',
                'Corrective morphs for quality'
            ]
        },
        {
            'name': 'character_generator_advanced',
            'title': 'Character Generator Core',
            'description': 'Main character generation and management system',
            'key_features': [
                '48+ adjustable parameters',
                'Preset management',
                'Quality level control',
                'Export system'
            ]
        },
        {
            'name': 'character_gui_simple_3d',
            'title': 'User Interface',
            'description': 'Professional GUI with real-time 3D visualization',
            'key_features': [
                'PyQt6-based interface',
                'Matplotlib 3D viewport',
                'Tabbed parameter controls',
                'Camera controls',
                'Export functionality'
            ]
        }
    ],
    'parameters': None,  # Will be loaded dynamically
    'tutorials': [
        {
            'id': 'quickstart',
            'title': 'Quick Start Guide',
            'steps': [
                'Launch the GUI: python character_gui_simple_3d.py',
                'Select a preset (Human, Dwarf, Elf, Orc, Goblin)',
                'Adjust parameters using sliders',
                'View real-time changes in 3D viewport',
                'Export your character (File → Export)'
            ]
        },
        {
            'id': 'custom_preset',
            'title': 'Creating Custom Presets',
            'steps': [
                'Adjust all parameters to desired values',
                'Click "Save Preset" button',
                'Enter a name for your preset',
                'Preset will be saved and added to dropdown',
                'Share preset files (.json) with team'
            ]
        },
        {
            'id': 'advanced_morphing',
            'title': 'Advanced Morphing Techniques',
            'steps': [
                'Understanding parameter ranges (-1 to 1)',
                'Global parameters affect entire body',
                'Regional parameters target specific areas',
                'Muscle definition creates anatomical detail',
                'Combine parameters for unique characters'
            ]
        }
    ]
}

def load_parameter_documentation():
    """Load parameter documentation from the CharacterParameters class"""
    if not MODULES_LOADED:
        return []
    
    params = []
    param_obj = CharacterParameters()
    param_dict = param_obj.to_dict()
    
    # Group parameters by category
    categories = {
        'Global': ['height', 'build', 'muscle_definition'],
        'Head': ['head_size', 'head_width', 'head_depth'],
        'Face': ['jaw_width', 'jaw_height', 'chin_size', 'cheek_bones', 'brow_ridge'],
        'Eyes': ['eye_size', 'eye_spacing', 'eye_height', 'eye_depth'],
        'Nose': ['nose_width', 'nose_length', 'nose_height', 'nose_bridge'],
        'Mouth': ['mouth_width', 'mouth_height', 'lip_thickness'],
        'Body': ['shoulder_width', 'chest_size', 'waist_size', 'hip_width'],
        'Arms': ['arm_length', 'upper_arm_size', 'forearm_size', 'hand_size'],
        'Legs': ['leg_length', 'thigh_size', 'calf_size', 'foot_size'],
        'Special': ['horn_size', 'horn_position', 'tail_length', 'tail_thickness']
    }
    
    for category, param_names in categories.items():
        for param in param_names:
            if param in param_dict:
                params.append({
                    'name': param,
                    'category': category,
                    'default': param_dict[param],
                    'range': '-1.0 to 1.0' if param != 'height' else '0.5 to 1.5',
                    'description': param.replace('_', ' ').title()
                })
    
    return params

# Load parameters
DOCUMENTATION['parameters'] = load_parameter_documentation()

@app.route('/')
def index():
    """Main documentation page"""
    return render_template('doc_index.html', docs=DOCUMENTATION)

@app.route('/api')
def api_documentation():
    """API reference page"""
    api_docs = []
    
    if MODULES_LOADED:
        # Document main classes
        classes = [
            (AdvancedCharacterGenerator, 'Main character generator class'),
            (SymmetricHumanoidBuilder, 'Symmetric mesh builder'),
            (AdvancedMorphingSystem, 'Morphing system'),
            (CharacterParameters, 'Parameter container')
        ]
        
        for cls, description in classes:
            methods = []
            for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
                if not name.startswith('_'):
                    doc = inspect.getdoc(method) or 'No documentation'
                    signature = str(inspect.signature(method)) if hasattr(method, '__call__') else ''
                    methods.append({
                        'name': name,
                        'signature': signature,
                        'doc': doc.split('\n')[0]  # First line only
                    })
            
            api_docs.append({
                'class': cls.__name__,
                'description': description,
                'methods': methods
            })
    
    return render_template('doc_api.html', api_docs=api_docs)

@app.route('/architecture')
def architecture():
    """Architecture documentation page"""
    # Read ARCHITECTURE.md if it exists
    arch_file = Path(__file__).parent / 'ARCHITECTURE.md'
    if arch_file.exists():
        with open(arch_file, 'r') as f:
            content = f.read()
        html_content = markdown.markdown(content, extensions=['extra', 'codehilite'])
    else:
        html_content = '<p>Architecture documentation not found</p>'
    
    return render_template('doc_architecture.html', content=html_content)

@app.route('/examples')
def examples():
    """Code examples page"""
    examples = [
        {
            'title': 'Basic Character Generation',
            'code': '''from character_generator_advanced import AdvancedCharacterGenerator

# Create generator
generator = AdvancedCharacterGenerator()

# Load a preset
generator.load_preset('human')

# Adjust parameters
generator.set_parameter('height', 1.2)
generator.set_parameter('muscle_definition', 0.5)

# Save character
generator.save_character('my_character.json')
'''
        },
        {
            'title': 'Creating Custom Morphs',
            'code': '''from morphing_system import AdvancedMorphingSystem
import numpy as np

# Create morphing system
morph_system = AdvancedMorphingSystem(base_mesh)

# Define custom deformation
def create_broad_shoulders(vertices):
    for i, v in enumerate(vertices):
        if 1.3 < v[1] < 1.5:  # Shoulder height
            vertices[i, 0] *= 1.2  # Widen
    return vertices

# Create morph target
morph_system.create_morph_target(
    'broad_shoulders',
    create_broad_shoulders,
    category='torso',
    region='shoulders'
)
'''
        },
        {
            'title': 'Symmetric Mesh Generation',
            'code': '''from humanoid_builder_symmetric import create_symmetric_humanoid

# Create meshes at different quality levels
low_quality = create_symmetric_humanoid('low')     # ~316 vertices
medium_quality = create_symmetric_humanoid('medium') # ~442 vertices  
high_quality = create_symmetric_humanoid('high')    # ~2270 vertices

# Export mesh
medium_quality.export('character.obj')

# Check symmetry
print(f"Watertight: {medium_quality.is_watertight}")
print(f"Vertices: {len(medium_quality.vertices)}")
'''
        }
    ]
    return render_template('doc_examples.html', examples=examples)

@app.route('/parameters')
def parameters():
    """Parameter reference page"""
    return render_template('doc_parameters.html', parameters=DOCUMENTATION['parameters'])

@app.route('/tutorials')
def tutorials():
    """Tutorial guides page"""
    return render_template('doc_tutorials.html', tutorials=DOCUMENTATION['tutorials'])

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

def create_app():
    """Create and configure the Flask application"""
    # Create templates directory if it doesn't exist
    templates_dir = Path(__file__).parent / 'templates'
    templates_dir.mkdir(exist_ok=True)
    
    # Create static directory for CSS
    static_dir = Path(__file__).parent / 'static'
    static_dir.mkdir(exist_ok=True)
    
    return app

if __name__ == '__main__':
    print("=" * 60)
    print("Character Generator Documentation Server")
    print("=" * 60)
    print("\nStarting documentation server...")
    print("Access documentation at: http://localhost:5000")
    print("\nPress Ctrl+C to stop the server")
    print("-" * 60)
    
    app = create_app()
    app.run(debug=True, host='localhost', port=5000)

