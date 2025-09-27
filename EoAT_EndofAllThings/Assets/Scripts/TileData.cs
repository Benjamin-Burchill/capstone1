using UnityEngine;
using UnityEngine.Tilemaps;
using System.Collections.Generic;

/// <summary>
/// Data structure that holds all information about a tile
/// This is the key to flexibility - rich data without GameObject overhead!
/// Each tile has this data whether or not it has a GameObject
/// </summary>
[System.Serializable]
public class TileData
{
    [Header("Core Properties")]
    public Vector3Int position;
    public TerrainType terrainType;
    public TileBase tileAsset;
    
    [Header("Gameplay Properties")]
    public int movementCost = 1;
    public float defenseBonus = 1.0f;
    public bool isPassable = true;
    public bool needsLogicObject = false;
    
    [Header("State")]
    public Unit occupyingUnit;
    public bool isVisible = true;
    public bool isExplored = false;
    
    [Header("Visual Effects")]
    public bool isHighlighted = false;
    public Color highlightColor = Color.white;
    
    // The flexibility magic: Custom properties for ANY behavior!
    // This addresses your brother's concerns about "logic in texture"
    private Dictionary<string, object> customProperties = new Dictionary<string, object>();
    
    /// <summary>
    /// Set any custom property on this tile
    /// Examples: "hasResource", "citySize", "buildingType", "animationState"
    /// </summary>
    public void SetCustomProperty(string key, object value)
    {
        customProperties[key] = value;
    }
    
    /// <summary>
    /// Get custom property with type safety
    /// </summary>
    public T GetCustomProperty<T>(string key)
    {
        if (customProperties.ContainsKey(key))
        {
            try
            {
                return (T)customProperties[key];
            }
            catch (System.InvalidCastException)
            {
                Debug.LogWarning($"TileData: Property '{key}' exists but cannot be cast to {typeof(T)}");
                return default(T);
            }
        }
        return default(T);
    }
    
    /// <summary>
    /// Check if tile has a specific property
    /// </summary>
    public bool HasProperty(string key)
    {
        return customProperties.ContainsKey(key);
    }
    
    /// <summary>
    /// Remove a custom property
    /// </summary>
    public void RemoveProperty(string key)
    {
        customProperties.Remove(key);
    }
    
    /// <summary>
    /// Get all property keys (useful for debugging)
    /// </summary>
    public string[] GetAllPropertyKeys()
    {
        string[] keys = new string[customProperties.Count];
        customProperties.Keys.CopyTo(keys, 0);
        return keys;
    }
    
    // Convenience methods for common properties
    public bool IsOccupied => occupyingUnit != null;
    public bool CanMoveThrough => isPassable && !IsOccupied;
    public bool IsImpassable => !isPassable || movementCost >= 999;
    
    /// <summary>
    /// Get movement cost with unit-specific modifiers
    /// </summary>
    public int GetMovementCostForUnit(Unit unit)
    {
        float baseCost = movementCost;
        
        // Apply unit-specific modifiers based on unit type
        if (unit != null)
        {
            // Example: Different unit types have different movement modifiers
            switch (unit.unitType)
            {
                case UnitType.Cavalry:
                    // Cavalry move faster on grass but slower in hills
                    if (terrainType == TerrainType.Grass)
                        baseCost *= 0.75f;
                    else if (terrainType == TerrainType.Hills)
                        baseCost *= 1.25f;
                    break;
                    
                case UnitType.Warrior:
                    // Warriors are standard melee - no modifiers
                    break;
                    
                case UnitType.Archer:
                    // Archers move slightly slower but can attack from range
                    baseCost *= 1.1f;
                    break;
                    
                case UnitType.Scout:
                    // Scouts move faster on all terrain
                    baseCost *= 0.8f;
                    break;
                    
                case UnitType.Siege:
                    // Siege units move very slowly
                    baseCost *= 1.5f;
                    break;
                    
                // Add more unit types as needed
                default:
                    break;
            }
        }
        
        return Mathf.RoundToInt(baseCost);
    }
    
    /// <summary>
    /// Get defense bonus with unit-specific considerations
    /// </summary>
    public float GetDefenseBonusForUnit(Unit unit)
    {
        float bonus = defenseBonus;
        
        // Apply unit-specific modifiers based on unit type
        if (unit != null)
        {
            // Different unit types get bonuses on different terrain
            switch (unit.unitType)
            {
                case UnitType.Warrior:
                    // Warriors get extra defense bonus in hills
                    if (terrainType == TerrainType.Hills)
                        bonus += 0.15f;
                    break;
                    
                case UnitType.Archer:
                    // Archers get bonus on hills (high ground advantage)
                    if (terrainType == TerrainType.Hills)
                        bonus += 0.2f;
                    break;
                    
                case UnitType.Cavalry:
                    // Cavalry get less defense bonus (harder to take cover)
                    bonus *= 0.9f;
                    break;
                    
                case UnitType.Scout:
                    // Scouts are lightly armored - less defense
                    bonus *= 0.8f;
                    break;
                    
                case UnitType.Siege:
                    // Siege units are heavily armored
                    bonus += 0.1f;
                    break;
                    
                case UnitType.Mage:
                    // Mages are fragile but get bonus in special terrain
                    if (terrainType == TerrainType.Special)
                        bonus += 0.3f;
                    else
                        bonus *= 0.9f;
                    break;
                    
                // Add more unit types as needed
                default:
                    break;
            }
        }
        
        return bonus;
    }
    
    /// <summary>
    /// For debugging - show all tile information
    /// </summary>
    public override string ToString()
    {
        return $"TileData({position.x},{position.y}): {terrainType}, Cost:{movementCost}, Defense:{defenseBonus:F1}x, " +
               $"Passable:{isPassable}, Occupied:{IsOccupied}, Properties:{customProperties.Count}";
    }
    
    // Serialization support for saving/loading
    public TileDataSerialized ToSerialized()
    {
        return new TileDataSerialized
        {
            position = position,
            terrainType = terrainType,
            movementCost = movementCost,
            defenseBonus = defenseBonus,
            isPassable = isPassable,
            isVisible = isVisible,
            isExplored = isExplored,
            // Note: Custom properties and GameObject references aren't serialized by default
            // You'd need custom serialization for those if needed
        };
    }
    
    public static TileData FromSerialized(TileDataSerialized data)
    {
        return new TileData
        {
            position = data.position,
            terrainType = data.terrainType,
            movementCost = data.movementCost,
            defenseBonus = data.defenseBonus,
            isPassable = data.isPassable,
            isVisible = data.isVisible,
            isExplored = data.isExplored
        };
    }
}

/// <summary>
/// Serializable version of TileData for save/load
/// </summary>
[System.Serializable]
public class TileDataSerialized
{
    public Vector3Int position;
    public TerrainType terrainType;
    public int movementCost;
    public float defenseBonus;
    public bool isPassable;
    public bool isVisible;
    public bool isExplored;
}

