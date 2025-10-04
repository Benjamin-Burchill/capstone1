# 🏰 EoAT (End of All Things) - Setup Guide

## 🎮 Game Overview
**EoAT** is a **Wesnoth-style turn-based strategy game** with:
- **Image-based map generation** (PNG → playable world)
- **Hex tile movement** system
- **Turn-based combat** with multiple players
- **Unit management** and tactical gameplay

## 🏗️ Required GameObjects in Scene

### **1. MapLoader GameObject**
```
MapLoader (Empty GameObject)
├── Map.cs script
├── Assign: Map Image (PNG)
├── Assign: Tile Colour Key (TXT)
├── Set: Tile Size (e.g., 1, 0.866 for hex)
```

### **2. Main Camera**
```
Main Camera
├── Camera component (Orthographic)
├── CamScript.cs
├── Position: (0, 0, -10)
├── Orthographic Size: 15
```

### **3. GameManager GameObject**
```
GameManager (Empty GameObject)
├── GameState.cs script
├── Set: Total Players (2-4)
```

### **4. UICanvas GameObject**
```
UICanvas
├── Canvas component (Screen Space - Overlay)
├── UIManager.cs script
├── Child UI panels (see UI Setup below)
```

### **5. Unit GameObjects (Prefabs)**
```
Warrior Unit Prefab
├── SpriteRenderer (unit sprite)
├── Unit.cs script
├── BoxCollider2D (for mouse clicking)
├── Configure: Stats, owner, unit type
```

## 🎨 UI Setup (Canvas Hierarchy)

### **Canvas Structure:**
```
UICanvas
├── TurnInfoPanel
│   ├── TurnNumberText (TextMeshPro)
│   ├── CurrentPlayerText (TextMeshPro)
│   ├── GamePhaseText (TextMeshPro)
│   └── EndTurnButton (Button)
├── UnitInfoPanel
│   ├── UnitNameText (TextMeshPro)
│   ├── UnitHealthText (TextMeshPro)
│   ├── UnitStatsText (TextMeshPro)
│   ├── UnitMovementText (TextMeshPro)
│   └── DeselectButton (Button)
└── ControlsPanel
    └── ControlsText (TextMeshPro)
```

### **UI Panel Positions:**
- **TurnInfoPanel**: Top-left corner
- **UnitInfoPanel**: Bottom-left corner (shows when unit selected)
- **ControlsPanel**: Bottom-right corner

## 🔧 Step-by-Step Setup

### **Phase 1: Basic Map Setup**
1. **Create Empty GameObject** → Rename "MapLoader"
2. **Add Map.cs script**
3. **Assign your PNG map** to Map Image field
4. **Assign Tile Colour Key.txt** to Mapping File field
5. **Set Tile Size** to (1, 0.866) for proper hex spacing

### **Phase 2: Camera Setup**
1. **Select Main Camera**
2. **Add CamScript.cs**
3. **Set Camera to Orthographic** (not Perspective)
4. **Set Orthographic Size** to 15
5. **Position** at (0, 0, -10)

### **Phase 3: Game State Setup**
1. **Create Empty GameObject** → Rename "GameManager"
2. **Add GameState.cs script**
3. **Set Total Players** (2 for basic game)

### **Phase 4: UI Setup**
1. **Create UI Canvas** (Right-click → UI → Canvas)
2. **Add UIManager.cs script** to Canvas
3. **Create UI panels** as children of Canvas:

#### **Turn Info Panel:**
```
1. Right-click Canvas → UI → Panel → Rename "TurnInfoPanel"
2. Position: Top-left
3. Add child: UI → Text - TextMeshPro → "TurnNumberText"
4. Add child: UI → Text - TextMeshPro → "CurrentPlayerText"  
5. Add child: UI → Text - TextMeshPro → "GamePhaseText"
6. Add child: UI → Button → "EndTurnButton"
```

#### **Unit Info Panel:**
```
1. Right-click Canvas → UI → Panel → Rename "UnitInfoPanel"
2. Position: Bottom-left
3. Add TextMeshPro children for unit stats
4. Add Deselect Button
5. Set Active: False (hidden until unit selected)
```

### **Phase 5: Create Unit Prefabs**
1. **Create Empty GameObject** → Rename "Warrior"
2. **Add SpriteRenderer** component
3. **Add Unit.cs script**
4. **Add BoxCollider2D** (for mouse clicking)
5. **Configure Unit.cs**:
   - Unit Type: Warrior
   - Owner: 0 (Player 1)
   - Stats: HP=100, ATK=25, DEF=10, Move=3, Range=1
6. **Drag to Project** to create prefab
7. **Delete from scene** (will be spawned by game logic)

### **Phase 6: Connect UI References**
1. **Select UICanvas**
2. **In UIManager script**, drag UI elements into corresponding fields:
   - Turn Number Text → TurnNumberText field
   - Current Player Text → CurrentPlayerText field
   - etc.

## 🎮 Gameplay Flow

### **Turn Structure (Like Wesnoth):**
1. **Unit Selection Phase**:
   - Click unit to select it
   - Movement range highlights in blue
   - Unit info appears in UI panel

2. **Movement Phase**:
   - Click highlighted tile to move
   - Unit moves to tile
   - Attack range highlights in red (if unit can still attack)

3. **Attack Phase** (Optional):
   - Click enemy unit to attack
   - Combat calculation performed
   - Damage applied

4. **End Turn**:
   - Click "End Turn" button
   - Next player's turn begins
   - All units reset for new turn

### **Combat System:**
- **Damage Calculation**: Attacker ATK - Defender DEF
- **Terrain Bonuses**: Hills give +30% defense
- **Movement Costs**: Hills cost 2 movement, grass costs 1
- **Impassable Terrain**: Mountains and deep water block movement

## 🎯 Key Features Implemented

### **✅ Wesnoth-Style Features:**
- **Hex grid movement** with proper offset coordinates
- **Turn-based gameplay** with multiple players
- **Terrain effects** (defense bonuses, movement costs)
- **Unit selection** and movement range display
- **Combat system** with damage calculation
- **Image-based map generation** (like scenario editors)

### **✅ Professional Architecture:**
- **Event-driven UI** updates automatically
- **Modular components** (Map, GameState, UIManager separate)
- **Extensible unit system** (easy to add new unit types)
- **Clean separation** between data and presentation

## 🚀 Next Steps

### **Immediate (Get Basic Game Working):**
1. **Setup the GameObjects** as described above
2. **Create basic UI panels**
3. **Test map generation** with your PNG
4. **Create one unit prefab** and test selection/movement

### **Expansion Features:**
- **Multiple unit types** (Archer, Cavalry, Mage)
- **Fog of war** system
- **Unit experience** and leveling
- **City/building** system
- **Resource management**
- **Campaign mode** with multiple scenarios

This gives you a **complete Wesnoth-style strategy game foundation**! 🏰













