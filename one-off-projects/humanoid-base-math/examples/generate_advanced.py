#!/usr/bin/env python3
"""
Advanced Mathematical Humanoid Generation
==========================================

This script demonstrates how far pure mathematics can go toward realism
by stacking multiple layers of mathematical "rules":

1. Basic geometric primitives (your Phase 1)
2. SMPL-style parametric blend shapes
3. NURBS-based smooth surfaces
4. Fractal noise for organic detail
5. Volume-preserving deformations

Shows the progression from 450-vert geometric to ~2k-vert semi-realistic.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.params import HumanoidParams, get_preset
from src.mesh import generate_base_mesh
from src.advanced_math import (
    AdvancedMathematicalModel,
    enhance_mesh_with_advanced_math
)
import numpy as np


def demonstrate_progression():
    """Show progression from geometric to advanced mathematical."""
    
    print("=" * 80)
    print("MATHEMATICAL HUMANOID PROGRESSION DEMONSTRATION")
    print("Exploring how many 'rules' we can stack before needing artist input")
    print("=" * 80)
    print()
    
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'outputs', 'advanced')
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize advanced math model
    adv_model = AdvancedMathematicalModel()
    
    # ========================================================================
    # LEVEL 1: Basic Geometric (Your Current System)
    # ========================================================================
    print("\n" + "=" * 80)
    print("LEVEL 1: Basic Geometric Primitives")
    print("=" * 80)
    print("Rules: ~50 (cylinder radii, ellipse ratios, spline control points)")
    print("-" * 80)
    
    params = HumanoidParams(height=1.75, stockiness=1.0)
    basic_mesh = generate_base_mesh(params, apply_smoothing=True)
    
    basic_path = os.path.join(output_dir, 'level1_basic_geometric.obj')
    basic_mesh.export(basic_path)
    
    print(f"Generated: {len(basic_mesh.vertices)} vertices")
    print(f"Quality: Intentionally geometric (Minecraft/Roblox style)")
    print(f"Exported: {basic_path}")
    
    # ========================================================================
    # LEVEL 2: SMPL-Style Blend Shapes
    # ========================================================================
    print("\n" + "=" * 80)
    print("LEVEL 2: Adding SMPL-Style Parametric Blend Shapes")
    print("=" * 80)
    print("Rules: ~50 + 10 blend shapes (each = 100s of local deformation rules)")
    print("Total effective rules: ~5,000")
    print("-" * 80)
    
    # Create blend shapes for the base mesh
    blend_shapes = adv_model.create_smpl_blend_shapes(
        basic_mesh.vertices,
        n_shapes=10
    )
    
    # Apply blend shapes with example weights
    blend_weights = np.array([
        0.3,   # Overall size
        0.5,   # Stockiness
        -0.2,  # Leg length
        0.1,   # Torso length
        0.4,   # Shoulder width
        0.2,   # Hip width
        0.15,  # Chest depth
        0.6,   # Muscle bulk
        0.0,   # Head size
        0.3    # Limb thickness
    ])
    
    blended_verts = adv_model.apply_blend_shapes(
        basic_mesh.vertices,
        blend_shapes,
        blend_weights
    )
    
    # Create new mesh with blended vertices
    import trimesh
    blend_mesh = trimesh.Trimesh(vertices=blended_verts, faces=basic_mesh.faces)
    
    blend_path = os.path.join(output_dir, 'level2_smpl_blendshapes.obj')
    blend_mesh.export(blend_path)
    
    print(f"Generated: {len(blend_mesh.vertices)} vertices")
    print(f"Quality: Smooth geometric with anatomical proportions")
    print(f"Improvement: Better body shape variation, still clean topology")
    print(f"Exported: {blend_path}")
    
    # ========================================================================
    # LEVEL 3: Adding Organic Detail via Fractal Noise
    # ========================================================================
    print("\n" + "=" * 80)
    print("LEVEL 3: Adding Fractal Organic Detail")
    print("=" * 80)
    print("Rules: ~5,000 + multi-octave noise (simulates 100k+ surface variations)")
    print("Total effective rules: ~100,000")
    print("-" * 80)
    
    # Calculate normals for noise displacement
    normals = blend_mesh.vertex_normals
    
    # Add organic detail
    detailed_verts = adv_model.add_organic_detail(
        blended_verts,
        normals,
        detail_amplitude=0.004,  # Subtle
        detail_scale=12.0
    )
    
    # Add muscle striations in vertical direction
    detailed_verts = adv_model.add_muscle_striations(
        detailed_verts,
        normals,
        direction=np.array([0, 1, 0]),
        strength=0.002
    )
    
    detailed_mesh = trimesh.Trimesh(vertices=detailed_verts, faces=basic_mesh.faces)
    
    detail_path = os.path.join(output_dir, 'level3_fractal_detail.obj')
    detailed_mesh.export(detail_path)
    
    print(f"Generated: {len(detailed_mesh.vertices)} vertices")
    print(f"Quality: Organic surface texture, less 'plasticky'")
    print(f"Improvement: Subtle variations mimic biological complexity")
    print(f"Exported: {detail_path}")
    
    # ========================================================================
    # LEVEL 4: Volume-Preserving Deformations
    # ========================================================================
    print("\n" + "=" * 80)
    print("LEVEL 4: Volume-Preserving Transformations")
    print("=" * 80)
    print("Rules: ~100,000 + physical conservation laws")
    print("Mimics: Biological constraints (squash & stretch)")
    print("-" * 80)
    
    # Apply volume-preserving scale
    vp_verts = adv_model.volume_preserving_scale(
        detailed_verts,
        scale_factors=np.array([1.0, 1.2, 1.0])  # Taller, compensate width
    )
    
    vp_mesh = trimesh.Trimesh(vertices=vp_verts, faces=basic_mesh.faces)
    
    vp_path = os.path.join(output_dir, 'level4_volume_preserving.obj')
    vp_mesh.export(vp_path)
    
    print(f"Generated: {len(vp_mesh.vertices)} vertices")
    print(f"Quality: Natural-looking proportions with physical plausibility")
    print(f"Improvement: Deformations respect mass conservation")
    print(f"Exported: {vp_path}")
    
    # ========================================================================
    # COMPARISON: Generate Different Body Types
    # ========================================================================
    print("\n" + "=" * 80)
    print("BONUS: Generating Different Body Types with Advanced Math")
    print("=" * 80)
    
    body_types = {
        'athletic': {
            'params': HumanoidParams(height=1.85, stockiness=1.1),
            'weights': np.array([0.2, 0.3, 0.1, 0.0, 0.5, 0.1, 0.2, 0.8, 0.0, 0.4])
        },
        'stocky': {
            'params': HumanoidParams(height=1.65, stockiness=1.4),
            'weights': np.array([0.0, 0.8, -0.2, 0.0, 0.4, 0.6, 0.3, 0.5, 0.1, 0.6])
        },
        'slender': {
            'params': HumanoidParams(height=1.80, stockiness=0.8),
            'weights': np.array([0.1, -0.4, 0.2, 0.1, -0.2, -0.2, -0.1, -0.3, 0.0, -0.2])
        }
    }
    
    for body_type, config in body_types.items():
        print(f"\nGenerating: {body_type}")
        
        # Generate base
        base = generate_base_mesh(config['params'], apply_smoothing=True)
        
        # Apply blend shapes
        shapes = adv_model.create_smpl_blend_shapes(base.vertices)
        verts = adv_model.apply_blend_shapes(base.vertices, shapes, config['weights'])
        
        # Add detail
        normals = trimesh.Trimesh(vertices=verts, faces=base.faces).vertex_normals
        verts = adv_model.add_organic_detail(verts, normals, 0.004, 12.0)
        
        # Export
        mesh = trimesh.Trimesh(vertices=verts, faces=base.faces)
        path = os.path.join(output_dir, f'advanced_{body_type}.obj')
        mesh.export(path)
        
        print(f"  Vertices: {len(mesh.vertices)}")
        print(f"  Exported: {path}")
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("\n" + "=" * 80)
    print("SUMMARY: The Mathematical Progression")
    print("=" * 80)
    print()
    print("Level 1 (Basic):          ~450 verts,   ~50 rules")
    print("Level 2 (Blend Shapes):   ~450 verts,   ~5,000 effective rules")
    print("Level 3 (Fractal Detail): ~450 verts,   ~100,000 effective rules")
    print("Level 4 (Physics):        ~450 verts,   Physical constraints added")
    print()
    print("Quality Progression:")
    print("  Level 1: Minecraft/Roblox style (intentionally geometric)")
    print("  Level 2: Smooth humanoid with good proportions")
    print("  Level 3: Organic surface texture, less 'plastic'")
    print("  Level 4: Natural deformations with physical plausibility")
    print()
    print("The Reality:")
    print("  - Still ~450 vertices (topology unchanged)")
    print("  - More rules != more vertices != more detail")
    print("  - To get detailed faces/hands: need 10k+ vertices")
    print("  - To get photorealism: need artist sculpting + textures")
    print()
    print("Mathematical Ceiling:")
    print("  [YES] Can achieve: Smooth, organic-looking stylized humanoids")
    print("  [NO]  Cannot achieve: Realistic faces, fine details, true photorealism")
    print("  -> Reason: Complexity explosion (millions of verts needed)")
    print()
    print("Conclusion:")
    print("  Pure math gets you from 'geometric' to 'semi-realistic'")
    print("  For production: Use MakeHuman base (artist-sculpted) + your morphs")
    print("  This exercise: Valuable for understanding the limits!")
    print()
    print("=" * 80)
    print("\nAll files exported to:")
    print(f"  {output_dir}")
    print()
    print("View in Blender to compare the progression!")
    print("=" * 80)


if __name__ == "__main__":
    try:
        demonstrate_progression()
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

