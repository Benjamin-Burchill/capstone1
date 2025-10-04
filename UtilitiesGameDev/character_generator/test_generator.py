#!/usr/bin/env python3
"""
Test script for Character Generator
Demonstrates basic functionality without GUI
"""

import os
import sys
from pathlib import Path

# Add parent directory to path if needed
sys.path.insert(0, str(Path(__file__).parent))

from character_generator import CharacterGenerator, CharacterParameters

def test_basic_generation():
    """Test basic character generation"""
    print("=" * 60)
    print("Character Generator Test Suite")
    print("=" * 60)
    
    # Create generator
    print("\n1. Creating character generator...")
    generator = CharacterGenerator()
    print("   [OK] Generator created")
    
    # Test presets
    print("\n2. Testing presets...")
    presets = ["human", "dwarf", "elf", "orc", "goblin"]
    
    for preset in presets:
        print(f"\n   Testing {preset} preset:")
        generator.load_preset(preset)
        
        # Get some key parameters
        params = generator.parameters
        print(f"   - Height: {params.height:.2f}")
        print(f"   - Build: {params.build:.2f}")
        print(f"   - Head size: {params.head_size:.2f}")
        
        # Save the preset character
        filename = f"test_{preset}.json"
        generator.save_character(filename)
        print(f"   [OK] Saved to {filename}")
    
    # Test parameter modification
    print("\n3. Testing parameter modification...")
    generator.load_preset("human")
    print("   Starting with human preset")
    
    # Make it a muscular warrior type
    generator.set_parameter("muscle_definition", 0.8)
    generator.set_parameter("shoulder_width", 0.5)
    generator.set_parameter("chest_size", 0.4)
    generator.set_parameter("jaw_width", 0.3)
    generator.set_parameter("brow_ridge", 0.5)
    
    print("   Modified to warrior type:")
    params = generator.parameters
    print(f"   - Muscle: {params.muscle_definition:.2f}")
    print(f"   - Shoulders: {params.shoulder_width:.2f}")
    print(f"   - Chest: {params.chest_size:.2f}")
    
    generator.save_character("test_warrior.json")
    print("   [OK] Saved warrior character")
    
    # Test randomization
    print("\n4. Testing randomization...")
    for i in range(3):
        generator.randomize(variation=0.4)
        filename = f"test_random_{i}.json"
        generator.save_character(filename)
        print(f"   [OK] Generated random character {i+1}")
    
    # Test extreme values
    print("\n5. Testing extreme values...")
    
    # Tiny character
    generator.reset()
    generator.set_parameter("height", 0.5)
    generator.set_parameter("build", -1.0)
    generator.save_character("test_tiny.json")
    print("   [OK] Created tiny character")
    
    # Large character
    generator.reset()
    generator.set_parameter("height", 1.5)
    generator.set_parameter("build", 1.0)
    generator.save_character("test_large.json")
    print("   [OK] Created large character")
    
    # Fantasy character with special features
    print("\n6. Testing fantasy features...")
    generator.load_preset("elf")
    generator.set_parameter("ear_point", 1.0)
    generator.set_parameter("horn_size", 0.3)
    generator.set_parameter("tail_length", 0.5)
    generator.save_character("test_fantasy.json")
    print("   [OK] Created fantasy character with horns and tail")
    
    print("\n" + "=" * 60)
    print("All tests completed successfully!")
    print("=" * 60)
    
    # List generated files
    print("\nGenerated files:")
    test_files = list(Path(".").glob("test_*.json"))
    obj_files = list(Path(".").glob("test_*.obj"))
    
    for f in test_files:
        size = f.stat().st_size
        print(f"   - {f.name} ({size} bytes)")
    
    for f in obj_files:
        size = f.stat().st_size
        print(f"   - {f.name} ({size} bytes)")
    
    # Cleanup option
    print("\nCleanup test files? (y/n):", end=" ")
    if input().lower() == 'y':
        for f in test_files + obj_files:
            f.unlink()
        print("Test files cleaned up.")
    else:
        print("Test files kept for inspection.")

def test_mesh_info():
    """Display information about the generated mesh"""
    print("\n" + "=" * 60)
    print("Mesh Information Test")
    print("=" * 60)
    
    generator = CharacterGenerator()
    
    # Get mesh info
    mesh = generator.mesh.base_mesh
    print(f"\nBase mesh statistics:")
    print(f"  - Vertices: {len(mesh.vertices)}")
    print(f"  - Faces: {len(mesh.faces)}")
    print(f"  - Bounds: {mesh.bounds}")
    print(f"  - Watertight: {mesh.is_watertight}")
    
    # Apply some morphs and check again
    generator.load_preset("orc")
    mesh = generator.mesh.base_mesh
    print(f"\nOrc preset mesh statistics:")
    print(f"  - Vertices: {len(mesh.vertices)}")
    print(f"  - Faces: {len(mesh.faces)}")
    print(f"  - Bounds: {mesh.bounds}")

def test_parameter_ranges():
    """Test parameter value ranges"""
    print("\n" + "=" * 60)
    print("Parameter Range Test")
    print("=" * 60)
    
    params = CharacterParameters()
    param_dict = params.to_dict()
    
    print(f"\nTotal parameters: {len(param_dict)}")
    print("\nParameter list:")
    
    for i, (name, default) in enumerate(param_dict.items(), 1):
        print(f"  {i:2}. {name:20} (default: {default:6.2f})")

def main():
    """Run all tests"""
    try:
        # Run tests
        test_basic_generation()
        test_mesh_info()
        test_parameter_ranges()
        
        print("\n" + "=" * 60)
        print("[SUCCESS] All tests passed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n[ERROR] Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
