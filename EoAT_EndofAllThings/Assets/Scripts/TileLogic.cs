using UnityEngine;

/// <summary>
/// Component for tiles that need special logic and behaviors
/// Only created for tiles that actually need it - addressing performance concerns
/// This is where your brother's "logic in texture" concept gets implemented!
/// </summary>
public class TileLogic : MonoBehaviour
{
    [Header("Tile Reference")]
    [Tooltip("The tile data this logic component manages")]
    public TileData tileData;
    
    [Header("Runtime References")]
    [Tooltip("Reference to the main hybrid map")]
    public HybridMap hybridMap;
    
    [Header("Logic Settings")]
    [Tooltip("Update frequency for this tile's logic (0 = every frame)")]
    public float updateInterval = 0f;
    
    [Tooltip("Enable custom tile behaviors")]
    public bool enableCustomBehaviors = true;
    
    // Internal state
    private float lastUpdateTime = 0f;
    
    /// <summary>
    /// Initialize this logic component with tile data
    /// Called by HybridMap when creating logic objects
    /// </summary>
    public void Initialize(TileData data, HybridMap map)
    {
        tileData = data;
        hybridMap = map;
        
        // Set up GameObject name and position for debugging
        gameObject.name = $"{data.terrainType}_Logic_{data.position.x}_{data.position.y}";
        
        // Call virtual method for subclasses to override
        OnTileInitialized();
        
        Debug.Log($"TileLogic: Initialized logic for {data.terrainType} at {data.position}");
    }
    
    /// <summary>
    /// Override this in subclasses for custom initialization
    /// </summary>
    protected virtual void OnTileInitialized()
    {
        // Example: Set up particle systems, audio sources, etc.
        // Example: Subscribe to events
        // Example: Initialize custom properties based on terrain type
        
        switch (tileData.terrainType)
        {
            case TerrainType.City:
                InitializeCityTile();
                break;
            case TerrainType.Resource:
                InitializeResourceTile();
                break;
            case TerrainType.Special:
                InitializeSpecialTile();
                break;
        }
    }
    
    void InitializeCityTile()
    {
        // Example city tile logic
        tileData.SetCustomProperty("citySize", Random.Range(1, 4));
        tileData.SetCustomProperty("population", Random.Range(100, 1000));
        tileData.SetCustomProperty("defenseWalls", Random.value > 0.5f);
        
        Debug.Log($"City tile initialized: Size {tileData.GetCustomProperty<int>("citySize")}, Pop {tileData.GetCustomProperty<int>("population")}");
    }
    
    void InitializeResourceTile()
    {
        // Example resource tile logic
        string[] resourceTypes = {"Gold", "Iron", "Food", "Wood"};
        string resourceType = resourceTypes[Random.Range(0, resourceTypes.Length)];
        
        tileData.SetCustomProperty("resourceType", resourceType);
        tileData.SetCustomProperty("resourceAmount", Random.Range(50, 200));
        tileData.SetCustomProperty("harvestable", true);
        
        Debug.Log($"Resource tile initialized: {resourceType} x{tileData.GetCustomProperty<int>("resourceAmount")}");
    }
    
    void InitializeSpecialTile()
    {
        // Example special tile logic
        tileData.SetCustomProperty("magicalAura", true);
        tileData.SetCustomProperty("spellPowerBonus", 1.5f);
        tileData.SetCustomProperty("glowColor", Color.cyan);
        
        Debug.Log($"Special tile initialized with magical properties");
    }
    
    void Update()
    {
        if (!enableCustomBehaviors) return;
        
        // Throttle updates if needed for performance
        if (updateInterval > 0f && Time.time - lastUpdateTime < updateInterval)
        {
            return;
        }
        lastUpdateTime = Time.time;
        
        // Call custom update logic
        OnTileUpdate();
    }
    
    /// <summary>
    /// Override this for custom per-frame logic
    /// Only runs on tiles that actually need it!
    /// </summary>
    protected virtual void OnTileUpdate()
    {
        // Example behaviors based on tile properties
        HandleCityLogic();
        HandleResourceLogic();
        HandleSpecialEffects();
        HandleAnimations();
    }
    
    void HandleCityLogic()
    {
        if (tileData.terrainType == TerrainType.City)
        {
            // Example: City population growth
            if (Time.time % 60f < Time.deltaTime) // Every minute
            {
                int currentPop = tileData.GetCustomProperty<int>("population");
                int citySize = tileData.GetCustomProperty<int>("citySize");
                int growthRate = citySize * 10;
                
                tileData.SetCustomProperty("population", currentPop + growthRate);
                Debug.Log($"City at {tileData.position} grew to {currentPop + growthRate} population");
            }
        }
    }
    
