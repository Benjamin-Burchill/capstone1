#!/usr/bin/env python3
"""
Generate All Presets - Create meshes for all built-in character types
======================================================================

This script generates meshes for all available presets to see the variety.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.params import PRESETS, get_preset
from src.mesh import generate_base_mesh


def main():
    print("=" * 70)
    print("GENERATING ALL PRESETS")
    print("=" * 70)
    print()
    
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'outputs', 'presets')
    os.makedirs(output_dir, exist_ok=True)
    
    results = []
    
    for preset_name in PRESETS.keys():
        print(f"\nGenerating: {preset_name}")
        print("-" * 70)
        
        # Get preset params
        params = get_preset(preset_name)
        
        # Display key parameters
        print(f"  Height: {params.height:.2f}m")
        print(f"  Stockiness: {params.stockiness:.2f}")
        print(f"  Head ratio: {params.head_ratio:.3f}")
        print(f"  Arm length: {params.arm_length_ratio:.3f}")
        print(f"  Leg length: {params.leg_length_ratio:.3f}")
        
        # Generate mesh
        mesh = generate_base_mesh(params)
        
        # Export
        output_path = os.path.join(output_dir, f'{preset_name}.obj')
        mesh.export(output_path)
        
        print(f"  ✅ Saved: {output_path}")
        print(f"     Vertices: {len(mesh.vertices)}, Faces: {len(mesh.faces)}")
        
        results.append({
            'name': preset_name,
            'path': output_path,
            'vertices': len(mesh.vertices),
            'faces': len(mesh.faces)
        })
    
    # Summary table
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"\n{'Preset':<15} {'Vertices':>10} {'Faces':>10}")
    print("-" * 70)
    for result in results:
        print(f"{result['name']:<15} {result['vertices']:>10} {result['faces']:>10}")
    
    print(f"\n📂 All files saved to: {output_dir}")
    print("\n🎨 Compare these in Blender to see parameter effects!")
    print("=" * 70)


if __name__ == "__main__":
    main()


