# 🚀 Quick Start Guide

## Get Running in 5 Minutes

### 1. Install Dependencies
```bash
cd one-off-projects/humanoid-base-math
pip install -r requirements.txt
```

### 2. Generate Your First Humanoid
```bash
python examples/generate_human.py
```

This creates `outputs/base_human.obj` - a mathematical humanoid mesh!

### 3. View the Result
Open `outputs/base_human.obj` in:
- **Blender** (recommended, free from blender.org)
- **MeshLab** (lightweight viewer, meshlab.net)
- **Windows 3D Viewer** (built-in on Windows 10/11)

### 4. What You'll See

**Expected Output:**
```
A geometric biped humanoid with:
- Spherical head
- Cylindrical neck
- Elliptical torso with waist taper
- Tapered cylinder limbs
- ~500-800 vertices
- Clean quad topology
```

**NOT photorealistic** - intentionally stylized/geometric.

---

## Understanding the Output

### Quality Levels

| Preset | Height | Vertex Count | Style | Use Case |
|--------|--------|--------------|-------|----------|
| `human_male` | 1.75m | ~600 | Standard | Default |
| `human_female` | 1.65m | ~600 | Slimmer | Variation |
| `dwarf` | 1.2m | ~600 | Stocky | Fantasy race |
| `elf` | 1.85m | ~600 | Lean | Fantasy race |
| `orc` | 1.95m | ~700 | Muscular | Fantasy race |
| `goblin` | 1.0m | ~500 | Small | Fantasy race |

All have similar vertex counts - differences are in proportions, not detail.

---

## Adjusting Parameters

### Example 1: Make a Tall, Thin Character
```python
from src.params import HumanoidParams
from src.mesh import generate_base_mesh

params = HumanoidParams(
    height=2.0,         # 2 meters tall
    stockiness=0.7,     # Thin
    leg_length_ratio=0.55  # Long legs
)

mesh = generate_base_mesh(params)
mesh.export('tall_thin.obj')
```

### Example 2: Stocky Warrior
```python
params = HumanoidParams(
    height=1.7,
    stockiness=1.4,        # Wide/stocky
    shoulder_width_ratio=0.30,  # Broad shoulders
    upper_arm_thickness=0.07,   # Thick arms
    thigh_thickness=0.09        # Thick legs
)

mesh = generate_base_mesh(params)
mesh.export('warrior.obj')
```

### Example 3: Fantasy Elf
```python
params = HumanoidParams(
    height=1.85,
    stockiness=0.85,     # Slim
    ear_length=0.8,      # Long ears (not yet implemented)
    arm_length_ratio=0.42,  # Longer arms
    leg_length_ratio=0.52   # Longer legs
)

mesh = generate_base_mesh(params)
mesh.export('elf.obj')
```

---

## Common Tasks

### Generate All Presets at Once
```bash
python examples/generate_all_presets.py
```

This creates a `outputs/presets/` folder with all 8 character types.

### Save Custom Parameters
```python
from src.params import HumanoidParams

params = HumanoidParams(height=1.9, stockiness=1.2)
params.save('my_character.json')

# Later, reload:
loaded = HumanoidParams.load('my_character.json')
mesh = generate_base_mesh(loaded)
```

### Adjust Mesh Quality
```python
params = HumanoidParams(
    height=1.75,
    body_segments=16,    # More vertical divisions (smoother)
    limb_segments=12,    # More limb divisions
    radial_segments=16   # More vertices around circumference
)

mesh = generate_base_mesh(params)
# Result: ~1200 vertices instead of ~600
```

---

## Integration with Main Project

### Option A: Export and Import
1. Generate base mesh here
2. Export to OBJ
3. Import into Blender or your main character creator
4. Apply morphs/textures on top

### Option B: Direct Integration
```python
# In your main character creator:
from one_off_projects.humanoid_base_math.src import generate_base_mesh, HumanoidParams

def create_base_for_race(race: str):
    if race == "human":
        params = HumanoidParams()
    elif race == "dwarf":
        params = get_preset('dwarf')
    # ... etc
    
    return generate_base_mesh(params)

# Use as starting point for your morphing system
base = create_base_for_race("human")
# Apply your advanced morphs...
```

---

## Troubleshooting

### Import Error
```
ModuleNotFoundError: No module named 'trimesh'
```
**Solution:** `pip install -r requirements.txt`

### Mesh Looks Broken in Viewer
Some viewers don't handle quad faces well. In `src/mesh.py`, change:
```python
mesh.export(output_path, file_type='obj')
```
to:
```python
mesh.export(output_path, file_type='obj', include_normals=True)
```

### Mesh Has Holes
Check `mesh.is_watertight` in output. If `False`:
- Increase `body_segments` and `limb_segments`
- Disable smoothing: `generate_base_mesh(params, apply_smoothing=False)`

### Performance Issues
For faster generation:
```python
params.body_segments = 8   # Lower (default: 12)
params.radial_segments = 8  # Lower (default: 12)
```

---

## Next Steps

### ✅ You've Got the Basics Working
- ✅ Generated first humanoid
- ✅ Viewed in 3D software
- ✅ Understand parameters

### 🎯 Level Up
1. **Experiment:** Adjust parameters, see what breaks
2. **Compare:** Generate human vs dwarf, analyze differences
3. **Integrate:** Use in your main project as base mesh
4. **Hybrid:** Import to Blender, sculpt details, export back

### 📚 Learn More
- Read `REALITY_CHECK.md` for honest limitations
- Read `ARCHITECTURE.md` (coming soon) for code structure
- Study `src/geometry.py` to understand the math

---

## Reality Check Reminder

✅ **This system is great for:**
- Low-poly game characters (mobile, VR)
- Rapid prototyping of proportions
- Understanding topology fundamentals
- Base meshes for sculpting
- Educational purposes

❌ **This system is NOT for:**
- Photorealistic characters
- Detailed faces
- Individual fingers/toes
- Extreme fantasy creatures (dragons, etc.)
- Production AAA games (use MakeHuman + artist touch-up instead)

---

## Support

**Questions?** Check:
1. `README.md` for overview
2. `REALITY_CHECK.md` for limitations
3. Source code comments in `src/`

**Bugs?** File issues or check your parameter values are in valid ranges.

**Want to Contribute?** See areas for improvement in `README.md`

---

**Happy Generating! 🎨**


