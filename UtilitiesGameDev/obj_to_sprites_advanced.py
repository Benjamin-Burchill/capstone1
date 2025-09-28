#!/usr/bin/env python3
"""
Advanced OBJ to Sprite Converter using PyRender
Higher quality rendering with proper lighting and materials
"""

import numpy as np
import trimesh
import pyrender
from PIL import Image
import os
from pathlib import Path
import argparse

class AdvancedObjToSpriteConverter:
    """
    Advanced converter using PyRender for higher quality sprites
    Includes proper lighting, shadows, and material support
    """
    
    def __init__(self, obj_path, output_dir="sprites_hq", sprite_size=(256, 256), 
                 directions=6, use_lighting=True):
        """
        Initialize the advanced converter
        
        Args:
            obj_path: Path to the OBJ file
            output_dir: Directory to save sprites
            sprite_size: Size of each sprite (width, height)
            directions: Number of directional views (6 or 8)
            use_lighting: Enable advanced lighting
        """
        self.obj_path = Path(obj_path)
        self.output_dir = Path(output_dir)
        self.sprite_size = sprite_size
        self.directions = directions
        self.use_lighting = use_lighting
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load the 3D model
        self.trimesh_mesh = self.load_obj()
        
        # Create pyrender scene
        self.scene = pyrender.Scene(ambient_light=[0.3, 0.3, 0.3])
        
        # Define camera angles for different directions
        if directions == 6:
            # Hexagonal directions
            self.angles = [
                ('east', 0),
                ('southeast', 60),
                ('southwest', 120),
                ('west', 180),
                ('northwest', 240),
                ('northeast', 300)
            ]
        else:
            # 8-directional
            self.angles = [
                ('north', 0),
                ('northeast', 45),
                ('east', 90),
                ('southeast', 135),
                ('south', 180),
                ('southwest', 225),
                ('west', 270),
                ('northwest', 315)
            ]
    
    def load_obj(self):
        """Load and prepare the OBJ file"""
        try:
            # Load mesh
            mesh = trimesh.load(self.obj_path)
            print(f"✓ Loaded OBJ file: {self.obj_path}")
            print(f"  Vertices: {len(mesh.vertices)}")
            print(f"  Faces: {len(mesh.faces)}")
            
            # Center the mesh
            mesh.vertices -= mesh.center_mass
            
            # Normalize to unit cube
            scale = 1.5 / mesh.extents.max()
            mesh.vertices *= scale
            
            # Apply a default material if none exists
            if not hasattr(mesh.visual, 'material') or mesh.visual.material is None:
                mesh.visual = trimesh.visual.TextureVisuals(
                    material=trimesh.visual.material.SimpleMaterial(
                        diffuse=[200, 200, 200, 255],
                        ambient=[100, 100, 100, 255],
                        specular=[255, 255, 255, 255],
                        glossiness=32
                    )
                )
            
            return mesh
            
        except Exception as e:
            print(f"✗ Error loading OBJ file: {e}")
            raise
    
    def setup_scene(self, mesh, camera_pose):
        """
        Set up the rendering scene with mesh, camera, and lights
        
        Args:
            mesh: Trimesh mesh object
            camera_pose: 4x4 transformation matrix for camera
        """
        # Clear previous scene
        self.scene.clear()
        
        # Add mesh to scene
        mesh_node = pyrender.Mesh.from_trimesh(mesh)
        self.scene.add(mesh_node)
        
        # Add camera
        camera = pyrender.PerspectiveCamera(yfov=np.pi / 3.0, aspectRatio=1.0)
        self.scene.add(camera, pose=camera_pose)
        
        if self.use_lighting:
            # Add multiple lights for better illumination
            # Key light (main light)
            key_light = pyrender.DirectionalLight(color=[1.0, 1.0, 1.0], intensity=3.0)
            key_pose = self.create_look_at_matrix([2, 2, 2], [0, 0, 0])
            self.scene.add(key_light, pose=key_pose)
            
            # Fill light (softer, from opposite side)
            fill_light = pyrender.DirectionalLight(color=[0.8, 0.8, 1.0], intensity=1.5)
            fill_pose = self.create_look_at_matrix([-2, 1, -1], [0, 0, 0])
            self.scene.add(fill_light, pose=fill_pose)
            
            # Rim light (back light for edge definition)
            rim_light = pyrender.DirectionalLight(color=[1.0, 0.9, 0.8], intensity=2.0)
            rim_pose = self.create_look_at_matrix([0, 1, -3], [0, 0, 0])
            self.scene.add(rim_light, pose=rim_pose)
    
    def create_look_at_matrix(self, eye, target, up=[0, 1, 0]):
        """
        Create a look-at transformation matrix
        
        Args:
            eye: Camera position
            target: Look-at target
            up: Up vector
        """
        eye = np.array(eye)
        target = np.array(target)
        up = np.array(up)
        
        # Calculate forward, right, and up vectors
        forward = target - eye
        forward = forward / np.linalg.norm(forward)
        
        right = np.cross(forward, up)
        right = right / np.linalg.norm(right)
        
        up = np.cross(right, forward)
        
        # Create rotation matrix
        matrix = np.eye(4)
        matrix[:3, 0] = right
        matrix[:3, 1] = up
        matrix[:3, 2] = -forward
        matrix[:3, 3] = eye
        
        return matrix
    
    def render_sprite(self, mesh, angle, elevation=30):
        """
        Render a single sprite from given angle
        
        Args:
            mesh: Trimesh mesh
            angle: Horizontal rotation angle in degrees
            elevation: Camera elevation in degrees
        """
        # Calculate camera position
        angle_rad = np.radians(angle)
        elev_rad = np.radians(elevation)
        
        # Camera distance
        distance = 3.0
        
        # Calculate camera position in spherical coordinates
        x = distance * np.cos(elev_rad) * np.cos(angle_rad)
        y = distance * np.sin(elev_rad)
        z = distance * np.cos(elev_rad) * np.sin(angle_rad)
        
        # Create camera pose matrix
        camera_pose = self.create_look_at_matrix([x, y, z], [0, 0, 0])
        
        # Setup scene
        self.setup_scene(mesh, camera_pose)
        
        # Create renderer
        r = pyrender.OffscreenRenderer(self.sprite_size[0], self.sprite_size[1])
        
        # Render
        color, depth = r.render(self.scene)
        
        # Convert to PIL Image
        image = Image.fromarray(color, 'RGBA')
        
        # Clean up renderer
        r.delete()
        
        return image
    
    def process_sprite(self, image):
        """
        Post-process the rendered sprite
        
        Args:
            image: PIL Image
        """
        # Convert to RGBA if needed
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        # Get alpha channel
        data = np.array(image)
        
        # Create alpha mask from non-black pixels
        # (assuming black background from renderer)
        alpha = np.ones((data.shape[0], data.shape[1]), dtype=np.uint8) * 255
        black_pixels = (data[:,:,0] == 0) & (data[:,:,1] == 0) & (data[:,:,2] == 0)
        alpha[black_pixels] = 0
        
        # Apply alpha channel
        data[:,:,3] = alpha
        
        # Convert back to PIL Image
        processed = Image.fromarray(data, 'RGBA')
        
        return processed
    
    def generate_all_sprites(self, elevation=30):
        """
        Generate sprites from all angles
        
        Args:
            elevation: Camera elevation angle
        """
        print(f"\n🎨 Generating {self.directions} high-quality sprites...")
        sprites = {}
        
        for direction, angle in self.angles:
            print(f"  Rendering {direction} view (angle={angle}°)...")
            
            # Render sprite
            image = self.render_sprite(self.trimesh_mesh, angle, elevation)
            
            # Post-process
            image = self.process_sprite(image)
            
            # Save sprite
            sprite_path = self.output_dir / f"{self.obj_path.stem}_{direction}.png"
            image.save(sprite_path, 'PNG')
            sprites[direction] = image
            
            print(f"    ✓ Saved: {sprite_path}")
        
        # Create sprite sheet
        self.create_sprite_sheet(sprites)
        
        return sprites
    
    def create_sprite_sheet(self, sprites):
        """Create a combined sprite sheet"""
        columns = min(4, len(sprites))  # Max 4 columns
        rows = (len(sprites) + columns - 1) // columns
        
        sheet_width = self.sprite_size[0] * columns
        sheet_height = self.sprite_size[1] * rows
        
        # Create sprite sheet
        sprite_sheet = Image.new('RGBA', (sheet_width, sheet_height), (0, 0, 0, 0))
        
        for idx, (direction, image) in enumerate(sprites.items()):
            row = idx // columns
            col = idx % columns
            x = col * self.sprite_size[0]
            y = row * self.sprite_size[1]
            sprite_sheet.paste(image, (x, y))
        
        # Save
        sheet_path = self.output_dir / f"{self.obj_path.stem}_spritesheet_hq.png"
        sprite_sheet.save(sheet_path, 'PNG')
        print(f"\n✓ High-quality sprite sheet saved: {sheet_path}")
        
        # Save metadata
        self.save_metadata(sprites)
    
    def save_metadata(self, sprites):
        """Save JSON metadata for Unity import"""
        import json
        
        metadata = {
            "name": self.obj_path.stem,
            "sprite_size": list(self.sprite_size),
            "directions": list(sprites.keys()),
            "format": "RGBA",
            "usage": "unit_sprite",
            "unity_settings": {
                "texture_type": "Sprite",
                "sprite_mode": "Multiple",
                "pixels_per_unit": 100,
                "filter_mode": "Point",
                "compression": "None"
            }
        }
        
        metadata_path = self.output_dir / f"{self.obj_path.stem}_metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"✓ Metadata saved: {metadata_path}")


