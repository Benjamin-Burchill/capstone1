# Unity Goblin RPG Scripts

This folder contains C# scripts for recreating the goblin RPG in Unity.

## 🎮 Scripts Overview

### Core Gameplay Scripts

1. **`PlayerController.cs`**
   - WASD movement with smooth rotation
   - World bounds enforcement
   - Optional footstep audio
   - Rigidbody physics support

2. **`GoblinAI.cs`**
   - Proximity-based AI (chase when player is close)
   - Idle bobbing animation
   - State machine (Idle, Chasing, Attacking, Fleeing)
   - Visual feedback (color changes, scaling)
   - Audio integration

3. **`HealthSystem.cs`**
   - HP management for players and enemies
   - Automatic world-space health bars
   - Color-coded health display
   - Death handling with fade effect
   - Event system for other scripts

4. **`GameManager.cs`**
   - Overall game coordination
   - Goblin pack spawning
   - Win/lose conditions
   - UI updates and game state
   - Scene management

## 🔧 Unity Setup Instructions

### 1. Create New Unity Project
- Unity Hub → New Project → 3D Core
- Name: `GoblinRPG` or similar

### 2. Scene Setup
1. **Delete** default Main Camera and Directional Light
2. **Create Ground**: GameObject → 3D Object → Plane
   - Scale: (30, 1, 30) for 300x300m world
   - Material: Create green material
3. **Create Player**: GameObject → 3D Object → Cube
   - Scale: (1, 1.5, 1)
   - Material: Create green material
   - Tag: "Player"
4. **Create Goblin Prefab**: GameObject → 3D Object → Cube
   - Scale: (0.8, 1.2, 0.8)
   - Material: Create red material
   - Tag: "Enemy"
   - Save as Prefab in Assets folder

### 3. Attach Scripts
1. **Player**: Add `PlayerController.cs` and `HealthSystem.cs`
2. **Goblin Prefab**: Add `GoblinAI.cs` and `HealthSystem.cs`
3. **Empty GameObject**: Create "GameManager", add `GameManager.cs`
4. **Main Camera**: Add `CameraFollow.cs`

### 4. Configure Components
- **GameManager**: Drag prefabs into slots
- **CameraFollow**: Set target to Player
- **GoblinAI**: Will auto-find player by tag

## 🎯 Features Implemented

### Player System
- ✅ WASD movement
- ✅ Smooth rotation toward movement
- ✅ World bounds (300x300m)
- ✅ Health system with HP bar
- ✅ Camera follow

### Goblin System  
- ✅ Proximity detection (20m range)
- ✅ Chase behavior
- ✅ Idle bobbing animation
- ✅ Health system with HP bars
- ✅ Visual feedback (color/size changes)
- ✅ Pack spawning system

### Game Management
- ✅ Automatic goblin spawning
- ✅ Win/lose conditions
- ✅ Real-time UI updates
- ✅ Game state management

## 🚀 Next Steps

### Easy Additions
- **Combat System**: Click to attack nearby goblins
- **Sound Effects**: Footsteps, goblin sounds, combat
- **Particle Effects**: Hit effects, death explosions
- **Loot System**: Goblins drop items when killed

### Advanced Features
- **Level System**: XP and player progression
- **Equipment**: Weapons and armor
- **Magic System**: Spells and abilities
- **Multiple Enemy Types**: Different goblin variants
- **Quest System**: Objectives and rewards

## 📊 Performance Benefits vs Panda3D

- **5-10x better frame rate**
- **Built-in LOD system** for large worlds
- **Modern graphics pipeline**
- **Better memory management**
- **Mobile deployment** possible
- **Professional tools** and asset store

## 🔄 Asset Pipeline

Your Python terrain generation scripts can export to:
- **.obj files** (geometry)
- **.png heightmaps** (for Unity Terrain system)
- **.fbx models** (with textures)

Unity can import all of these directly!
