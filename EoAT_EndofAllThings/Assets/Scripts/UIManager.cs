using UnityEngine;
using UnityEngine.UI;
using TMPro;

/// <summary>
/// UI Manager for EoAT strategy game - handles all user interface elements
/// Similar to Wesnoth's UI with turn info, unit stats, and game controls
/// </summary>
public class UIManager : MonoBehaviour
{
    [Header("UI Panels")]
    [Tooltip("Main game UI canvas")]
    public Canvas gameCanvas;
    
    [Tooltip("Panel showing current turn info")]
    public GameObject turnInfoPanel;
    
    [Tooltip("Panel showing selected unit info")]
    public GameObject unitInfoPanel;
    
    [Tooltip("Panel with game controls")]
    public GameObject controlsPanel;
    
    [Header("Turn Info UI")]
    [Tooltip("Text showing current turn number")]
    public TextMeshProUGUI turnNumberText;
    
    [Tooltip("Text showing current player")]
    public TextMeshProUGUI currentPlayerText;
    
    [Tooltip("Text showing current game phase")]
    public TextMeshProUGUI gamePhaseText;
    
    [Tooltip("Button to end current turn")]
    public Button endTurnButton;
    
    [Header("Unit Info UI")]
    [Tooltip("Text showing selected unit name")]
    public TextMeshProUGUI unitNameText;
    
    [Tooltip("Text showing unit health")]
    public TextMeshProUGUI unitHealthText;
    
    [Tooltip("Text showing unit stats")]
    public TextMeshProUGUI unitStatsText;
    
    [Tooltip("Text showing unit movement status")]
    public TextMeshProUGUI unitMovementText;
    
    [Header("Controls UI")]
    [Tooltip("Text showing current controls")]
    public TextMeshProUGUI controlsText;
    
    [Tooltip("Button to deselect current unit")]
    public Button deselectButton;
    
    // References
    private GameState gameState;
    
    void Start()
    {
        // Find game state
        gameState = FindFirstObjectByType<GameState>();
        
        // Subscribe to game state events
        if (gameState != null)
        {
            gameState.OnTurnChanged += UpdateTurnDisplay;
            gameState.OnPlayerChanged += UpdatePlayerDisplay;
            gameState.OnPhaseChanged += UpdatePhaseDisplay;
            gameState.OnUnitSelected += UpdateUnitDisplay;
        }
        
        // Setup button events
        if (endTurnButton != null)
        {
            endTurnButton.onClick.AddListener(EndTurn);
        }
        
        if (deselectButton != null)
        {
            deselectButton.onClick.AddListener(DeselectUnit);
        }
        
        // Initialize UI
        UpdateAllDisplays();
        
        Debug.Log("UI Manager initialized");
    }
    
    void UpdateAllDisplays()
    {
        if (gameState == null) return;
        
        UpdateTurnDisplay(gameState.GetTurnNumber());
        UpdatePlayerDisplay(gameState.GetCurrentPlayer());
        UpdatePhaseDisplay(gameState.GetCurrentPhase());
        UpdateUnitDisplay(gameState.GetSelectedUnit());
        UpdateControlsDisplay();
    }
    
    void UpdateTurnDisplay(int turnNumber)
    {
        if (turnNumberText != null)
        {
            turnNumberText.text = $"Turn {turnNumber}";
        }
    }
    
    void UpdatePlayerDisplay(int currentPlayer)
    {
        if (currentPlayerText != null)
        {
            string playerName = GetPlayerName(currentPlayer);
            Color playerColor = GetPlayerColor(currentPlayer);
            
            currentPlayerText.text = $"{playerName}'s Turn";
            currentPlayerText.color = playerColor;
        }
    }
    
    void UpdatePhaseDisplay(GamePhase phase)
    {
        if (gamePhaseText != null)
        {
            string phaseText = phase switch
            {
                GamePhase.UnitSelection => "Select Unit",
                GamePhase.UnitMovement => "Move Unit", 
                GamePhase.UnitAttack => "Attack Target",
                GamePhase.TurnEnd => "Processing...",
                GamePhase.GameOver => "Game Over",
                _ => "Unknown"
            };
            
            gamePhaseText.text = phaseText;
        }
    }
    
