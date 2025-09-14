using UnityEngine;

/// <summary>
/// Goblin-specific AI behavior - inherits from HostileNPC
/// Small, fast, pack-oriented creatures
/// </summary>
[RequireComponent(typeof(HealthSystem))]
public class GoblinAI : HostileNPC
{
    [Header("AI Settings")]
    [Tooltip("The player transform to chase")]
    public Transform player;
    
    [Tooltip("How fast the goblin moves (units per second)")]
    public float moveSpeed = 8f;
    
    [Tooltip("Distance at which goblin starts chasing player")]
    public float detectionRange = 20f;
    
    [Tooltip("Distance at which goblin stops chasing (slightly larger than detection)")]
    public float stopChaseRange = 25f;
    
    [Header("Animation Settings")]
    [Tooltip("How fast the idle bobbing animation plays")]
    public float bobSpeed = 2f;
    
    [Tooltip("How high the goblin bobs when idle")]
    public float bobHeight = 0.1f;
    
    [Header("Audio (Optional)")]
    [Tooltip("Sound to play when starting to chase")]
    public AudioClip chaseSound;
    
    [Tooltip("Sound to play when idle/wandering")]
    public AudioClip idleSound;
    
    // Private state
    private Vector3 startPosition;
    private float bobTimer = 0f;
    private AudioSource audioSource;
    private Renderer goblinRenderer;
    
    // AI States
    public enum GoblinState
    {
        Idle,
        Chasing,
        Attacking,
        Fleeing
    }
    
    public GoblinState currentState = GoblinState.Idle;
    
    void Start()
    {
        // Store starting position for idle behavior
        startPosition = transform.position;
        
        // Get components
        audioSource = GetComponent<AudioSource>();
        goblinRenderer = GetComponent<Renderer>();
        
        // Find player if not assigned
        if (player == null)
        {
            GameObject playerObj = GameObject.FindWithTag("Player");
            if (playerObj != null)
            {
                player = playerObj.transform;
            }
            else
            {
                Debug.LogWarning("GoblinAI: No player found! Make sure player has 'Player' tag.");
            }
        }
        
        // Random starting bob timer for variety
        bobTimer = Random.Range(0f, Mathf.PI * 2f);
        
        Debug.Log($"Goblin {gameObject.name} initialized at {startPosition}");
    }
    
    void Update()
    {
        if (player == null) return;
        
        float distanceToPlayer = Vector3.Distance(transform.position, player.position);
        
        // State machine
        switch (currentState)
        {
            case GoblinState.Idle:
                if (distanceToPlayer <= detectionRange)
                {
                    StartChasing();
                }
                else
                {
                    IdleBehavior();
                }
                break;
                
            case GoblinState.Chasing:
                if (distanceToPlayer > stopChaseRange)
                {
                    StopChasing();
                }
                else
                {
                    ChasePlayer(distanceToPlayer);
                }
                break;
        }
        
        // Keep goblin on ground level
        Vector3 pos = transform.position;
        pos.y = 0.5f; // Half the goblin's height
        transform.position = pos;
    }
    
    void StartChasing()
    {
        currentState = GoblinState.Chasing;
        
        // Visual feedback - make goblin slightly larger when chasing
        transform.localScale = Vector3.one * 1.1f;
        
        // Audio feedback
        if (audioSource && chaseSound)
        {
            audioSource.PlayOneShot(chaseSound);
        }
        
        // Color change - make redder when chasing
        if (goblinRenderer)
        {
            goblinRenderer.material.color = new Color(1f, 0.2f, 0.2f); // Bright red
        }
        
        Debug.Log($"Goblin {gameObject.name} started chasing player!");
    }
    
    void StopChasing()
    {
        currentState = GoblinState.Idle;
        
        // Return to normal size
        transform.localScale = Vector3.one;
        
        // Return to normal color
        if (goblinRenderer)
        {
            goblinRenderer.material.color = new Color(0.8f, 0.2f, 0.2f); // Normal red
        }
        
        Debug.Log($"Goblin {gameObject.name} stopped chasing player.");
    }
    
    void ChasePlayer(float distance)
    {
        // Move toward player
        Vector3 direction = (player.position - transform.position).normalized;
        
        // Apply movement
        Vector3 movement = direction * moveSpeed * Time.deltaTime;
        transform.Translate(movement, Space.World);
        
        // Face the player
        transform.LookAt(new Vector3(player.position.x, transform.position.y, player.position.z));
        
        // Optional: Slow down when very close to avoid jittering
        if (distance < 2f)
        {
            // Could add attack behavior here later
        }
    }
    
    void IdleBehavior()
    {
        // Gentle bobbing animation
        bobTimer += Time.deltaTime * bobSpeed;
        float bob = Mathf.Sin(bobTimer) * bobHeight;
        
        Vector3 pos = startPosition;
        pos.y = 0.5f + bob; // Base height + bobbing
        transform.position = pos;
        
        // Occasional random rotation for variety
        if (Random.Range(0f, 1f) < 0.01f) // 1% chance per frame
        {
            transform.Rotate(0, Random.Range(-30f, 30f), 0);
        }
    }
    
    // Public methods for external systems (combat, etc.)
    public void TakeDamage(int damage)
    {
        // Could implement health system here
        Debug.Log($"Goblin {gameObject.name} took {damage} damage!");
        
        // Flash red when hit
        if (goblinRenderer)
        {
            StartCoroutine(FlashRed());
        }
    }
    
    public void Die()
    {
        Debug.Log($"Goblin {gameObject.name} died!");
        // Could play death animation, drop loot, etc.
        Destroy(gameObject);
    }
    
    // Coroutine for damage flash effect
    System.Collections.IEnumerator FlashRed()
    {
        Color originalColor = goblinRenderer.material.color;
        goblinRenderer.material.color = Color.white;
        yield return new WaitForSeconds(0.1f);
        goblinRenderer.material.color = originalColor;
    }
    
    // Gizmos for debugging in Scene view
    void OnDrawGizmosSelected()
    {
        // Draw detection range
        Gizmos.color = Color.yellow;
        Gizmos.DrawWireSphere(transform.position, detectionRange);
        
        // Draw stop chase range
        Gizmos.color = Color.red;
        Gizmos.DrawWireSphere(transform.position, stopChaseRange);
    }
}
