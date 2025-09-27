using UnityEngine;

/// <summary>
/// Unit class for EoAT strategy game - represents military units on the battlefield
/// Similar to Wesnoth units with movement, combat, and turn-based mechanics
/// </summary>
public class Unit : MonoBehaviour
{
    [Header("Unit Identity")]
    [Tooltip("What type of unit this is")]
    public UnitType unitType = UnitType.Warrior;
    
    [Tooltip("Which player owns this unit")]
    public int owner = 0;
    
    [Tooltip("Unit's display name")]
    public string unitName = "Warrior";
    
    [Header("Combat Stats")]
    [Tooltip("Unit's maximum health")]
    public int maxHealth = 100;
    
    [Tooltip("Current health")]
    public int currentHealth = 100;
    
    [Tooltip("Attack power")]
    public int attackPower = 25;
    
    [Tooltip("Defense value")]
    public int defense = 10;
    
    [Header("Movement")]
    [Tooltip("How many tiles this unit can move per turn")]
    public int movementRange = 3;
    
    [Tooltip("Attack range in tiles")]
    public int attackRange = 1;
    
    [Header("Turn State")]
    [Tooltip("Has this unit moved this turn?")]
    public bool hasMoved = false;
    
    [Tooltip("Has this unit attacked this turn?")]
    public bool hasAttacked = false;
    
    [Header("Visual")]
    [Tooltip("Sprite when unit is selected")]
    public Sprite selectedSprite;
    
    [Tooltip("Sprite when unit is normal")]
    public Sprite normalSprite;
    
    // Private state
    private bool isSelected = false;
    private Tile currentTile;
    private SpriteRenderer spriteRenderer;
    private GameState gameState;
    
    // Health bar (3D text like your other project)
    private TextMesh healthDisplay;
    
    void Start()
    {
        // Get components
        spriteRenderer = GetComponent<SpriteRenderer>();
        gameState = FindFirstObjectByType<GameState>();
        
        // Set initial health
        currentHealth = maxHealth;
        
        // Create health display
        CreateHealthDisplay();
        
        // Find current tile
        UpdateCurrentTile();
        
        Debug.Log($"Unit {unitName} initialized - Owner: Player {owner + 1}");
    }
    
    void CreateHealthDisplay()
    {
        // Create 3D text for health display (like your RPG project)
        GameObject healthObj = new GameObject($"{unitName}_Health");
        healthObj.transform.SetParent(transform);
        healthObj.transform.localPosition = new Vector3(0, 1f, -1); // Above unit, in front
        
        healthDisplay = healthObj.AddComponent<TextMesh>();
        healthDisplay.text = $"{currentHealth}/{maxHealth}";
        healthDisplay.fontSize = 20;
        healthDisplay.color = GetPlayerColor();
        healthDisplay.anchor = TextAnchor.MiddleCenter;
        healthDisplay.alignment = TextAlignment.Center;
        
        // Scale for 2D game
        healthObj.transform.localScale = Vector3.one * 0.1f;
    }
    
    Color GetPlayerColor()
    {
        // Different colors for different players
        switch (owner)
        {
            case 0: return Color.blue;   // Player 1
            case 1: return Color.red;    // Player 2
            case 2: return Color.green;  // Player 3
            case 3: return Color.yellow; // Player 4
            default: return Color.white;
        }
    }
    
    void UpdateCurrentTile()
    {
        // Find which tile this unit is on
        Map map = FindFirstObjectByType<Map>();
        if (map != null)
        {
            Vector2 tileCoords = map.worldToMapPoint(transform.position);
            currentTile = map.GetTileAt((int)tileCoords.x, (int)tileCoords.y);
            
            if (currentTile != null)
            {
                currentTile.SetUnit(this);
            }
        }
    }
    
