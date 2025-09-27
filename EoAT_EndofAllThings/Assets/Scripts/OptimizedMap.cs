using UnityEngine;
using UnityEngine.Tilemaps;
using System.Collections.Generic;

/// <summary>
/// Optimized map system using Unity's Tilemap instead of individual GameObjects
/// This replaces the current Map.cs approach for much better performance
/// </summary>
public class OptimizedMap : MonoBehaviour
{
    [Header("Tilemap Components")]
    [Tooltip("The main tilemap - drag from scene")]
    public Tilemap tilemap;
    
    [Tooltip("Tilemap renderer component")]
    public TilemapRenderer tilemapRenderer;
    
    [Tooltip("Tilemap collider for mouse interaction")]
    public TilemapCollider2D tilemapCollider;
    
    [Header("Map Generation")]
    [Tooltip("PNG image to convert to map")]
    public Texture2D mapImage;
    
    [Tooltip("Text file mapping colors to tile types")]
    public TextAsset mappingFile;
    
    [Header("Tile Assets")]
    [Tooltip("Tile assets (ScriptableObjects) for each terrain type")]
    public TileBase[] tileAssets;
    
    [Tooltip("Names corresponding to tile assets (must match mapping file)")]
    public string[] tileAssetNames;
    
    [Header("Settings")]
    public Vector2 tileSize = new Vector2(1f, 0.866f); // Hex tile size
    
    // Internal data
    private Dictionary<Color, TileBase> colorToTileMapping;
    private Dictionary<Vector3Int, TerrainType> tileTerrainTypes;
    private Dictionary<Vector3Int, Unit> tileUnits; // Track units on tiles
    
