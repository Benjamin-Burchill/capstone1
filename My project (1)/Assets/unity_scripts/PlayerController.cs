using UnityEngine;
using UnityEngine.InputSystem;

/// <summary>
/// Player movement controller with NEW Input System
/// Attach this script to the Player GameObject
/// </summary>
public class PlayerController : MonoBehaviour
{
    [Header("Movement Settings")]
    [Tooltip("How fast the player moves (units per second)")]
    public float moveSpeed = 15f;
    
    [Tooltip("How fast the player rotates to face movement direction")]
    public float rotationSpeed = 10f;
    
    [Header("Bounds")]
    [Tooltip("Maximum distance from center (for 300x300m world)")]
    public float worldBounds = 150f;
    
    [Header("Input Actions")]
    [Tooltip("Input Action for movement (WASD)")]
    public InputAction moveAction;
    
    [Tooltip("Input Action for attacking (Left Mouse Click)")]
    public InputAction attackAction;
    
    [Header("Combat Settings")]
    [Tooltip("How far player can attack (units)")]
    public float attackRange = 3f;
    
    [Tooltip("How much damage player deals")]
    public int attackDamage = 25;
    
    [Tooltip("Time between attacks (seconds)")]
    public float attackCooldown = 1f;
    
    [Header("Audio (Optional)")]
    [Tooltip("Footstep sound effect")]
    public AudioClip footstepSound;
    
    [Tooltip("How often to play footstep sounds (seconds)")]
    public float footstepInterval = 0.5f;
    
    // Private state
    private Vector2 moveInput;
    private Vector3 movement;
    private bool isMoving = false;
    private float footstepTimer = 0f;
    private float lastAttackTime = 0f;
    private AudioSource audioSource;
    private Rigidbody rb;
    
    void Start()
    {
        // Get components
        audioSource = GetComponent<AudioSource>();
        rb = GetComponent<Rigidbody>();
        
        // Configure rigidbody if present
        if (rb != null)
        {
            rb.freezeRotation = true; // Prevent tipping over
        }
        
        Debug.Log("Player controller initialized");
    }
    
    void OnEnable()
    {
        // Enable input actions
        moveAction.Enable();
        attackAction.Enable();
    }
    
    void OnDisable()
    {
        // Disable input actions
        moveAction.Disable();
        attackAction.Disable();
    }
    
    void Update()
    {
        HandleInput();
        HandleMovement();
        HandleCombat();
        HandleAudio();
        EnforceBounds();
    }
    
    void HandleCombat()
    {
        // Check for attack input
        if (attackAction.WasPressedThisFrame())
        {
            // Check cooldown
            if (Time.time >= lastAttackTime + attackCooldown)
            {
                PerformAttack();
                lastAttackTime = Time.time;
            }
            else
            {
                Debug.Log("Attack on cooldown!");
            }
        }
    }
    
    void PerformAttack()
    {
        Debug.Log("Player attacks!");
        
        // Find all enemies within attack range
        Collider[] nearbyObjects = Physics.OverlapSphere(transform.position, attackRange);
        
        int enemiesHit = 0;
        foreach (Collider col in nearbyObjects)
        {
            if (col.CompareTag("Enemy"))
            {
                // Deal damage to enemy
                HealthSystem enemyHealth = col.GetComponent<HealthSystem>();
                if (enemyHealth != null)
                {
                    enemyHealth.TakeDamage(attackDamage);
                    enemiesHit++;
                    Debug.Log($"Hit {col.name} for {attackDamage} damage!");
                }
            }
        }
        
        if (enemiesHit == 0)
        {
            Debug.Log("Attack missed - no enemies in range");
        }
        
        // Visual feedback - scale up briefly
        StartCoroutine(AttackFeedback());
    }
    
    System.Collections.IEnumerator AttackFeedback()
    {
        // Scale up for attack animation
        Vector3 originalScale = transform.localScale;
        transform.localScale = originalScale * 1.2f;
        
        yield return new WaitForSeconds(0.1f);
        
        // Return to normal size
        transform.localScale = originalScale;
    }
    
    void HandleInput()
    {
        // NEW INPUT SYSTEM: Read from Input Action
        moveInput = moveAction.ReadValue<Vector2>();
        
        // DEBUG: Show input values
        if (moveInput.magnitude > 0.1f)
        {
            Debug.Log($"New Input System - Move Input: {moveInput}");
        }
        
        // Create 3D movement vector from 2D input
        movement = new Vector3(moveInput.x, 0, moveInput.y);
        
        // Check if player is moving
        isMoving = movement.magnitude > 0.1f;
        
        // Normalize for consistent speed in all directions
        if (isMoving)
        {
            movement = movement.normalized;
        }
    }
    
    void HandleMovement()
    {
        if (isMoving)
        {
            // Apply movement
            Vector3 moveVector = movement * moveSpeed * Time.deltaTime;
            
            if (rb != null)
            {
                // Use physics if rigidbody present
                rb.MovePosition(transform.position + moveVector);
            }
            else
            {
                // Direct transform movement
                transform.Translate(moveVector, Space.World);
            }
            
            // Rotate to face movement direction
            if (movement != Vector3.zero)
            {
                Quaternion targetRotation = Quaternion.LookRotation(movement);
                transform.rotation = Quaternion.Slerp(
                    transform.rotation, 
                    targetRotation, 
                    rotationSpeed * Time.deltaTime
                );
            }
        }
    }
    
    void HandleAudio()
    {
        if (isMoving && audioSource && footstepSound)
        {
            footstepTimer += Time.deltaTime;
            
            if (footstepTimer >= footstepInterval)
            {
                audioSource.PlayOneShot(footstepSound);
                footstepTimer = 0f;
            }
        }
        else
        {
            footstepTimer = 0f;
        }
    }
    
    void EnforceBounds()
    {
        // Keep player within world bounds
        Vector3 pos = transform.position;
        pos.x = Mathf.Clamp(pos.x, -worldBounds, worldBounds);
        pos.z = Mathf.Clamp(pos.z, -worldBounds, worldBounds);
        
        // Keep player on ground
        pos.y = Mathf.Max(pos.y, 0.5f); // Half player height above ground
        
        transform.position = pos;
    }
    
    // Public methods for other systems
    public bool IsMoving()
    {
        return isMoving;
    }
    
    public Vector3 GetMovementDirection()
    {
        return movement;
    }
    
    public float GetCurrentSpeed()
    {
        return isMoving ? moveSpeed : 0f;
    }
    
    // Debug visualization in Scene view
    void OnDrawGizmos()
    {
        // Draw world bounds
        Gizmos.color = Color.yellow;
        Gizmos.DrawWireCube(Vector3.zero, new Vector3(worldBounds * 2, 1, worldBounds * 2));
        
        // Draw movement direction when moving
        if (isMoving && Application.isPlaying)
        {
            Gizmos.color = Color.green;
            Gizmos.DrawRay(transform.position, movement * 5f);
        }
        
        // Draw attack range
        Gizmos.color = Color.red;
        Gizmos.DrawWireSphere(transform.position, attackRange);
    }
}
