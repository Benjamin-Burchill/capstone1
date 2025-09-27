using UnityEngine;
using System.Collections;
using System.Collections.Generic;

/// <summary>
/// AI Controller for computer players
/// Handles AI decision making and unit actions
/// </summary>
public class AIController : MonoBehaviour
{
    [Header("AI Behavior")]
    [Tooltip("How long AI thinks before making a move")]
    public float thinkingTime = 1.0f;
    
    [Tooltip("How long between AI unit actions")]
    public float actionDelay = 0.5f;
    
    [Header("AI Difficulty Settings")]
    [Tooltip("AI Easy settings")]
    public AIDifficultySettings easySettings;
    
    [Tooltip("AI Medium settings")]
    public AIDifficultySettings mediumSettings;
    
    [Tooltip("AI Hard settings")]
    public AIDifficultySettings hardSettings;
    
    // References
    private GameState gameState;
    private Map mapController;
    private PlayerController playerController;
    
    // Current AI turn state
    private Player currentAIPlayer;
    private System.Action onTurnCompleteCallback;
    private List<Unit> aiUnitsToMove;
    private int currentUnitIndex;
    
    void Start()
    {
        gameState = FindFirstObjectByType<GameState>();
        mapController = FindFirstObjectByType<Map>();
        playerController = FindFirstObjectByType<PlayerController>();
        
        // Initialize default difficulty settings if not set
        InitializeDefaultSettings();
    }
    
    void InitializeDefaultSettings()
    {
        if (easySettings == null)
        {
            easySettings = new AIDifficultySettings
            {
                lookAheadDepth = 1,
                aggressionLevel = 0.3f,
                mistakeChance = 0.3f,
                preferredRange = AIPreferredRange.Defensive
            };
        }
        
        if (mediumSettings == null)
        {
            mediumSettings = new AIDifficultySettings
            {
                lookAheadDepth = 2,
                aggressionLevel = 0.6f,
                mistakeChance = 0.1f,
                preferredRange = AIPreferredRange.Balanced
            };
        }
        
        if (hardSettings == null)
        {
            hardSettings = new AIDifficultySettings
            {
                lookAheadDepth = 3,
                aggressionLevel = 0.8f,
                mistakeChance = 0.05f,
                preferredRange = AIPreferredRange.Aggressive
            };
        }
    }
    
    public void ExecuteAITurn(Player aiPlayer, System.Action onComplete)
    {
        if (aiPlayer == null || !aiPlayer.IsAI())
        {
            Debug.LogError("ExecuteAITurn called with invalid AI player!");
            onComplete?.Invoke();
            return;
        }
        
        currentAIPlayer = aiPlayer;
        onTurnCompleteCallback = onComplete;
        
        Debug.Log($"AI {aiPlayer.playerName} is thinking...");
        
        // Get AI difficulty settings
        AIDifficultySettings settings = GetSettingsForPlayer(aiPlayer);
        
        // Find all AI units that can act
        aiUnitsToMove = GetActiveAIUnits(aiPlayer);
        currentUnitIndex = 0;
        
        Debug.Log($"AI found {aiUnitsToMove.Count} units to control");
        
        // Start AI turn sequence
        StartCoroutine(ExecuteAITurnSequence(settings));
    }
    
    AIDifficultySettings GetSettingsForPlayer(Player player)
    {
        switch (player.playerType)
        {
            case PlayerType.AIEasy:
                return easySettings;
            case PlayerType.AIMedium:
                return mediumSettings;
            case PlayerType.AIHard:
                return hardSettings;
            default:
                return easySettings;
        }
    }
    
    List<Unit> GetActiveAIUnits(Player aiPlayer)
    {
        List<Unit> activeUnits = new List<Unit>();
        
        // Find all units belonging to this AI player
        Unit[] allUnits = FindObjectsByType<Unit>(FindObjectsSortMode.None);
        foreach (Unit unit in allUnits)
        {
            if (unit.owner == aiPlayer.playerID && unit.currentHealth > 0 && CanUnitAct(unit))
            {
                activeUnits.Add(unit);
            }
        }
        
        return activeUnits;
    }
    