    void HandleResourceLogic()
    {
        if (tileData.terrainType == TerrainType.Resource)
        {
            // Example: Resource regeneration
            bool harvestable = tileData.GetCustomProperty<bool>("harvestable");
            if (!harvestable && Time.time % 30f < Time.deltaTime) // Regenerate every 30 seconds
            {
                tileData.SetCustomProperty("harvestable", true);
                Debug.Log($"Resource at {tileData.position} has regenerated");
            }
        }
    }
    
    void HandleSpecialEffects()
    {
        if (tileData.HasProperty("magicalAura"))
        {
            // Example: Magical glow effect
            Color glowColor = tileData.GetCustomProperty<Color>("glowColor");
            float intensity = Mathf.Sin(Time.time * 2f) * 0.5f + 0.5f;
            
            // Apply glow effect (you'd implement actual visual effects here)
            tileData.highlightColor = glowColor * intensity;
        }
    }
    
    void HandleAnimations()
    {
        // Example: Water tiles could have wave animations
        if (tileData.terrainType == TerrainType.ShallowWater || tileData.terrainType == TerrainType.DeepWater)
        {
            // Animate water (example - you'd implement actual sprite animation)
            float waveOffset = Mathf.Sin(Time.time + tileData.position.x * 0.1f + tileData.position.y * 0.1f);
            transform.position = hybridMap.TileToWorldPosition(tileData.position) + Vector3.up * waveOffset * 0.05f;
        }
    }
    
    /// <summary>
    /// Called when the terrain type changes at runtime
    /// </summary>
    public virtual void OnTerrainChanged(TerrainType newTerrain)
    {
        Debug.Log($"TileLogic: Terrain changed from {tileData.terrainType} to {newTerrain} at {tileData.position}");
        
        // Clean up old terrain logic
        CleanupTerrainLogic(tileData.terrainType);
        
        // Update tile data
        tileData.terrainType = newTerrain;
        
        // Initialize new terrain logic
        OnTileInitialized();
    }
    
    /// <summary>
    /// Unity message system overload - converts int to TerrainType
    /// This fixes the "message parameter has to be of type: int" error
    /// </summary>
    public virtual void OnTerrainChanged(int terrainIndex)
    {
        // Convert int to TerrainType enum safely
        if (System.Enum.IsDefined(typeof(TerrainType), terrainIndex))
        {
            TerrainType newTerrain = (TerrainType)terrainIndex;
            OnTerrainChanged(newTerrain); // Call the main method
        }
        else
        {
            Debug.LogWarning($"TileLogic: Invalid terrain index {terrainIndex} - ignoring terrain change");
        }
    }
    
    void CleanupTerrainLogic(TerrainType oldTerrain)
    {
        // Clean up terrain-specific logic
        switch (oldTerrain)
        {
            case TerrainType.City:
                // Clean up city-specific components/effects
                break;
            case TerrainType.Resource:
                // Clean up resource-specific components/effects
                break;
        }
    }
    
    /// <summary>
    /// Called when a unit enters this tile
    /// </summary>
    public virtual void OnUnitEntered(Unit unit)
    {
        Debug.Log($"TileLogic: Unit {unit.name} entered {tileData.terrainType} at {tileData.position}");
        
        // Update tile data
        tileData.occupyingUnit = unit;
        
        // Handle terrain-specific effects
        switch (tileData.terrainType)
        {
            case TerrainType.City:
                OnUnitEnteredCity(unit);
                break;
            case TerrainType.Resource:
                OnUnitEnteredResource(unit);
                break;
            case TerrainType.Special:
                OnUnitEnteredSpecial(unit);
                break;
        }
    }
    
    void OnUnitEnteredCity(Unit unit)
    {
        // Example: Unit gains defensive bonus in cities
        bool hasWalls = tileData.GetCustomProperty<bool>("defenseWalls");
        if (hasWalls)
        {
            Debug.Log($"Unit {unit.name} gains defensive bonus from city walls");
            // Apply defensive bonus logic
        }
    }
    
