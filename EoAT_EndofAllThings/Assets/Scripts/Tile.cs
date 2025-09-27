using UnityEngine;



public class Tile : MonoBehaviour
{
    [Header("Tile Visuals")]
    public Sprite baseTexture;
    public Sprite selectedTexture;
    public Sprite shadedTexture;
    
    [Header("Tile Properties")]
    public Color colorCode;
    public string type;
    public bool isPassable = true;
    public float defenseBonus = 1.0f; // 1.0 = normal, 1.5 = defensive terrain
    public int movementCost = 1; // How many movement points to enter
    
    [Header("Tile Coordinates")]
    public int tileX;
    public int tileY;
    
    // Unit on this tile
    private Unit unitOnTile = null;
    private SpriteRenderer spriteRenderer;
    public void changeTileTexture(int textureCode)
    {
        //changes the tiles texture (sprite) according to the texture code and in the case of selectedTexture - move it towards the camera to make it "pop"

        //0-base,1-selected,2-shaded
        if (textureCode == 0)
        {
            spriteRenderer.sprite = baseTexture;
            transform.position = new Vector3(transform.position.x, transform.position.y, 0);
        }
        else if (textureCode == 1)
        {
            spriteRenderer.sprite = selectedTexture;
            transform.position = new Vector3(transform.position.x, transform.position.y,- 1);
        }else if(textureCode == 2)
        {
            spriteRenderer.sprite = shadedTexture;
            transform.position = new Vector3(transform.position.x, transform.position.y, 0);
        }
        else
        {
            Debug.LogError("Unrecognised texture code: " + textureCode.ToString());
        }
        
    }

    void Start() {
        spriteRenderer = gameObject.GetComponent<SpriteRenderer>();
    }
    
    // Unit management methods
    public void SetUnit(Unit unit)
    {
        unitOnTile = unit;
    }
    
    public Unit GetUnit()
    {
        return unitOnTile;
    }
    
    public bool HasUnit()
    {
        return unitOnTile != null;
    }
    
    // Tile property getters
    public bool IsPassable()
    {
        return isPassable && !HasUnit(); // Can't move to occupied tiles
    }
    
    public float GetDefenseBonus()
    {
        return defenseBonus;
    }
    
    public int GetMovementCost()
    {
        return movementCost;
    }
    
    public int GetX() => tileX;
    public int GetY() => tileY;
    
    // Mouse interaction for tile selection
    void OnMouseDown()
    {
        GameState gameState = FindFirstObjectByType<GameState>();
        if (gameState != null)
        {
            gameState.SelectTile(this);
        }
    }
    
    // Initialize tile coordinates (called by Map when creating tiles)
    public void Initialize(int x, int y, string tileType)
    {
        tileX = x;
        tileY = y;
        type = tileType;
        
        // Set tile properties based on type
        switch (tileType)
        {
            case "GrassTile":
                isPassable = true;
                defenseBonus = 1.0f;
                movementCost = 1;
                break;
                
            case "HillsTile":
                isPassable = true;
                defenseBonus = 1.3f; // Defensive bonus
                movementCost = 2; // Harder to move through
                break;
                
            case "MountainsTile":
                isPassable = false; // Impassable
                defenseBonus = 2.0f;
                movementCost = 999;
                break;
                
            case "DeepWaterTile":
                isPassable = false; // Most units can't cross
                defenseBonus = 1.0f;
                movementCost = 999;
                break;
                
            case "ShallowWaterTile":
                isPassable = true;
                defenseBonus = 0.8f; // Penalty for being in water
                movementCost = 2;
                break;
                
            default:
                isPassable = true;
                defenseBonus = 1.0f;
                movementCost = 1;
                break;
        }
    }
}