    IEnumerator ExecuteAITurnSequence(AIDifficultySettings settings)
    {
        // Thinking delay
        yield return new WaitForSeconds(thinkingTime);
        
        // Process each unit
        while (currentUnitIndex < aiUnitsToMove.Count)
        {
            Unit currentUnit = aiUnitsToMove[currentUnitIndex];
            
            if (currentUnit != null && currentUnit.currentHealth > 0 && CanUnitAct(currentUnit))
            {
                Debug.Log($"AI controlling unit: {currentUnit.name}");
                
                // Select the unit (visual feedback)
                if (gameState != null)
                {
                    gameState.SelectUnit(currentUnit);
                }
                
                yield return new WaitForSeconds(actionDelay);
                
                // Make AI decision for this unit
                yield return StartCoroutine(ExecuteUnitAction(currentUnit, settings));
                
                yield return new WaitForSeconds(actionDelay);
            }
            
            currentUnitIndex++;
        }
        
        // AI turn complete
        Debug.Log($"AI {currentAIPlayer.playerName} turn complete");
        onTurnCompleteCallback?.Invoke();
    }
    
    IEnumerator ExecuteUnitAction(Unit unit, AIDifficultySettings settings)
    {
        // Simple AI logic - you can expand this significantly
        
        // 1. Look for enemies to attack
        Unit targetEnemy = FindBestTarget(unit, settings);
        if (targetEnemy != null)
        {
            Debug.Log($"AI unit attacking {targetEnemy.name}");
            
            // Move closer if needed
            Tile bestPosition = FindBestAttackPosition(unit, targetEnemy, settings);
            if (bestPosition != null && bestPosition != unit.GetCurrentTile())
            {
                yield return StartCoroutine(MoveUnitToTile(unit, bestPosition));
            }
            
            // Attack if in range
            if (CanUnitAttack(unit, targetEnemy))
            {
                yield return StartCoroutine(AttackTarget(unit, targetEnemy));
            }
        }
        else
        {
            // 2. No enemies in range - move strategically
            Tile strategicPosition = FindStrategicPosition(unit, settings);
            if (strategicPosition != null && strategicPosition != unit.GetCurrentTile())
            {
                yield return StartCoroutine(MoveUnitToTile(unit, strategicPosition));
            }
        }
        
        // Mark unit as having acted
        unit.hasMoved = true;
        unit.hasAttacked = true;
    }
    
    Unit FindBestTarget(Unit aiUnit, AIDifficultySettings settings)
    {
        Unit bestTarget = null;
        float bestScore = -1f;
        
        Unit[] allUnits = FindObjectsByType<Unit>(FindObjectsSortMode.None);
        foreach (Unit potentialTarget in allUnits)
        {
            // Skip if same team or dead
            if (potentialTarget.owner == aiUnit.owner || potentialTarget.currentHealth <= 0)
                continue;
            
            // Check if within reasonable range
            float distance = Vector3.Distance(aiUnit.transform.position, potentialTarget.transform.position);
            if (distance > aiUnit.attackRange * 2) // Within 2x max range
                continue;
            
            // Calculate target score based on AI settings
            float score = CalculateTargetScore(aiUnit, potentialTarget, settings);
            
            if (score > bestScore)
            {
                bestScore = score;
                bestTarget = potentialTarget;
            }
        }
        
        return bestTarget;
    }
    
    float CalculateTargetScore(Unit aiUnit, Unit target, AIDifficultySettings settings)
    {
        float score = 0f;
        
        // Base score - prefer weaker enemies
        score += (100f - target.currentHealth) * 0.01f;
        
        // Distance factor - prefer closer enemies
        float distance = Vector3.Distance(aiUnit.transform.position, target.transform.position);
        score += Mathf.Max(0, 10f - distance) * 0.1f;
        
        // Aggression modifier
        score *= settings.aggressionLevel;
        
        // Add some randomness for mistakes
        if (Random.value < settings.mistakeChance)
        {
            score *= Random.Range(0.5f, 1.5f);
        }
        
        return score;
    }
    
