using UnityEngine;
using System.Collections.Generic;
using System.Linq;

/// <summary>
/// Enhanced turn management system supporting various game modes
/// Supports single player, co-op campaigns, and team battles
/// </summary>
public class TurnManager : MonoBehaviour
{
    [Header("Game Mode")]
    public GameMode currentGameMode = GameMode.SinglePlayer;
    
    [Header("Turn Order")]
    [Tooltip("List of all players in turn order")]
    public List<PlayerData> turnOrder = new List<PlayerData>();
    
    [Tooltip("Current player index in turn order")]
    public int currentPlayerIndex = 0;
    
    [Tooltip("Current round number")]
    public int roundNumber = 1;
    
    [Header("Teams")]
    [Tooltip("Enable team-based gameplay")]
    public bool useTeams = false;
    
    [Tooltip("Team configurations")]
    public List<TeamData> teams = new List<TeamData>();
    
    [Header("Turn Settings")]
    [Tooltip("Time limit per turn in seconds (0 = no limit)")]
    public float turnTimeLimit = 0f;
    
    [Tooltip("Auto-end turn when all units have acted")]
    public bool autoEndTurnWhenDone = true;
    
    [Header("Initiative")]
    [Tooltip("How to determine turn order")]
    public InitiativeMode initiativeMode = InitiativeMode.Fixed;
    
    // Current turn state
    private float currentTurnTime = 0f;
    private bool isProcessingTurn = false;
    
    // Events
    public System.Action<PlayerData> OnPlayerTurnStart;
    public System.Action<PlayerData> OnPlayerTurnEnd;
    public System.Action<int> OnRoundStart;
    public System.Action<TeamData> OnTeamVictory;
    public System.Action OnGameEnd;
    
    // References
    private GameState gameState;
    private AIController aiController;
    private UIManager uiManager;
    
    void Start()
    {
        gameState = FindFirstObjectByType<GameState>();
        aiController = FindFirstObjectByType<AIController>();
        uiManager = FindFirstObjectByType<UIManager>();
        
        InitializeGameMode();
    }
    
    void InitializeGameMode()
    {
        switch (currentGameMode)
        {
            case GameMode.SinglePlayer:
                SetupSinglePlayer();
                break;
            case GameMode.LocalMultiplayer:
                SetupLocalMultiplayer();
                break;
            case GameMode.CoopCampaign:
                SetupCoopCampaign();
                break;
            case GameMode.Versus:
                SetupVersus();
                break;
            case GameMode.TeamBattle:
                SetupTeamBattle();
                break;
        }
        
        DetermineInitiative();
        StartFirstTurn();
    }
    
    void SetupSinglePlayer()
    {
        // Player always goes first in single player
        turnOrder.Clear();
        
        // Add human player
        turnOrder.Add(new PlayerData
        {
            playerID = 0,
            playerName = "Player",
            playerType = PlayerType.Human,
            teamID = 0,
            color = Color.blue,
            isLocalPlayer = true
        });
        
        // Add AI opponents
        turnOrder.Add(new PlayerData
        {
            playerID = 1,
            playerName = "AI Enemy 1",
            playerType = PlayerType.AIMedium,
            teamID = 1,
            color = Color.red
        });
        
        // Optional: Add more AI
        if (PlayerPrefs.GetInt("NumAIOpponents", 1) > 1)
        {
            turnOrder.Add(new PlayerData
            {
                playerID = 2,
                playerName = "AI Enemy 2",
                playerType = PlayerType.AIEasy,
                teamID = 1,
                color = Color.yellow
            });
        }
    }
    
    void SetupLocalMultiplayer()
    {
        // Local hot-seat multiplayer
        turnOrder.Clear();
        
        int numPlayers = PlayerPrefs.GetInt("NumLocalPlayers", 2);
        for (int i = 0; i < numPlayers; i++)
        {
            turnOrder.Add(new PlayerData
            {
                playerID = i,
                playerName = $"Player {i + 1}",
                playerType = PlayerType.Human,
                teamID = i, // Each player is their own team
                color = GetPlayerColor(i),
                isLocalPlayer = true
            });
        }
    }
    
