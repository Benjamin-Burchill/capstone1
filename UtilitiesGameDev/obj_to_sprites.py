#!/usr/bin/env python3
"""
OBJ to Sprite Converter for EoAT Game
Converts 3D OBJ models to 2D sprite sheets with multiple viewing angles
Perfect for creating unit sprites from 3D models
"""

import numpy as np
import trimesh
from PIL import Image, ImageDraw
import os
import argparse
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import warnings
warnings.filterwarnings('ignore')

class ObjToSpriteConverter:
    """
    Converts OBJ 3D models to 2D sprites from multiple angles
    Generates sprites for 6 or 8 directional views
    """
    
    def __init__(self, obj_path, output_dir="sprites", sprite_size=(128, 128), 
                 directions=6, background_color=(0, 0, 0, 0)):
        """
        Initialize the converter
        
        Args:
            obj_path: Path to the OBJ file
            output_dir: Directory to save sprites
            sprite_size: Size of each sprite (width, height)
            directions: Number of directional views (6 or 8)
            background_color: RGBA background color
        """
        self.obj_path = Path(obj_path)
        self.output_dir = Path(output_dir)
        self.sprite_size = sprite_size
        self.directions = directions
        self.background_color = background_color
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load the 3D model
        self.mesh = self.load_obj()
        
        # Define viewing angles for different directions
        if directions == 6:
            # Hexagonal directions (for hex-based game)
            self.angles = {
                'east': 0,
                'southeast': 60,
                'southwest': 120,
                'west': 180,
                'northwest': 240,
                'northeast': 300
            }
        else:
            # 8-directional (standard isometric)
            self.angles = {
                'east': 0,
                'southeast': 45,
                'south': 90,
                'southwest': 135,
                'west': 180,
                'northwest': 225,
                'north': 270,
                'northeast': 315
            }
    
    def load_obj(self):
        """Load the OBJ file using trimesh"""
        try:
            mesh = trimesh.load(self.obj_path)
            print(f"✓ Loaded OBJ file: {self.obj_path}")
            print(f"  Vertices: {len(mesh.vertices)}")
            print(f"  Faces: {len(mesh.faces)}")
            
            # Center and normalize the mesh
            mesh.vertices -= mesh.center_mass
            scale = 2.0 / mesh.extents.max()
            mesh.vertices *= scale
            
            return mesh
        except Exception as e:
            print(f"✗ Error loading OBJ file: {e}")
            raise
    
    def render_view(self, mesh, azimuth, elevation=20, ax=None):
        """
        Render a single view of the mesh
        
        Args:
            mesh: Trimesh object
            azimuth: Horizontal rotation angle
            elevation: Vertical viewing angle
            ax: Matplotlib axis (creates new if None)
        """
        if ax is None:
            fig = plt.figure(figsize=(self.sprite_size[0]/100, self.sprite_size[1]/100), dpi=100)
            ax = fig.add_subplot(111, projection='3d')
        
        # Get mesh vertices and faces
        vertices = mesh.vertices
        faces = mesh.faces
        
        # Create polygon collection
        poly3d = []
        for face in faces:
            poly3d.append(vertices[face])
        
        # Add the collection to the axes
        face_collection = Poly3DCollection(poly3d, 
                                          facecolors='lightgray',
                                          edgecolors='black',
                                          linewidths=0.5,
                                          alpha=0.9)
        ax.add_collection3d(face_collection)
        
        # Set the viewing angle
        ax.view_init(elev=elevation, azim=azimuth)
        
        # Set axis properties
        ax.set_xlim([-1, 1])
        ax.set_ylim([-1, 1])
        ax.set_zlim([-1, 1])
        
        # Hide axes for clean sprite
        ax.set_axis_off()
        
        # Set background
        ax.xaxis.pane.fill = False
        ax.yaxis.pane.fill = False
        ax.zaxis.pane.fill = False
        
        return ax.figure
    
    def figure_to_image(self, fig):
        """Convert matplotlib figure to PIL Image"""
        # Draw the figure on a canvas
        canvas = FigureCanvasAgg(fig)
        canvas.draw()
        
        # Get the RGBA buffer from the figure
        buf = canvas.buffer_rgba()
        w, h = canvas.get_width_height()
        
        # Convert to PIL Image
        image = Image.frombytes("RGBA", (w, h), buf)
        
        # Close the figure to free memory
        plt.close(fig)
        
        return image
    
    def apply_outline(self, image, outline_color=(0, 0, 0, 255), width=2):
        """
        Add an outline to the sprite for better visibility
        
        Args:
            image: PIL Image
            outline_color: RGBA color for outline
            width: Outline width in pixels
        """
        # Create a mask from alpha channel
        alpha = image.split()[-1]
        
        # Create outline by expanding the mask
        outline = Image.new('RGBA', image.size, (0, 0, 0, 0))
        outline_draw = ImageDraw.Draw(outline)
        
        # Simple outline by checking neighbors
        pixels = alpha.load()
        w, h = image.size
        
        for x in range(w):
            for y in range(h):
                if pixels[x, y] > 128:  # If pixel is visible
                    # Check if any neighbor is transparent
                    for dx in range(-width, width+1):
                        for dy in range(-width, width+1):
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < w and 0 <= ny < h:
                                if pixels[nx, ny] < 128:
                                    outline_draw.point((x, y), outline_color)
                                    break
        
        # Composite outline under the original image
        result = Image.alpha_composite(outline, image)
        return result
    
    def generate_sprites(self, add_outline=True, elevation=20):
        """
        Generate sprites from all viewing angles
        
        Args:
            add_outline: Whether to add outline to sprites
            elevation: Vertical viewing angle (degrees)
        """
        sprites = {}
        sprite_images = []
        
        print(f"\n🎨 Generating {self.directions} directional sprites...")
        
        for direction, angle in self.angles.items():
            print(f"  Rendering {direction} view (azimuth={angle}°)...")
            
            # Render the view
            fig = self.render_view(self.mesh, azimuth=angle, elevation=elevation)
            
            # Convert to image
            image = self.figure_to_image(fig)
            
            # Resize to target size
            image = image.resize(self.sprite_size, Image.Resampling.LANCZOS)
            
            # Add outline if requested
            if add_outline:
                image = self.apply_outline(image)
            
            sprites[direction] = image
            sprite_images.append(image)
            
            # Save individual sprite
            sprite_path = self.output_dir / f"{self.obj_path.stem}_{direction}.png"
            image.save(sprite_path, 'PNG')
            print(f"    ✓ Saved: {sprite_path}")
        
        return sprites, sprite_images
    
    def create_sprite_sheet(self, sprites, columns=3):
        """
        Create a sprite sheet with all directions
        
        Args:
            sprites: Dictionary of direction->image
            columns: Number of columns in sprite sheet
        """
        num_sprites = len(sprites)
        rows = (num_sprites + columns - 1) // columns
        
        sheet_width = self.sprite_size[0] * columns
        sheet_height = self.sprite_size[1] * rows
        
        # Create sprite sheet with transparent background
        sprite_sheet = Image.new('RGBA', (sheet_width, sheet_height), self.background_color)
        
        # Place each sprite
        for idx, (direction, image) in enumerate(sprites.items()):
            row = idx // columns
            col = idx % columns
            x = col * self.sprite_size[0]
            y = row * self.sprite_size[1]
            sprite_sheet.paste(image, (x, y), image)
        
        # Save sprite sheet
        sheet_path = self.output_dir / f"{self.obj_path.stem}_spritesheet.png"
        sprite_sheet.save(sheet_path, 'PNG')
        print(f"\n✓ Sprite sheet saved: {sheet_path}")
        
        # Also save a reference guide
        self.save_reference_guide(sprites, sheet_path)
        
        return sprite_sheet
    
    def save_reference_guide(self, sprites, sheet_path):
        """Save a text file explaining the sprite sheet layout"""
        guide_path = self.output_dir / f"{self.obj_path.stem}_reference.txt"
        
        with open(guide_path, 'w') as f:
            f.write(f"Sprite Sheet Reference for {self.obj_path.name}\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Sprite Size: {self.sprite_size[0]}x{self.sprite_size[1]} pixels\n")
            f.write(f"Total Directions: {len(sprites)}\n")
            f.write(f"Sprite Sheet: {sheet_path.name}\n\n")
            f.write("Direction Layout:\n")
            f.write("-" * 30 + "\n")
            
            for idx, direction in enumerate(sprites.keys()):
                f.write(f"{idx}: {direction}\n")
            
            f.write("\nUsage in Unity:\n")
            f.write("-" * 30 + "\n")
            f.write("1. Import the sprite sheet into Unity\n")
            f.write("2. Set Texture Type to 'Sprite'\n")
            f.write("3. Set Sprite Mode to 'Multiple'\n")
            f.write("4. Use Sprite Editor to slice the sheet\n")
            f.write(f"5. Grid size: {self.sprite_size[0]}x{self.sprite_size[1]}\n")
        
        print(f"✓ Reference guide saved: {guide_path}")
    
    def generate_animation_preview(self, sprites):
        """Generate an animated GIF preview of all directions"""
        images = list(sprites.values())
        
        # Save as animated GIF
        gif_path = self.output_dir / f"{self.obj_path.stem}_preview.gif"
        images[0].save(
            gif_path,
            save_all=True,
            append_images=images[1:],
            duration=200,  # 200ms per frame
            loop=0
        )
        
        print(f"✓ Animation preview saved: {gif_path}")
        return gif_path


