using System;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;

public class Map : MonoBehaviour
{
    public Vector2 tileSize;
   
    public TextAsset mappingFile;//txt file containing the mappings between tiles and the colours they are represented by in the map image
    public Texture2D mapimg;//the map image - each pixel corresponds to a tile to be generated
    public Texture2D initUnitImg;//defines the initial position of units

    //vectors containing the extremes of the map in map space
    public int mapWidth;
    public int mapHeight;

    //vectors containing the top right and bottom left extremes of the map in world space
    public Vector2 mapMaxDim;
    public Vector2 mapMinDim;

    private Dictionary<Color, GameObject> colorToTilePrefabMapping;//dictionary mapping colours to tile prefabs (used for map loading and other things)
    private GameObject[,] tileMap;
    private Camera mainCamera;
    
    // Smart color classification system for PNG images with anti-aliasing and compression
    private GameObject FindTileForColor(Color targetColor, Dictionary<Color, GameObject> tileMapping)
    {
        // First try exact match (for perfect pixel art)
        if (tileMapping.ContainsKey(targetColor))
        {
            return tileMapping[targetColor];
        }
        
        // Use HSV-based color range classification for robust matching
        GameObject bestMatch = ClassifyColorByRange(targetColor, tileMapping);
        if (bestMatch != null)
        {
            return bestMatch;
        }
        
        // Fallback to distance-based matching with large tolerance
        float tolerance = 0.5f; // Very large tolerance for edge cases
        GameObject closestMatch = null;
        float closestDistance = float.MaxValue;
        
        foreach (var kvp in tileMapping)
        {
            Color keyColor = kvp.Key;
            float distance = Mathf.Abs(targetColor.r - keyColor.r) + 
                           Mathf.Abs(targetColor.g - keyColor.g) + 
                           Mathf.Abs(targetColor.b - keyColor.b);
            
            if (distance < closestDistance)
            {
                closestDistance = distance;
                closestMatch = kvp.Value;
            }
        }
        
        if (closestDistance < tolerance)
        {
            Debug.Log($"Fallback color match: Target({targetColor.r:F3},{targetColor.g:F3},{targetColor.b:F3}) Distance={closestDistance:F4}");
            return closestMatch;
        }
        
        // No match found
        Debug.LogWarning($"No tile found for color: {targetColor}");
        Debug.LogWarning($"Available colors in mapping: {string.Join(", ", tileMapping.Keys.Select(c => $"RGB({c.r:F3},{c.g:F3},{c.b:F3})"))}");
        return null;
    }
    
    // Classify colors by HSV ranges - much more robust for real images
    private GameObject ClassifyColorByRange(Color targetColor, Dictionary<Color, GameObject> tileMapping)
    {
        Color.RGBToHSV(targetColor, out float h, out float s, out float v);
        
        // Convert hue to degrees for easier understanding
        float hue = h * 360f;
        
        Debug.Log($"Classifying color RGB({targetColor.r:F3},{targetColor.g:F3},{targetColor.b:F3}) -> HSV({hue:F1}°, {s:F2}, {v:F2})");
        
        // Water classification (blues)
        if (IsBlueish(hue, s, v))
        {
            // Dark blue = Deep water, Light blue = Shallow water
            if (v < 0.4f || (s > 0.7f && v < 0.7f)) // Dark or saturated blue
            {
                GameObject deepWater = FindTileByName(tileMapping, "DeepWaterTile");
                if (deepWater != null)
                {
                    Debug.Log($"Classified as DeepWater: HSV({hue:F1}°, {s:F2}, {v:F2})");
                    return deepWater;
                }
            }
            else // Light blue
            {
                GameObject shallowWater = FindTileByName(tileMapping, "ShallowWaterTile");
                if (shallowWater != null)
                {
                    Debug.Log($"Classified as ShallowWater: HSV({hue:F1}°, {s:F2}, {v:F2})");
                    return shallowWater;
                }
            }
        }
        
        // Green classification (grass)
        if (IsGreenish(hue, s, v))
        {
            GameObject grass = FindTileByName(tileMapping, "GrassTile");
            if (grass != null)
            {
                Debug.Log($"Classified as Grass: HSV({hue:F1}°, {s:F2}, {v:F2})");
                return grass;
            }
        }
        
        // Brown classification (hills/mountains)
        if (IsBrownish(hue, s, v))
        {
            // Darker brown = mountains, lighter = hills
            if (v < 0.4f)
            {
                GameObject mountains = FindTileByName(tileMapping, "MountainsTile");
                if (mountains != null)
                {
                    Debug.Log($"Classified as Mountains: HSV({hue:F1}°, {s:F2}, {v:F2})");
                    return mountains;
                }
            }
            else
            {
                GameObject hills = FindTileByName(tileMapping, "HillsTile");
                if (hills != null)
                {
                    Debug.Log($"Classified as Hills: HSV({hue:F1}°, {s:F2}, {v:F2})");
                    return hills;
                }
            }
        }
        
        // Black/very dark = Error tile
        if (v < 0.1f)
        {
            GameObject error = FindTileByName(tileMapping, "ErrorTile");
            if (error != null)
            {
                Debug.Log($"Classified as Error: HSV({hue:F1}°, {s:F2}, {v:F2})");
                return error;
            }
        }
        
        return null; // No classification found
    }
    