    void SetupCoopCampaign()
    {
        // Multiple human players on same team vs AI
        turnOrder.Clear();
        useTeams = true;
        
        // Team 0: Human players
        TeamData humanTeam = new TeamData
        {
            teamID = 0,
            teamName = "Alliance",
            teamColor = Color.blue
        };
        
        // Add human players
        int numHumans = PlayerPrefs.GetInt("NumCoopPlayers", 2);
        for (int i = 0; i < numHumans; i++)
        {
            turnOrder.Add(new PlayerData
            {
                playerID = i,
                playerName = $"Player {i + 1}",
                playerType = PlayerType.Human,
                teamID = 0,
                color = Color.Lerp(Color.blue, Color.cyan, i * 0.3f),
                isLocalPlayer = true // For hot-seat co-op
            });
            humanTeam.memberPlayerIDs.Add(i);
        }
        
        // Team 1: AI enemies
        TeamData aiTeam = new TeamData
        {
            teamID = 1,
            teamName = "Enemy Forces",
            teamColor = Color.red
        };
        
        // Add AI enemies
        int numAI = PlayerPrefs.GetInt("NumAIEnemies", 2);
        for (int i = 0; i < numAI; i++)
        {
            int playerID = numHumans + i;
            turnOrder.Add(new PlayerData
            {
                playerID = playerID,
                playerName = $"Enemy {i + 1}",
                playerType = i == 0 ? PlayerType.AIHard : PlayerType.AIMedium,
                teamID = 1,
                color = Color.Lerp(Color.red, Color.magenta, i * 0.3f)
            });
            aiTeam.memberPlayerIDs.Add(playerID);
        }
        
        teams.Add(humanTeam);
        teams.Add(aiTeam);
    }
    
    void SetupVersus()
    {
        // Human vs Human
        turnOrder.Clear();
        
        // Player 1
        turnOrder.Add(new PlayerData
        {
            playerID = 0,
            playerName = "Player 1",
            playerType = PlayerType.Human,
            teamID = 0,
            color = Color.blue,
            isLocalPlayer = true
        });
        
        // Player 2
        turnOrder.Add(new PlayerData
        {
            playerID = 1,
            playerName = "Player 2",
            playerType = PlayerType.Human,
            teamID = 1,
            color = Color.red,
            isLocalPlayer = true
        });
    }
    
    void SetupTeamBattle()
    {
        // Team-based battle with mixed human/AI
        turnOrder.Clear();
        useTeams = true;
        
        // Configure based on settings
        // This is a placeholder - you'd configure this via UI
        SetupCoopCampaign(); // For now, use co-op setup
    }
    
    Color GetPlayerColor(int playerIndex)
    {
        Color[] colors = { Color.blue, Color.red, Color.green, Color.yellow };
        return colors[playerIndex % colors.Length];
    }
    
    void DetermineInitiative()
    {
        switch (initiativeMode)
        {
            case InitiativeMode.Fixed:
                // Keep current order (player first)
                break;
                
            case InitiativeMode.Random:
                // Randomize turn order
                turnOrder = turnOrder.OrderBy(x => Random.value).ToList();
                break;
                
            case InitiativeMode.Alternating:
                // Alternate between teams
                if (useTeams)
                {
                    turnOrder = turnOrder.OrderBy(p => p.teamID)
                                       .ThenBy(p => p.playerID).ToList();
                }
                break;
                
            case InitiativeMode.Speed:
                // Order by unit speed (future feature)
                // This would look at all units and order by average speed
                break;
        }
        
        Debug.Log($"Turn order determined: {string.Join(", ", turnOrder.Select(p => p.playerName))}");
    }
    
