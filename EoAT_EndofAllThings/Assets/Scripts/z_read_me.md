# 📋 EoAT Scripts Overview

## 🎮 **End of All Things** - File Functions Documentation

This folder contains all the C# scripts for the **EoAT turn-based strategy game**. Each script handles a specific aspect of the Wesnoth-style gameplay system.

---

## 🗺️ **Core Game Systems**

### **`Map.cs`** - World Generation & Tile Management
**Purpose**: Converts PNG images into playable hex-based game worlds
- **Image-to-Map Generation**: Reads PNG pixels and spawns corresponding tile prefabs
- **Color Mapping**: Uses `Tile Colour Key.txt` to map RGB values to tile types
- **Coordinate System**: Handles hex grid coordinate transformations (world ↔ map coordinates)
- **Mouse Interaction**: Detects which tile is under the mouse cursor
- **Tile Queries**: Provides `GetTileAt()` and `GetNeighboringTiles()` for game logic
- **Map Properties**: Manages map dimensions and world bounds

**Key Methods**:
- `parseMappingFromTxt()` - Loads tile prefab mappings from text file
- `generateMapFromImg()` - Creates tile grid from PNG image
- `worldToMapPoint()` / `mapToWorldPoint()` - Coordinate conversions
- `getTileUnderMouse()` - Mouse-to-tile detection

---

### **`GameState.cs`** - Turn Management & Game Flow
**Purpose**: Central controller for turn-based strategy gameplay
- **Turn System**: Manages player turns, turn numbers, and game phases
- **Unit Selection**: Handles which unit is currently selected
- **Movement System**: Shows movement ranges and validates moves
- **Combat System**: Manages attack ranges and damage calculations
- **Game Phases**: Controls flow between Selection → Movement → Attack → End Turn
- **Event System**: Notifies UI and other systems of state changes

**Key Features**:
- Multi-player support (2-4 players)
- Movement range highlighting (blue tiles)
- Attack range highlighting (red tiles)
- Combat damage calculation with terrain bonuses
- Turn progression and player switching

**Key Methods**:
- `SelectUnit()` - Choose active unit
- `SelectTile()` - Handle tile clicks for movement/attack
- `ShowMovementRange()` - Highlight valid moves
- `EndTurn()` - Switch to next player

---

### **`Unit.cs`** - Military Unit Behavior
**Purpose**: Individual units with combat stats and turn-based actions
- **Unit Stats**: Health, attack, defense, movement range, attack range
- **Turn State**: Tracks if unit has moved/attacked this turn
- **Combat**: Damage calculation and health management
- **Movement**: Tile-based movement with validation
- **Visual Feedback**: Selection highlighting and health display
- **Player Ownership**: Units belong to specific players

**Unit Properties**:
- **Combat**: ATK/DEF stats with terrain modifiers
- **Movement**: Range-based movement per turn
- **Health**: Current/max HP with visual health bar
- **Turn Tracking**: Prevents multiple moves/attacks per turn

**Key Methods**:
- `MoveToTile()` - Move unit to target tile
- `TakeDamage()` - Apply damage and check for death
- `ResetForNewTurn()` - Reset movement/attack flags

---

### **`Tile.cs`** - Individual Hex Tiles
**Purpose**: Represents single hexagonal tiles with terrain properties
- **Terrain Types**: Grass, Hills, Mountains, Water (deep/shallow)
- **Movement Properties**: Passable/impassable, movement costs
- **Combat Modifiers**: Defense bonuses for different terrains
- **Unit Tracking**: Knows which unit (if any) occupies the tile
- **Visual States**: Base, selected, and shaded textures
- **Mouse Interaction**: Click-to-select functionality

**Terrain Effects**:
- **Grass**: Normal movement (1 cost), no defense bonus
- **Hills**: Slow movement (2 cost), +30% defense bonus
- **Mountains**: Impassable, high defense
- **Deep Water**: Impassable for most units
- **Shallow Water**: Passable but slow, defense penalty