    // Helper functions for color range detection
    private bool IsBlueish(float hue, float saturation, float value)
    {
        // Blue hue range: 180-270 degrees, with some tolerance
        return (hue >= 160f && hue <= 280f) && saturation > 0.2f && value > 0.1f;
    }
    
    private bool IsGreenish(float hue, float saturation, float value)
    {
        // Green hue range: 60-160 degrees
        return (hue >= 60f && hue <= 160f) && saturation > 0.2f && value > 0.1f;
    }
    
    private bool IsBrownish(float hue, float saturation, float value)
    {
        // Brown/orange hue range: 10-60 degrees
        return (hue >= 10f && hue <= 60f) && saturation > 0.2f && value > 0.1f;
    }
    
    private GameObject FindTileByName(Dictionary<Color, GameObject> tileMapping, string tileName)
    {
        foreach (var kvp in tileMapping)
        {
            if (kvp.Value != null && kvp.Value.name.Contains(tileName))
            {
                return kvp.Value;
            }
        }
        return null;
    }

    Tile tileUnderMouse = null;
    Tile previousTileUnderMouse = null;

    //can reuse for units
    private Dictionary<Color, GameObject> parseMappingFromTxt(TextAsset txtFile)
    {
        //takes the tile to colour mapping txt,
        //loads the gameobjects named, and returns a dictionary of colours to tile prefabs

        //read string from txt - and split by line into an array (getting mappings)
        string txt = txtFile.text;
        // Handle different line endings (Windows \r\n, Unix \n, Mac \r)
        string[] mappings = txt.Split(new char[] { '\n', '\r' }, System.StringSplitOptions.RemoveEmptyEntries);

        Dictionary<Color, GameObject> colorToPrefabMapping = new Dictionary<Color, GameObject>();

        Debug.Log($"Parsing {mappings.Length} tile mappings from text file");
        Debug.Log($"Map image dimensions: {mapimg.width}x{mapimg.height} = {mapimg.width * mapimg.height} pixels");
        
        //for each mapping ....
        for (int i=0;i<mappings.Length;i++)
        {
            // Clean the line and skip if empty
            string line = mappings[i].Trim();
            if (string.IsNullOrWhiteSpace(line)) continue;
            
            // Skip lines that don't contain proper format (should have commas for CSV format)
            if (!line.Contains(",")) 
            {
                Debug.LogWarning($"Skipping malformed line: '{line}'");
                continue;
            }
            
            //split the line by commas: TileName,R,G,B
            string[] parts = line.Split(",");
            if (parts.Length < 4) continue; // Skip malformed lines (need tileName + 3 RGB values)
            
            string tileName = parts[0];

            //load the tileprefab from the assets
            GameObject tilePrefab = (GameObject)Resources.Load("GameObjects/Tiles/" + tileName + "/" + tileName);
            
            if (tilePrefab == null)
            {
                Debug.LogError($"Could not load tile prefab: {tileName} from path: Resources/GameObjects/Tiles/{tileName}/{tileName}");
                continue; // Skip this tile entirely
            }

            // RGB values are parts[1], parts[2], parts[3]
            string[] tileColourRGB = new string[] { parts[1], parts[2], parts[3] };
            if (tileColourRGB.Length < 3) 
            {
                Debug.LogWarning($"Invalid color data for {tileName}: {parts[1]}");
                continue; // Skip if not enough color values
            }
            
            //parse a colour from the rgb part of the mapping
            float.TryParse(tileColourRGB[0], out float r);
            float.TryParse(tileColourRGB[1], out float g);
            float.TryParse(tileColourRGB[2], out float b);
            Color tileColour = new Color(r / 255f, g / 255f, b / 255f);

            // Only add to dictionary if prefab is valid
            if (tilePrefab != null)
            {
                colorToPrefabMapping.Add(tileColour, tilePrefab);
                Debug.Log($"Loaded tile: {tileName} with color RGB({r},{g},{b}) = Unity({tileColour.r:F3},{tileColour.g:F3},{tileColour.b:F3})");
            }
        }
        
        Debug.Log($"Successfully loaded {colorToPrefabMapping.Count} tile types:");
        foreach (var kvp in colorToPrefabMapping)
        {
            Color c = kvp.Key;
            if (kvp.Value != null)
            {
                Debug.Log($"  - {kvp.Value.name}: RGB({c.r * 255:F0},{c.g * 255:F0},{c.b * 255:F0})");
            }
            else
            {
                Debug.LogError($"  - NULL PREFAB: RGB({c.r * 255:F0},{c.g * 255:F0},{c.b * 255:F0})");
            }
        }
        
        return colorToPrefabMapping;
    }

