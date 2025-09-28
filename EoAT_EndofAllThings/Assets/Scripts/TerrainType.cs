/// <summary>
/// Terrain types enum for the EoAT strategy game
/// Used by all map systems (Map.cs, OptimizedMap.cs, HybridMap.cs)
/// Defines all possible terrain types that can exist on tiles
/// </summary>
public enum TerrainType
{
    Grass,        // Basic passable terrain
    Hills,        // Slow movement, defense bonus
    Mountains,    // Impassable for most units
    ShallowWater, // Passable but slow
    DeepWater,    // Impassable for most units
    
    // Additional terrain types for expanded gameplay:
    Forest,       // Cover, hiding bonus
    Desert,       // Hot, movement penalty
    City,         // Player settlements
    Resource,     // Harvestable resources
    Special,      // Magical or unique tiles
    
    // You can add more terrain types here as needed:
    // Swamp,
    // Ice,
    // Lava,
    // Bridge,
    // Road,
    // etc.
}




