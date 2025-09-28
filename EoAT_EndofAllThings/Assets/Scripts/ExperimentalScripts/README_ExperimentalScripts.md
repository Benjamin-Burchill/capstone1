# 🧪 Experimental Scripts for EoAT

This folder contains **experimental turn management scripts** that enhance the existing turn-based system with support for multiple game modes, co-op campaigns, and conditional UI buttons.

## 📁 Scripts Overview

### **TurnManager.cs**
Enhanced turn management system that supports:
- **Single Player** - Human vs AI(s)
- **Local Multiplayer** - Hot-seat multiple humans
- **Co-op Campaign** - Multiple humans on same team vs AI
- **Versus Mode** - Human vs Human
- **Team Battles** - Mixed teams of humans and AI

**Key Features:**
- Flexible turn order system (fixed, random, alternating, speed-based)
- Team support with victory conditions
- Turn time limits
- Auto-end turn when all units have acted
- Round tracking
- Player elimination detection

### **TurnUIController.cs**
Manages conditional UI buttons and turn display:
- **End Turn Button** - Only visible for human players
- **Undo Move Button** - Available after moving but before attacking
- **Pause Button** - Pause/resume gameplay
- **Concede Button** - For competitive modes
- **Auto-play Button** - For testing (optional)

**Visual Features:**
- Turn timer with color-coded warnings
- Team information display
- Round number tracking
- Phase indicators
- Player type indicators (human vs AI)
- Turn transition animations

## 🎮 How to Use

### **Setup Steps:**

1. **Create a GameObject** in your scene called "TurnManager"
2. **Add TurnManager.cs** component to it
3. **Configure game mode** in the inspector:
   - Select Game Mode (SinglePlayer, CoopCampaign, etc.)
   - Set Initiative Mode (how turn order is determined)
   - Configure turn settings (time limits, auto-end)

4. **Create UI Canvas** if you don't have one
5. **Add TurnUIController.cs** to a GameObject
6. **Create UI elements** and assign them in the inspector:
   - TextMeshPro texts for player info, round number, timer
   - Buttons for End Turn, Undo, Pause, Concede
   - Panels for organizing UI

### **Integration with Existing Code:**

These scripts are designed to work alongside your existing `GameState.cs` and `PlayerController.cs`:

```csharp
// Option 1: Use TurnManager instead of GameState for turn management
// Disable the turn logic in GameState and let TurnManager handle it

// Option 2: Integrate gradually
// Use TurnManager for advanced features while keeping GameState for basic turns
```

## 🔧 Configuration Examples

### **Single Player vs AI:**
```
Game Mode: Single Player
Initiative Mode: Fixed (player first)
Turn Time Limit: 0 (unlimited)
Auto End Turn: True
```

### **Co-op Campaign (2 Players vs AI):**
```
Game Mode: Coop Campaign
Use Teams: True
Initiative Mode: Alternating
Turn Time Limit: 60 seconds
Auto End Turn: False
```

### **Competitive Versus:**
```
Game Mode: Versus
Initiative Mode: Random
Turn Time Limit: 120 seconds
Auto End Turn: False
```

## 🎯 Game Mode Mechanics

### **Turn Order Philosophy:**
- **Single Player**: Human always goes first (tactical advantage)
- **Co-op**: Humans alternate, then all AI (promotes coordination)
- **Versus**: Random or scenario-based
- **Teams**: Alternating between teams for balance

### **Victory Conditions:**
- **Individual**: Last player with units wins
- **Team**: Last team with units wins
- **Custom**: Can be extended for objectives

## ⚠️ Important Notes

1. **These are EXPERIMENTAL** - Test thoroughly before replacing existing systems
2. **Backup your project** before major integration
3. **Can coexist** with current GameState/PlayerController
4. **Requires TextMeshPro** for UI elements

## 🔄 Migration Path

To migrate from existing system:

1. **Phase 1**: Add TurnManager alongside GameState
2. **Phase 2**: Route turn endings through TurnManager
3. **Phase 3**: Migrate UI to TurnUIController
4. **Phase 4**: Deprecate old turn logic in GameState

## 📝 TODO/Future Enhancements

- [ ] Network multiplayer support
- [ ] Save/load turn state
- [ ] Replay system
- [ ] Advanced AI coordination in team modes
- [ ] Tournament mode
- [ ] Spectator mode
- [ ] Turn history/undo multiple moves

## 🐛 Known Limitations

- AI turn processing still uses existing AIController
- No network support yet (local only)
- Undo only works for last move
- No save/load integration

## 💡 Tips

- Start with SinglePlayer mode for testing
- Use Debug.Log messages to understand turn flow
- Test victory conditions with different scenarios
- Adjust turn time limits based on map size

---

**Remember**: These scripts provide a foundation for advanced turn management. Feel free to modify and extend them to fit your specific game needs!
