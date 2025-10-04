#!/usr/bin/env python3
"""
Parametric Character Generator - Core System
A versatile 3D character creation tool for MMORPG development
"""

import numpy as np
import trimesh
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
import json
import os
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.WARNING)  # Only show warnings and errors
logger = logging.getLogger(__name__)

@dataclass
class MorphTarget:
    """Represents a single morph target/blend shape"""
    name: str
    vertex_deltas: np.ndarray  # Difference from base mesh
    region: str  # Head, Body, Limbs, etc.
    category: str  # Shape, Size, Detail
    default_weight: float = 0.0
    min_weight: float = -1.0
    max_weight: float = 1.0
    
    def apply(self, vertices: np.ndarray, weight: float) -> np.ndarray:
        """Apply morph target with given weight"""
        weight = np.clip(weight, self.min_weight, self.max_weight)
        return vertices + (self.vertex_deltas * weight)

@dataclass
class CharacterParameters:
    """All adjustable parameters for character generation"""
    
    # Global Parameters
    height: float = 1.0
    build: float = 0.0  # -1 thin, 0 normal, 1 heavy
    muscle_definition: float = 0.0
    
    # Head Parameters
    head_size: float = 0.0
    head_width: float = 0.0
    head_depth: float = 0.0
    
    # Face Shape
    jaw_width: float = 0.0
    jaw_height: float = 0.0
    chin_size: float = 0.0
    cheek_bones: float = 0.0
    
    # Eyes
    eye_size: float = 0.0
    eye_spacing: float = 0.0
    eye_height: float = 0.0
    eye_depth: float = 0.0
    
    # Nose
    nose_width: float = 0.0
    nose_length: float = 0.0
    nose_height: float = 0.0
    nose_bridge: float = 0.0
    
    # Mouth
    mouth_width: float = 0.0
    mouth_height: float = 0.0
    lip_thickness: float = 0.0
    
    # Forehead/Brow
    brow_ridge: float = 0.0
    forehead_size: float = 0.0
    forehead_slope: float = 0.0
    
    # Ears
    ear_size: float = 0.0
    ear_angle: float = 0.0
    ear_point: float = 0.0  # For elf-like ears
    
    # Neck
    neck_thickness: float = 0.0
    neck_length: float = 0.0
    
    # Torso
    shoulder_width: float = 0.0
    shoulder_height: float = 0.0
    chest_size: float = 0.0
    chest_depth: float = 0.0
    waist_size: float = 0.0
    hip_width: float = 0.0
    torso_length: float = 0.0
    
    # Arms
    arm_length: float = 0.0
    upper_arm_size: float = 0.0
    forearm_size: float = 0.0
    hand_size: float = 0.0
    
    # Legs
    leg_length: float = 0.0
    thigh_size: float = 0.0
    calf_size: float = 0.0
    foot_size: float = 0.0
    
    # Special Features
    horn_size: float = 0.0
    horn_position: float = 0.0
    tail_length: float = 0.0
    tail_thickness: float = 0.0
    
    def to_dict(self) -> Dict[str, float]:
        """Convert parameters to dictionary"""
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}
    
    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> 'CharacterParameters':
        """Create from dictionary"""
        return cls(**data)