**Key Methods**:
- `changeTileTexture()` - Visual feedback for selection/highlighting
- `Initialize()` - Set tile coordinates and terrain properties
- `SetUnit()` / `GetUnit()` - Unit occupancy management

---

## 🎨 **User Interface**

### **`UIManager.cs`** - Complete UI System
**Purpose**: Manages all user interface elements and displays
- **Turn Display**: Shows current player, turn number, game phase
- **Unit Information**: Selected unit stats, health, movement status
- **Controls Help**: Instructions for player actions
- **Event Integration**: Automatically updates when game state changes
- **Button Handling**: End turn and deselect unit buttons

**UI Panels**:
- **Turn Info Panel**: Top-left corner with turn/player info
- **Unit Info Panel**: Bottom-left, shows selected unit details
- **Controls Panel**: Bottom-right with help text

**Key Features**:
- Real-time updates via event system
- Color-coded player information
- Health status with color indicators
- Turn phase descriptions

---

### **`CamScript.cs`** - Camera Control System
**Purpose**: Handles camera movement and zoom for map navigation
- **Pan Controls**: Arrow keys move camera around map
- **Zoom System**: +/- keys for zoom in/out with limits
- **Boundary Checking**: Prevents camera from going outside map
- **Smooth Movement**: Proportional movement based on zoom level
- **Map Integration**: Uses map dimensions for boundary calculations

**Controls**:
- **Arrow Keys**: Pan camera in four directions
- **Keypad +/-**: Zoom in/out (limited range: 5-30)
- **Auto-correction**: Keeps camera within map bounds when zooming

---

## 📚 **Documentation Files**

### **`EoAT_SETUP_GUIDE.md`** - Complete Setup Instructions
**Purpose**: Step-by-step guide for setting up the entire game
- **GameObject Setup**: Required scene objects and their configuration
- **UI Creation**: Canvas hierarchy and panel setup
- **Script Assignment**: Which scripts go on which GameObjects
- **Prefab Creation**: How to create unit prefabs
- **Gameplay Flow**: How the turn-based system works
- **Feature Overview**: What's implemented and what can be expanded

### **`0_read_me.md`** - This File
**Purpose**: Overview of all scripts and their functions

---

## 🔄 **System Integration**

### **How Everything Works Together**:

1. **`Map.cs`** generates the world from your PNG image
2. **`Tile.cs`** represents each hex with terrain properties
3. **`Unit.cs`** creates military units that can move and fight
4. **`GameState.cs`** orchestrates turn-based gameplay
5. **`UIManager.cs`** displays information and handles player input
6. **`CamScript.cs`** lets players navigate the map

### **Data Flow**:
```
PNG Image → Map.cs → Tile.cs (world creation)
         ↓
Player Input → GameState.cs → Unit.cs (gameplay)
         ↓
Game Events → UIManager.cs (display updates)
```

### **Event System**:
- **GameState** fires events when things change
- **UIManager** listens and updates displays automatically
- **Units** and **Tiles** handle mouse clicks
- **Camera** responds to keyboard input

---

## 🎯 **Game Features Implemented**

### ✅ **Core Wesnoth-Style Features**:
- **Image-based map generation** (unique to EoAT)
- **Hex grid movement** with proper coordinate system
- **Turn-based combat** with terrain effects
- **Multi-player support** (2-4 players)
- **Unit management** with stats and abilities
- **Professional UI** with real-time updates

### ✅ **Technical Architecture**:
- **Event-driven design** for loose coupling
- **Modular components** for easy expansion
- **Clean separation** of concerns
- **Extensible systems** for new features

---

## 🚀 **Ready for Development**

This system provides a **complete foundation** for a Wesnoth-style strategy game. All core systems are implemented and integrated, ready for gameplay testing and feature expansion!

**Next Steps**: Follow the `EoAT_SETUP_GUIDE.md` to set up your Unity scene and start playing! 🏰





