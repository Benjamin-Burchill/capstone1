using UnityEngine;
using System.Collections.Generic;

/// <summary>
/// Defines different types of players (Human vs AI)
/// </summary>
public enum PlayerType
{
    Human,      // Controlled by mouse/keyboard
    AIEasy,     // Simple AI
    AIMedium,   // Tactical AI
    AIHard      // Advanced AI
}

/// <summary>
/// Represents a player in the turn-based game
/// Can be human or AI controlled
/// </summary>
[System.Serializable]
public class Player
{
    public int playerID;
    public string playerName;
    public PlayerType playerType;
    public Color playerColor;
    public bool isDefeated = false;
    public List<Unit> units = new List<Unit>();
    
    public Player(int id, string name, PlayerType type, Color color)
    {
        playerID = id;
        playerName = name;
        playerType = type;
        playerColor = color;
    }
    
    public bool IsAI()
    {
        return playerType != PlayerType.Human;
    }
    
    public bool HasUnitsLeft()
    {
        foreach (Unit unit in units)
        {
            if (unit != null && unit.currentHealth > 0)
            {
                return true;
            }
        }
        return false;
    }
}

/// <summary>
/// Manages all players in the game and coordinates turns between human and AI
/// </summary>
public class PlayerController : MonoBehaviour
{
    [Header("Player Setup")]
    [Tooltip("List of all players in the game")]
    public List<Player> players = new List<Player>();
    
    [Header("AI Settings")]
    [Tooltip("Time delay for AI actions (seconds)")]
    public float aiActionDelay = 1.0f;
    
    [Tooltip("Time delay between AI units")]
    public float aiUnitDelay = 0.5f;
    
    // References
    private GameState gameState;
    private AIController aiController;
    
    // Events
    public System.Action<Player> OnPlayerTurnStarted;
    public System.Action<Player> OnPlayerTurnEnded;
    public System.Action<Player> OnPlayerDefeated;
    
    void Start()
    {
        gameState = FindFirstObjectByType<GameState>();
        aiController = FindFirstObjectByType<AIController>();
        
        InitializePlayers();
        
        // Listen for turn changes from GameState
        if (gameState != null)
        {
            gameState.OnPlayerChanged += OnPlayerTurnChanged;
        }
    }
    
    void InitializePlayers()
    {
        // Example setup - you can customize this
        if (players.Count == 0)
        {
            // Player 1 (Human)
            players.Add(new Player(0, "Player", PlayerType.Human, Color.blue));
            
            // Player 2 (AI Easy)
            players.Add(new Player(1, "AI Enemy 1", PlayerType.AIEasy, Color.red));
            
            // Player 3 (AI Medium) - Optional
            // players.Add(new Player(2, "AI Enemy 2", PlayerType.AIMedium, Color.green));
        }
        
        Debug.Log($"Initialized {players.Count} players");
        foreach (Player player in players)
        {
            Debug.Log($"  - {player.playerName} ({player.playerType})");
        }
    }
    
    void OnPlayerTurnChanged(int newPlayerIndex)
    {
        if (newPlayerIndex < 0 || newPlayerIndex >= players.Count) return;
        
        Player currentPlayer = players[newPlayerIndex];
        
        Debug.Log($"Turn started for {currentPlayer.playerName} ({currentPlayer.playerType})");
        
        // Notify listeners
        OnPlayerTurnStarted?.Invoke(currentPlayer);
        
        // If it's an AI player, start AI turn
        if (currentPlayer.IsAI())
        {
            StartAITurn(currentPlayer);
        }
        // If human player, wait for input (handled by existing GameState)
    }
    
    void StartAITurn(Player aiPlayer)
    {
        Debug.Log($"Starting AI turn for {aiPlayer.playerName}");
        
        if (aiController != null)
        {
            aiController.ExecuteAITurn(aiPlayer, OnAITurnComplete);
        }
        else
        {
            Debug.LogWarning("No AIController found! AI turn will be skipped.");
            // Skip AI turn
            Invoke(nameof(EndCurrentPlayerTurn), aiActionDelay);
        }
    }
    
    void OnAITurnComplete()
    {
        Debug.Log("AI turn completed");
        EndCurrentPlayerTurn();
    }
    
    public void EndCurrentPlayerTurn()
    {
        if (gameState == null) return;
        
        Player currentPlayer = GetCurrentPlayer();
        if (currentPlayer != null)
        {
            OnPlayerTurnEnded?.Invoke(currentPlayer);
        }
        
        // Check for victory conditions
        CheckGameEnd();
        
        // Advance to next player's turn
        gameState.EndTurn();
    }
    
    public Player GetCurrentPlayer()
    {
        if (gameState == null) return null;
        
        int currentIndex = gameState.currentPlayerTurn;
        if (currentIndex >= 0 && currentIndex < players.Count)
        {
            return players[currentIndex];
        }
        return null;
    }
    
    public Player GetPlayer(int playerID)
    {
        foreach (Player player in players)
        {
            if (player.playerID == playerID)
                return player;
        }
        return null;
    }
    
    void CheckGameEnd()
    {
        List<Player> alivePlayers = new List<Player>();
        
        foreach (Player player in players)
        {
            if (!player.isDefeated && player.HasUnitsLeft())
            {
                alivePlayers.Add(player);
            }
            else if (!player.isDefeated)
            {
                // Player has no units left - defeat them
                player.isDefeated = true;
                OnPlayerDefeated?.Invoke(player);
                Debug.Log($"{player.playerName} has been defeated!");
            }
        }
        
        // Check victory conditions
        if (alivePlayers.Count <= 1)
        {
            if (alivePlayers.Count == 1)
            {
                Debug.Log($"Game Over! {alivePlayers[0].playerName} wins!");
                // TODO: Show victory screen
            }
            else
            {
                Debug.Log("Game Over! Draw!");
                // TODO: Show draw screen
            }
        }
    }
    
    // Helper method to check if current player is AI
    public bool IsCurrentPlayerAI()
    {
        Player currentPlayer = GetCurrentPlayer();
        return currentPlayer != null && currentPlayer.IsAI();
    }
    
    // Helper method to check if current player is human
    public bool IsCurrentPlayerHuman()
    {
        Player currentPlayer = GetCurrentPlayer();
        return currentPlayer != null && !currentPlayer.IsAI();
    }
}