class CharacterMesh:
    """Manages the base mesh and morphing operations"""
    
    def __init__(self, base_mesh_path: Optional[str] = None):
        """Initialize with base mesh"""
        if base_mesh_path and os.path.exists(base_mesh_path):
            self.base_mesh = trimesh.load(base_mesh_path)
        else:
            # Create a simple base humanoid mesh for testing
            self.base_mesh = self._create_default_humanoid()
        
        self.base_vertices = np.array(self.base_mesh.vertices, dtype=np.float32)
        self.current_vertices = self.base_vertices.copy()
        self.morph_targets: Dict[str, MorphTarget] = {}
        self.vertex_groups: Dict[str, np.ndarray] = {}
        
        # Initialize vertex groups (regions for targeted morphing)
        self._initialize_vertex_groups()
    
    def _create_default_humanoid(self) -> trimesh.Trimesh:
        """Create a properly connected humanoid mesh"""
        # Import the improved humanoid builder with better connectivity
        try:
            from humanoid_builder_v2 import create_base_humanoid
        except ImportError:
            # Fallback to original if v2 not available
            from humanoid_builder import create_base_humanoid
        return create_base_humanoid(resolution=8)
    
    def _initialize_vertex_groups(self):
        """Define vertex groups for different body regions"""
        # This would be more sophisticated with a real mesh
        # Using simple height-based regions for now
        
        vertices = self.base_vertices
        y_coords = vertices[:, 1]
        
        # Head vertices (top 15%)
        head_threshold = np.percentile(y_coords, 85)
        self.vertex_groups['head'] = y_coords > head_threshold
        
        # Torso (middle 40%)
        torso_upper = np.percentile(y_coords, 60)
        torso_lower = np.percentile(y_coords, 20)
        self.vertex_groups['torso'] = (y_coords <= torso_upper) & (y_coords > torso_lower)
        
        # Legs (bottom 20%)
        leg_threshold = np.percentile(y_coords, 20)
        self.vertex_groups['legs'] = y_coords <= leg_threshold
        
        # Arms (based on x-coordinate distance from center)
        x_coords = np.abs(vertices[:, 0])
        arm_threshold = np.percentile(x_coords, 70)
        self.vertex_groups['arms'] = x_coords > arm_threshold
    
    def add_morph_target(self, morph: MorphTarget):
        """Add a morph target to the collection"""
        self.morph_targets[morph.name] = morph
        logger.info(f"Added morph target: {morph.name}")
    
    def apply_parameters(self, params: CharacterParameters):
        """Apply all parameters to generate the final mesh"""
        # Start with base vertices
        self.current_vertices = self.base_vertices.copy()
        
        # Apply height scaling
        if params.height != 1.0:
            self.current_vertices[:, 1] *= params.height
        
        # Apply build/weight morphs
        self._apply_build_morphs(params.build)
        
        # Apply head morphs
        self._apply_head_morphs(params)
        
        # Apply body morphs
        self._apply_body_morphs(params)
        
        # Apply limb morphs
        self._apply_limb_morphs(params)
        
        # Update mesh
        self.base_mesh.vertices = self.current_vertices
        
        return self.base_mesh
    
    def _apply_build_morphs(self, build: float):
        """Apply overall build/weight changes"""
        if build != 0:
            # Scale x and z based on build parameter
            # Positive = heavier, Negative = thinner
            scale_factor = 1.0 + (build * 0.3)
            
            # Don't scale uniformly - vary by height
            for i, vertex in enumerate(self.current_vertices):
                # Less scaling at extremities
                height_factor = 1.0 - abs(vertex[1] - 1.0) / 2.0
                final_scale = 1.0 + (scale_factor - 1.0) * height_factor
                
                self.current_vertices[i, 0] *= final_scale
                self.current_vertices[i, 2] *= final_scale
    
    def _apply_head_morphs(self, params: CharacterParameters):
        """Apply head-related morphs"""
        head_mask = self.vertex_groups.get('head', np.ones(len(self.current_vertices), dtype=bool))
        
        if params.head_size != 0:
            scale = 1.0 + params.head_size * 0.2
            self.current_vertices[head_mask] *= scale
        
        if params.jaw_width != 0:
            # Find lower head vertices and scale horizontally
            head_verts = self.current_vertices[head_mask]
            if len(head_verts) > 0:
                lower_head = head_verts[:, 1] < np.median(head_verts[:, 1])
                indices = np.where(head_mask)[0]
                for i in indices[lower_head]:
                    self.current_vertices[i, 0] *= (1.0 + params.jaw_width * 0.3)
    
    def _apply_body_morphs(self, params: CharacterParameters):
        """Apply torso-related morphs"""
        torso_mask = self.vertex_groups.get('torso', np.ones(len(self.current_vertices), dtype=bool))
        
        if params.shoulder_width != 0:
            # Find upper torso vertices
            torso_verts = self.current_vertices[torso_mask]
            if len(torso_verts) > 0:
                upper_torso = torso_verts[:, 1] > np.median(torso_verts[:, 1])
                indices = np.where(torso_mask)[0]
                for i in indices[upper_torso]:
                    self.current_vertices[i, 0] *= (1.0 + params.shoulder_width * 0.3)
        
        if params.waist_size != 0:
            # Find middle torso vertices
            torso_verts = self.current_vertices[torso_mask]
            if len(torso_verts) > 0:
                indices = np.where(torso_mask)[0]
                for i in indices:
                    # Inverse scaling for waist (negative = smaller)
                    self.current_vertices[i, 0] *= (1.0 - params.waist_size * 0.2)
                    self.current_vertices[i, 2] *= (1.0 - params.waist_size * 0.2)
    
    def _apply_limb_morphs(self, params: CharacterParameters):
        """Apply limb-related morphs"""
        arms_mask = self.vertex_groups.get('arms', np.ones(len(self.current_vertices), dtype=bool))
        legs_mask = self.vertex_groups.get('legs', np.ones(len(self.current_vertices), dtype=bool))
        
        if params.arm_length != 0:
            # Scale arms vertically
            self.current_vertices[arms_mask, 1] *= (1.0 + params.arm_length * 0.2)
        
        if params.leg_length != 0:
            # Scale legs vertically
            self.current_vertices[legs_mask, 1] *= (1.0 + params.leg_length * 0.3)
    
    def export_mesh(self, filepath: str, format: str = 'obj'):
        """Export the current mesh to file"""
        export_mesh = trimesh.Trimesh(
            vertices=self.current_vertices,
            faces=self.base_mesh.faces
        )
        export_mesh.export(filepath)
        logger.info(f"Exported mesh to {filepath}")
    
    def reset_to_base(self):
        """Reset mesh to base state"""
        self.current_vertices = self.base_vertices.copy()
        self.base_mesh.vertices = self.current_vertices


