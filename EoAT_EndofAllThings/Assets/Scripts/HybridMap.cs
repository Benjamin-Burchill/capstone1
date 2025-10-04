using UnityEngine;
using UnityEngine.Tilemaps;
using System.Collections.Generic;

/// <summary>
/// Hybrid map system that combines Tilemap performance with GameObject flexibility
/// Uses Tilemap for visual rendering, but maintains tile logic and data separately
/// </summary>
public class HybridMap : MonoBehaviour
{
    [Header("Tilemap Rendering (Performance)")]
    [Tooltip("Main tilemap for visual rendering")]
    public Tilemap tilemap;
    public TilemapRenderer tilemapRenderer;
    public TilemapCollider2D tilemapCollider;
    
    [Header("Tile Logic System (Flexibility)")]
    [Tooltip("Enable per-tile logic objects for special tiles")]
    public bool enableTileLogic = true;
    
    [Tooltip("Prefabs for tiles that need custom logic")]
    public GameObject[] logicTilePrefabs;
    
    [Header("Map Generation")]
    [Tooltip("PNG image to convert to map")]
    public Texture2D mapImage;
    
    [Tooltip("Text file mapping colors to tile types")]
    public TextAsset mappingFile;
    
    [Tooltip("Tile assets for visual rendering")]
    public TileBase[] tileAssets;
    
    [Tooltip("Names corresponding to tile assets")]
    public string[] tileAssetNames;
    
    [Header("Performance Settings")]
    [Tooltip("Only create GameObjects for tiles that actually need logic")]
    public bool optimizedLogicSpawning = true;
    
    [Tooltip("Tile types that need GameObject logic (cities, resources, etc.)")]
    public string[] tilesNeedingLogic = {"CityTile", "ResourceTile", "SpecialTile", "AnimatedTile"};
    
    [Header("Settings")]
    public Vector2 tileSize = new Vector2(1f, 0.866f); // Hex tile size
    
    // Data structures - The key to flexibility!
    private TileData[,] tileDataGrid; // Stores ALL tile information efficiently
    private Dictionary<Vector3Int, GameObject> logicTileObjects; // Only special tiles
    private Dictionary<Vector3Int, Unit> unitPositions;
    private Dictionary<Color, TileBase> colorToTileMapping;
    
    // Map properties
    public int mapWidth { get; private set; }
    public int mapHeight { get; private set; }
    public Vector2 mapMaxDim { get; private set; }
    public Vector2 mapMinDim { get; private set; }
    
    // Mouse interaction
    private Vector3Int lastHoveredTile = Vector3Int.zero;
    private Camera mainCamera;
    
    void Start()
    {
        mainCamera = Camera.main;
        InitializeHybridSystem();
        GenerateHybridMap();
    }
    
    void InitializeHybridSystem()
    {
        if (mapImage == null)
        {
            Debug.LogError("No map image assigned to HybridMap!");
            return;
        }
        
        mapWidth = mapImage.width;
        mapHeight = mapImage.height;
        
        // Initialize data structures
        tileDataGrid = new TileData[mapWidth, mapHeight];
        logicTileObjects = new Dictionary<Vector3Int, GameObject>();
        unitPositions = new Dictionary<Vector3Int, Unit>();
        colorToTileMapping = new Dictionary<Color, TileBase>();
        
        // Calculate world bounds
        mapMinDim = Vector2.zero;
        mapMaxDim = new Vector2(mapWidth * tileSize.x, mapHeight * tileSize.y);
        
        // Build color to tile mapping
        BuildColorToTileMapping();
        
        Debug.Log("HybridMap: Initialized - Visual performance + Logic flexibility");
        Debug.Log($"Map size: {mapWidth}x{mapHeight} = {mapWidth * mapHeight} tiles");
    }
    
    void BuildColorToTileMapping()
    {
        if (mappingFile == null || tileAssets == null)
        {
            Debug.LogError("Missing mapping file or tile assets!");
            return;
        }
        
        string[] lines = mappingFile.text.Split(new char[] { '\n', '\r' }, System.StringSplitOptions.RemoveEmptyEntries);
        
        foreach (string line in lines)
        {
            if (string.IsNullOrWhiteSpace(line) || !line.Contains(",")) continue;
            
            string[] parts = line.Trim().Split(',');
            if (parts.Length < 4) continue;
            
            string tileName = parts[0];
            
            // Parse RGB values
            if (float.TryParse(parts[1], out float r) &&
                float.TryParse(parts[2], out float g) &&
                float.TryParse(parts[3], out float b))
            {
                Color color = new Color(r / 255f, g / 255f, b / 255f);
                TileBase tileAsset = FindTileAssetByName(tileName);
                
                if (tileAsset != null)
                {
                    colorToTileMapping[color] = tileAsset;
                    Debug.Log($"HybridMap: Mapped {tileName} to color RGB({r},{g},{b})");
                }
                else
                {
                    Debug.LogWarning($"HybridMap: No tile asset found for {tileName}");
                }
            }
        }
        
        Debug.Log($"HybridMap: Built color mapping with {colorToTileMapping.Count} entries");
    }
    