    Tile FindBestAttackPosition(Unit aiUnit, Unit target, AIDifficultySettings settings)
    {
        // Simple implementation - find closest tile within attack range
        // You can make this much more sophisticated
        
        if (mapController == null) return null;
        
        Tile targetTile = target.GetCurrentTile();
        if (targetTile == null) return null;
        
        // Get tiles around target within attack range
        List<Tile> possiblePositions = GetTilesInRange(targetTile, aiUnit.attackRange);
        
        Tile bestPosition = null;
        float bestScore = -1f;
        
        foreach (Tile tile in possiblePositions)
        {
            // Check if tile is passable and not occupied
            if (!tile.isPassable || tile.HasUnit()) continue;
            
            // Check if unit can reach this tile
            if (!CanUnitReachTile(aiUnit, tile)) continue;
            
            // Calculate position score
            float score = CalculatePositionScore(aiUnit, tile, target, settings);
            
            if (score > bestScore)
            {
                bestScore = score;
                bestPosition = tile;
            }
        }
        
        return bestPosition;
    }
    
    float CalculatePositionScore(Unit aiUnit, Tile position, Unit target, AIDifficultySettings settings)
    {
        float score = 0f;
        
        // Prefer defensive positions (higher defense bonus)
        score += position.defenseBonus * 2f;
        
        // Consider movement cost
        score -= position.movementCost * 0.5f;
        
        // Tactical positioning based on AI preference
        switch (settings.preferredRange)
        {
            case AIPreferredRange.Aggressive:
                // Prefer closer positions
                score += (5f - Vector3.Distance(position.transform.position, target.transform.position));
                break;
            case AIPreferredRange.Defensive:
                // Prefer positions with good defense
                score += position.defenseBonus * 3f;
                break;
            case AIPreferredRange.Balanced:
                // Balance between offense and defense
                score += position.defenseBonus;
                score += (3f - Vector3.Distance(position.transform.position, target.transform.position));
                break;
        }
        
        return score;
    }
    
    Tile FindStrategicPosition(Unit aiUnit, AIDifficultySettings settings)
    {
        // Simple strategic movement - move toward nearest enemy or defensive position
        // This is a basic implementation - you can make it much more sophisticated
        
        if (mapController == null) return null;
        
        // Find nearest enemy
        Unit nearestEnemy = FindNearestEnemy(aiUnit);
        if (nearestEnemy != null)
        {
            // Move toward enemy
            return FindTileTowardTarget(aiUnit, nearestEnemy.GetCurrentTile());
        }
        
        // No enemies found - hold position or move to center
        return aiUnit.GetCurrentTile();
    }
    
    Unit FindNearestEnemy(Unit aiUnit)
    {
        Unit nearestEnemy = null;
        float nearestDistance = float.MaxValue;
        
        Unit[] allUnits = FindObjectsByType<Unit>(FindObjectsSortMode.None);
        foreach (Unit unit in allUnits)
        {
            if (unit.owner != aiUnit.owner && unit.currentHealth > 0)
            {
                float distance = Vector3.Distance(aiUnit.transform.position, unit.transform.position);
                if (distance < nearestDistance)
                {
                    nearestDistance = distance;
                    nearestEnemy = unit;
                }
            }
        }
        
        return nearestEnemy;
    }
    
    Tile FindTileTowardTarget(Unit aiUnit, Tile targetTile)
    {
        // Simple pathfinding - move one step toward target
        if (mapController == null || targetTile == null) return null;
        
        Tile currentTile = aiUnit.GetCurrentTile();
        if (currentTile == null) return null;
        
        List<Tile> neighbors = mapController.GetNeighboringTiles(currentTile.tileX, currentTile.tileY);
        
        Tile bestTile = null;
        float bestDistance = float.MaxValue;
        
        foreach (Tile neighbor in neighbors)
        {
            if (!neighbor.isPassable || neighbor.HasUnit()) continue;
            if (!CanUnitReachTile(aiUnit, neighbor)) continue;
            
            float distance = Vector3.Distance(neighbor.transform.position, targetTile.transform.position);
            if (distance < bestDistance)
            {
                bestDistance = distance;
                bestTile = neighbor;
            }
        }
        
        return bestTile;
    }
    
