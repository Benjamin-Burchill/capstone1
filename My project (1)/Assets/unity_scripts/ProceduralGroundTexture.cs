using UnityEngine;

/// <summary>
/// Creates a procedural checkered texture for the ground to make movement visible
/// Attach this to the Ground plane GameObject
/// </summary>
public class ProceduralGroundTexture : MonoBehaviour
{
    [Header("Texture Settings")]
    [Tooltip("Size of the generated texture (power of 2 recommended)")]
    public int textureSize = 512;
    
    [Tooltip("Size of each checker square in texture pixels")]
    public int checkerSize = 32;
    
    [Header("Colors")]
    [Tooltip("Light squares color")]
    public Color lightColor = new Color(0.4f, 0.7f, 0.4f, 1f); // Light green
    
    [Tooltip("Dark squares color")]
    public Color darkColor = new Color(0.2f, 0.5f, 0.2f, 1f); // Dark green
    
    [Header("Pattern Options")]
    [Tooltip("Add noise for more organic look")]
    public bool addNoise = true;
    
    [Tooltip("Strength of noise variation")]
    [Range(0f, 0.2f)]
    public float noiseStrength = 0.05f;
    
    [Tooltip("Scale of noise pattern")]
    public float noiseScale = 50f;
    
    [Header("Grid Lines")]
    [Tooltip("Add subtle grid lines")]
    public bool addGridLines = true;
    
    [Tooltip("Grid line color")]
    public Color gridColor = new Color(0.3f, 0.6f, 0.3f, 1f);
    
    [Tooltip("Grid line thickness")]
    [Range(1, 5)]
    public int gridThickness = 2;
    
    void Start()
    {
        GenerateGroundTexture();
    }
    
    [ContextMenu("Regenerate Texture")]
    public void GenerateGroundTexture()
    {
        // Create texture
        Texture2D texture = new Texture2D(textureSize, textureSize);
        texture.name = "ProceduralGroundTexture";
        
        // Generate checkered pattern
        for (int y = 0; y < textureSize; y++)
        {
            for (int x = 0; x < textureSize; x++)
            {
                // Determine if this pixel is light or dark square
                int checkX = x / checkerSize;
                int checkY = y / checkerSize;
                bool isLight = (checkX + checkY) % 2 == 0;
                
                // Base color
                Color pixelColor = isLight ? lightColor : darkColor;
                
                // Add noise for organic variation
                if (addNoise)
                {
                    float noise = Mathf.PerlinNoise(x / noiseScale, y / noiseScale);
                    float variation = (noise - 0.5f) * noiseStrength;
                    
                    pixelColor.r = Mathf.Clamp01(pixelColor.r + variation);
                    pixelColor.g = Mathf.Clamp01(pixelColor.g + variation);
                    pixelColor.b = Mathf.Clamp01(pixelColor.b + variation);
                }
                
                // Add grid lines
                if (addGridLines)
                {
                    int distToEdgeX = x % checkerSize;
                    int distToEdgeY = y % checkerSize;
                    
                    if (distToEdgeX < gridThickness || distToEdgeX >= checkerSize - gridThickness ||
                        distToEdgeY < gridThickness || distToEdgeY >= checkerSize - gridThickness)
                    {
                        pixelColor = Color.Lerp(pixelColor, gridColor, 0.3f);
                    }
                }
                
                texture.SetPixel(x, y, pixelColor);
            }
        }
        
        // Apply texture
        texture.Apply();
        
        // Create and apply material
        Material groundMaterial = new Material(Shader.Find("Universal Render Pipeline/Lit"));
        groundMaterial.mainTexture = texture;
        groundMaterial.name = "ProceduralGroundMaterial";
        
        // Set texture tiling for proper scale
        float tilingScale = 10f; // Adjust this to make squares bigger/smaller
        groundMaterial.mainTextureScale = new Vector2(tilingScale, tilingScale);
        
        // Apply to renderer
        Renderer renderer = GetComponent<Renderer>();
        if (renderer != null)
        {
            renderer.material = groundMaterial;
        }
        else
        {
            Debug.LogError("No Renderer component found on Ground object!");
        }
        
        Debug.Log($"Generated {textureSize}x{textureSize} checkered ground texture");
    }
    
    // Alternative patterns you can enable
    [ContextMenu("Generate Fractal Pattern")]
    public void GenerateFractalPattern()
    {
        Texture2D texture = new Texture2D(textureSize, textureSize);
        
        for (int y = 0; y < textureSize; y++)
        {
            for (int x = 0; x < textureSize; x++)
            {
                // Multi-octave noise for fractal pattern
                float noise1 = Mathf.PerlinNoise(x * 0.01f, y * 0.01f) * 0.5f;
                float noise2 = Mathf.PerlinNoise(x * 0.02f, y * 0.02f) * 0.25f;
                float noise3 = Mathf.PerlinNoise(x * 0.05f, y * 0.05f) * 0.125f;
                
                float totalNoise = noise1 + noise2 + noise3;
                
                Color pixelColor = Color.Lerp(darkColor, lightColor, totalNoise);
                texture.SetPixel(x, y, pixelColor);
            }
        }
        
        texture.Apply();
        
        Material groundMaterial = new Material(Shader.Find("Universal Render Pipeline/Lit"));
        groundMaterial.mainTexture = texture;
        groundMaterial.mainTextureScale = new Vector2(5f, 5f);
        
        GetComponent<Renderer>().material = groundMaterial;
        
        Debug.Log("Generated fractal ground texture");
    }
    
    [ContextMenu("Generate Grid Pattern")]
    public void GenerateGridPattern()
    {
        Texture2D texture = new Texture2D(textureSize, textureSize);
        
        for (int y = 0; y < textureSize; y++)
        {
            for (int x = 0; x < textureSize; x++)
            {
                // Create grid lines
                bool isGridLine = (x % checkerSize < gridThickness) || (y % checkerSize < gridThickness);
                
                Color pixelColor = isGridLine ? gridColor : lightColor;
                texture.SetPixel(x, y, pixelColor);
            }
        }
        
        texture.Apply();
        
        Material groundMaterial = new Material(Shader.Find("Universal Render Pipeline/Lit"));
        groundMaterial.mainTexture = texture;
        groundMaterial.mainTextureScale = new Vector2(20f, 20f);
        
        GetComponent<Renderer>().material = groundMaterial;
        
        Debug.Log("Generated grid ground texture");
    }
}