    TileBase FindTileAssetByName(string tileName)
    {
        for (int i = 0; i < tileAssetNames.Length && i < tileAssets.Length; i++)
        {
            if (tileAssetNames[i] == tileName)
            {
                return tileAssets[i];
            }
        }
        return null;
    }
    
    void GenerateHybridMap()
    {
        Debug.Log($"HybridMap: Generating hybrid map - {mapWidth}x{mapHeight} tiles");
        
        // Phase 1: Generate visual tilemap (FAST - single draw call)
        GenerateVisualTilemap();
        
        // Phase 2: Create logic objects only where needed (SELECTIVE)
        if (enableTileLogic)
        {
            GenerateLogicTiles();
        }
        
        Debug.Log("=== HYBRID MAP GENERATION COMPLETE ===");
        Debug.Log($"Visual tiles: {mapWidth * mapHeight} (rendered as single tilemap)");
        Debug.Log($"Logic objects: {logicTileObjects.Count} (only where needed)");
        Debug.Log($"Performance: ~{((float)logicTileObjects.Count / (mapWidth * mapHeight) * 100):F1}% of tiles have GameObjects");
    }
    
    void GenerateVisualTilemap()
    {
        // Prepare arrays for bulk tilemap operation (much faster than individual SetTile calls)
        TileBase[] tilesToPlace = new TileBase[mapWidth * mapHeight];
        Dictionary<string, int> tileStats = new Dictionary<string, int>();
        
        int index = 0;
        for (int x = 0; x < mapWidth; x++)
        {
            for (int y = 0; y < mapHeight; y++)
            {
                Color pixelColor = mapImage.GetPixel(x, y);
                TileBase tileAsset = GetTileAssetForColor(pixelColor);
                TerrainType terrainType = GetTerrainTypeFromTileAsset(tileAsset);
                
                // Store visual tile for bulk placement
                tilesToPlace[index] = tileAsset;
                
                // Create comprehensive tile data (THIS IS THE FLEXIBILITY!)
                tileDataGrid[x, y] = new TileData
                {
                    position = new Vector3Int(x, y, 0),
                    terrainType = terrainType,
                    tileAsset = tileAsset,
                    needsLogicObject = TileNeedsLogic(tileAsset?.name),
                    // Set gameplay properties based on terrain
                    movementCost = GetMovementCostForTerrain(terrainType),
                    defenseBonus = GetDefenseBonusForTerrain(terrainType),
                    isPassable = GetPassabilityForTerrain(terrainType)
                };
                
                // Track statistics
                string tileName = tileAsset?.name ?? "Unknown";
                tileStats[tileName] = tileStats.GetValueOrDefault(tileName, 0) + 1;
                
                index++;
            }
        }
        
        // Set ALL tiles at once - this is the performance magic!
        tilemap.SetTilesBlock(new BoundsInt(0, 0, 0, mapWidth, mapHeight, 1), tilesToPlace);
        
        // Print tile statistics
        Debug.Log("Visual tilemap generation complete:");
        foreach (var kvp in tileStats)
        {
            float percentage = (kvp.Value / (float)(mapWidth * mapHeight)) * 100f;
            Debug.Log($"  - {kvp.Key}: {kvp.Value} tiles ({percentage:F1}%)");
        }
    }
    
    void GenerateLogicTiles()
    {
        int logicTilesCreated = 0;
        
        for (int x = 0; x < mapWidth; x++)
        {
            for (int y = 0; y < mapHeight; y++)
            {
                TileData tileData = tileDataGrid[x, y];
                
                // Only create GameObjects for tiles that actually need complex logic
                if (tileData.needsLogicObject)
                {
                    CreateLogicTileObject(x, y, tileData);
                    logicTilesCreated++;
                }
                
                // For tiles that DON'T need GameObjects, all their data is still
                // stored in tileDataGrid - so you still have full access!
            }
        }
        
        Debug.Log($"Logic tile generation complete:");
        Debug.Log($"  - Created {logicTilesCreated} logic GameObjects");
        Debug.Log($"  - {mapWidth * mapHeight - logicTilesCreated} tiles use data-only (efficient!)");
        Debug.Log($"  - Memory saved: ~{((mapWidth * mapHeight - logicTilesCreated) * 500):N0} bytes from avoided GameObjects");
    }
    