def main():
    """Main function for command-line usage"""
    parser = argparse.ArgumentParser(
        description="Convert OBJ 3D models to 2D sprites for EoAT game"
    )
    parser.add_argument("obj_file", help="Path to the OBJ file")
    parser.add_argument("-o", "--output", default="sprites", 
                       help="Output directory (default: sprites)")
    parser.add_argument("-s", "--size", type=int, default=128,
                       help="Sprite size in pixels (default: 128)")
    parser.add_argument("-d", "--directions", type=int, choices=[6, 8], default=6,
                       help="Number of directions (6 for hex, 8 for isometric)")
    parser.add_argument("-e", "--elevation", type=float, default=20,
                       help="Camera elevation angle in degrees (default: 20)")
    parser.add_argument("--no-outline", action="store_true",
                       help="Don't add outline to sprites")
    parser.add_argument("--no-sheet", action="store_true",
                       help="Don't create sprite sheet")
    parser.add_argument("--no-animation", action="store_true",
                       help="Don't create animation preview")
    
    args = parser.parse_args()
    
    # Create converter
    converter = ObjToSpriteConverter(
        obj_path=args.obj_file,
        output_dir=args.output,
        sprite_size=(args.size, args.size),
        directions=args.directions
    )
    
    # Generate sprites
    sprites, sprite_images = converter.generate_sprites(
        add_outline=not args.no_outline,
        elevation=args.elevation
    )
    
    # Create sprite sheet
    if not args.no_sheet:
        converter.create_sprite_sheet(sprites)
    
    # Create animation preview
    if not args.no_animation:
        converter.generate_animation_preview(sprites)
    
    print(f"\n✅ Conversion complete! {len(sprites)} sprites generated.")
    print(f"📁 Output directory: {converter.output_dir}")


if __name__ == "__main__":
    main()
