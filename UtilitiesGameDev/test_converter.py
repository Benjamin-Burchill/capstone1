#!/usr/bin/env python3
"""
Test script for OBJ to Sprite Converter
Creates sample 3D models and converts them to sprites
"""

import trimesh
import numpy as np
from pathlib import Path
from obj_to_sprites import ObjToSpriteConverter

def create_sample_warrior():
    """Create a simple warrior model (stylized humanoid)"""
    meshes = []
    
    # Body (rectangular prism)
    body = trimesh.creation.box(extents=[0.4, 0.8, 0.2])
    body.apply_translation([0, 0, 0])
    meshes.append(body)
    
    # Head (sphere)
    head = trimesh.creation.icosphere(subdivisions=2, radius=0.2)
    head.apply_translation([0, 0.6, 0])
    meshes.append(head)
    
    # Arms (cylinders)
    left_arm = trimesh.creation.cylinder(radius=0.08, height=0.6)
    left_arm.apply_translation([-0.3, 0, 0])
    meshes.append(left_arm)
    
    right_arm = trimesh.creation.cylinder(radius=0.08, height=0.6)
    right_arm.apply_translation([0.3, 0, 0])
    meshes.append(right_arm)
    
    # Legs (cylinders)
    left_leg = trimesh.creation.cylinder(radius=0.1, height=0.8)
    left_leg.apply_translation([-0.15, -0.8, 0])
    meshes.append(left_leg)
    
    right_leg = trimesh.creation.cylinder(radius=0.1, height=0.8)
    right_leg.apply_translation([0.15, -0.8, 0])
    meshes.append(right_leg)
    
    # Sword (elongated box)
    sword = trimesh.creation.box(extents=[0.05, 1.0, 0.02])
    sword.apply_translation([0.4, 0, 0.1])
    sword.apply_transform(trimesh.transformations.rotation_matrix(
        np.radians(15), [0, 0, 1], point=[0.4, 0, 0]
    ))
    meshes.append(sword)
    
    # Shield (flattened cylinder)
    shield = trimesh.creation.cylinder(radius=0.25, height=0.05)
    shield.apply_translation([-0.4, 0.1, 0.1])
    shield.apply_transform(trimesh.transformations.rotation_matrix(
        np.radians(90), [0, 1, 0]
    ))
    meshes.append(shield)
    
    # Combine all parts
    warrior = trimesh.util.concatenate(meshes)
    
    # Apply color
    warrior.visual.vertex_colors = [100, 100, 200, 255]  # Blueish color
    
    return warrior

def create_sample_archer():
    """Create a simple archer model"""
    meshes = []
    
    # Body (slimmer)
    body = trimesh.creation.box(extents=[0.3, 0.7, 0.15])
    body.apply_translation([0, 0, 0])
    meshes.append(body)
    
    # Head with hood (cone + sphere)
    head = trimesh.creation.icosphere(subdivisions=2, radius=0.18)
    head.apply_translation([0, 0.55, 0])
    meshes.append(head)
    
    hood = trimesh.creation.cone(radius=0.22, height=0.3)
    hood.apply_translation([0, 0.6, -0.05])
    meshes.append(hood)
    
    # Arms
    left_arm = trimesh.creation.cylinder(radius=0.07, height=0.5)
    left_arm.apply_translation([-0.25, 0, 0])
    meshes.append(left_arm)
    
    right_arm = trimesh.creation.cylinder(radius=0.07, height=0.5)
    right_arm.apply_translation([0.25, 0, 0])
    meshes.append(right_arm)
    
    # Legs
    left_leg = trimesh.creation.cylinder(radius=0.08, height=0.7)
    left_leg.apply_translation([-0.12, -0.7, 0])
    meshes.append(left_leg)
    
    right_leg = trimesh.creation.cylinder(radius=0.08, height=0.7)
    right_leg.apply_translation([0.12, -0.7, 0])
    meshes.append(right_leg)
    
    # Bow (arc)
    # Create bow - simplified version that doesn't require slice_plane
    try:
        # Try to create bow using torus section (requires shapely)
        bow = trimesh.creation.torus(major_radius=0.4, minor_radius=0.02)
        bow.apply_translation([-0.3, 0, 0.1])
        bow.apply_transform(trimesh.transformations.rotation_matrix(
            np.radians(90), [0, 1, 0]
        ))
        # Slice to create arc
        bow = bow.slice_plane([0, 0, 0], [0, -1, 0])
        meshes.append(bow)
    except:
        # Fallback: Create simple bow using cylinders
        # Vertical part of bow
        bow_shaft = trimesh.creation.cylinder(radius=0.02, height=0.6)
        bow_shaft.apply_translation([-0.35, 0, 0])
        bow_shaft.apply_transform(trimesh.transformations.rotation_matrix(
            np.radians(15), [0, 0, 1]
        ))
        meshes.append(bow_shaft)
    
    # Quiver (cylinder)
    quiver = trimesh.creation.cylinder(radius=0.08, height=0.4)
    quiver.apply_translation([0.1, -0.1, -0.2])
    quiver.apply_transform(trimesh.transformations.rotation_matrix(
        np.radians(20), [1, 0, 0]
    ))
    meshes.append(quiver)
    
    # Combine
    archer = trimesh.util.concatenate(meshes)
    archer.visual.vertex_colors = [50, 150, 50, 255]  # Greenish color
    
    return archer