    //refactor generalise otherwise good - will need to define awake for units
    private GameObject[,] generateMapFromImg(Texture2D img,Dictionary<Color,GameObject> tileMapping)
    {
        GameObject[,] tiles = new GameObject[img.width,img.height];
        GameObject tile = null;
        
        // Track tile type statistics
        Dictionary<string, int> tileTypeCount = new Dictionary<string, int>();
        
        //takes an img and a tile to colour mapping, then spawns the correct tiles in and stores them in Tiles
        for(int x=0;x<img.width;x++)
        {
            for(int  y=0;y<img.height;y++)
            {
                Color pixelColor = img.GetPixel(x,y);
                
                // Use robust color matching
                tile = FindTileForColor(pixelColor, tileMapping);
                
                if (tile != null)
                {
                    tile.name = tile.name; // Keep original prefab name
                }
                else
                {
                    // Fallback to ErrorTile
                    Color errorColor = new Color(1/255f, 1/255f, 1/255f);
                    tile = FindTileForColor(errorColor, tileMapping);
                    
                    if (tile != null)
                    {
                        tile.name = $"Error_{x}_{y}";
                        Debug.LogWarning($"Using ErrorTile for unknown color at ({x},{y}): RGB({pixelColor.r:F3},{pixelColor.g:F3},{pixelColor.b:F3})");
                    }
                    else
                    {
                        Debug.LogError($"No ErrorTile available! Skipping pixel at ({x},{y})");
                        continue; // Skip this tile
                    }
                }

                tile = Instantiate(tile);
                tile.GetComponent<Transform>().position = mapToWorldPoint(new Vector2(x,y));
                tile.name += " - " + x.ToString() + " ," + y.ToString();
                
                // Track tile type statistics
                string tileType = tile.name.Split(' ')[0];
                if (tileTypeCount.ContainsKey(tileType))
                    tileTypeCount[tileType]++;
                else
                    tileTypeCount[tileType] = 1;
                
                // Initialize tile with coordinates and type
                Tile tileComponent = tile.GetComponent<Tile>();
                if (tileComponent != null)
                {
                    tileComponent.Initialize(x, y, tileType);
                }
                
                tiles[x,y] = tile; 
            }
        }
        
        // Print tile type statistics
        Debug.Log("=== MAP GENERATION COMPLETE ===");
        Debug.Log($"Generated {img.width}x{img.height} = {img.width * img.height} tiles");
        Debug.Log("Tile type breakdown:");
        foreach (var kvp in tileTypeCount)
        {
            float percentage = (kvp.Value / (float)(img.width * img.height)) * 100f;
            Debug.Log($"  - {kvp.Key}: {kvp.Value} tiles ({percentage:F1}%)");
        }
        Debug.Log("===============================");
        
        return tiles;
    }

    public Vector2 worldToMapPoint(Vector2 coords)
    {
        int x = (int)(coords.x / tileSize.x + 0.5);
        int y = 0;
        if (x % 2 == 1)
        {
            y = (int)(coords.y / tileSize.y );
        }
        else
        {
            y = (int)(coords.y / tileSize.y + 0.5f);
        }

        
        //force result w/in map dimensions
        if(x>mapWidth-1)
        {
            x = mapWidth-1;
        }
        else if (x < 0)
        {
            x = 0;
        }

        if (y >mapHeight -1) 
        {
            y = mapHeight-1; 
        } 
        else if(y<0)
        {
            y = 0; 
        }

        return new Vector2(x, y);

    }