    // Map bounds
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
        InitializeTilemapSystem();
        GenerateOptimizedMap();
    }
    
    void InitializeTilemapSystem()
    {
        // Create tilemap GameObject if not assigned
        if (tilemap == null)
        {
            CreateTilemapGameObject();
        }
        
        // Initialize data structures
        colorToTileMapping = new Dictionary<Color, TileBase>();
        tileTerrainTypes = new Dictionary<Vector3Int, TerrainType>();
        tileUnits = new Dictionary<Vector3Int, Unit>();
        
        // Parse mapping file and build dictionary
        BuildColorToTileMapping();
        
        Debug.Log($"OptimizedMap initialized with {tileAssets.Length} tile types");
    }
    
    void CreateTilemapGameObject()
    {
        // Create tilemap structure
        GameObject tilemapObj = new GameObject("Tilemap");
        tilemapObj.transform.SetParent(transform);
        
        // Add required components
        tilemap = tilemapObj.AddComponent<Tilemap>();
        tilemapRenderer = tilemapObj.AddComponent<TilemapRenderer>();
        tilemapCollider = tilemapObj.AddComponent<TilemapCollider2D>();
        
        // Configure tilemap renderer
        tilemapRenderer.sortingLayerName = "Default";
        tilemapRenderer.sortingOrder = 0;
        
        Debug.Log("Created tilemap GameObject automatically");
    }
    
    void BuildColorToTileMapping()
    {
        if (mappingFile == null || tileAssets == null)
        {
            Debug.LogError("Missing mapping file or tile assets!");
            return;
        }
        
        string[] lines = mappingFile.text.Split('\n');
        
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
                    Debug.Log($"Mapped {tileName} to color RGB({r},{g},{b})");
                }
                else
                {
                    Debug.LogWarning($"No tile asset found for {tileName}");
                }
            }
        }
        
        Debug.Log($"Built color mapping with {colorToTileMapping.Count} entries");
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
    
    void GenerateOptimizedMap()
    {
        if (mapImage == null)
        {
            Debug.LogError("No map image assigned!");
            return;
        }
        
        mapWidth = mapImage.width;
        mapHeight = mapImage.height;
        
        // Calculate world bounds
        mapMinDim = Vector2.zero;
        mapMaxDim = new Vector2(mapWidth * tileSize.x, mapHeight * tileSize.y);
        
        Debug.Log($"Generating optimized map: {mapWidth}x{mapHeight} = {mapWidth * mapHeight} tiles");
        
        // Clear existing tiles
        tilemap.CompressBounds();
        
        // Set all tiles efficiently
        TileBase[] tilesToPlace = new TileBase[mapWidth * mapHeight];
        Vector3Int[] positions = new Vector3Int[mapWidth * mapHeight];
        
        int index = 0;
        Dictionary<string, int> tileStats = new Dictionary<string, int>();
        
        for (int x = 0; x < mapWidth; x++)
        {
            for (int y = 0; y < mapHeight; y++)
            {
                Color pixelColor = mapImage.GetPixel(x, y);
                TileBase tileToPlace = GetTileForColor(pixelColor);
                TerrainType terrainType = GetTerrainTypeFromTile(tileToPlace);
                
                // Store position and tile
                positions[index] = new Vector3Int(x, y, 0);
                tilesToPlace[index] = tileToPlace;
                
                // Store terrain type for gameplay logic
                tileTerrainTypes[positions[index]] = terrainType;
                
                // Track statistics
                string tileName = tileToPlace?.name ?? "Unknown";
                tileStats[tileName] = tileStats.GetValueOrDefault(tileName, 0) + 1;
                
                index++;
            }
        }
        
        // Set all tiles at once (much faster than individual SetTile calls)
        tilemap.SetTilesBlock(new BoundsInt(0, 0, 0, mapWidth, mapHeight, 1), tilesToPlace);
        
        // Print statistics
        Debug.Log("=== OPTIMIZED MAP GENERATION COMPLETE ===");
        Debug.Log($"Generated {mapWidth}x{mapHeight} = {mapWidth * mapHeight} tiles");
        foreach (var kvp in tileStats)
        {
            float percentage = (kvp.Value / (float)(mapWidth * mapHeight)) * 100f;
            Debug.Log($"  - {kvp.Key}: {kvp.Value} tiles ({percentage:F1}%)");
        }
        Debug.Log("✅ Using single Tilemap instead of individual GameObjects!");
    }
    
    TileBase GetTileForColor(Color targetColor)
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
    
    TerrainType GetTerrainTypeFromTile(TileBase tile)
    {
        if (tile == null) return TerrainType.Grass;
        
        string tileName = tile.name.ToLower();
        
        if (tileName.Contains("grass")) return TerrainType.Grass;
        if (tileName.Contains("hill")) return TerrainType.Hills;
        if (tileName.Contains("mountain")) return TerrainType.Mountains;
        if (tileName.Contains("deepwater")) return TerrainType.DeepWater;
        if (tileName.Contains("shallowwater")) return TerrainType.ShallowWater;
        
        return TerrainType.Grass; // Default
    }
    
    // Public interface methods for gameplay systems
    public Vector3Int WorldToTilePosition(Vector3 worldPosition)
    {
        return tilemap.WorldToCell(worldPosition);
    }
    
    public Vector3 TileToWorldPosition(Vector3Int tilePosition)
    {
        return tilemap.CellToWorld(tilePosition);
    }
    
    public TerrainType GetTerrainAt(Vector3Int tilePosition)
    {
        return tileTerrainTypes.GetValueOrDefault(tilePosition, TerrainType.Grass);
    }
    
    public TerrainType GetTerrainAt(int x, int y)
    {
        return GetTerrainAt(new Vector3Int(x, y, 0));
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
    
    // Unit management on tiles
    public void SetUnitOnTile(Vector3Int tilePosition, Unit unit)
    {
        if (IsValidTilePosition(tilePosition))
        {
            tileUnits[tilePosition] = unit;
        }
    }
    
    public Unit GetUnitOnTile(Vector3Int tilePosition)
    {
        return tileUnits.GetValueOrDefault(tilePosition, null);
    }
    
    public void RemoveUnitFromTile(Vector3Int tilePosition)
    {
        tileUnits.Remove(tilePosition);
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
            // Tile hover changed - could trigger UI updates
            lastHoveredTile = currentTile;
            
            // You can add tile highlighting here if needed
            // But avoid creating/destroying GameObjects!
        }
    }
}

