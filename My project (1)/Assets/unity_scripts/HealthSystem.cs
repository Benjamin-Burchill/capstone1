
using UnityEngine;
using UnityEngine.UI;

/// <summary>
/// Health system with HP bars for players and enemies
/// Attach to any GameObject that needs health
/// </summary>
public class HealthSystem : MonoBehaviour
{
    [Header("Health Settings")]
    [Tooltip("Maximum health points")]
    public int maxHealth = 100;
    
    [Tooltip("Current health (will be set to maxHealth on start)")]
    public int currentHealth;
    
    [Header("UI Settings")]
    [Tooltip("Health text display (will be created automatically)")]
    public TextMesh healthText;
    
    [Tooltip("Height above object to place health bar")]
    public float healthBarHeight = 3f;
    
    [Tooltip("Scale of the health bar")]
    public float healthBarScale = 1f;
    
    [Header("Visual Feedback")]
    [Tooltip("Color when at full health")]
    public Color fullHealthColor = Color.green;
    
    [Tooltip("Color when at low health")]
    public Color lowHealthColor = Color.red;
    
    [Tooltip("Health percentage considered 'low' (for color change)")]
    [Range(0f, 1f)]
    public float lowHealthThreshold = 0.3f;
    
    // Events for other systems to listen to
    public System.Action<int, int> OnHealthChanged; // (currentHealth, maxHealth)
    public System.Action OnDeath;
    public System.Action<int> OnDamageTaken; // (damage amount)
    
    // Private state
    private bool isDead = false;
    
    void Start()
    {
        // Initialize health
        currentHealth = maxHealth;
        
        // Create health display
        CreateHealthBar();
        
        // Update UI
        UpdateHealthBar();
        
        Debug.Log($"{gameObject.name} health system initialized: {currentHealth}/{maxHealth} HP");
    }
    
    void CreateHealthBar()
    {
        // SIMPLIFIED: Create a basic 3D text instead of complex UI
        GameObject healthDisplay = new GameObject($"{gameObject.name}_Health");
        healthDisplay.transform.SetParent(transform);
        healthDisplay.transform.localPosition = new Vector3(0, healthBarHeight, 0);
        
        // Create 3D text
        TextMesh textMesh = healthDisplay.AddComponent<TextMesh>();
        textMesh.text = $"{currentHealth}/{maxHealth}";
        textMesh.fontSize = 20;
        textMesh.color = Color.white;
        textMesh.anchor = TextAnchor.MiddleCenter;
        textMesh.alignment = TextAlignment.Center;
        
        // Scale it appropriately
        healthDisplay.transform.localScale = Vector3.one * 0.1f;
        
        // Make it always face camera
        healthDisplay.AddComponent<Billboard>();
        
        // Store reference for updates
        this.healthText = textMesh;
        
        Debug.Log($"Created simplified health display for {gameObject.name}");
    }
    
    void UpdateHealthBar()
    {
        // Update 3D text display
        if (healthText != null)
        {
            float healthPercent = (currentHealth / (float)maxHealth) * 100f;
            
            healthText.text = $"{currentHealth}/{maxHealth} ({healthPercent:F0}%)";
            
            // Change color based on health
            if (healthPercent > 60)
                healthText.color = Color.green;
            else if (healthPercent > 30)
                healthText.color = Color.yellow;
            else
                healthText.color = Color.red;
        }
    }
    
    // Public methods for combat system
    public void TakeDamage(int damage)
    {
        if (isDead) return;
        
        currentHealth = Mathf.Max(0, currentHealth - damage);
        
        Debug.Log($"{gameObject.name} took {damage} damage. Health: {currentHealth}/{maxHealth}");
        
        // Trigger events
        OnHealthChanged?.Invoke(currentHealth, maxHealth);
        OnDamageTaken?.Invoke(damage);
        
        // Update UI
        UpdateHealthBar();
        
        // Check for death
        if (currentHealth <= 0 && !isDead)
        {
            Die();
        }
    }
    
    public void Heal(int amount)
    {
        if (isDead) return;
        
        currentHealth = Mathf.Min(maxHealth, currentHealth + amount);
        
        Debug.Log($"{gameObject.name} healed {amount} HP. Health: {currentHealth}/{maxHealth}");
        
        // Trigger events
        OnHealthChanged?.Invoke(currentHealth, maxHealth);
        
        // Update UI
        UpdateHealthBar();
    }
    
    public void SetMaxHealth(int newMaxHealth)
    {
        maxHealth = newMaxHealth;
        currentHealth = Mathf.Min(currentHealth, maxHealth);
        
        // Update display
        UpdateHealthBar();
    }
    
    void Die()
    {
        isDead = true;
        
        Debug.Log($"{gameObject.name} died!");
        
        // Give XP to player if this is an enemy
        if (gameObject.CompareTag("Enemy"))
        {
            GameObject player = GameObject.FindWithTag("Player");
            if (player != null)
            {
                PlayerStats playerStats = player.GetComponent<PlayerStats>();
                if (playerStats != null)
                {
                    playerStats.OnEnemyKilled("goblin");
                }
            }
        }
        
        // Trigger death event
        OnDeath?.Invoke();
        
        // Visual feedback
        StartCoroutine(DeathSequence());
    }
    
    System.Collections.IEnumerator DeathSequence()
    {
        // Fade out over 1 second
        Renderer renderer = GetComponent<Renderer>();
        if (renderer != null)
        {
            Color originalColor = renderer.material.color;
            float elapsed = 0f;
            float duration = 1f;
            
            while (elapsed < duration)
            {
                elapsed += Time.deltaTime;
                float alpha = Mathf.Lerp(1f, 0f, elapsed / duration);
                
                Color newColor = originalColor;
                newColor.a = alpha;
                renderer.material.color = newColor;
                
                yield return null;
            }
        }
        
        // Destroy after fade
        Destroy(gameObject);
    }
    
    // Public getters
    public bool IsDead() => isDead;
    public bool IsFullHealth() => currentHealth >= maxHealth;
    public float GetHealthPercentage() => (float)currentHealth / maxHealth;
}

/// <summary>
/// Helper component to make UI elements always face the camera
/// Attach to Canvas objects that should act as billboards
/// </summary>
public class Billboard : MonoBehaviour
{
    private Camera mainCamera;
    
    void Start()
    {
        mainCamera = Camera.main;
    }
    
    void LateUpdate()
    {
        if (mainCamera != null)
        {
            transform.LookAt(transform.position + mainCamera.transform.rotation * Vector3.forward,
                           mainCamera.transform.rotation * Vector3.up);
        }
    }
}
