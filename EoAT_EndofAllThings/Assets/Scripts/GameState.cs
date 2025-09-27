using UnityEngine;
using System.Collections.Generic;

/// <summary>
/// Game State Manager for EoAT - Turn-based strategy game state
/// Handles turns, game phases, and overall game flow
/// </summary>
public class GameState : MonoBehaviour
{
    [Header("Game State")]
    [Tooltip("Current player turn (0 = Player 1, 1 = Player 2, etc.)")]
    public int currentPlayerTurn = 0;
    
    [Tooltip("Total number of players")]
    public int totalPlayers = 2;
    
    [Tooltip("Current turn number")]
    public int turnNumber = 1;
    
    [Header("Game Phase")]
    [Tooltip("What phase of the turn we're in")]
    public GamePhase currentPhase = GamePhase.UnitSelection;
    
    [Header("Selection State")]
    [Tooltip("Currently selected unit")]
    public Unit selectedUnit = null;
    
    [Tooltip("Currently highlighted tile")]
    public Tile selectedTile = null;
    
    [Tooltip("Tiles showing movement range")]
    public List<Tile> movementRangeTiles = new List<Tile>();
    
    [Tooltip("Tiles showing attack range")]
    public List<Tile> attackRangeTiles = new List<Tile>();
    
    // Events for UI to listen to
    public System.Action<int> OnTurnChanged;
    public System.Action<int> OnPlayerChanged;
    public System.Action<GamePhase> OnPhaseChanged;
    public System.Action<Unit> OnUnitSelected;
    public System.Action<Tile> OnTileSelected;
    
    // References
    private Map mapController;
    private UIManager uiManager;
    
    void Start()
    {
        // Find required components
        mapController = FindFirstObjectByType<Map>();
        uiManager = FindFirstObjectByType<UIManager>();
        
        // Initialize game state
        StartNewGame();
        
        Debug.Log("Game State initialized - Turn-based strategy ready");
    }
    
    void StartNewGame()
    {
        currentPlayerTurn = 0;
        turnNumber = 1;
        currentPhase = GamePhase.UnitSelection;
        
        // Notify UI
        OnTurnChanged?.Invoke(turnNumber);
        OnPlayerChanged?.Invoke(currentPlayerTurn);
        OnPhaseChanged?.Invoke(currentPhase);
        
        Debug.Log($"New game started - Player {currentPlayerTurn + 1}'s turn");
    }
    
    public void SelectUnit(Unit unit)
    {
        // Deselect previous unit
        if (selectedUnit != null)
        {
            selectedUnit.SetSelected(false);
            ClearMovementRange();
        }
        
        // Select new unit
        selectedUnit = unit;
        if (selectedUnit != null)
        {
            selectedUnit.SetSelected(true);
            ShowMovementRange(selectedUnit);
            currentPhase = GamePhase.UnitMovement;
        }
        else
        {
            currentPhase = GamePhase.UnitSelection;
        }
        
        // Notify systems
        OnUnitSelected?.Invoke(selectedUnit);
        OnPhaseChanged?.Invoke(currentPhase);
        
        Debug.Log($"Unit selected: {selectedUnit?.name ?? "None"}");
    }
    
    public void SelectTile(Tile tile)
    {
        selectedTile = tile;
        OnTileSelected?.Invoke(tile);
        
        // Handle tile selection based on current phase
        switch (currentPhase)
        {
            case GamePhase.UnitMovement:
                if (selectedUnit != null && CanMoveToTile(tile))
                {
                    MoveUnitToTile(selectedUnit, tile);
                }
                break;
                
            case GamePhase.UnitAttack:
                if (selectedUnit != null && CanAttackTile(tile))
                {
                    AttackTile(selectedUnit, tile);
                }
                break;
        }
    }
    
    void ShowMovementRange(Unit unit)
    {
        ClearMovementRange();
        
        // Get tiles within movement range
        Vector2 unitTilePos = mapController.worldToMapPoint(unit.transform.position);
        int movementRange = unit.GetMovementRange();
        
        for (int x = -movementRange; x <= movementRange; x++)
        {
            for (int y = -movementRange; y <= movementRange; y++)
            {
                Vector2 checkPos = unitTilePos + new Vector2(x, y);
                
                // Check if within map bounds
                if (checkPos.x >= 0 && checkPos.x < mapController.mapWidth &&
                    checkPos.y >= 0 && checkPos.y < mapController.mapHeight)
                {
                    // Check if within movement distance
                    if (Mathf.Abs(x) + Mathf.Abs(y) <= movementRange)
                    {
                        Tile tile = mapController.GetTileAt((int)checkPos.x, (int)checkPos.y);
                        if (tile != null && tile.IsPassable())
                        {
                            tile.changeTileTexture(2); // Shaded texture for movement range
                            movementRangeTiles.Add(tile);
                        }
                    }
                }
            }
        }
    }
    
    void ClearMovementRange()
    {
        foreach (Tile tile in movementRangeTiles)
        {
            if (tile != null)
            {
                tile.changeTileTexture(0); // Back to base texture
            }
        }
        movementRangeTiles.Clear();
        
        foreach (Tile tile in attackRangeTiles)
        {
            if (tile != null)
            {
                tile.changeTileTexture(0);
            }
        }
        attackRangeTiles.Clear();
    }
    
