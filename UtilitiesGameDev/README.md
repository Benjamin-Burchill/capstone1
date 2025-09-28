# 🎨 OBJ to Sprite Converter for EoAT Game

This utility converts 3D OBJ model files into 2D sprite sheets for use in the End of All Things (EoAT) turn-based strategy game. Perfect for creating unit sprites from 3D models!

## 🚀 Features

- **Multiple viewing angles**: Generate 6 (hexagonal) or 8 (isometric) directional sprites
- **Two rendering modes**: 
  - Basic (matplotlib) - Fast and simple
  - Advanced (pyrender) - High quality with proper lighting
- **Sprite sheets**: Automatic sprite sheet generation for Unity import
- **Customizable output**: Adjustable sprite size, angles, and lighting
- **Unity-ready**: Includes metadata for easy Unity integration

## 📦 Installation

1. **Install Python 3.8+** if you haven't already

2. **Install dependencies**:
```bash
cd UtilitiesGameDev
pip install -r requirements.txt
```

For the advanced renderer, you might also need:
```bash
pip install pyrender pyglet
```

## 🎮 Usage

### Basic Converter (obj_to_sprites.py)
Fast conversion using matplotlib rendering:

```bash
# Convert a model with default settings (6 directions, 128x128 sprites)
python obj_to_sprites.py path/to/model.obj

# Custom settings
python obj_to_sprites.py model.obj -o output_folder -s 256 -d 8 -e 30

# Options:
#   -o, --output DIR     Output directory (default: sprites)
#   -s, --size SIZE      Sprite size in pixels (default: 128)
#   -d, --directions N   Number of directions: 6 or 8 (default: 6)
#   -e, --elevation DEG  Camera elevation angle (default: 20)
#   --no-outline         Don't add outline to sprites
#   --no-sheet          Don't create sprite sheet
#   --no-animation      Don't create animation preview
```

### Advanced Converter (obj_to_sprites_advanced.py)
High-quality rendering with proper lighting:

```bash
# High-quality conversion with lighting
python obj_to_sprites_advanced.py model.obj

# Custom settings
python obj_to_sprites_advanced.py model.obj -o sprites_hq -s 512 -d 8

# Options:
#   -o, --output DIR     Output directory (default: sprites_hq)
#   -s, --size SIZE      Sprite size in pixels (default: 256)
#   -d, --directions N   Number of directions: 6 or 8 (default: 6)
#   -e, --elevation DEG  Camera elevation angle (default: 30)
#   --no-lighting        Disable advanced lighting
```

## 📁 Output Files

Each conversion generates:

1. **Individual sprites**: `modelname_direction.png` (e.g., `warrior_east.png`)
2. **Sprite sheet**: `modelname_spritesheet.png` - All directions in one image
3. **Reference guide**: `modelname_reference.txt` - Layout documentation
4. **Animation preview**: `modelname_preview.gif` - Animated rotation
5. **Metadata**: `modelname_metadata.json` - Unity import settings

## 🎯 Direction Layout

### 6 Directions (Hexagonal - Perfect for EoAT)
```
   NE     NW
     \   /
  E —— * —— W
     /   \
   SE     SW
```

### 8 Directions (Isometric)
```
  NW  N  NE
    \ | /
  W — * — E
    / | \
  SW  S  SE
```

## 🎮 Unity Integration

1. **Import the sprite sheet** into Unity's Assets folder

2. **Configure the texture**:
   - Texture Type: `Sprite`
   - Sprite Mode: `Multiple`
   - Pixels Per Unit: `100`
   - Filter Mode: `Point` (for pixel-perfect sprites)

3. **Slice the sprite sheet**:
   - Open Sprite Editor
   - Slice → Type: `Grid By Cell Count`
   - Set columns and rows based on your direction count

4. **Use in your game**:
```csharp
// Example: Assign sprites to unit based on facing direction
public class UnitSprites : MonoBehaviour {
    public Sprite[] directionalSprites; // Assign sliced sprites
    private SpriteRenderer spriteRenderer;
    
    void UpdateSprite(Direction facing) {
        int index = (int)facing; // 0-5 or 0-7
        spriteRenderer.sprite = directionalSprites[index];
    }
}
```

## 📊 Examples

### Convert a warrior model for hex-based game:
```bash
python obj_to_sprites.py models/warrior.obj -d 6 -s 128
```

### High-quality sprites for a boss unit:
```bash
python obj_to_sprites_advanced.py models/dragon.obj -s 512 -d 8
```

### Batch conversion:
```bash
for model in models/*.obj; do
    python obj_to_sprites.py "$model" -o sprites/units
done
```

## 🛠️ Tips & Tricks

1. **Model Preparation**:
   - Center your model at origin before export
   - Face the model towards +Z axis
   - Keep polygon count reasonable (< 10k for best results)

2. **Sprite Size Guidelines**:
   - Regular units: 128x128
   - Hero units: 256x256
   - Buildings: 256x256 or 512x512
   - UI portraits: 512x512

3. **Performance**:
   - Basic converter is faster for batch processing
   - Advanced converter produces better quality for hero units

4. **Troubleshooting**:
   - If sprites are too dark, increase elevation angle
   - If outline is too thick, edit the outline width in code
   - For transparent materials, use the advanced converter

## 🔧 Customization

The scripts are designed to be easily modified:

- **Change camera angles**: Edit the `angles` dictionary
- **Adjust lighting**: Modify light positions in `setup_scene()`
- **Custom post-processing**: Add filters in `process_sprite()`
- **Different backgrounds**: Change `background_color` parameter

## 📝 Requirements

- Python 3.8+
- trimesh (OBJ loading)
- Pillow (image processing)
- matplotlib (basic rendering)
- pyrender (advanced rendering)
- numpy (math operations)

## 🐛 Known Issues

- Some complex materials might not render correctly in basic mode
- Very large models (>100k polygons) may be slow
- Transparent materials work better with advanced renderer

## 🚀 Future Enhancements

- [ ] Animation support (for animated OBJ sequences)
- [ ] Normal map generation
- [ ] Batch processing with configuration files
- [ ] Shadow generation as separate layer
- [ ] Team color mask generation

## 📄 License

Free to use for the EoAT project. Modify as needed!

---

**Happy sprite generation! 🎮**