    void StartFirstTurn()
    {
        currentPlayerIndex = 0;
        roundNumber = 1;
        OnRoundStart?.Invoke(roundNumber);
        StartPlayerTurn(turnOrder[currentPlayerIndex]);
    }
    
    public void StartPlayerTurn(PlayerData player)
    {
        if (isProcessingTurn) return;
        
        isProcessingTurn = true;
        currentTurnTime = 0f;
        
        Debug.Log($"Starting turn for {player.playerName} (Round {roundNumber})");
        
        // Reset units for this player
        ResetPlayerUnits(player);
        
        // Fire event
        OnPlayerTurnStart?.Invoke(player);
        
        // Handle AI turns
        if (player.IsAI())
        {
            StartCoroutine(ProcessAITurn(player));
        }
        else
        {
            // Human turn - enable UI controls
            EnablePlayerControls(player);
        }
    }
    
    public void EndCurrentTurn()
    {
        if (!isProcessingTurn) return;
        
        PlayerData currentPlayer = turnOrder[currentPlayerIndex];
        
        Debug.Log($"{currentPlayer.playerName} ends turn");
        
        // Fire event
        OnPlayerTurnEnd?.Invoke(currentPlayer);
        
        // Check victory conditions
        if (CheckVictoryConditions())
        {
            EndGame();
            return;
        }
        
        // Move to next player
        currentPlayerIndex++;
        
        // Check if round is complete
        if (currentPlayerIndex >= turnOrder.Count)
        {
            currentPlayerIndex = 0;
            roundNumber++;
            OnRoundStart?.Invoke(roundNumber);
        }
        
        isProcessingTurn = false;
        
        // Start next turn
        StartPlayerTurn(turnOrder[currentPlayerIndex]);
    }
    
    bool CheckVictoryConditions()
    {
        if (useTeams)
        {
            // Team victory: all enemy teams eliminated
            foreach (TeamData team in teams)
            {
                bool hasActiveUnits = false;
                foreach (PlayerData player in turnOrder.Where(p => p.teamID == team.teamID))
                {
                    if (PlayerHasActiveUnits(player))
                    {
                        hasActiveUnits = true;
                        break;
                    }
                }
                
                if (!hasActiveUnits)
                {
                    // This team is eliminated
                    team.isEliminated = true;
                }
            }
            
            // Check if only one team remains
            var activeTeams = teams.Where(t => !t.isEliminated).ToList();
            if (activeTeams.Count == 1)
            {
                OnTeamVictory?.Invoke(activeTeams[0]);
                return true;
            }
        }
        else
        {
            // Individual victory: last player standing
            var activePlayers = turnOrder.Where(p => PlayerHasActiveUnits(p)).ToList();
            if (activePlayers.Count <= 1)
            {
                if (activePlayers.Count == 1)
                {
                    Debug.Log($"Victory! {activePlayers[0].playerName} wins!");
                }
                return true;
            }
        }
        
        return false;
    }
    
    void Update()
    {
        // Handle turn time limits
        if (isProcessingTurn && turnTimeLimit > 0)
        {
            currentTurnTime += Time.deltaTime;
            
            if (currentTurnTime >= turnTimeLimit)
            {
                Debug.Log("Turn time limit reached - auto-ending turn");
                EndCurrentTurn();
            }
        }
        
        // Auto-end turn if all units have acted
        if (isProcessingTurn && autoEndTurnWhenDone)
        {
            PlayerData currentPlayer = turnOrder[currentPlayerIndex];
            if (!currentPlayer.IsAI() && AllPlayerUnitsHaveActed(currentPlayer))
            {
                Debug.Log("All units have acted - auto-ending turn");
                EndCurrentTurn();
            }
        }
    }
    
    // Helper methods
    void ResetPlayerUnits(PlayerData player)
    {
        Unit[] allUnits = FindObjectsByType<Unit>(FindObjectsSortMode.None);
        foreach (Unit unit in allUnits)
        {
            if (unit.GetOwner() == player.playerID)
            {
                unit.ResetForNewTurn();
            }
        }
    }
    