    bool CanMoveToTile(Tile tile)
    {
        return movementRangeTiles.Contains(tile) && tile.IsPassable() && !tile.HasUnit();
    }
    
    bool CanAttackTile(Tile tile)
    {
        return attackRangeTiles.Contains(tile) && tile.HasUnit();
    }
    
    void MoveUnitToTile(Unit unit, Tile targetTile)
    {
        Debug.Log($"Moving {unit.name} to {targetTile.name}");
        
        // Move unit
        unit.MoveToTile(targetTile);
        
        // Clear ranges
        ClearMovementRange();
        
        // Check if unit can still attack
        if (unit.CanAttackThisTurn())
        {
            ShowAttackRange(unit);
            currentPhase = GamePhase.UnitAttack;
        }
        else
        {
            // Unit turn complete
            selectedUnit.SetSelected(false);
            selectedUnit = null;
            currentPhase = GamePhase.UnitSelection;
        }
        
        OnPhaseChanged?.Invoke(currentPhase);
    }
    
    void ShowAttackRange(Unit unit)
    {
        // Similar to ShowMovementRange but for attack range
        Vector2 unitTilePos = mapController.worldToMapPoint(unit.transform.position);
        int attackRange = unit.GetAttackRange();
        
        for (int x = -attackRange; x <= attackRange; x++)
        {
            for (int y = -attackRange; y <= attackRange; y++)
            {
                Vector2 checkPos = unitTilePos + new Vector2(x, y);
                
                if (checkPos.x >= 0 && checkPos.x < mapController.mapWidth &&
                    checkPos.y >= 0 && checkPos.y < mapController.mapHeight)
                {
                    if (Mathf.Abs(x) + Mathf.Abs(y) <= attackRange)
                    {
                        Tile tile = mapController.GetTileAt((int)checkPos.x, (int)checkPos.y);
                        if (tile != null && tile.HasUnit() && tile.GetUnit().GetOwner() != currentPlayerTurn)
                        {
                            tile.changeTileTexture(1); // Selected texture for attack targets
                            attackRangeTiles.Add(tile);
                        }
                    }
                }
            }
        }
    }
    
    void AttackTile(Unit attacker, Tile targetTile)
    {
        Unit target = targetTile.GetUnit();
        if (target != null)
        {
            Debug.Log($"{attacker.name} attacks {target.name}");
            
            // Perform combat calculation
            int damage = CalculateDamage(attacker, target);
            target.TakeDamage(damage);
            
            // Mark attacker as having attacked
            attacker.SetHasAttacked(true);
            
            // Clear ranges and deselect
            ClearMovementRange();
            selectedUnit.SetSelected(false);
            selectedUnit = null;
            currentPhase = GamePhase.UnitSelection;
            
            OnPhaseChanged?.Invoke(currentPhase);
        }
    }
    
    int CalculateDamage(Unit attacker, Unit defender)
    {
        // Simple damage calculation - can be expanded
        int baseDamage = attacker.GetAttackPower();
        int defense = defender.GetDefense();
        
        // Terrain bonuses
        Tile defenderTile = defender.GetCurrentTile();
        float terrainBonus = defenderTile.GetDefenseBonus();
        
        int finalDamage = Mathf.Max(1, baseDamage - Mathf.RoundToInt(defense * terrainBonus));
        
        Debug.Log($"Combat: {attacker.name} ({baseDamage} ATK) vs {defender.name} ({defense} DEF, {terrainBonus:F1}x terrain) = {finalDamage} damage");
        
        return finalDamage;
    }
    
    public void EndTurn()
    {
        Debug.Log($"Player {currentPlayerTurn + 1} ends turn");
        
        // Reset all units for current player
        Unit[] allUnits = FindObjectsByType<Unit>(FindObjectsSortMode.None);
        foreach (Unit unit in allUnits)
        {
            if (unit.GetOwner() == currentPlayerTurn)
            {
                unit.ResetForNewTurn();
            }
        }
        
        // Clear selection
        if (selectedUnit != null)
        {
            selectedUnit.SetSelected(false);
            selectedUnit = null;
        }
        ClearMovementRange();
        
        // Next player
        currentPlayerTurn = (currentPlayerTurn + 1) % totalPlayers;
        
        // If back to player 0, increment turn
        if (currentPlayerTurn == 0)
        {
            turnNumber++;
            OnTurnChanged?.Invoke(turnNumber);
        }
        
        currentPhase = GamePhase.UnitSelection;
        
        // Notify systems
        OnPlayerChanged?.Invoke(currentPlayerTurn);
        OnPhaseChanged?.Invoke(currentPhase);
        
        Debug.Log($"Turn {turnNumber} - Player {currentPlayerTurn + 1}'s turn begins");
    }
    
    // Public getters for UI
    public int GetCurrentPlayer() => currentPlayerTurn;
    public int GetTurnNumber() => turnNumber;
    public GamePhase GetCurrentPhase() => currentPhase;
    public Unit GetSelectedUnit() => selectedUnit;
}

// Game phases enum
public enum GamePhase
{
    UnitSelection,  // Selecting which unit to control
    UnitMovement,   // Moving the selected unit
    UnitAttack,     // Attacking with the selected unit
    TurnEnd,        // End of turn processing
    GameOver        // Game finished
}




