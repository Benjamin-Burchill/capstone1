# 🧙‍♂️ Parametric Character Generator

A powerful, Python-based 3D character generation system for creating highly customizable humanoid/bipedal characters for MMORPGs. Built with real-time morphing capabilities and extensive parameter control.

## ✨ Features

### Core Functionality
- **Real-time Morphing**: See changes instantly as you adjust parameters
- **60+ Parameters**: Fine control over every aspect of character appearance
- **Species Presets**: Built-in templates for Human, Dwarf, Elf, Orc, Goblin
- **Export Options**: Save to OBJ format with parameters

### Advanced Features
- **Blend Shape System**: Smooth interpolation between morph targets
- **Regional Morphing**: Target specific body parts (head, torso, limbs)
- **Preset Management**: Save and load custom character templates
- **Random Generation**: Create variations with controlled randomization

## 🚀 Quick Start

### Installation

```bash
# Navigate to the character generator directory
cd UtilitiesGameDev/character_generator

# Create virtual environment (optional but recommended)
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Application

#### GUI Mode (Recommended)
```bash
python character_gui_simple_3d.py
```

#### Command Line Mode
```bash
python character_generator.py
```

#### Simple Test Script
```bash
python test_generator.py
```

## 🎮 How to Use

### GUI Interface

1. **Launch the Application**
   ```bash
   python character_gui_simple_3d.py
   ```

2. **Select a Preset**
   - Choose from dropdown: Human, Dwarf, Elf, Orc, or Goblin

3. **Adjust Parameters**
   - Use tabbed interface to access different parameter categories:
     - **Global**: Height, build, muscle definition
     - **Head**: Size, width, depth
     - **Face**: Jaw, chin, cheekbones, brow
     - **Features**: Eyes, nose, mouth, ears
     - **Body**: Shoulders, chest, waist, hips
     - **Limbs**: Arms and legs proportions
     - **Special**: Horns, tails (for fantasy creatures)

4. **Export Your Character**
   - Click "💾 Export" to save both mesh (OBJ) and parameters (JSON)

### Command Line Usage

```python
from character_generator import CharacterGenerator

# Create a generator
gen = CharacterGenerator()

# Load a preset
gen.load_preset("dwarf")

# Adjust specific parameters
gen.set_parameter("muscle_definition", 0.7)
gen.set_parameter("shoulder_width", 0.5)

# Save the character
gen.save_character("my_dwarf.json")
```

## 📦 File Structure

```
character_generator/
├── __init__.py              # Package initialization
├── character_generator.py   # Core generator logic
├── character_gui_simple_3d.py  # GUI application with 3D visualization
├── requirements.txt        # Dependencies
├── README.md              # This file
├── test_generator.py      # Test script
└── presets/              # Saved presets directory
    ├── human.json
    ├── dwarf.json
    ├── elf.json
    └── ...
```

## 🎨 Parameter Guide

### Global Parameters
- **Height** (0.5-1.5): Overall character scale
- **Build** (-1 to 1): Body weight from thin to heavy
- **Muscle Definition** (-1 to 1): Muscle visibility

### Head & Face
- **Head Size/Width/Depth**: Overall head proportions
- **Jaw Width/Height**: Lower face structure
- **Brow Ridge**: Forehead prominence
- **Cheekbones**: Facial structure definition

### Body Proportions
- **Shoulder Width**: Upper body broadness
- **Chest/Waist/Hip**: Torso shape
- **Torso Length**: Body proportion

### Limbs
- **Arm/Leg Length**: Limb proportions
- **Size Parameters**: Muscle/thickness of limbs

### Special Features
- **Ear Point** (0-1): Elf-like ear pointiness
- **Horn Size/Position**: Fantasy creature features
- **Tail Length/Thickness**: Additional appendages

## 🔧 Creating Custom Presets

### Via GUI
1. Adjust all parameters to desired values
2. Click "Save Preset"
3. Enter a name for your preset
4. Preset is saved and added to dropdown

### Via Code
```python
from character_generator import CharacterParameters, CharacterPreset

# Create custom parameters
params = CharacterParameters(
    height=0.9,
    build=0.3,
    ear_point=0.8,
    jaw_width=-0.2
)

# Save as preset
preset_manager = CharacterPreset()
preset_manager.save_preset("wood_elf", params)
```

## 📊 Export Formats

### Current Support
- **OBJ**: Universal 3D mesh format
- **JSON**: Parameter data for recreation

### File Output
When you export a character named "my_character":
- `my_character.obj` - 3D mesh file
- `my_character.json` - Parameters and metadata

## 🎯 Example Characters

### Dwarf Warrior
```python
gen = CharacterGenerator()
gen.load_preset("dwarf")
gen.set_parameter("muscle_definition", 0.8)
gen.set_parameter("shoulder_width", 0.6)
gen.set_parameter("jaw_width", 0.4)
gen.save_character("dwarf_warrior.json")
```

### Elven Mage
```python
gen = CharacterGenerator()
gen.load_preset("elf")
gen.set_parameter("build", -0.3)
gen.set_parameter("ear_point", 1.0)
gen.set_parameter("forehead_size", 0.3)
gen.save_character("elven_mage.json")
```

## 🚧 Current Limitations

1. **3D Viewport**: Currently shows placeholder (mesh export works fine)
2. **Base Mesh**: Using simple primitive shapes (proper base mesh recommended)
3. **Textures**: No texture support yet
4. **Animation**: Static meshes only

## 🔮 Future Enhancements

### Near Term
- [ ] Integrated 3D viewport with OpenGL
- [ ] Better base humanoid mesh
- [ ] More export formats (FBX, glTF)
- [ ] Undo/Redo functionality

### Long Term
- [ ] Auto-rigging system
- [ ] Texture projection
- [ ] Hair/clothing system
- [ ] Animation support
- [ ] AI-assisted generation

## 🐛 Troubleshooting

### Common Issues

**ImportError for PyQt6**
```bash
pip install PyQt6
```

**ImportError for trimesh**
```bash
pip install trimesh numpy
```

**GUI doesn't start**
- Ensure all requirements are installed
- Check Python version (3.8+ required)

**Export creates empty file**
- Check write permissions in directory
- Ensure valid filename is provided

## 📚 Technical Details

### Morphing System
The system uses vertex displacement morphing:
```python
final_vertex = base_vertex + Σ(parameter * displacement * region_mask)
```

### Region Masking
Vertices are grouped into regions for targeted morphing:
- Head region: Top 15% of vertices
- Torso region: Middle 40%
- Limbs: Based on distance from center
- Extremities: Bottom 20%

## 🤝 Contributing

Contributions welcome! Areas for improvement:
1. Better base mesh creation
2. OpenGL viewport implementation
3. Additional presets
4. Export format support
5. Performance optimization

## 📄 License

Created for MMORPG development project. Free to modify and extend.

## 💬 Support

For issues or questions:
1. Check this README
2. Review the test script for examples
3. Examine the source code comments

---

**Happy Character Creating! 🎮**
