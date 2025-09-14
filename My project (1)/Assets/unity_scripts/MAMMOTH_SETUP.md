# 🐘 Mammoth Setup Guide

## Creating the Mammoth Prefab

### Step 1: Create Mammoth GameObject
1. **GameObject** → **3D Object** → **Cube**
2. **Rename** to "Mammoth"
3. **Scale**: (3, 2, 4) - Much larger than goblins
4. **Position**: (0, 1, 0) - Above ground

### Step 2: Create Mammoth Material
1. **Project** → **Create** → **Material** → "MammothMaterial"
2. **Shader**: Universal Render Pipeline/Lit
3. **Albedo Color**: Brown/gray (0.6, 0.5, 0.4) - Mammoth color
4. **Drag material** onto Mammoth cube

### Step 3: Attach Scripts (Automatic with RequireComponent)
1. **Add Component** → "MammothAI"
2. **HealthSystem automatically added** (RequireComponent)
3. **Add Component** → **Physics** → **Rigidbody**
4. **Add Component** → **Physics** → **Box Collider**

### Step 4: Configure Components
**MammothAI Settings:**
- Detection Range: 8 (small aggro radius)
- Stop Chase Range: 12
- Move Speed: 4 (slow)
- Attack Range: 3 (long trunk reach)
- Mammoth Damage: 40 (powerful)
- Is Peaceful: ✅ (starts peaceful)

**HealthSystem Settings:**
- Max Health: 150 (much more than goblins)
- Health Bar Height: 4 (higher for tall creature)

**Rigidbody Settings:**
- Mass: 5 (heavy creature)
- Drag: 2 (slow to start/stop)
- Freeze Rotation: X, Y, Z ✅

### Step 5: Make Prefab
1. **Drag Mammoth** from Hierarchy to Project window
2. **Creates "Mammoth" prefab**
3. **Delete original** from scene (GameManager will spawn them)

### Step 6: Configure GameManager
1. **Select GameManager** in Hierarchy
2. **Drag Mammoth prefab** into "Mammoth Prefab" field
3. **Set Mammoth Count**: 2

## 🎮 Mammoth Behavior

### Peaceful Giant Concept:
- **Small aggro radius** (8 units vs goblin's 20)
- **Starts peaceful** - won't attack unless provoked
- **Becomes hostile** when:
  - Player gets too close (within 4 units)
  - Player attacks it
  - Takes any damage

### Combat Characteristics:
- **High HP**: 150 (vs goblin's 30)
- **High damage**: 40 (vs goblin's 10)
- **Slow movement**: 4 units/sec (vs goblin's 8)
- **Knockback attack**: Sends player flying
- **Ground shake**: Camera shakes when mammoth moves/attacks
- **Area attack**: Hits everything in 3-unit radius

### XP Reward:
- **50 XP for killing mammoth** (vs 15 for goblin)
- **High risk, high reward** encounter

## 🏗️ Architecture Benefits

This demonstrates proper modular design:

### Base Class (HostileNPC):
- Generic hostile behavior
- State machine (Idle, Chasing, Attacking)
- Reusable for ANY enemy type

### Specific Classes:
- **GoblinAI**: Fast, pack-oriented, aggressive
- **MammothAI**: Slow, powerful, peaceful until provoked
- **Future**: OrcAI, DragonAI, etc. - all inherit from HostileNPC

### Manager Coordination:
- **GameManager**: Spawns appropriate numbers of each type
- **Handles different XP rewards** per enemy type
- **Coordinates between different AI systems**

This is exactly how professional games structure enemy systems!