    public Vector2 mapToWorldPoint(Vector2 coords){
        if ((int)coords.x % 2 == 1){
            return new Vector2((int)coords.x * tileSize.x, ((int)coords.y +0.5f)* tileSize.y);
        }else{  
            return new Vector2((int)coords.x * tileSize.x, (int)coords.y * tileSize.y);
        }
    }

    public GameObject getTileUnderMouse()
    {
        // Safety checks
        if (mainCamera == null || tileMap == null) return null;
        
        Vector2 mousepos = mainCamera.ScreenToWorldPoint(Input.mousePosition);
        Vector2 tileCoords = worldToMapPoint(mousepos);
        
        // Check bounds
        int x = (int)tileCoords.x;
        int y = (int)tileCoords.y;
        
        if (x >= 0 && x < mapWidth && y >= 0 && y < mapHeight)
        {
            return tileMap[x, y];
        }
        
        return null; // Mouse outside map bounds
    }
    
    // Public method to get tile at coordinates
    public Tile GetTileAt(int x, int y)
    {
        if (x >= 0 && x < mapWidth && y >= 0 && y < mapHeight)
        {
            GameObject tileObj = tileMap[x, y];
            return tileObj?.GetComponent<Tile>();
        }
        return null;
    }
    
    // Get neighboring tiles (for pathfinding, range calculations)
    public List<Tile> GetNeighboringTiles(int x, int y)
    {
        List<Tile> neighbors = new List<Tile>();
        
        // Hex grid neighbors (offset coordinates)
        Vector2[] neighborOffsets;
        
        if (x % 2 == 0) // Even column
        {
            neighborOffsets = new Vector2[]
            {
                new Vector2(0, 1),   // North
                new Vector2(1, 0),   // Northeast
                new Vector2(1, -1),  // Southeast
                new Vector2(0, -1),  // South
                new Vector2(-1, -1), // Southwest
                new Vector2(-1, 0)   // Northwest
            };
        }
        else // Odd column
        {
            neighborOffsets = new Vector2[]
            {
                new Vector2(0, 1),   // North
                new Vector2(1, 1),   // Northeast
                new Vector2(1, 0),   // Southeast
                new Vector2(0, -1),  // South
                new Vector2(-1, 0),  // Southwest
                new Vector2(-1, 1)   // Northwest
            };
        }
        
        foreach (Vector2 offset in neighborOffsets)
        {
            int newX = x + (int)offset.x;
            int newY = y + (int)offset.y;
            
            Tile neighbor = GetTileAt(newX, newY);
            if (neighbor != null)
            {
                neighbors.Add(neighbor);
            }
        }
        
        return neighbors;
    }


    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {

        mainCamera = Camera.main;//find the main camera

        //set max and min map dimensions 
        mapMinDim = Vector2.zero;
        mapMaxDim = mapToWorldPoint(new Vector2(mapimg.width-1, mapimg.height-1));

        mapWidth=mapimg.width;  
        mapHeight=mapimg.height;

        //read and parse the tile to colour mapping
        colorToTilePrefabMapping = parseMappingFromTxt(mappingFile);

        //generate the map from mapimg
        tileMap = generateMapFromImg(mapimg, colorToTilePrefabMapping);
        //print(tileMap.GetLength(0).ToString() + " " + tileMap.GetLength(1).ToString());
}

    void OnMouseOverNewTile()
    {

    }
    
    void OnNewTurn()
    {

    }

    void OnNextTurn()
    {
      
    }


    // Update is called once per frame
    void Update()
    {
        // Safety check - only update if map is generated
        if (tileMap == null) return;
           
        GameObject tileObj = getTileUnderMouse();
        tileUnderMouse = tileObj?.GetComponent<Tile>(); // Safe null check
        

        if (tileUnderMouse != previousTileUnderMouse)
        {
            // Highlight new tile
            if (tileUnderMouse != null)
            {
                tileUnderMouse.changeTileTexture(1); // Highlight current tile
            }
            
            // Unhighlight previous tile
            if (previousTileUnderMouse != null)
            {  
                previousTileUnderMouse.changeTileTexture(0); // Back to normal
            }
        }

        //if mousebutton down and unit mouseovered != null
            //unit selected = true - move to new mouseover logic
            //changeallothertiles to hashed 
            //on newtilemouseover set tile to selected 
            //and call unit pathfind function returning a 2d array of tiles
            //change tile textures accordingly (will need to create new textures)
            //on next click start unit moving


            

        previousTileUnderMouse = tileUnderMouse;

    }
   
}
