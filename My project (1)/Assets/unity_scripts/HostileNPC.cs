using UnityEngine;

/// <summary>
/// Base class for all hostile NPCs - provides common hostile behavior
/// Inherit from this for specific creature types (Goblin, Mammoth, Orc, etc.)
/// </summary>
public class HostileNPC : MonoBehaviour
{
    [Header("Generic Hostile Settings")]
    [Tooltip("Target to chase (usually player)")]
    public Transform target;
    
    [Tooltip("Distance at which NPC detects and chases target")]
    public float detectionRange = 20f;
    
    [Tooltip("Distance at which NPC stops chasing (slightly larger than detection)")]
    public float stopChaseRange = 25f;
    
    [Tooltip("How fast this NPC moves")]
    public float moveSpeed = 8f;
    
    [Tooltip("How close NPC gets before attacking")]
    public float attackRange = 2f;
    
    [Tooltip("Time between attacks")]
    public float attackCooldown = 2f;
    
    // Protected state (accessible to inheriting classes)
    protected Vector3 startPosition;
    protected float lastAttackTime = 0f;
    protected bool isTargetInRange = false;
    
    // AI States
    public enum NPCState
    {
        Idle,
        Chasing,
        Attacking,
        Fleeing,
        Patrolling
    }
    
    public NPCState currentState = NPCState.Idle;
    
    protected virtual void Start()
    {
        // Store starting position
        startPosition = transform.position;
        
        // Auto-find player if not assigned
        if (target == null)
        {
            GameObject player = GameObject.FindWithTag("Player");
            if (player != null)
            {
                target = player.transform;
            }
        }
        
        Debug.Log($"{gameObject.name} HostileNPC initialized");
    }
    
    protected virtual void Update()
    {
        if (target == null) return;
        
        float distanceToTarget = Vector3.Distance(transform.position, target.position);
        UpdateState(distanceToTarget);
        ExecuteCurrentState(distanceToTarget);
    }
    
    protected virtual void UpdateState(float distanceToTarget)
    {
        // Generic state machine logic
        switch (currentState)
        {
            case NPCState.Idle:
                if (distanceToTarget <= detectionRange)
                {
                    StartChasing();
                }
                break;
                
            case NPCState.Chasing:
                if (distanceToTarget > stopChaseRange)
                {
                    StopChasing();
                }
                else if (distanceToTarget <= attackRange)
                {
                    StartAttacking();
                }
                break;
                
            case NPCState.Attacking:
                if (distanceToTarget > attackRange)
                {
                    StartChasing();
                }
                break;
        }
    }
    
    protected virtual void ExecuteCurrentState(float distanceToTarget)
    {
        switch (currentState)
        {
            case NPCState.Idle:
                IdleBehavior();
                break;
                
            case NPCState.Chasing:
                ChaseBehavior(distanceToTarget);
                break;
                
            case NPCState.Attacking:
                AttackBehavior();
                break;
        }
    }
    
    // Virtual methods - can be overridden by specific creature types
    protected virtual void IdleBehavior()
    {
        // Default idle - stay in place
        transform.position = startPosition;
    }
    
    protected virtual void ChaseBehavior(float distance)
    {
        // Move toward target
        Vector3 direction = (target.position - transform.position).normalized;
        Vector3 newPosition = transform.position + direction * moveSpeed * Time.deltaTime;
        transform.position = newPosition;
        
        // Face target
        transform.LookAt(new Vector3(target.position.x, transform.position.y, target.position.z));
    }
    
    protected virtual void AttackBehavior()
    {
        // Check attack cooldown
        if (Time.time >= lastAttackTime + attackCooldown)
        {
            PerformAttack();
            lastAttackTime = Time.time;
        }
    }
    
    protected virtual void PerformAttack()
    {
        Debug.Log($"{gameObject.name} attacks!");
        
        // Deal damage to target if it has health system
        HealthSystem targetHealth = target.GetComponent<HealthSystem>();
        if (targetHealth != null)
        {
            targetHealth.TakeDamage(GetAttackDamage());
        }
    }
    
    protected virtual int GetAttackDamage()
    {
        return 10; // Default damage - override in specific creatures
    }
    
    // State change methods (can be overridden for custom behavior)
    protected virtual void StartChasing()
    {
        currentState = NPCState.Chasing;
        OnStartChasing();
    }
    
    protected virtual void StopChasing()
    {
        currentState = NPCState.Idle;
        OnStopChasing();
    }
    
    protected virtual void StartAttacking()
    {
        currentState = NPCState.Attacking;
        OnStartAttacking();
    }
    
    // Hook methods for specific creatures to override
    protected virtual void OnStartChasing() { }
    protected virtual void OnStopChasing() { }
    protected virtual void OnStartAttacking() { }
    
    // Debug visualization
    protected virtual void OnDrawGizmosSelected()
    {
        // Draw detection range
        Gizmos.color = Color.yellow;
        Gizmos.DrawWireSphere(transform.position, detectionRange);
        
        // Draw attack range
        Gizmos.color = Color.red;
        Gizmos.DrawWireSphere(transform.position, attackRange);
        
        // Draw stop chase range
        Gizmos.color = Color.orange;
        Gizmos.DrawWireSphere(transform.position, stopChaseRange);
    }
}
