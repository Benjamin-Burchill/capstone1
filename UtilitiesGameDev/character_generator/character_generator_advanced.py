#!/usr/bin/env python3
"""
Advanced Character Generator - Professional parametric character creation system
==============================================================================

This module provides a complete character generation system with advanced features
including symmetric mesh generation, sophisticated morphing algorithms, muscle
group definitions, and subdivision surface support.

Features:
---------
- Symmetric mesh generation (perfect bilateral symmetry)
- Advanced morphing with RBF interpolation
- Anatomically correct muscle groups
- Multiple quality levels (low/medium/high)
- Subdivision surface smoothing
- Preset management system
- Export to standard 3D formats

Architecture:
------------
The system uses a modular architecture:
1. Mesh Builder: Creates base humanoid mesh with perfect symmetry
2. Morphing System: Applies parametric deformations
3. Parameter Manager: Handles character parameters and presets
4. Export System: Saves meshes and metadata

Usage:
------
    generator = AdvancedCharacterGenerator()
    generator.load_preset('human')
    generator.set_parameter('height', 1.2)
    generator.save_character('my_character.json')

Author: Character Generator Team
Version: 2.0
Date: 2024
License: MIT
"""

import numpy as np
import trimesh
from dataclasses import dataclass
from typing import Dict, List, Optional
import json
import os
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Import advanced components
try:
    # Use symmetric builder for perfect bilateral symmetry
    from humanoid_builder_symmetric import create_symmetric_humanoid
    def create_advanced_humanoid(detail_level='medium'):
        """Wrapper to use symmetric builder."""
        return create_symmetric_humanoid(detail_level=detail_level)
except ImportError:
    # Fallback to previous version
    try:
        from humanoid_builder_advanced_fixed import create_fixed_advanced_humanoid as create_advanced_humanoid
    except ImportError:
        from humanoid_builder_advanced import create_advanced_humanoid
        
from morphing_system import AdvancedMorphingSystem
from character_generator import CharacterParameters, CharacterPreset


class AdvancedCharacterMesh:
    """Advanced mesh management with all new features"""
    
    def __init__(self, resolution: int = 12, subdivision: int = 0):
        """Initialize with advanced humanoid"""
        self.resolution = resolution
        self.subdivision = subdivision
        
        # Create advanced base mesh - map resolution to detail level
        if resolution <= 8:
            detail = 'low'
        elif resolution <= 12:
            detail = 'medium'
        else:
            detail = 'high'
        
        self.base_mesh = create_advanced_humanoid(detail_level=detail)
        
        # Initialize morphing system
        self.morphing_system = AdvancedMorphingSystem(self.base_mesh)
        
        # Store original vertices
        self.base_vertices = np.array(self.base_mesh.vertices, dtype=np.float32)
        self.current_vertices = self.base_vertices.copy()
        
        # Initialize morph targets
        self._create_morph_targets()
        
        logger.info(f"Created advanced humanoid: {len(self.base_vertices)} vertices")
    
    def _create_morph_targets(self):
        """Create predefined morph targets"""
        # Head morphs
        self.morphing_system.create_morph_target(
            'head_large',
            lambda v: self._scale_region(v, 'head', 1.2),
            'head', 'head'
        )
        
        # Body morphs
        self.morphing_system.create_morph_target(
            'broad_shoulders',
            lambda v: self._widen_shoulders(v, 1.3),
            'torso', 'chest'
        )
        
        # Add more morph targets as needed
    
    def _scale_region(self, vertices: np.ndarray, region: str, scale: float) -> np.ndarray:
        """Scale a specific region"""
        if region == 'head':
            mask = vertices[:, 1] > 1.5
            center = np.mean(vertices[mask], axis=0)
            vertices[mask] = center + (vertices[mask] - center) * scale
        return vertices
    
    def _widen_shoulders(self, vertices: np.ndarray, scale: float) -> np.ndarray:
        """Widen shoulder area"""
        mask = (vertices[:, 1] > 1.3) & (vertices[:, 1] < 1.5)
        vertices[mask, 0] *= scale
        return vertices
    
    def apply_parameters(self, params: CharacterParameters):
        """Apply parameters using advanced morphing"""
        # Convert parameters to dict
        param_dict = params.to_dict()
        
        # Apply morphing
        self.current_vertices = self.morphing_system.apply_parameters(param_dict)
        
        # Update mesh
        self.base_mesh.vertices = self.current_vertices
        
        return self.base_mesh
    
    def set_subdivision(self, level: int):
        """Change subdivision level"""
        if level != self.subdivision:
            self.subdivision = level
            # Recreate mesh with new subdivision
            if self.resolution <= 8:
                detail = 'low'
            elif self.resolution <= 12:
                detail = 'medium'
            else:
                detail = 'high'
            
            self.base_mesh = create_advanced_humanoid(detail_level=detail)
            
            # Apply subdivision if requested
            if level > 0:
                for _ in range(level):
                    self.base_mesh = self.base_mesh.subdivide()
            
            self.morphing_system = AdvancedMorphingSystem(self.base_mesh)
            self.base_vertices = np.array(self.base_mesh.vertices)
            self.current_vertices = self.base_vertices.copy()
    
    def export_mesh(self, filepath: str, format: str = 'obj'):
        """Export current mesh"""
        export_mesh = trimesh.Trimesh(
            vertices=self.current_vertices,
            faces=self.base_mesh.faces
        )
        export_mesh.export(filepath)
        logger.info(f"Exported mesh to {filepath}")
    
    def get_mesh_stats(self) -> Dict:
        """Get mesh statistics"""
        return {
            'vertices': len(self.current_vertices),
            'faces': len(self.base_mesh.faces),
            'watertight': self.base_mesh.is_watertight,
            'bounds': self.base_mesh.bounds.tolist(),
            'subdivision': self.subdivision
        }