    void UpdateUnitDisplay(Unit selectedUnit)
    {
        if (unitInfoPanel != null)
        {
            // Show/hide unit info panel
            unitInfoPanel.SetActive(selectedUnit != null);
        }
        
        if (selectedUnit != null)
        {
            // Update unit info
            if (unitNameText != null)
            {
                unitNameText.text = selectedUnit.unitName;
                unitNameText.color = GetPlayerColor(selectedUnit.GetOwner());
            }
            
            if (unitHealthText != null)
            {
                unitHealthText.text = $"Health: {selectedUnit.currentHealth}/{selectedUnit.maxHealth}";
                
                // Color code health
                float healthPercent = (float)selectedUnit.currentHealth / selectedUnit.maxHealth;
                if (healthPercent > 0.6f)
                    unitHealthText.color = Color.green;
                else if (healthPercent > 0.3f)
                    unitHealthText.color = Color.yellow;
                else
                    unitHealthText.color = Color.red;
            }
            
            if (unitStatsText != null)
            {
                unitStatsText.text = $"ATK: {selectedUnit.GetAttackPower()} | DEF: {selectedUnit.GetDefense()}\n" +
                                   $"Move: {selectedUnit.GetMovementRange()} | Range: {selectedUnit.GetAttackRange()}";
            }
            
            if (unitMovementText != null)
            {
                string moveStatus = selectedUnit.CanMoveThisTurn() ? "Can Move" : "Already Moved";
                string attackStatus = selectedUnit.CanAttackThisTurn() ? "Can Attack" : "Already Attacked";
                
                unitMovementText.text = $"{moveStatus} | {attackStatus}";
                unitMovementText.color = (selectedUnit.CanMoveThisTurn() || selectedUnit.CanAttackThisTurn()) ? 
                                        Color.green : Color.gray;
            }
        }
    }
    
    void UpdateControlsDisplay()
    {
        if (controlsText != null)
        {
            string controls = "Controls:\n" +
                            "• Click Unit: Select\n" +
                            "• Click Tile: Move/Attack\n" +
                            "• Arrow Keys: Pan Camera\n" +
                            "• +/-: Zoom\n" +
                            "• End Turn: Next Player";
            
            controlsText.text = controls;
        }
    }
    
    string GetPlayerName(int playerIndex)
    {
        return playerIndex switch
        {
            0 => "Player 1",
            1 => "Player 2", 
            2 => "Player 3",
            3 => "Player 4",
            _ => $"Player {playerIndex + 1}"
        };
    }
    
    Color GetPlayerColor(int playerIndex)
    {
        return playerIndex switch
        {
            0 => Color.blue,
            1 => Color.red,
            2 => Color.green,
            3 => Color.yellow,
            _ => Color.white
        };
    }
    
    void EndTurn()
    {
        if (gameState != null)
        {
            gameState.EndTurn();
        }
    }
    
    void DeselectUnit()
    {
        if (gameState != null)
        {
            gameState.SelectUnit(null);
        }
    }
    
    // Public methods for external systems
    public void ShowMessage(string message, float duration = 3f)
    {
        // Could implement popup messages here
        Debug.Log($"Game Message: {message}");
    }
    
    public void ShowCombatResult(Unit attacker, Unit defender, int damage)
    {
        string message = $"{attacker.unitName} attacks {defender.unitName} for {damage} damage!";
        ShowMessage(message);
    }
    
    /// <summary>
    /// Sets the active player and updates UI accordingly
    /// Called by TurnManager when switching players
    /// </summary>
    public void SetActivePlayer(PlayerData player)
    {
        if (player != null)
        {
            // Update the player display with the player ID
            UpdatePlayerDisplay(player.playerID);
            
            // Update player name with custom name if provided
            if (currentPlayerText != null && !string.IsNullOrEmpty(player.playerName))
            {
                currentPlayerText.text = $"{player.playerName}'s Turn";
                currentPlayerText.color = player.color != Color.clear ? player.color : GetPlayerColor(player.playerID);
            }
            
            // Enable/disable end turn button based on player type
            if (endTurnButton != null)
            {
                // Only enable for human players
                endTurnButton.interactable = !player.IsAI();
            }
            
            // Show/hide controls based on player type
            if (controlsPanel != null)
            {
                // Show controls only for human players
                controlsPanel.SetActive(!player.IsAI());
            }
            
            // Log for debugging
            Debug.Log($"Active player set to: {player.playerName} (ID: {player.playerID}, Type: {player.playerType})");
        }
    }
    
    void OnDestroy()
    {
        // Unsubscribe from events
        if (gameState != null)
        {
            gameState.OnTurnChanged -= UpdateTurnDisplay;
            gameState.OnPlayerChanged -= UpdatePlayerDisplay;
            gameState.OnPhaseChanged -= UpdatePhaseDisplay;
            gameState.OnUnitSelected -= UpdateUnitDisplay;
        }
    }
}





