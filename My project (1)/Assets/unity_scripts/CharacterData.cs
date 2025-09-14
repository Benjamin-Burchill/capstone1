using UnityEngine;

/// <summary>
/// ScriptableObject that defines character stats and properties
/// This is how Skyrim/WoW store character data separately from code
/// </summary>
[CreateAssetMenu(fileName = "New Character Data", menuName = "RPG/Character Data")]
public class CharacterData : ScriptableObject
{
    [Header("Basic Stats")]
    [Tooltip("Character's maximum health")]
    public int maxHealth = 100;
    
    [Tooltip("Character's movement speed")]
    public float moveSpeed = 10f;
    
    [Tooltip("Character's attack damage")]
    public int attackDamage = 25;
    
    [Tooltip("Character's attack range")]
    public float attackRange = 2f;
    
    [Tooltip("Time between attacks")]
    public float attackCooldown = 1f;
    
    [Header("AI Behavior (if NPC)")]
    [Tooltip("How far this character can detect enemies/targets")]
    public float detectionRange = 20f;
    
    [Tooltip("How aggressive this character is (0=passive, 1=normal, 2=aggressive)")]
    [Range(0f, 2f)]
    public float aggressionLevel = 1f;
    
    [Tooltip("Does this character flee when low on health?")]
    public bool fleeWhenLowHealth = false;
    
    [Tooltip("Health percentage at which character flees")]
    [Range(0f, 0.5f)]
    public float fleeThreshold = 0.2f;
    
    [Header("Rewards (if enemy)")]
    [Tooltip("XP given when this character is killed")]
    public int xpReward = 15;
    
    [Tooltip("Possible loot drops when killed")]
    public LootDrop[] lootTable;
    
    [Header("Audio")]
    [Tooltip("Sounds this character can make")]
    public AudioClip[] idleSounds;
    public AudioClip[] combatSounds;
    public AudioClip[] deathSounds;
    
    [Header("Visual")]
    [Tooltip("Material to apply to this character")]
    public Material characterMaterial;
    
    [Tooltip("Scale of this character")]
    public Vector3 characterScale = Vector3.one;
    
    [Tooltip("Particle effects for this character")]
    public GameObject[] particleEffects;
}

[System.Serializable]
public class LootDrop
{
    public GameObject itemPrefab;
    [Range(0f, 1f)]
    public float dropChance = 0.5f;
    public int minQuantity = 1;
    public int maxQuantity = 1;
}

/// <summary>
/// Character movement controller - handles all movement logic
/// Same system used by player and NPCs
/// </summary>
public class CharacterMovement
{
    private UniversalCharacter character;
    private Rigidbody rb;
    private float moveSpeed;
    
    public CharacterMovement(UniversalCharacter character)
    {
        this.character = character;
        this.rb = character.GetComponent<Rigidbody>();
    }
    
    public void SetMoveSpeed(float speed)
    {
        moveSpeed = speed;
    }
    
    public void HandleMovement(Vector2 input)
    {
        if (input.magnitude < 0.1f) return;
        
        // Convert 2D input to 3D movement
        Vector3 movement = new Vector3(input.x, 0, input.y).normalized;
        Vector3 moveVector = movement * moveSpeed * Time.deltaTime;
        
        // Apply movement (same for player and NPCs)
        if (rb != null)
        {
            rb.MovePosition(character.transform.position + moveVector);
        }
        else
        {
            character.transform.Translate(moveVector, Space.World);
        }
        
        // Face movement direction (same for player and NPCs)
        if (movement != Vector3.zero)
        {
            Quaternion targetRotation = Quaternion.LookRotation(movement);
            character.transform.rotation = Quaternion.Slerp(
                character.transform.rotation,
                targetRotation,
                10f * Time.deltaTime
            );
        }
    }
}

/// <summary>
/// Character combat controller - handles all combat logic
/// Same system used by player and NPCs
/// </summary>
public class CharacterCombat
{
    private UniversalCharacter character;
    private float attackDamage;
    private float attackRange;
    private float attackCooldown;
    private float lastAttackTime = 0f;
    
    public CharacterCombat(UniversalCharacter character)
    {
        this.character = character;
    }
    
    public void SetAttackDamage(int damage) => attackDamage = damage;
    public void SetAttackRange(float range) => attackRange = range;
    public void SetAttackCooldown(float cooldown) => attackCooldown = cooldown;
    
    public void HandleCombat(bool attackInput)
    {
        if (!attackInput) return;
        
        // Check cooldown (same for player and NPCs)
        if (Time.time < lastAttackTime + attackCooldown) return;
        
        // Perform attack (same logic for everyone)
        PerformAttack();
        lastAttackTime = Time.time;
    }
    
    void PerformAttack()
    {
        Debug.Log($"{character.name} attacks!");
        
        // Find targets in range (same for player and NPCs)
        Collider[] targets = Physics.OverlapSphere(character.transform.position, attackRange);
        
        foreach (Collider target in targets)
        {
            // Determine if this is a valid target
            bool isValidTarget = false;
            
            if (character.IsPlayer() && target.CompareTag("Enemy"))
            {
                isValidTarget = true; // Player attacks enemies
            }
            else if (character.IsEnemy() && target.CompareTag("Player"))
            {
                isValidTarget = true; // Enemies attack player
            }
            
            if (isValidTarget)
            {
                // Deal damage (same system for everyone)
                HealthSystem targetHealth = target.GetComponent<HealthSystem>();
                if (targetHealth != null)
                {
                    targetHealth.TakeDamage((int)attackDamage);
                }
            }
        }
        
        // Visual feedback (same for everyone)
        character.StartCoroutine(AttackAnimation());
    }
    
    System.Collections.IEnumerator AttackAnimation()
    {
        Vector3 originalScale = character.transform.localScale;
        character.transform.localScale = originalScale * 1.2f;
        
        yield return new WaitForSeconds(0.1f);
        
        character.transform.localScale = originalScale;
    }
}