def main():
    """Main function for command-line usage"""
    parser = argparse.ArgumentParser(
        description="Advanced OBJ to Sprite converter with high-quality rendering"
    )
    parser.add_argument("obj_file", help="Path to the OBJ file")
    parser.add_argument("-o", "--output", default="sprites_hq",
                       help="Output directory")
    parser.add_argument("-s", "--size", type=int, default=256,
                       help="Sprite size in pixels (default: 256)")
    parser.add_argument("-d", "--directions", type=int, choices=[6, 8], default=6,
                       help="Number of directions")
    parser.add_argument("-e", "--elevation", type=float, default=30,
                       help="Camera elevation angle")
    parser.add_argument("--no-lighting", action="store_true",
                       help="Disable advanced lighting")
    
    args = parser.parse_args()
    
    # Create converter
    converter = AdvancedObjToSpriteConverter(
        obj_path=args.obj_file,
        output_dir=args.output,
        sprite_size=(args.size, args.size),
        directions=args.directions,
        use_lighting=not args.no_lighting
    )
    
    # Generate sprites
    sprites = converter.generate_all_sprites(elevation=args.elevation)
    
    print(f"\n✅ Advanced conversion complete!")
    print(f"📁 Output directory: {converter.output_dir}")


if __name__ == "__main__":
    main()