class CharacterPreset:
    """Manages character presets and templates"""
    
    def __init__(self, preset_dir: str = "presets"):
        self.preset_dir = Path(preset_dir)
        self.preset_dir.mkdir(exist_ok=True)
        self.presets: Dict[str, CharacterParameters] = {}
        self._load_default_presets()
    
    def _load_default_presets(self):
        """Load built-in preset templates"""
        # Human preset
        self.presets['human'] = CharacterParameters(
            height=1.0,
            build=0.0,
            head_size=0.0,
            shoulder_width=0.0
        )
        
        # Dwarf preset
        self.presets['dwarf'] = CharacterParameters(
            height=0.7,
            build=0.5,
            head_size=0.1,
            shoulder_width=0.3,
            arm_length=-0.1,
            leg_length=-0.3
        )
        
        # Elf preset  
        self.presets['elf'] = CharacterParameters(
            height=1.1,
            build=-0.2,
            head_size=-0.1,
            ear_size=0.3,
            ear_point=1.0,
            jaw_width=-0.2
        )
        
        # Orc preset
        self.presets['orc'] = CharacterParameters(
            height=1.15,
            build=0.7,
            head_size=0.2,
            jaw_width=0.5,
            brow_ridge=0.8,
            shoulder_width=0.5,
            arm_length=0.1
        )
        
        # Goblin preset
        self.presets['goblin'] = CharacterParameters(
            height=0.6,
            build=-0.3,
            head_size=0.3,
            ear_size=0.5,
            ear_point=0.7,
            nose_length=0.3,
            arm_length=0.2,
            leg_length=-0.2
        )
    
    def save_preset(self, name: str, params: CharacterParameters):
        """Save a preset to file"""
        filepath = self.preset_dir / f"{name}.json"
        with open(filepath, 'w') as f:
            json.dump(params.to_dict(), f, indent=2)
        self.presets[name] = params
        logger.info(f"Saved preset: {name}")
    
    def load_preset(self, name: str) -> Optional[CharacterParameters]:
        """Load a preset by name"""
        if name in self.presets:
            return self.presets[name]
        
        filepath = self.preset_dir / f"{name}.json"
        if filepath.exists():
            with open(filepath, 'r') as f:
                data = json.load(f)
            params = CharacterParameters.from_dict(data)
            self.presets[name] = params
            return params
        
        return None
    
    def list_presets(self) -> List[str]:
        """List all available presets"""
        return list(self.presets.keys())


class CharacterGenerator:
    """Main character generation system"""
    
    def __init__(self, base_mesh_path: Optional[str] = None):
        """Initialize the character generator"""
        self.mesh = CharacterMesh(base_mesh_path)
        self.parameters = CharacterParameters()
        self.preset_manager = CharacterPreset()
        self.history: List[CharacterParameters] = []
        
    def set_parameter(self, name: str, value: float):
        """Set a single parameter"""
        if hasattr(self.parameters, name):
            setattr(self.parameters, name, value)
            self.update_mesh()
        else:
            logger.warning(f"Unknown parameter: {name}")
    
    def set_parameters(self, params: CharacterParameters):
        """Set all parameters at once"""
        self.parameters = params
        self.update_mesh()
    
    def update_mesh(self):
        """Update mesh based on current parameters"""
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
        """Save character mesh and parameters"""
        # Save mesh
        mesh_path = filepath.replace('.json', '.obj')
        self.mesh.export_mesh(mesh_path)
        
        # Save parameters
        with open(filepath, 'w') as f:
            json.dump({
                'parameters': self.parameters.to_dict(),
                'mesh_file': os.path.basename(mesh_path)
            }, f, indent=2)
        
        logger.info(f"Saved character to {filepath}")
    
    def randomize(self, variation: float = 0.3):
        """Generate random character within variation bounds"""
        import random
        
        params_dict = self.parameters.to_dict()
        for key in params_dict:
            if key != 'height':  # Keep height more controlled
                params_dict[key] = random.uniform(-variation, variation)
            else:
                params_dict[key] = random.uniform(0.8, 1.2)
        
        self.set_parameters(CharacterParameters.from_dict(params_dict))
        logger.info("Generated random character")
    
    def reset(self):
        """Reset to default character"""
        self.parameters = CharacterParameters()
        self.mesh.reset_to_base()
        self.update_mesh()


# Example usage and testing
if __name__ == "__main__":
    # Create generator
    generator = CharacterGenerator()
    
    # Test with dwarf preset
    generator.load_preset('dwarf')
    
    # Customize further
    generator.set_parameter('muscle_definition', 0.5)
    generator.set_parameter('brow_ridge', 0.7)
    
    # Save the character
    generator.save_character('test_dwarf.json')
    
    # Test randomization
    generator.randomize(variation=0.4)
    generator.save_character('random_character.json')
    
    print("Character generation test complete!")
