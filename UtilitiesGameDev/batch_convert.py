#!/usr/bin/env python3
"""
Batch OBJ to Sprite Converter
Converts multiple OBJ files at once with consistent settings
"""

import os
import json
from pathlib import Path
import argparse
from obj_to_sprites import ObjToSpriteConverter
import time

class BatchConverter:
    """Batch convert multiple OBJ files with consistent settings"""
    
    def __init__(self, config_file=None):
        """
        Initialize batch converter
        
        Args:
            config_file: Optional JSON configuration file
        """
        self.config = self.load_config(config_file) if config_file else self.default_config()
        self.results = []
    
    def default_config(self):
        """Default configuration for batch conversion"""
        return {
            "sprite_size": 128,
            "directions": 6,
            "elevation": 20,
            "add_outline": True,
            "create_sheet": True,
            "create_animation": True,
            "output_base": "sprites",
            "categories": {
                "units": {
                    "size": 128,
                    "directions": 6
                },
                "heroes": {
                    "size": 256,
                    "directions": 8
                },
                "buildings": {
                    "size": 256,
                    "directions": 4
                },
                "props": {
                    "size": 64,
                    "directions": 8
                }
            }
        }
    
    def load_config(self, config_file):
        """Load configuration from JSON file"""
        with open(config_file, 'r') as f:
            return json.load(f)
    
    def save_config(self, config_file):
        """Save current configuration to JSON file"""
        with open(config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def convert_directory(self, input_dir, category="units"):
        """
        Convert all OBJ files in a directory
        
        Args:
            input_dir: Directory containing OBJ files
            category: Category name for settings lookup
        """
        input_path = Path(input_dir)
        obj_files = list(input_path.glob("*.obj"))
        
        if not obj_files:
            print(f"No OBJ files found in {input_dir}")
            return
        
        print(f"\n📦 Found {len(obj_files)} OBJ files in {input_dir}")
        print(f"📏 Using settings for category: {category}")
        
        # Get category settings
        settings = self.config["categories"].get(category, self.config["categories"]["units"])
        
        # Create output directory
        output_dir = Path(self.config["output_base"]) / category
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Convert each file
        for idx, obj_file in enumerate(obj_files, 1):
            print(f"\n[{idx}/{len(obj_files)}] Converting {obj_file.name}...")
            
            try:
                start_time = time.time()
                
                # Create converter
                converter = ObjToSpriteConverter(
                    obj_path=obj_file,
                    output_dir=output_dir,
                    sprite_size=(settings["size"], settings["size"]),
                    directions=settings["directions"]
                )
                
                # Generate sprites
                sprites, _ = converter.generate_sprites(
                    add_outline=self.config.get("add_outline", True),
                    elevation=self.config.get("elevation", 20)
                )
                
                # Create sprite sheet
                if self.config.get("create_sheet", True):
                    converter.create_sprite_sheet(sprites)
                
                # Create animation
                if self.config.get("create_animation", True):
                    converter.generate_animation_preview(sprites)
                
                elapsed_time = time.time() - start_time
                
                # Record result
                self.results.append({
                    "file": str(obj_file),
                    "category": category,
                    "sprites_generated": len(sprites),
                    "time": elapsed_time,
                    "status": "success"
                })
                
                print(f"✓ Completed in {elapsed_time:.2f} seconds")
                
            except Exception as e:
                print(f"✗ Error converting {obj_file.name}: {e}")
                self.results.append({
                    "file": str(obj_file),
                    "category": category,
                    "error": str(e),
                    "status": "failed"
                })
    
    def convert_with_mapping(self, mapping_file):
        """
        Convert files based on a mapping file
        
        Mapping file format (JSON):
        {
            "units": ["warrior.obj", "archer.obj"],
            "heroes": ["hero_knight.obj"],
            "buildings": ["castle.obj", "tower.obj"]
        }
        """
        with open(mapping_file, 'r') as f:
            mapping = json.load(f)
        
        for category, files in mapping.items():
            print(f"\n🎨 Processing category: {category}")
            for obj_file in files:
                self.convert_file(obj_file, category)
    
    def convert_file(self, obj_file, category="units"):
        """Convert a single file with specified category settings"""
        obj_path = Path(obj_file)
        if not obj_path.exists():
            print(f"✗ File not found: {obj_file}")
            return
        
        settings = self.config["categories"].get(category, self.config["categories"]["units"])
        output_dir = Path(self.config["output_base"]) / category
        output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            converter = ObjToSpriteConverter(
                obj_path=obj_path,
                output_dir=output_dir,
                sprite_size=(settings["size"], settings["size"]),
                directions=settings["directions"]
            )
            
            sprites, _ = converter.generate_sprites()
            
            if self.config.get("create_sheet", True):
                converter.create_sprite_sheet(sprites)
            
            print(f"✓ Converted {obj_path.name}")
            
        except Exception as e:
            print(f"✗ Error: {e}")
    
    def generate_report(self, report_file="conversion_report.json"):
        """Generate a report of all conversions"""
        report = {
            "total_files": len(self.results),
            "successful": len([r for r in self.results if r["status"] == "success"]),
            "failed": len([r for r in self.results if r["status"] == "failed"]),
            "total_time": sum(r.get("time", 0) for r in self.results),
            "details": self.results
        }
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📊 Conversion Report:")
        print(f"  Total files: {report['total_files']}")
        print(f"  Successful: {report['successful']}")
        print(f"  Failed: {report['failed']}")
        print(f"  Total time: {report['total_time']:.2f} seconds")
        print(f"  Report saved: {report_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Batch convert OBJ files to sprites"
    )
    parser.add_argument("input", help="Input directory or mapping file")
    parser.add_argument("-c", "--category", default="units",
                       choices=["units", "heroes", "buildings", "props"],
                       help="Asset category (affects size and settings)")
    parser.add_argument("--config", help="JSON configuration file")
    parser.add_argument("-o", "--output", default="sprites",
                       help="Base output directory")
    parser.add_argument("--save-config", help="Save configuration to file")
    parser.add_argument("--mapping", action="store_true",
                       help="Input is a mapping file, not a directory")
    
    args = parser.parse_args()
    
    # Create batch converter
    converter = BatchConverter(args.config)
    
    if args.output:
        converter.config["output_base"] = args.output
    
    # Save config if requested
    if args.save_config:
        converter.save_config(args.save_config)
        print(f"Configuration saved to {args.save_config}")
    
    # Perform conversion
    if args.mapping:
        converter.convert_with_mapping(args.input)
    else:
        converter.convert_directory(args.input, args.category)
    
    # Generate report
    converter.generate_report()


if __name__ == "__main__":
    main()
