using UnityEngine;
using UnityEngine.InputSystem;

/// <summary>
/// Universal Character System - used by Player, Goblins, Mammoths, ALL characters
/// The ONLY difference between characters is their input source and data
/// </summary>
public class UniversalCharacter : MonoBehaviour
{
    [Header("Character Identity")]
    [Tooltip("What type of character this is")]
    public CharacterType characterType = CharacterType.Goblin;
    
    [Tooltip("Character data (stats, abilities, appearance)")]
    public CharacterData characterData;
    
    [Header("Input Source")]
    [Tooltip("How this character gets input (Player Input vs AI)")]
    public InputSourceType inputType = InputSourceType.AI;
    
    // Input Actions (only used if inputType = PlayerInput)
    [Header("Player Input Actions (if Player)")]
    public InputAction moveAction;
    public InputAction attackAction;
    
    // Universal character controllers
    private IInputSource inputSource;
    private CharacterMovement characterMovement;
    private CharacterCombat characterCombat;
    private HealthSystem healthSystem;
    
    // Shared character state
    public Vector2 currentMoveInput { get; private set; }
    public bool attackRequested { get; private set; }
    public bool isMoving { get; private set; }
    
    void Start()
    {
        InitializeCharacter();
    }
    
    void InitializeCharacter()
    {
        // Get or add required components
        healthSystem = GetComponent<HealthSystem>();
        if (healthSystem == null)
        {
            healthSystem = gameObject.AddComponent<HealthSystem>();
        }
        
        // Initialize movement controller
        characterMovement = new CharacterMovement(this);
        
        // Initialize combat controller
        characterCombat = new CharacterCombat(this);
        
        // Create appropriate input source
        switch (inputType)
        {
            case InputSourceType.PlayerInput:
                inputSource = new PlayerInputSource(moveAction, attackAction);
                break;
                
            case InputSourceType.AI:
                inputSource = CreateAIForCharacterType();
                break;
        }
        
        // Apply character data
        ApplyCharacterData();
        
        Debug.Log($"Universal Character {gameObject.name} initialized as {characterType}");
    }
    
    IInputSource CreateAIForCharacterType()
    {
        switch (characterType)
        {
            case CharacterType.Goblin:
                return new GoblinAI_InputSource(this);
                
            case CharacterType.Mammoth:
                return new MammothAI_InputSource(this);
                
            case CharacterType.Player:
                return new PlayerInputSource(moveAction, attackAction);
                
            default:
                return new BasicAI_InputSource(this);
        }
    }
    
    void ApplyCharacterData()
    {
        if (characterData == null) return;
        
        // Apply stats from ScriptableObject data
        if (healthSystem != null)
        {
            healthSystem.maxHealth = characterData.maxHealth;
            healthSystem.currentHealth = characterData.maxHealth;
        }
        
        // Apply movement settings
        if (characterMovement != null)
        {
            characterMovement.SetMoveSpeed(characterData.moveSpeed);
        }
        
        // Apply combat settings
        if (characterCombat != null)
        {
            characterCombat.SetAttackDamage(characterData.attackDamage);
            characterCombat.SetAttackRange(characterData.attackRange);
        }
    }
    
    void Update()
    {
        // UNIVERSAL UPDATE LOOP - same for ALL characters
        if (inputSource == null) return;
        
        // Get input (from player or AI)
        currentMoveInput = inputSource.GetMovementInput();
        attackRequested = inputSource.GetAttackInput();
        
        // Process movement (same logic for everyone)
        characterMovement?.HandleMovement(currentMoveInput);
        
        // Process combat (same logic for everyone)
        characterCombat?.HandleCombat(attackRequested);
        
        // Update movement state
        isMoving = currentMoveInput.magnitude > 0.1f;
    }
    
    void OnEnable()
    {
        if (inputType == InputSourceType.PlayerInput)
        {
            moveAction?.Enable();
            attackAction?.Enable();
        }
    }
    
    void OnDisable()
    {
        if (inputType == InputSourceType.PlayerInput)
        {
            moveAction?.Disable();
            attackAction?.Disable();
        }
    }
    