    public void SetSelected(bool selected)
    {
        isSelected = selected;
        
        // Change sprite based on selection
        if (spriteRenderer != null)
        {
            spriteRenderer.sprite = selected ? selectedSprite : normalSprite;
        }
        
        // Visual feedback
        if (selected)
        {
            transform.localScale = Vector3.one * 1.1f; // Slightly larger when selected
        }
        else
        {
            transform.localScale = Vector3.one;
        }
    }
    
    public void MoveToTile(Tile targetTile)
    {
        if (hasMoved || targetTile == null) return;
        
        // Remove from current tile
        if (currentTile != null)
        {
            currentTile.SetUnit(null);
        }
        
        // Move to new position
        Vector2 worldPos = FindFirstObjectByType<Map>().mapToWorldPoint(new Vector2(targetTile.GetX(), targetTile.GetY()));
        transform.position = new Vector3(worldPos.x, worldPos.y, -2); // Units above tiles
        
        // Update current tile
        currentTile = targetTile;
        targetTile.SetUnit(this);
        
        // Mark as moved
        hasMoved = true;
        
        Debug.Log($"{unitName} moved to tile ({targetTile.GetX()}, {targetTile.GetY()})");
    }
    
    public void TakeDamage(int damage)
    {
        currentHealth = Mathf.Max(0, currentHealth - damage);
        
        // Update health display
        if (healthDisplay != null)
        {
            healthDisplay.text = $"{currentHealth}/{maxHealth}";
            
            // Change color based on health
            float healthPercent = (float)currentHealth / maxHealth;
            if (healthPercent > 0.6f)
                healthDisplay.color = GetPlayerColor();
            else if (healthPercent > 0.3f)
                healthDisplay.color = Color.yellow;
            else
                healthDisplay.color = Color.red;
        }
        
        Debug.Log($"{unitName} takes {damage} damage. Health: {currentHealth}/{maxHealth}");
        
        // Check for death
        if (currentHealth <= 0)
        {
            Die();
        }
    }
    
    void Die()
    {
        Debug.Log($"{unitName} has been defeated!");
        
        // Remove from tile
        if (currentTile != null)
        {
            currentTile.SetUnit(null);
        }
        
        // Deselect if selected
        if (gameState != null && gameState.GetSelectedUnit() == this)
        {
            gameState.SelectUnit(null);
        }
        
        // Death effect (fade out)
        StartCoroutine(DeathAnimation());
    }
    
    System.Collections.IEnumerator DeathAnimation()
    {
        float fadeTime = 1f;
        Color originalColor = spriteRenderer.color;
        
        for (float t = 0; t < fadeTime; t += Time.deltaTime)
        {
            float alpha = Mathf.Lerp(1f, 0f, t / fadeTime);
            spriteRenderer.color = new Color(originalColor.r, originalColor.g, originalColor.b, alpha);
            yield return null;
        }
        
        Destroy(gameObject);
    }
    
    public void ResetForNewTurn()
    {
        hasMoved = false;
        hasAttacked = false;
        
        Debug.Log($"{unitName} ready for new turn");
    }
    
    // Getters for game systems
    public int GetOwner() => owner;
    public int GetMovementRange() => movementRange;
    public int GetAttackRange() => attackRange;
    public int GetAttackPower() => attackPower;
    public int GetDefense() => defense;
    public bool CanMoveThisTurn() => !hasMoved;
    public bool CanAttackThisTurn() => !hasAttacked;
    public Tile GetCurrentTile() => currentTile;
    public bool IsSelected() => isSelected;
    
    public void SetHasMoved(bool moved) => hasMoved = moved;
    public void SetHasAttacked(bool attacked) => hasAttacked = attacked;
    
    // Mouse interaction for unit selection
    void OnMouseDown()
    {
        if (gameState != null && owner == gameState.GetCurrentPlayer())
        {
            gameState.SelectUnit(this);
        }
    }
}

// Unit types enum
public enum UnitType
{
    Warrior,    // Basic melee unit
    Archer,     // Ranged unit
    Cavalry,    // Fast moving unit
    Mage,       // Magic user
    Scout,      // High movement, low combat
    Siege       // Anti-building unit
}