    void CreateLogicTileObject(int x, int y, TileData tileData)
    {
        // Get appropriate logic prefab
        GameObject logicPrefab = GetLogicPrefabForTerrain(tileData.terrainType);
        if (logicPrefab == null)
        {
            // Create simple logic object if no specific prefab
            logicPrefab = new GameObject();
        }
        
        Vector3 worldPos = tilemap.CellToWorld(new Vector3Int(x, y, 0));
        GameObject logicObj = logicPrefab == null ? new GameObject() : Instantiate(logicPrefab, worldPos, Quaternion.identity);
        
        logicObj.name = $"{tileData.terrainType}_Logic_{x}_{y}";
        logicObj.transform.SetParent(transform);
        
        // Add or get logic component
        TileLogic tileLogic = logicObj.GetComponent<TileLogic>();
        if (tileLogic == null)
        {
            tileLogic = logicObj.AddComponent<TileLogic>();
        }
        
        // Initialize with our tile data - this connects the systems!
        tileLogic.Initialize(tileData, this);
        logicTileObjects[new Vector3Int(x, y, 0)] = logicObj;
    }
    
    // Determine which tiles need GameObject logic
    bool TileNeedsLogic(string tileName)
    {
        if (string.IsNullOrEmpty(tileName)) return false;
        
        // Check if tile type is in our "needs logic" list
        foreach (string logicTileName in tilesNeedingLogic)
        {
            if (tileName.Contains(logicTileName))
            {
                return true;
            }
        }
        
        // You can add more complex logic here
        // For example: return true for tiles with special properties
        return false;
    }
    
    GameObject GetLogicPrefabForTerrain(TerrainType terrain)
    {
        // Return appropriate prefab based on terrain type
        // This is where you'd specify which prefabs to use for different terrains
        if (logicTilePrefabs != null && logicTilePrefabs.Length > 0)
        {
            return logicTilePrefabs[0]; // Default for now - you can expand this
        }
        return null;
    }
    
    // Terrain property helpers
    int GetMovementCostForTerrain(TerrainType terrain)
    {
        return terrain switch
        {
            TerrainType.Grass => 1,
            TerrainType.Hills => 2,
            TerrainType.Mountains => 999, // Impassable
            TerrainType.ShallowWater => 2,
            TerrainType.DeepWater => 999, // Impassable
            _ => 1
        };
    }
    
    float GetDefenseBonusForTerrain(TerrainType terrain)
    {
        return terrain switch
        {
            TerrainType.Grass => 1.0f,
            TerrainType.Hills => 1.3f,
            TerrainType.Mountains => 1.5f,
            TerrainType.ShallowWater => 0.8f,
            TerrainType.DeepWater => 1.0f,
            _ => 1.0f
        };
    }
    
    bool GetPassabilityForTerrain(TerrainType terrain)
    {
        return terrain switch
        {
            TerrainType.Mountains => false,
            TerrainType.DeepWater => false,
            _ => true
        };
    }
    
    TileBase GetTileAssetForColor(Color targetColor)
    {
        // Try exact match first
        if (colorToTileMapping.ContainsKey(targetColor))
        {
            return colorToTileMapping[targetColor];
        }
        
        // Fallback to closest color match
        float closestDistance = float.MaxValue;
        TileBase closestTile = null;
        
        foreach (var kvp in colorToTileMapping)
        {
            float distance = Mathf.Abs(targetColor.r - kvp.Key.r) +
                           Mathf.Abs(targetColor.g - kvp.Key.g) +
                           Mathf.Abs(targetColor.b - kvp.Key.b);
            
            if (distance < closestDistance)
            {
                closestDistance = distance;
                closestTile = kvp.Value;
            }
        }
        
        return closestTile;
    }
    
    TerrainType GetTerrainTypeFromTileAsset(TileBase tileAsset)
    {
        if (tileAsset == null) return TerrainType.Grass;
        
        string tileName = tileAsset.name.ToLower();
        
        if (tileName.Contains("grass")) return TerrainType.Grass;
        if (tileName.Contains("hill")) return TerrainType.Hills;
        if (tileName.Contains("mountain")) return TerrainType.Mountains;
        if (tileName.Contains("deepwater")) return TerrainType.DeepWater;
        if (tileName.Contains("shallowwater")) return TerrainType.ShallowWater;
        
        return TerrainType.Grass; // Default
    }
    
    // PUBLIC INTERFACE - This is what your GameState and other scripts will use
    
    /// <summary>
    /// Get complete tile data - works for ALL tiles (with or without GameObjects)
    /// This addresses your brother's flexibility concerns!
    /// </summary>
    public TileData GetTileData(int x, int y)
    {
        if (x >= 0 && x < mapWidth && y >= 0 && y < mapHeight)
        {
            return tileDataGrid[x, y];
        }
        return null;
    }
    
