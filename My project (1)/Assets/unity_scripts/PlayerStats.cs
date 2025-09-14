using UnityEngine;

/// <summary>
/// Player progression system - XP, levels, stats
/// Attach this to the Player GameObject
/// </summary>
public class PlayerStats : MonoBehaviour
{
    [Header("Level Settings")]
    [Tooltip("Current player level")]
    public int currentLevel = 1;
    
    [Tooltip("Current experience points")]
    public int currentXP = 0;
    
    [Tooltip("XP needed for next level")]
    public int xpToNextLevel = 100;
    
    [Tooltip("XP multiplier per level (each level needs more XP)")]
    public float xpMultiplier = 1.5f;
    
    [Header("Stat Bonuses Per Level")]
    [Tooltip("Max health increase per level")]
    public int healthPerLevel = 10;
    
    [Tooltip("Attack damage increase per level")]
    public int damagePerLevel = 5;
    
    [Tooltip("Movement speed increase per level")]
    public float speedPerLevel = 1f;
    
    [Header("XP Rewards")]
    [Tooltip("XP gained for killing a goblin")]
    public int goblinXP = 15;
    
    // Events
    public System.Action<int> OnLevelUp; // (newLevel)
    public System.Action<int> OnXPGained; // (xpAmount)
    
    // UI Display
    private TextMesh xpDisplay;
    
    // References to other components
    private HealthSystem healthSystem;
    private PlayerController playerController;
    
    void Start()
    {
        // Get components
        healthSystem = GetComponent<HealthSystem>();
        playerController = GetComponent<PlayerController>();
        
        // Create XP display
        CreateXPDisplay();
        
        // Apply initial level bonuses
        ApplyLevelBonuses();
        
        Debug.Log($"Player stats initialized - Level {currentLevel}, {currentXP}/{xpToNextLevel} XP");
    }
    
    void CreateXPDisplay()
    {
        // Create 3D text for XP display
        GameObject xpDisplayObj = new GameObject("XP_Display");
        xpDisplayObj.transform.SetParent(transform);
        xpDisplayObj.transform.localPosition = new Vector3(0, 4f, 0); // Above health
        
        xpDisplay = xpDisplayObj.AddComponent<TextMesh>();
        xpDisplay.text = $"Level {currentLevel} - {currentXP}/{xpToNextLevel} XP";
        xpDisplay.fontSize = 16;
        xpDisplay.color = Color.cyan;
        xpDisplay.anchor = TextAnchor.MiddleCenter;
        xpDisplay.alignment = TextAlignment.Center;
        
        // Scale appropriately
        xpDisplayObj.transform.localScale = Vector3.one * 0.08f;
        
        // Make it face camera
        xpDisplayObj.AddComponent<Billboard>();
    }
    
    public void GainXP(int amount)
    {
        currentXP += amount;
        Debug.Log($"Gained {amount} XP! Total: {currentXP}/{xpToNextLevel}");
        
        // Trigger event
        OnXPGained?.Invoke(amount);
        
        // Check for level up
        CheckLevelUp();
        
        // Update display
        UpdateXPDisplay();
    }
    
    void CheckLevelUp()
    {
        while (currentXP >= xpToNextLevel)
        {
            // Level up!
            currentXP -= xpToNextLevel;
            currentLevel++;
            
            // Increase XP requirement for next level
            xpToNextLevel = Mathf.RoundToInt(xpToNextLevel * xpMultiplier);
            
            Debug.Log($"LEVEL UP! Now level {currentLevel}. Next level needs {xpToNextLevel} XP.");
            
            // Apply level bonuses
            ApplyLevelBonuses();
            
            // Trigger event
            OnLevelUp?.Invoke(currentLevel);
            
            // Visual feedback
            StartCoroutine(LevelUpEffect());
        }
    }
    
    void ApplyLevelBonuses()
    {
        // Increase max health
        if (healthSystem != null)
        {
            int newMaxHealth = 100 + ((currentLevel - 1) * healthPerLevel);
            healthSystem.SetMaxHealth(newMaxHealth);
            
            // Heal to full on level up
            healthSystem.Heal(healthSystem.maxHealth);
        }
        
        // Increase attack damage
        if (playerController != null)
        {
            playerController.attackDamage = 25 + ((currentLevel - 1) * damagePerLevel);
        }
        
        // Increase movement speed
        if (playerController != null)
        {
            playerController.moveSpeed = 15f + ((currentLevel - 1) * speedPerLevel);
        }
        
        Debug.Log($"Level {currentLevel} bonuses applied - HP: {healthSystem?.maxHealth}, Damage: {playerController?.attackDamage}, Speed: {playerController?.moveSpeed}");
    }
    
    void UpdateXPDisplay()
    {
        if (xpDisplay != null)
        {
            xpDisplay.text = $"Level {currentLevel} - {currentXP}/{xpToNextLevel} XP";
        }
    }
    
    System.Collections.IEnumerator LevelUpEffect()
    {
        // Visual level up effect - flash and scale
        Vector3 originalScale = transform.localScale;
        Color originalColor = GetComponent<Renderer>().material.color;
        
        // Flash bright and scale up
        GetComponent<Renderer>().material.color = Color.yellow;
        transform.localScale = originalScale * 1.5f;
        
        yield return new WaitForSeconds(0.2f);
        
        // Return to normal
        GetComponent<Renderer>().material.color = originalColor;
        transform.localScale = originalScale;
        
        Debug.Log("Level up effect complete!");
    }
    
    // Public methods for other systems
    public void OnEnemyKilled(string enemyType)
    {
        int xpReward = 0;
        
        switch (enemyType.ToLower())
        {
            case "goblin":
                xpReward = goblinXP;
                break;
            default:
                xpReward = 10; // Default XP
                break;
        }
        
        GainXP(xpReward);
    }
    
    // Getters for other systems
    public int GetLevel() => currentLevel;
    public int GetCurrentXP() => currentXP;
    public int GetXPToNextLevel() => xpToNextLevel;
    public float GetXPPercentage() => (float)currentXP / xpToNextLevel;
}
