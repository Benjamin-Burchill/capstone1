using UnityEngine;

/// <summary>
/// Mammoth-specific AI behavior - inherits from HostileNPC
/// Large, slow, powerful creature with small aggro radius
/// </summary>
[RequireComponent(typeof(HealthSystem))]
public class MammothAI : HostileNPC
{
    [Header("Mammoth-Specific Settings")]
    [Tooltip("Mammoth trumpet sound when aggroed")]
    public AudioClip trumpetSound;
    
    [Tooltip("Ground shake intensity when mammoth moves")]
    public float groundShakeIntensity = 0.1f;
    
    [Tooltip("How much damage mammoth deals")]
    public int mammothDamage = 40;
    
    [Tooltip("Mammoth is peaceful unless provoked")]
    public bool isPeaceful = true;
    
    [Tooltip("Distance mammoth can be hit from (larger hitbox)")]
    public float hitboxRadius = 2f;
    
    // Mammoth-specific state
    private bool hasBeenProvoked = false;
    private float lastGroundShake = 0f;
    private AudioSource audioSource;
    
    protected override void Start()
    {
        base.Start();
        
        // Mammoth-specific setup
        audioSource = GetComponent<AudioSource>();
        
        // Configure mammoth stats
        detectionRange = 8f;      // Small aggro radius - peaceful giant
        stopChaseRange = 12f;     // Gives up chase easily
        moveSpeed = 4f;           // Slow but steady
        attackRange = 3f;         // Long reach with trunk
        attackCooldown = 3f;      // Slow, powerful attacks
        
        // Setup health
        HealthSystem health = GetComponent<HealthSystem>();
        if (health != null)
        {
            health.maxHealth = 150;  // Much more HP than goblins
            health.currentHealth = 150;
        }
        
        Debug.Log($"Mammoth {gameObject.name} initialized - Peaceful: {isPeaceful}");
    }
    
    protected override void UpdateState(float distanceToTarget)
    {
        // Mammoth-specific state logic
        if (isPeaceful && !hasBeenProvoked)
        {
            // Peaceful mammoth only aggros if attacked or if player gets very close
            if (distanceToTarget <= detectionRange * 0.5f) // Half normal range when peaceful
            {
                BecomeProvoked("Player got too close!");
            }
        }
        else
        {
            // Use standard hostile behavior once provoked
            base.UpdateState(distanceToTarget);
        }
    }
    
    public void BecomeProvoked(string reason)
    {
        if (!hasBeenProvoked)
        {
            hasBeenProvoked = true;
            isPeaceful = false;
            
            Debug.Log($"Mammoth provoked: {reason}");
            
            // Play trumpet sound
            if (audioSource && trumpetSound)
            {
                audioSource.PlayOneShot(trumpetSound);
            }
            
            // Visual feedback - become slightly red
            Renderer renderer = GetComponent<Renderer>();
            if (renderer != null)
            {
                renderer.material.color = new Color(0.8f, 0.6f, 0.6f); // Slightly red tint
            }
            
            // Increase detection range when provoked
            detectionRange = 15f;
            stopChaseRange = 20f;
        }
    }
    
    protected override void IdleBehavior()
    {
        // Mammoth idle - gentle swaying
        float sway = Mathf.Sin(Time.time * 0.5f) * 0.1f;
        Vector3 pos = startPosition;
        pos.x += sway;
        transform.position = pos;
        
        // Occasional trumpet sound when idle
        if (Random.Range(0f, 1f) < 0.001f && audioSource && trumpetSound)
        {
            audioSource.PlayOneShot(trumpetSound, 0.3f); // Quieter when idle
        }
    }
    
    protected override void ChaseBehavior(float distance)
    {
        // Mammoth chase - slower but with ground shake
        base.ChaseBehavior(distance);
        
        // Ground shake effect when moving
        if (Time.time >= lastGroundShake + 0.5f)
        {
            ShakeGround();
            lastGroundShake = Time.time;
        }
    }
    
    protected override void PerformAttack()
    {
        Debug.Log($"Mammoth {gameObject.name} trunk attack!");
        
        // Mammoth has area attack - hits everything in range
        Collider[] targets = Physics.OverlapSphere(transform.position, attackRange);
        
        foreach (Collider col in targets)
        {
            if (col.CompareTag("Player"))
            {
                HealthSystem targetHealth = col.GetComponent<HealthSystem>();
                if (targetHealth != null)
                {
                    targetHealth.TakeDamage(mammothDamage);
                    Debug.Log($"Mammoth hit {col.name} for {mammothDamage} damage!");
                }
                
                // Knockback effect
                Rigidbody targetRb = col.GetComponent<Rigidbody>();
                if (targetRb != null)
                {
                    Vector3 knockDirection = (col.transform.position - transform.position).normalized;
                    targetRb.AddForce(knockDirection * 500f); // Strong knockback
                }
            }
        }
        
        // Visual attack feedback
        StartCoroutine(AttackAnimation());
        
        // Ground shake on attack
        ShakeGround(groundShakeIntensity * 2f);
    }
    
    void ShakeGround(float intensity = -1f)
    {
        if (intensity < 0) intensity = groundShakeIntensity;
        
        // Shake camera if player is close
        Camera mainCamera = Camera.main;
        if (mainCamera != null)
        {
            CameraFollow cameraFollow = mainCamera.GetComponent<CameraFollow>();
            if (cameraFollow != null)
            {
                cameraFollow.ShakeCamera(intensity, 0.3f);
            }
        }
    }
    
    System.Collections.IEnumerator AttackAnimation()
    {
        // Scale up for attack
        Vector3 originalScale = transform.localScale;
        transform.localScale = originalScale * 1.3f;
        
        yield return new WaitForSeconds(0.2f);
        
        // Return to normal
        transform.localScale = originalScale;
    }
    
    protected override int GetAttackDamage()
    {
        return mammothDamage;
    }
    
    // Mammoth takes damage - becomes provoked
    public void OnTakeDamage()
    {
        if (isPeaceful)
        {
            BecomeProvoked("Attacked by player!");
        }
    }
    
    // Debug visualization - larger gizmos for mammoth
    protected override void OnDrawGizmosSelected()
    {
        base.OnDrawGizmosSelected();
        
        // Draw peaceful detection range (smaller)
        if (isPeaceful && !hasBeenProvoked)
        {
            Gizmos.color = Color.green;
            Gizmos.DrawWireSphere(transform.position, detectionRange * 0.5f);
        }
        
        // Draw hitbox
        Gizmos.color = Color.blue;
        Gizmos.DrawWireSphere(transform.position, hitboxRadius);
    }
}