class AdvancedCharacterGenerator:
    """Advanced character generator with all features"""
    
    def __init__(self, resolution: int = 12, subdivision: int = 0):
        """Initialize advanced generator"""
        self.mesh = AdvancedCharacterMesh(resolution, subdivision)
        self.parameters = CharacterParameters()
        self.preset_manager = CharacterPreset()
        self.history: List[CharacterParameters] = []
        
        # Quality settings
        self.quality_settings = {
            'low': {'resolution': 8, 'subdivision': 0},
            'medium': {'resolution': 12, 'subdivision': 0},
            'high': {'resolution': 12, 'subdivision': 1},
            'ultra': {'resolution': 16, 'subdivision': 2}
        }
        
        self.current_quality = 'medium'
    
    def set_quality(self, quality: str):
        """Set mesh quality level"""
        if quality in self.quality_settings:
            settings = self.quality_settings[quality]
            self.mesh = AdvancedCharacterMesh(
                resolution=settings['resolution'],
                subdivision=settings['subdivision']
            )
            self.current_quality = quality
            self.update_mesh()
            logger.info(f"Set quality to {quality}")
    
    def set_parameter(self, name: str, value: float):
        """Set a single parameter"""
        if hasattr(self.parameters, name):
            setattr(self.parameters, name, value)
            self.update_mesh()
        else:
            logger.warning(f"Unknown parameter: {name}")
    
    def set_parameters(self, params: CharacterParameters):
        """Set all parameters"""
        self.parameters = params
        self.update_mesh()
    
    def update_mesh(self):
        """Update mesh with current parameters"""
        self.mesh.apply_parameters(self.parameters)
        self.history.append(CharacterParameters(**self.parameters.to_dict()))
    
    def load_preset(self, preset_name: str):
        """Load and apply a preset"""
        params = self.preset_manager.load_preset(preset_name)
        if params:
            self.set_parameters(params)
            logger.info(f"Loaded preset: {preset_name}")
        else:
            logger.warning(f"Preset not found: {preset_name}")
    
    def save_character(self, filepath: str):
        """Save character with metadata"""
        # Save mesh
        mesh_path = filepath.replace('.json', '.obj')
        self.mesh.export_mesh(mesh_path)
        
        # Save parameters and metadata
        with open(filepath, 'w') as f:
            json.dump({
                'parameters': self.parameters.to_dict(),
                'mesh_file': os.path.basename(mesh_path),
                'quality': self.current_quality,
                'mesh_stats': self.mesh.get_mesh_stats()
            }, f, indent=2)
        
        logger.info(f"Saved character to {filepath}")
    
    def randomize(self, variation: float = 0.3, respect_anatomy: bool = True):
        """Generate random character with anatomical constraints"""
        import random
        
        params_dict = self.parameters.to_dict()
        
        # Anatomical constraints
        constraints = {
            'height': (0.7, 1.3),
            'build': (-0.8, 0.8),
            'muscle_definition': (-0.5, 0.8),
            'head_size': (-0.3, 0.3),
            'shoulder_width': (-0.4, 0.4),
            'arm_length': (-0.2, 0.2),
            'leg_length': (-0.2, 0.2)
        }
        
        for key in params_dict:
            if respect_anatomy and key in constraints:
                min_val, max_val = constraints[key]
                params_dict[key] = random.uniform(
                    max(min_val, -variation),
                    min(max_val, variation)
                )
            else:
                if key != 'height':
                    params_dict[key] = random.uniform(-variation, variation)
                else:
                    params_dict[key] = random.uniform(0.8, 1.2)
        
        self.set_parameters(CharacterParameters.from_dict(params_dict))
        logger.info("Generated random character")
    
    def reset(self):
        """Reset to default"""
        self.parameters = CharacterParameters()
        self.mesh = AdvancedCharacterMesh(
            resolution=self.quality_settings[self.current_quality]['resolution'],
            subdivision=self.quality_settings[self.current_quality]['subdivision']
        )
        self.update_mesh()
    
    def get_info(self) -> Dict:
        """Get generator information"""
        return {
            'quality': self.current_quality,
            'mesh_stats': self.mesh.get_mesh_stats(),
            'parameters': self.parameters.to_dict(),
            'features': [
                'Advanced humanoid mesh',
                'Fingers and toes',
                'Facial features',
                'Muscle groups',
                'Subdivision smoothing',
                'RBF morphing',
                'Anatomical constraints'
            ]
        }


# Example usage
if __name__ == "__main__":
    # Create advanced generator
    print("Creating advanced character generator...")
    generator = AdvancedCharacterGenerator(resolution=12, subdivision=0)
    
    # Test quality settings
    print("\nTesting quality settings:")
    for quality in ['low', 'medium', 'high']:
        generator.set_quality(quality)
        stats = generator.mesh.get_mesh_stats()
        print(f"{quality}: {stats['vertices']} vertices, {stats['faces']} faces")
    
    # Test with preset
    generator.load_preset('orc')
    
    # Test randomization
    generator.randomize(variation=0.4, respect_anatomy=True)
    
    # Save character
    generator.save_character('advanced_test.json')
    
    # Get info
    info = generator.get_info()
    print(f"\nGenerator features: {', '.join(info['features'])}")
    print("Advanced character generation test complete!")