    IEnumerator MoveUnitToTile(Unit unit, Tile targetTile)
    {
        Debug.Log($"AI moving {unit.name} to {targetTile.name}");
        
        // Use existing movement system
        if (gameState != null)
        {
            gameState.SelectTile(targetTile);
            // Wait for movement to complete
            yield return new WaitForSeconds(0.5f);
        }
    }
    
    IEnumerator AttackTarget(Unit attacker, Unit target)
    {
        Debug.Log($"AI {attacker.name} attacking {target.name}");
        
        // Use existing combat system
        if (gameState != null)
        {
            gameState.SelectUnit(target); // Select target for attack
            // Wait for attack animation
            yield return new WaitForSeconds(1.0f);
        }
    }
    
    // Helper methods to bridge the gap between AI expectations and actual Unit API
    
    bool CanUnitAct(Unit unit)
    {
        // A unit can act if it hasn't moved and attacked yet this turn
        return !unit.hasMoved || !unit.hasAttacked;
    }
    
    bool CanUnitAttack(Unit attacker, Unit target)
    {
        if (attacker.hasAttacked) return false;
        if (target.currentHealth <= 0) return false;
        
        float distance = Vector3.Distance(attacker.transform.position, target.transform.position);
        return distance <= attacker.attackRange;
    }
    
    bool CanUnitReachTile(Unit unit, Tile tile)
    {
        if (unit.hasMoved) return false;
        if (!tile.isPassable || tile.HasUnit()) return false;
        
        // Simple distance check - you can make this more sophisticated with pathfinding
        float distance = Vector3.Distance(unit.transform.position, tile.transform.position);
        return distance <= unit.movementRange;
    }
    
    List<Tile> GetTilesInRange(Tile centerTile, int range)
    {
        List<Tile> tilesInRange = new List<Tile>();
        
        if (mapController == null || centerTile == null) return tilesInRange;
        
        // Simple implementation - get tiles in a square pattern
        // You can make this more sophisticated with proper hex distance calculation
        for (int x = centerTile.tileX - range; x <= centerTile.tileX + range; x++)
        {
            for (int y = centerTile.tileY - range; y <= centerTile.tileY + range; y++)
            {
                if (x >= 0 && x < mapController.mapWidth && y >= 0 && y < mapController.mapHeight)
                {
                    Tile tile = mapController.GetTileAt(x, y);
                    if (tile != null)
                    {
                        float distance = Mathf.Abs(x - centerTile.tileX) + Mathf.Abs(y - centerTile.tileY);
                        if (distance <= range)
                        {
                            tilesInRange.Add(tile);
                        }
                    }
                }
            }
        }
        
        return tilesInRange;
    }
}

/// <summary>
/// AI Difficulty Settings
/// </summary>
[System.Serializable]
public class AIDifficultySettings
{
    [Tooltip("How many moves ahead the AI considers")]
    public int lookAheadDepth = 1;
    
    [Tooltip("How aggressive the AI is (0.0 = passive, 1.0 = very aggressive)")]
    public float aggressionLevel = 0.5f;
    
    [Tooltip("Chance AI makes a suboptimal move (0.0 = perfect, 1.0 = random)")]
    public float mistakeChance = 0.1f;
    
    [Tooltip("AI's preferred combat range")]
    public AIPreferredRange preferredRange = AIPreferredRange.Balanced;
}

public enum AIPreferredRange
{
    Aggressive,  // Prefers close combat
    Balanced,    // Balances offense and defense
    Defensive    // Prefers ranged combat and defensive positions
}