    public TileData GetTileData(Vector3Int position)
    {
        return GetTileData(position.x, position.y);
    }
    
    /// <summary>
    /// Get logic GameObject (only exists for special tiles)
    /// </summary>
    public GameObject GetLogicObject(int x, int y)
    {
        Vector3Int pos = new Vector3Int(x, y, 0);
        return logicTileObjects.GetValueOrDefault(pos, null);
    }
    
    /// <summary>
    /// Modify tile at runtime - THIS IS THE FLEXIBILITY YOUR BROTHER WANTED!
    /// </summary>
    public void ModifyTileAtRuntime(int x, int y, TileBase newTileAsset, TerrainType newTerrain)
    {
        Vector3Int position = new Vector3Int(x, y, 0);
        
        // Update visual tilemap (fast!)
        tilemap.SetTile(position, newTileAsset);
        
        // Update data (flexible!)
        TileData tileData = tileDataGrid[x, y];
        if (tileData != null)
        {
            tileData.terrainType = newTerrain;
            tileData.tileAsset = newTileAsset;
            tileData.movementCost = GetMovementCostForTerrain(newTerrain);
            tileData.defenseBonus = GetDefenseBonusForTerrain(newTerrain);
            tileData.isPassable = GetPassabilityForTerrain(newTerrain);
        }
        
        // Update logic object if it exists
        if (logicTileObjects.ContainsKey(position))
        {
            GameObject logicObj = logicTileObjects[position];
            TileLogic tileLogic = logicObj.GetComponent<TileLogic>();
            // Call the UpdateTerrain method directly (not through Unity's message system)
            tileLogic?.UpdateTerrain(newTerrain);
        }
        
        Debug.Log($"HybridMap: Modified tile at ({x},{y}) to {newTerrain} - Easy runtime changes!");
    }
    
    /// <summary>
    /// Add custom property to any tile (even without GameObjects!)
    /// </summary>
    public void SetTileProperty(int x, int y, string key, object value)
    {
        TileData tileData = GetTileData(x, y);
        if (tileData != null)
        {
            tileData.SetCustomProperty(key, value);
        }
    }
    
    public T GetTileProperty<T>(int x, int y, string key)
    {
        TileData tileData = GetTileData(x, y);
        return tileData != null ? tileData.GetCustomProperty<T>(key) : default(T);
    }
    
    // Coordinate conversion methods
    public Vector3Int WorldToTilePosition(Vector3 worldPosition)
    {
        return tilemap.WorldToCell(worldPosition);
    }
    
    public Vector3 TileToWorldPosition(Vector3Int tilePosition)
    {
        return tilemap.CellToWorld(tilePosition);
    }
    
    public bool IsValidTilePosition(Vector3Int tilePosition)
    {
        return tilePosition.x >= 0 && tilePosition.x < mapWidth &&
               tilePosition.y >= 0 && tilePosition.y < mapHeight;
    }
    
    public Vector3Int GetTileUnderMouse()
    {
        if (mainCamera == null) return Vector3Int.zero;
        
        Vector3 mouseWorldPos = mainCamera.ScreenToWorldPoint(Input.mousePosition);
        Vector3Int tilePos = WorldToTilePosition(mouseWorldPos);
        
        return IsValidTilePosition(tilePos) ? tilePos : Vector3Int.zero;
    }
    
    // Unit management
    public void SetUnitOnTile(Vector3Int tilePosition, Unit unit)
    {
        if (IsValidTilePosition(tilePosition))
        {
            unitPositions[tilePosition] = unit;
            
            // Also update tile data
            TileData tileData = GetTileData(tilePosition);
            if (tileData != null)
            {
                tileData.occupyingUnit = unit;
            }
        }
    }
    
    public Unit GetUnitOnTile(Vector3Int tilePosition)
    {
        return unitPositions.GetValueOrDefault(tilePosition, null);
    }
    
    public void RemoveUnitFromTile(Vector3Int tilePosition)
    {
        unitPositions.Remove(tilePosition);
        
        // Also update tile data
        TileData tileData = GetTileData(tilePosition);
        if (tileData != null)
        {
            tileData.occupyingUnit = null;
        }
    }
    
    void Update()
    {
        HandleMouseInteraction();
    }
    
    void HandleMouseInteraction()
    {
        Vector3Int currentTile = GetTileUnderMouse();
        
        if (currentTile != lastHoveredTile)
        {
            // Tile hover changed - you can add UI updates here
            lastHoveredTile = currentTile;
            
            // Example: You could highlight tiles, show tile info, etc.
            // But without creating/destroying GameObjects!
        }
    }
}