    void OnUnitEnteredResource(Unit unit)
    {
        // Example: Unit can harvest resources
        bool harvestable = tileData.GetCustomProperty<bool>("harvestable");
        if (harvestable)
        {
            string resourceType = tileData.GetCustomProperty<string>("resourceType");
            int amount = tileData.GetCustomProperty<int>("resourceAmount");
            
            Debug.Log($"Unit {unit.name} can harvest {amount} {resourceType}");
            // You could trigger harvest UI or automatic collection
        }
    }
    
    void OnUnitEnteredSpecial(Unit unit)
    {
        // Example: Unit gains magical benefits
        float spellPowerBonus = tileData.GetCustomProperty<float>("spellPowerBonus");
        Debug.Log($"Unit {unit.name} gains {spellPowerBonus}x spell power bonus");
        // Apply magical effects
    }
    
    /// <summary>
    /// Called when a unit leaves this tile
    /// </summary>
    public virtual void OnUnitLeft(Unit unit)
    {
        Debug.Log($"TileLogic: Unit {unit.name} left {tileData.terrainType} at {tileData.position}");
        
        // Clear occupying unit if it matches
        if (tileData.occupyingUnit == unit)
        {
            tileData.occupyingUnit = null;
        }
        
        // Remove any temporary effects
        switch (tileData.terrainType)
        {
            case TerrainType.City:
                // Remove city bonuses
                break;
            case TerrainType.Special:
                // Remove magical bonuses
                break;
        }
    }
    
    /// <summary>
    /// Called when this tile is clicked
    /// </summary>
    public virtual void OnTileClicked()
    {
        Debug.Log($"TileLogic: {tileData.terrainType} tile clicked at {tileData.position}");
        
        // Show tile information
        ShowTileInfo();
        
        // Handle terrain-specific click behaviors
        switch (tileData.terrainType)
        {
            case TerrainType.City:
                OnCityClicked();
                break;
            case TerrainType.Resource:
                OnResourceClicked();
                break;
        }
    }
    
    void ShowTileInfo()
    {
        Debug.Log($"Tile Info: {tileData.ToString()}");
        
        // Example: Show UI panel with tile details
        // You could integrate with your UIManager here
    }
    
    void OnCityClicked()
    {
        int population = tileData.GetCustomProperty<int>("population");
        int citySize = tileData.GetCustomProperty<int>("citySize");
        bool hasWalls = tileData.GetCustomProperty<bool>("defenseWalls");
        
        Debug.Log($"City Info - Size: {citySize}, Population: {population}, Walls: {hasWalls}");
        // Show city management UI
    }
    
    void OnResourceClicked()
    {
        string resourceType = tileData.GetCustomProperty<string>("resourceType");
        int amount = tileData.GetCustomProperty<int>("resourceAmount");
        bool harvestable = tileData.GetCustomProperty<bool>("harvestable");
        
        Debug.Log($"Resource Info - Type: {resourceType}, Amount: {amount}, Available: {harvestable}");
        // Show resource management UI
    }
    
    /// <summary>
    /// Clean up when this GameObject is destroyed
    /// </summary>
    void OnDestroy()
    {
        // Unsubscribe from events, clean up resources
        OnTileDestroyed();
    }
    
    protected virtual void OnTileDestroyed()
    {
        // Override for custom cleanup
        Debug.Log($"TileLogic: Cleaning up logic for {tileData?.terrainType} at {tileData?.position}");
    }
    
    /// <summary>
    /// For debugging - visualize tile logic in scene view
    /// </summary>
    void OnDrawGizmos()
    {
        if (tileData == null) return;
        
        // Draw different colored gizmos based on tile properties
        Color gizmoColor = Color.white;
        
        switch (tileData.terrainType)
        {
            case TerrainType.City:
                gizmoColor = Color.blue;
                break;
            case TerrainType.Resource:
                gizmoColor = Color.yellow;
                break;
            case TerrainType.Special:
                gizmoColor = Color.magenta;
                break;
        }
        
        Gizmos.color = gizmoColor;
        Gizmos.DrawWireCube(transform.position, Vector3.one * 0.5f);
        
        // Show custom properties as text (in editor only)
        #if UNITY_EDITOR
        if (tileData.HasProperty("citySize"))
        {
            UnityEditor.Handles.Label(transform.position + Vector3.up, 
                $"City Size: {tileData.GetCustomProperty<int>("citySize")}");
        }
        if (tileData.HasProperty("resourceType"))
        {
            UnityEditor.Handles.Label(transform.position + Vector3.up, 
                $"{tileData.GetCustomProperty<string>("resourceType")}: {tileData.GetCustomProperty<int>("resourceAmount")}");
        }
        #endif
    }
}
