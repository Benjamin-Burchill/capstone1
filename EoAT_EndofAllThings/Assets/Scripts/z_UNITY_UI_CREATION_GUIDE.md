# 🎨 Unity UI Creation Guide - EoAT Strategy Game

## 📋 **Unity Editor 6000.0.27f1 - Step-by-Step UI Setup**

The `UIManager.cs` script references UI elements that need to be **manually created** in Unity Editor. Here's the complete guide to build the interface.

---

## 🏗️ **Phase 1: Create Main Canvas**

### **Step 1: Create Canvas**
1. **Right-click in Hierarchy** → **UI** → **Canvas**
2. **Rename** to `"GameCanvas"`
3. **Canvas Component Settings**:
   - **Render Mode**: Screen Space - Overlay
   - **Pixel Perfect**: ✅ Checked
   - **Sort Order**: 0

### **Step 2: Add Canvas Scaler**
1. **Select GameCanvas**
2. **Add Component** → **UI** → **Canvas Scaler**
3. **Canvas Scaler Settings**:
   - **UI Scale Mode**: Scale With Screen Size
   - **Reference Resolution**: 1920 x 1080
   - **Screen Match Mode**: Match Width Or Height
   - **Match**: 0.5

### **Step 3: Add UIManager Script**
1. **Select GameCanvas**
2. **Add Component** → **Scripts** → **UIManager**
3. **Leave fields empty for now** (we'll assign them later)

---

## 🎮 **Phase 2: Create Turn Info Panel (Top-Left)**

### **Step 1: Create Turn Info Panel**
1. **Right-click GameCanvas** → **UI** → **Panel**
2. **Rename** to `"TurnInfoPanel"`
3. **RectTransform Settings**:
   - **Anchor**: Top-Left
   - **Anchor Min**: (0, 1)
   - **Anchor Max**: (0, 1)
   - **Pivot**: (0, 1)
   - **Position**: (10, -10)
   - **Size**: (300, 120)

### **Step 2: Style the Panel**
1. **Select TurnInfoPanel**
2. **Image Component**:
   - **Color**: (0, 0, 0, 0.7) - Semi-transparent black
   - **Source Image**: UI-Skin-InputFieldBackground (or similar)

### **Step 3: Add Turn Number Text**
1. **Right-click TurnInfoPanel** → **UI** → **Text - TextMeshPro**
2. **Rename** to `"TurnNumberText"`
3. **RectTransform**:
   - **Anchor**: Top-Left
   - **Position**: (10, -10)
   - **Size**: (280, 30)
4. **TextMeshPro Settings**:
   - **Text**: "Turn 1"
   - **Font Size**: 18
   - **Color**: White
   - **Alignment**: Left

### **Step 4: Add Current Player Text**
1. **Right-click TurnInfoPanel** → **UI** → **Text - TextMeshPro**
2. **Rename** to `"CurrentPlayerText"`
3. **RectTransform**:
   - **Position**: (10, -40)
   - **Size**: (280, 30)
4. **TextMeshPro Settings**:
   - **Text**: "Player 1's Turn"
   - **Font Size**: 16
   - **Color**: Blue
   - **Alignment**: Left

### **Step 5: Add Game Phase Text**
1. **Right-click TurnInfoPanel** → **UI** → **Text - TextMeshPro**
2. **Rename** to `"GamePhaseText"`
3. **RectTransform**:
   - **Position**: (10, -70)
   - **Size**: (280, 30)
4. **TextMeshPro Settings**:
   - **Text**: "Select Unit"
   - **Font Size**: 14
   - **Color**: Yellow
   - **Alignment**: Left

### **Step 6: Add End Turn Button**
1. **Right-click TurnInfoPanel** → **UI** → **Button - TextMeshPro**
2. **Rename** to `"EndTurnButton"`
3. **RectTransform**:
   - **Position**: (150, -95)
   - **Size**: (140, 30)
4. **Button Settings**:
   - **Colors**: Normal=Green, Highlighted=Light Green
5. **Button Text**:
   - **Text**: "End Turn"
   - **Font Size**: 14
   - **Color**: White

---

## 🛡️ **Phase 3: Create Unit Info Panel (Bottom-Left)**

### **Step 1: Create Unit Info Panel**
1. **Right-click GameCanvas** → **UI** → **Panel**
2. **Rename** to `"UnitInfoPanel"`
3. **RectTransform Settings**:
   - **Anchor**: Bottom-Left
   - **Anchor Min**: (0, 0)
   - **Anchor Max**: (0, 0)
   - **Pivot**: (0, 0)
   - **Position**: (10, 10)
   - **Size**: (300, 180)
4. **Set Active**: ❌ **Unchecked** (hidden by default)

### **Step 2: Style the Panel**
1. **Image Component**:
   - **Color**: (0.1, 0.1, 0.1, 0.8) - Dark semi-transparent
   - **Source Image**: UI-Skin-InputFieldBackground

### **Step 3: Add Unit Name Text**
1. **Right-click UnitInfoPanel** → **UI** → **Text - TextMeshPro**
2. **Rename** to `"UnitNameText"`
3. **RectTransform**:
   - **Position**: (10, -10)
   - **Size**: (280, 30)
4. **TextMeshPro Settings**:
   - **Text**: "Warrior"
   - **Font Size**: 18
   - **Color**: White
   - **Alignment**: Left
   - **Style**: Bold

### **Step 4: Add Unit Health Text**
1. **Right-click UnitInfoPanel** → **UI** → **Text - TextMeshPro**
2. **Rename** to `"UnitHealthText"`
3. **RectTransform**:
   - **Position**: (10, -40)
   - **Size**: (280, 30)
4. **TextMeshPro Settings**:
   - **Text**: "Health: 100/100"
   - **Font Size**: 14
   - **Color**: Green
   - **Alignment**: Left

### **Step 5: Add Unit Stats Text**
1. **Right-click UnitInfoPanel** → **UI** → **Text - TextMeshPro**
2. **Rename** to `"UnitStatsText"`
3. **RectTransform**:
   - **Position**: (10, -80)
   - **Size**: (280, 40)
4. **TextMeshPro Settings**:
   - **Text**: "ATK: 25 | DEF: 10\nMove: 3 | Range: 1"
   - **Font Size**: 12
   - **Color**: Cyan
   - **Alignment**: Left

### **Step 6: Add Unit Movement Text**
1. **Right-click UnitInfoPanel** → **UI** → **Text - TextMeshPro**
2. **Rename** to `"UnitMovementText"`
3. **RectTransform**:
   - **Position**: (10, -130)
   - **Size**: (280, 30)
4. **TextMeshPro Settings**:
   - **Text**: "Can Move | Can Attack"
   - **Font Size**: 12
   - **Color**: Green
   - **Alignment**: Left

### **Step 7: Add Deselect Button**
1. **Right-click UnitInfoPanel** → **UI** → **Button - TextMeshPro**
2. **Rename** to `"DeselectButton"`
3. **RectTransform**:
   - **Position**: (150, -155)
   - **Size**: (140, 25)
4. **Button Settings**:
   - **Colors**: Normal=Red, Highlighted=Light Red
5. **Button Text**:
   - **Text**: "Deselect"
   - **Font Size**: 12

---

## ℹ️ **Phase 4: Create Controls Panel (Bottom-Right)**

### **Step 1: Create Controls Panel**
1. **Right-click GameCanvas** → **UI** → **Panel**
2. **Rename** to `"ControlsPanel"`
3. **RectTransform Settings**:
   - **Anchor**: Bottom-Right
   - **Anchor Min**: (1, 0)
   - **Anchor Max**: (1, 0)
   - **Pivot**: (1, 0)
   - **Position**: (-10, 10)
   - **Size**: (250, 150)

### **Step 2: Style the Panel**
1. **Image Component**:
   - **Color**: (0, 0, 0, 0.6) - Semi-transparent black

### **Step 3: Add Controls Text**
1. **Right-click ControlsPanel** → **UI** → **Text - TextMeshPro**
2. **Rename** to `"ControlsText"`
3. **RectTransform**:
   - **Anchor**: Fill (stretch to fill panel)
   - **Margin**: 10 pixels on all sides
4. **TextMeshPro Settings**:
   - **Text**: 
   ```
   Controls:
   • Click Unit: Select
   • Click Tile: Move/Attack
   • Arrow Keys: Pan Camera
   • +/-: Zoom
   • End Turn: Next Player
   ```
   - **Font Size**: 10
   - **Color**: Light Gray
   - **Alignment**: Left
   - **Vertical Alignment**: Top

---

## 🔗 **Phase 5: Connect UIManager References**

### **Step 1: Assign UI References**
1. **Select GameCanvas** (with UIManager script)
2. **In Inspector**, drag UI elements to corresponding fields:

**Game Canvas:**
- **Game Canvas**: Drag `GameCanvas` to this field

**Turn Info UI:**
- **Turn Info Panel**: Drag `TurnInfoPanel`
- **Turn Number Text**: Drag `TurnNumberText`
- **Current Player Text**: Drag `CurrentPlayerText`
- **Game Phase Text**: Drag `GamePhaseText`
- **End Turn Button**: Drag `EndTurnButton`

**Unit Info UI:**
- **Unit Info Panel**: Drag `UnitInfoPanel`
- **Unit Name Text**: Drag `UnitNameText`
- **Unit Health Text**: Drag `UnitHealthText`
- **Unit Stats Text**: Drag `UnitStatsText`
- **Unit Movement Text**: Drag `UnitMovementText`

**Controls UI:**
- **Controls Panel**: Drag `ControlsPanel`
- **Controls Text**: Drag `ControlsText`
- **Deselect Button**: Drag `DeselectButton`

---

## ✅ **Phase 6: Test the UI**

### **Test Setup:**
1. **Play the scene**
2. **Check Console** for any missing reference errors
3. **UI should display**:
   - Turn info in top-left
   - Controls in bottom-right
   - Unit info panel should be hidden (until unit selected)

### **Expected Behavior:**
- **Turn Info**: Shows current turn and player
- **End Turn Button**: Should be clickable (may show errors until GameState exists)
- **Unit Info Panel**: Hidden by default
- **Controls Panel**: Shows help text

---

## 🎨 **Phase 7: Visual Polish (Optional)**

### **Improve Panel Appearance:**
1. **Add borders** using UI → Image as children
2. **Add background gradients** 
3. **Use custom fonts** if available
4. **Add icons** next to text elements
5. **Adjust colors** to match your game theme

### **Responsive Design:**
- All panels use **anchors** so they scale with screen size
- **Canvas Scaler** ensures consistent sizing
- **Text sizes** will scale appropriately

---

## 🚀 **Next Steps**

After creating the UI:
1. **Create GameManager** with GameState script
2. **Create MapLoader** with Map script  
3. **Test unit selection** (UI should update when units are selected)
4. **Create unit prefabs** and test the complete system

The UI will automatically update when the game systems are connected! 🎮







