# 🎮 EoAT Input System & Settings UI - Setup Guide

## 🚀 New Features Added

### ✅ **Features Implemented:**
1. **Scroll wheel zoom support** - Mouse wheel now controls camera zoom
2. **Customizable key bindings** - Players can rebind all movement keys
3. **Settings UI with ESC access** - Professional settings panel
4. **Persistent settings** - Key bindings save automatically
5. **Alternative key support** - Each action can have 2 different keys

---

## 🏗️ Unity Setup Instructions

### **Step 1: Add InputManager to Scene**
1. **Create Empty GameObject** → Rename to "InputManager"
2. **Add InputManager.cs script**
3. **Configure settings**:
   - ✅ Check "Persist Key Bindings" 
   - Key bindings will auto-populate with defaults

### **Step 2: Setup Settings UI**
1. **Find your Canvas** (or create one if needed)
2. **Create Settings Panel Structure**:

```
Canvas
└── SettingsPanel (GameObject)
    ├── Background (Image - dark overlay)
    ├── TopPanel (GameObject)
    │   ├── Title (TextMeshPro - "Game Settings")
    │   ├── KeyBindingContainer (Vertical Layout Group)
    │   └── VolumeControls (Slider + Text)
    └── BottomPanel (GameObject)
        ├── CloseButton (Button - "Close")
        ├── ResetButton (Button - "Reset Defaults")
        └── ApplyButton (Button - "Apply")
```

3. **Add SettingsUI.cs script** to the Canvas
4. **Assign UI References** in SettingsUI inspector:
   - Settings Panel → Your settings panel GameObject
   - Top Panel → Your top panel GameObject  
   - Bottom Panel → Your bottom panel GameObject
   - Close Button → Your close button
   - Reset Defaults Button → Your reset button
   - Apply Button → Your apply button
   - Master Volume Slider → Your volume slider
   - Volume Text → Your volume display text

### **Step 3: Camera Setup (Already Done!)**
- CamScript.cs has been updated automatically
- Now works with InputManager events
- Fallback system if InputManager not found

---

## 🎯 How It Works

### **Default Key Bindings:**
| Action | Primary Key | Alternative Key |
|--------|------------|-----------------|
| Settings Menu | ESC | - |
| Camera Up | ↑ | W |
| Camera Down | ↓ | S |
| Camera Left | ← | A |
| Camera Right | → | D |
| Zoom In | Num + | + |
| Zoom Out | Num - | - |
| **Mouse Scroll** | **Wheel Up/Down** | **Auto Zoom** |

### **Settings UI Controls:**
- **ESC Key**: Open/Close settings panel
- **Click Key Buttons**: Rebind keys (shows "Press Key...")
- **Volume Slider**: Adjust master audio volume
- **Reset Defaults**: Restore original key bindings
- **Close/Apply**: Save settings and close panel

---

## 🔧 Advanced Customization

### **Adding New Key Bindings:**
```csharp
// In InputManager's InitializeKeyBindings()
keyBindings.Add(new KeyBinding("New Action", KeyCode.Space, KeyCode.Return));

// Add corresponding event
public System.Action OnNewAction;

// In HandleInputActions()
if (IsActionDown("New Action"))
{
    OnNewAction?.Invoke();
}
```

### **UI Styling Tips:**
1. **Settings Panel**: Set background to semi-transparent black (0,0,0,0.8)
2. **Key Buttons**: Use white background, black text for visibility
3. **Layout Groups**: Use Vertical Layout Group for key binding container
4. **Responsive Design**: Use anchor presets for different screen sizes

### **Visual Polish:**
- Add smooth transitions with DOTween
- Custom button styles for better UX
- Icon support for key bindings display
- Sound effects for button clicks

---

## 🐛 Troubleshooting

### **"InputManager not found" Warning:**
- Make sure InputManager GameObject exists in scene
- Check that InputManager.cs script is attached
- Verify InputManager has singleton setup (auto-handled)

### **Settings UI not appearing:**
- Check Canvas exists and has SettingsUI.cs
- Verify SettingsPanel GameObject is assigned
- Make sure panel starts as SetActive(false)

### **Key bindings not saving:**
- Check "Persist Key Bindings" is enabled
- Verify PlayerPrefs write permissions
- Test with PlayerPrefs.Save() call

### **Camera not responding:**
- InputManager events should auto-connect
- Check console for connection messages
- Fallback input system activates if InputManager missing

---

## 🎨 UI Structure Example

### **Complete Canvas Hierarchy:**
```
UICanvas
├── [Existing Game UI Panels]
├── TurnInfoPanel (existing)
├── UnitInfoPanel (existing)
├── ControlsPanel (existing)
└── SettingsPanel (NEW)
    ├── BackgroundImage (full screen, dark overlay)
    ├── MainContainer (centered panel)
    │   ├── TopPanel
    │   │   ├── SettingsTitle (TextMeshPro)
    │   │   ├── KeyBindingsSection
    │   │   │   ├── SectionTitle (TextMeshPro - "Key Bindings")
    │   │   │   └── KeyBindingContainer (Vertical Layout)
    │   │   │       ├── [Auto-generated key binding rows]
    │   │   │       └── [One row per action with 2 buttons]
    │   │   └── AudioSection
    │   │       ├── VolumeLabel (TextMeshPro - "Master Volume")
    │   │       ├── VolumeSlider (Slider)
    │   │       └── VolumeText (TextMeshPro - "Volume: 100%")
    │   └── BottomPanel
    │       ├── CloseButton (Button - "Close")
    │       ├── ResetDefaultsButton (Button - "Reset to Defaults")  
    │       └── ApplyButton (Button - "Apply Changes")
```

---

## 🎮 Player Experience

### **For Players:**
1. **Press ESC** during gameplay to open settings
2. **Click any key button** to rebind controls
3. **Press new key** when prompt appears
4. **Use volume slider** for audio control
5. **Settings save automatically** - no manual save needed

### **Enhanced Controls:**
- **Mouse wheel zoom** works immediately
- **WASD movement** as alternatives to arrow keys
- **Dual key support** - use either primary or alternative
- **Visual feedback** during key rebinding
- **Pause game** when settings open

---

## 🏆 Success! 

Your EoAT game now has:
- ✅ **Professional input system** with customizable controls
- ✅ **Modern settings UI** accessible via ESC
- ✅ **Mouse wheel support** for smooth camera control  
- ✅ **Persistent user preferences** that save automatically
- ✅ **Alternative key bindings** (WASD + Arrow keys)
- ✅ **Pause-friendly settings** that don't interrupt gameplay

The system is modular, extensible, and ready for additional features! 🎯