    bool PlayerHasActiveUnits(PlayerData player)
    {
        Unit[] allUnits = FindObjectsByType<Unit>(FindObjectsSortMode.None);
        return allUnits.Any(u => u.GetOwner() == player.playerID && u.currentHealth > 0);
    }
    
    bool AllPlayerUnitsHaveActed(PlayerData player)
    {
        Unit[] allUnits = FindObjectsByType<Unit>(FindObjectsSortMode.None);
        var playerUnits = allUnits.Where(u => u.GetOwner() == player.playerID && u.currentHealth > 0);
        
        foreach (Unit unit in playerUnits)
        {
            if (!unit.hasMoved || !unit.hasAttacked)
                return false;
        }
        
        return playerUnits.Any(); // Return true only if there are units
    }
    
    void EnablePlayerControls(PlayerData player)
    {
        // Enable UI buttons for human players
        if (uiManager != null)
        {
            uiManager.SetActivePlayer(player);
        }
    }
    
    System.Collections.IEnumerator ProcessAITurn(PlayerData aiPlayer)
    {
        yield return new WaitForSeconds(1f); // Thinking time
        
        if (aiController != null)
        {
            // Use existing AI controller with player data
            Player oldStylePlayer = new Player(aiPlayer.playerID, aiPlayer.playerName, 
                                              aiPlayer.playerType, aiPlayer.color);
            aiController.ExecuteAITurn(oldStylePlayer, () => EndCurrentTurn());
        }
        else
        {
            // No AI controller - just end turn
            yield return new WaitForSeconds(2f);
            EndCurrentTurn();
        }
    }
    
    void EndGame()
    {
        isProcessingTurn = false;
        OnGameEnd?.Invoke();
        Debug.Log("Game has ended!");
    }
    
    // Public methods for UI interaction
    public PlayerData GetCurrentPlayer()
    {
        return currentPlayerIndex < turnOrder.Count ? turnOrder[currentPlayerIndex] : null;
    }
    
    public bool IsCurrentPlayerHuman()
    {
        PlayerData current = GetCurrentPlayer();
        return current != null && !current.IsAI();
    }
    
    public bool CanEndTurn()
    {
        // Can end turn if it's a human player's turn and not processing
        return IsCurrentPlayerHuman() && isProcessingTurn;
    }
    
    public float GetTurnTimeRemaining()
    {
        if (turnTimeLimit <= 0) return -1;
        return Mathf.Max(0, turnTimeLimit - currentTurnTime);
    }
    
    public List<PlayerData> GetPlayersInTeam(int teamID)
    {
        return turnOrder.Where(p => p.teamID == teamID).ToList();
    }
}

// Game mode enum
public enum GameMode
{
    SinglePlayer,    // One human vs AI(s)
    LocalMultiplayer, // Multiple humans hot-seat
    CoopCampaign,    // Multiple humans vs AI
    Versus,          // Human vs Human
    TeamBattle       // Teams of mixed human/AI
}

// Initiative determination
public enum InitiativeMode
{
    Fixed,       // Predetermined order
    Random,      // Random each game
    Alternating, // Alternate between teams
    Speed        // Based on unit stats
}

// Enhanced player data
[System.Serializable]
public class PlayerData
{
    public int playerID;
    public string playerName;
    public PlayerType playerType;
    public int teamID = -1; // -1 = no team
    public Color color;
    public bool isLocalPlayer = false; // For network play later
    public bool isEliminated = false;
    
    public bool IsAI()
    {
        return playerType != PlayerType.Human;
    }
    
    public bool IsOnTeam(int checkTeamID)
    {
        return teamID == checkTeamID;
    }
}

// Team data for team-based modes
[System.Serializable]
public class TeamData
{
    public int teamID;
    public string teamName;
    public Color teamColor;
    public bool isEliminated = false;
    public List<int> memberPlayerIDs = new List<int>();
}