def create_sample_tower():
    """Create a simple tower/building model"""
    meshes = []
    
    # Base (larger cylinder)
    base = trimesh.creation.cylinder(radius=0.5, height=1.5)
    base.apply_translation([0, 0, 0])
    meshes.append(base)
    
    # Top (smaller cylinder)
    top = trimesh.creation.cylinder(radius=0.4, height=0.5)
    top.apply_translation([0, 1.0, 0])
    meshes.append(top)
    
    # Roof (cone)
    roof = trimesh.creation.cone(radius=0.5, height=0.6)
    roof.apply_translation([0, 1.5, 0])
    meshes.append(roof)
    
    # Windows (small boxes)
    for angle in [0, 90, 180, 270]:
        window = trimesh.creation.box(extents=[0.1, 0.15, 0.05])
        x = 0.45 * np.cos(np.radians(angle))
        z = 0.45 * np.sin(np.radians(angle))
        window.apply_translation([x, 0.3, z])
        meshes.append(window)
    
    # Door (rectangular box)
    door = trimesh.creation.box(extents=[0.15, 0.3, 0.05])
    door.apply_translation([0.45, -0.5, 0])
    meshes.append(door)
    
    # Combine
    tower = trimesh.util.concatenate(meshes)
    tower.visual.vertex_colors = [150, 120, 100, 255]  # Brown/stone color
    
    return tower

def test_basic_conversion():
    """Test the basic converter with sample models"""
    print("🧪 Testing OBJ to Sprite Converter")
    print("=" * 50)
    
    # Create test directory
    test_dir = Path("test_models")
    test_dir.mkdir(exist_ok=True)
    
    # Generate sample models
    models = {
        "warrior": create_sample_warrior(),
        "archer": create_sample_archer(),
        "tower": create_sample_tower()
    }
    
    print("\n📦 Creating sample models...")
    for name, mesh in models.items():
        obj_path = test_dir / f"{name}.obj"
        mesh.export(obj_path)
        print(f"  ✓ Created {obj_path}")
    
    print("\n🎨 Converting models to sprites...")
    for name in models.keys():
        obj_path = test_dir / f"{name}.obj"
        
        print(f"\nConverting {name}...")
        try:
            # Create converter with appropriate settings
            if name == "tower":
                # Buildings need fewer directions
                converter = ObjToSpriteConverter(
                    obj_path=obj_path,
                    output_dir=test_dir / "sprites",
                    sprite_size=(256, 256),
                    directions=4
                )
            else:
                # Units need 6 directions for hex movement
                converter = ObjToSpriteConverter(
                    obj_path=obj_path,
                    output_dir=test_dir / "sprites",
                    sprite_size=(128, 128),
                    directions=6
                )
            
            # Generate sprites
            sprites, _ = converter.generate_sprites(
                add_outline=True,
                elevation=25
            )
            
            # Create sprite sheet
            converter.create_sprite_sheet(sprites)
            
            # Create animation
            converter.generate_animation_preview(sprites)
            
            print(f"  ✓ Successfully converted {name}")
            
        except Exception as e:
            print(f"  ✗ Error converting {name}: {e}")
    
    print("\n✅ Test complete! Check the 'test_models/sprites' directory for output.")
    print("\n📝 Summary:")
    print("  - Sample OBJ files: test_models/*.obj")
    print("  - Generated sprites: test_models/sprites/")
    print("  - Sprite sheets: test_models/sprites/*_spritesheet.png")
    print("  - Animations: test_models/sprites/*_preview.gif")

def test_advanced_features():
    """Test advanced features like different angles and sizes"""
    print("\n🔬 Testing advanced features...")
    
    # Create a more complex model
    warrior = create_sample_warrior()
    
    # Test different configurations
    configs = [
        {"name": "tiny", "size": 64, "dirs": 4},
        {"name": "normal", "size": 128, "dirs": 6},
        {"name": "large", "size": 256, "dirs": 8},
        {"name": "huge", "size": 512, "dirs": 8},
    ]
    
    test_dir = Path("test_models/advanced")
    test_dir.mkdir(parents=True, exist_ok=True)
    
    # Save the model
    obj_path = test_dir / "test_warrior.obj"
    warrior.export(obj_path)
    
    for config in configs:
        print(f"\n  Testing {config['name']} configuration...")
        output_dir = test_dir / config['name']
        
        converter = ObjToSpriteConverter(
            obj_path=obj_path,
            output_dir=output_dir,
            sprite_size=(config['size'], config['size']),
            directions=config['dirs']
        )
        
        sprites, _ = converter.generate_sprites()
        converter.create_sprite_sheet(sprites)
        
        print(f"    ✓ Generated {config['size']}x{config['size']} sprites with {config['dirs']} directions")
    
    print("\n✅ Advanced tests complete! Check 'test_models/advanced/' for results.")

def cleanup_test_files():
    """Clean up test files"""
    import shutil
    
    test_dir = Path("test_models")
    if test_dir.exists():
        response = input("\n🗑️ Delete test files? (y/n): ")
        if response.lower() == 'y':
            shutil.rmtree(test_dir)
            print("  ✓ Test files deleted")
        else:
            print("  ℹ Test files kept in 'test_models' directory")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--advanced":
        test_basic_conversion()
        test_advanced_features()
    elif len(sys.argv) > 1 and sys.argv[1] == "--cleanup":
        cleanup_test_files()
    else:
        test_basic_conversion()
        
        print("\n💡 Tips:")
        print("  - Run with '--advanced' for more tests")
        print("  - Run with '--cleanup' to delete test files")
        print("  - Check generated sprites in 'test_models/sprites/'")
        print("  - Import sprite sheets into Unity for your game!")
