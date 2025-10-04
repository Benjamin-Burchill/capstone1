#!/usr/bin/env python3
"""
Generate Human Example - Create your first mathematical humanoid
================================================================

This script demonstrates basic humanoid generation from mathematical parameters.

Run: python examples/generate_human.py

Output: outputs/base_human.obj (view in Blender, MeshLab, or any 3D viewer)
"""

import sys
import os

# Add parent directory to path so we can import our modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.params import HumanoidParams, get_preset
from src.mesh import generate_base_mesh


def main():
    print("=" * 70)
    print("MATHEMATICAL HUMANOID GENERATOR")
    print("=" * 70)
    print()
    
    # Method 1: Use default parameters
    print("Method 1: Default human parameters")
    print("-" * 70)
    params = HumanoidParams()
    print(f"Height: {params.height}m")
    print(f"Stockiness: {params.stockiness}")
    print(f"Head ratio: {params.head_ratio}")
    print()
    
    # Generate mesh
    print("Generating mesh...")
    mesh = generate_base_mesh(params)
    
    # Export
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'outputs')
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, 'base_human.obj')
    mesh.export(output_path)
    print(f"\n[OK] Exported to: {output_path}")
    print(f"     Vertices: {len(mesh.vertices)}")
    print(f"     Faces: {len(mesh.faces)}")
    print(f"     Watertight: {mesh.is_watertight}")
    print()
    
    # Method 2: Use a preset
    print("\nMethod 2: Using preset (Dwarf)")
    print("-" * 70)
    dwarf_params = get_preset('dwarf')
    print(f"Height: {dwarf_params.height}m (shorter than human)")
    print(f"Stockiness: {dwarf_params.stockiness} (stockier)")
    
    dwarf_mesh = generate_base_mesh(dwarf_params)
    dwarf_path = os.path.join(output_dir, 'dwarf.obj')
    dwarf_mesh.export(dwarf_path)
    print(f"\n[OK] Exported to: {dwarf_path}")
    print()
    
    # Method 3: Custom parameters
    print("\nMethod 3: Custom parameters (Athletic build)")
    print("-" * 70)
    athletic = HumanoidParams(
        height=1.85,
        stockiness=1.1,
        shoulder_width_ratio=0.27,
        waist_width_ratio=0.14,
        upper_arm_thickness=0.065,
        thigh_thickness=0.085
    )
    print(f"Height: {athletic.height}m (tall)")
    print(f"Shoulder width: {athletic.shoulder_width_ratio * athletic.height:.2f}m")
    
    athletic_mesh = generate_base_mesh(athletic)
    athletic_path = os.path.join(output_dir, 'athletic.obj')
    athletic_mesh.export(athletic_path)
    print(f"\n[OK] Exported to: {athletic_path}")
    print()
    
    # Summary
    print("=" * 70)
    print("GENERATION COMPLETE!")
    print("=" * 70)
    print("\nGenerated 3 meshes:")
    print(f"  1. {output_path}")
    print(f"  2. {dwarf_path}")
    print(f"  3. {athletic_path}")
    print()
    print("[FILES] Open these files in:")
    print("   - Blender (free, blender.org)")
    print("   - MeshLab (free, meshlab.net)")
    print("   - Any 3D modeling software")
    print()
    print("[NEXT] Next steps:")
    print("   - Adjust parameters in this script")
    print("   - Try different presets (elf, orc, goblin)")
    print("   - Import into your main character creator")
    print()
    print("[WARN] Reality check:")
    print("   These are geometric/stylized meshes, not photorealistic.")
    print("   For production, consider hybrid approach with MakeHuman.")
    print("=" * 70)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