    // Public interface for other systems
    public CharacterType GetCharacterType() => characterType;
    public bool IsPlayer() => characterType == CharacterType.Player;
    public bool IsEnemy() => characterType != CharacterType.Player;
    public HealthSystem GetHealth() => healthSystem;
    public CharacterCombat GetCombat() => characterCombat;
}

// Enums for character classification
public enum CharacterType
{
    Player,
    Goblin,
    Mammoth,
    Orc,
    Skeleton,
    Dragon
}

public enum InputSourceType
{
    PlayerInput,    // Human player
    AI,            // Computer controlled
    NetworkPlayer  // Future: multiplayer
}

// Input source interface - the KEY to the whole system
public interface IInputSource
{
    Vector2 GetMovementInput();
    bool GetAttackInput();
    bool GetJumpInput();
    bool GetInteractInput();
}

// Player input implementation
public class PlayerInputSource : IInputSource
{
    private InputAction moveAction;
    private InputAction attackAction;
    
    public PlayerInputSource(InputAction move, InputAction attack)
    {
        moveAction = move;
        attackAction = attack;
    }
    
    public Vector2 GetMovementInput() => moveAction.ReadValue<Vector2>();
    public bool GetAttackInput() => attackAction.WasPressedThisFrame();
    public bool GetJumpInput() => false; // Not implemented yet
    public bool GetInteractInput() => false; // Not implemented yet
}

// AI input implementations for different creature types
public class GoblinAI_InputSource : IInputSource
{
    private UniversalCharacter character;
    private Transform target;
    
    public GoblinAI_InputSource(UniversalCharacter character)
    {
        this.character = character;
        // Find player target
        GameObject player = GameObject.FindWithTag("Player");
        if (player != null) target = player.transform;
    }
    
    public Vector2 GetMovementInput()
    {
        if (target == null) return Vector2.zero;
        
        float distance = Vector3.Distance(character.transform.position, target.position);
        
        // Goblin AI: aggressive, always chases if in range
        if (distance <= 20f) // Goblin detection range
        {
            Vector3 direction = (target.position - character.transform.position).normalized;
            return new Vector2(direction.x, direction.z);
        }
        
        return Vector2.zero;
    }
    
    public bool GetAttackInput()
    {
        if (target == null) return false;
        
        float distance = Vector3.Distance(character.transform.position, target.position);
        return distance <= 2f; // Attack when close
    }
    
    public bool GetJumpInput() => false;
    public bool GetInteractInput() => false;
}

public class MammothAI_InputSource : IInputSource
{
    private UniversalCharacter character;
    private Transform target;
    private bool isProvoked = false;
    
    public MammothAI_InputSource(UniversalCharacter character)
    {
        this.character = character;
        GameObject player = GameObject.FindWithTag("Player");
        if (player != null) target = player.transform;
    }
    
    public Vector2 GetMovementInput()
    {
        if (target == null) return Vector2.zero;
        
        float distance = Vector3.Distance(character.transform.position, target.position);
        
        // Mammoth AI: peaceful unless provoked, small aggro radius
        float aggroRange = isProvoked ? 15f : 5f; // Much smaller when peaceful
        
        if (distance <= aggroRange)
        {
            if (!isProvoked && distance <= 4f)
            {
                isProvoked = true; // Provoke when player gets too close
                Debug.Log("Mammoth provoked by proximity!");
            }
            
            Vector3 direction = (target.position - character.transform.position).normalized;
            return new Vector2(direction.x, direction.z) * 0.5f; // Slower movement
        }
        
        return Vector2.zero;
    }
    
    public bool GetAttackInput()
    {
        if (!isProvoked || target == null) return false;
        
        float distance = Vector3.Distance(character.transform.position, target.position);
        return distance <= 3f; // Longer attack range (trunk)
    }
    
    public void BecomeProvoked() => isProvoked = true;
    
    public bool GetJumpInput() => false;
    public bool GetInteractInput() => false;
}
