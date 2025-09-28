using UnityEngine;
using UnityEngine.UI;
using TMPro;
using System.Linq;

/// <summary>
/// Controls turn-based UI elements and conditional buttons
/// Manages the display and interaction of turn-specific UI
/// </summary>
public class TurnUIController : MonoBehaviour
{
    [Header("Turn Info Display")]
    public TextMeshProUGUI currentPlayerText;
    public TextMeshProUGUI roundNumberText;
    public TextMeshProUGUI turnTimerText;
    public TextMeshProUGUI teamInfoText;
    public TextMeshProUGUI phaseText;
    
    [Header("Control Buttons")]
    public Button endTurnButton;
    public Button undoMoveButton;
    public Button pauseButton;
    public Button concedeButton;
    public Button autoPlayButton;
    
    [Header("Button Conditions")]
    [Tooltip("Only show end turn for human players")]
    public bool hideEndTurnForAI = true;
    
    [Tooltip("Show undo only if move hasn't been confirmed")]
    public bool conditionalUndo = true;
    
    [Tooltip("Show auto-play for human players")]
    public bool allowAutoPlay = false;
    
    [Header("Visual Feedback")]
    public Color humanPlayerColor = Color.blue;
    public Color aiPlayerColor = Color.red;
    public Color allyColor = Color.cyan;
    public Color enemyColor = Color.magenta;
    public Color warningColor = Color.yellow;
    
    [Header("UI Panels")]
    public GameObject turnInfoPanel;
    public GameObject actionButtonPanel;
    public GameObject teamInfoPanel;
    
    // References
    private TurnManager turnManager;
    private GameState gameState;
    
    // State tracking
    private bool canUndo = false;
    private Unit lastMovedUnit = null;
    private Vector3 lastUnitPosition;
    private Tile lastUnitTile;
    private bool isPaused = false;
    
    void Start()
    {
        turnManager = FindFirstObjectByType<TurnManager>();
        gameState = FindFirstObjectByType<GameState>();
        
        // Subscribe to events
        if (turnManager != null)
        {
            turnManager.OnPlayerTurnStart += OnPlayerTurnStart;
            turnManager.OnPlayerTurnEnd += OnPlayerTurnEnd;
            turnManager.OnRoundStart += OnRoundStart;
            turnManager.OnTeamVictory += OnTeamVictory;
            turnManager.OnGameEnd += OnGameEnd;
        }
        
        if (gameState != null)
        {
            gameState.OnUnitSelected += OnUnitSelected;
            gameState.OnPhaseChanged += OnPhaseChanged;
        }
        
        // Button listeners
        if (endTurnButton != null)
            endTurnButton.onClick.AddListener(OnEndTurnClicked);
        if (undoMoveButton != null)
            undoMoveButton.onClick.AddListener(OnUndoClicked);
        if (pauseButton != null)
            pauseButton.onClick.AddListener(OnPauseClicked);
        if (concedeButton != null)
            concedeButton.onClick.AddListener(OnConcedeClicked);
        if (autoPlayButton != null)
            autoPlayButton.onClick.AddListener(OnAutoPlayClicked);
        
        UpdateButtonStates();
    }
    
    void OnPlayerTurnStart(PlayerData player)
    {
        // Update display
        if (currentPlayerText != null)
        {
            currentPlayerText.text = $"{player.playerName}'s Turn";
            currentPlayerText.color = player.color;
            
            // Add icon or indicator for AI players
            if (player.IsAI())
            {
                currentPlayerText.text += " 🤖";
            }
        }
        
        // Show/hide buttons based on player type
        UpdateButtonStates();
        
        // Reset undo state
        canUndo = false;
        lastMovedUnit = null;
        
        // Special UI for different game modes
        if (turnManager.useTeams && teamInfoText != null)
        {
            TeamData team = turnManager.teams.Find(t => t.teamID == player.teamID);
            if (team != null)
            {
                teamInfoText.text = $"Team: {team.teamName}";
                teamInfoText.color = team.teamColor;
                
                // Show team panel
                if (teamInfoPanel != null)
                    teamInfoPanel.SetActive(true);
            }
        }
        else
        {
            // Hide team panel in non-team modes
            if (teamInfoPanel != null)
                teamInfoPanel.SetActive(false);
        }
        
        // Animate turn transition
        StartCoroutine(AnimateTurnTransition(player));
    }
    
    void OnRoundStart(int roundNumber)
    {
        if (roundNumberText != null)
        {
            roundNumberText.text = $"Round {roundNumber}";
            
            // Special formatting for milestone rounds
            if (roundNumber % 5 == 0)
            {
                roundNumberText.color = Color.yellow;
                roundNumberText.fontSize = 28;
            }
            else
            {
                roundNumberText.color = Color.white;
                roundNumberText.fontSize = 24;
            }
        }
    }
    
    void OnPhaseChanged(GamePhase newPhase)
    {
        if (phaseText != null)
        {
            switch (newPhase)
            {
                case GamePhase.UnitSelection:
                    phaseText.text = "Select a Unit";
                    phaseText.color = Color.white;
                    break;
                case GamePhase.UnitMovement:
                    phaseText.text = "Move Unit";
                    phaseText.color = Color.green;
                    break;
                case GamePhase.UnitAttack:
                    phaseText.text = "Attack Phase";
                    phaseText.color = Color.red;
                    break;
                case GamePhase.TurnEnd:
                    phaseText.text = "Turn Ending...";
                    phaseText.color = Color.gray;
                    break;
                case GamePhase.GameOver:
                    phaseText.text = "Game Over";
                    phaseText.color = warningColor;
                    break;
            }
        }
    }
    
    void OnUnitSelected(Unit unit)
    {
        if (unit != null && unit.GetOwner() == turnManager.GetCurrentPlayer()?.playerID)
        {
            // Track for potential undo
            if (!unit.hasMoved)
            {
                lastMovedUnit = unit;
                lastUnitPosition = unit.transform.position;
                lastUnitTile = unit.GetCurrentTile();
            }
        }
    }
    
    void Update()
    {
        // Update turn timer if applicable
        if (turnTimerText != null && turnManager != null)
        {
            float timeRemaining = turnManager.GetTurnTimeRemaining();
            if (timeRemaining > 0)
            {
                turnTimerText.gameObject.SetActive(true);
                turnTimerText.text = FormatTime(timeRemaining);
                
                // Color code based on time remaining
                if (timeRemaining < 10)
                {
                    turnTimerText.color = Color.red;
                    // Flash warning
                    turnTimerText.fontSize = 24 + Mathf.Sin(Time.time * 10) * 2;
                }
                else if (timeRemaining < 30)
                {
                    turnTimerText.color = warningColor;
                    turnTimerText.fontSize = 22;
                }
                else
                {
                    turnTimerText.color = Color.white;
                    turnTimerText.fontSize = 20;
                }
            }
            else
            {
                turnTimerText.gameObject.SetActive(false);
            }
        }
        
        // Conditional button updates
        UpdateConditionalButtons();
    }
    
    string FormatTime(float seconds)
    {
        int minutes = Mathf.FloorToInt(seconds / 60);
        int secs = Mathf.FloorToInt(seconds % 60);
        return $"{minutes:00}:{secs:00}";
    }
    
    void UpdateButtonStates()
    {
        if (turnManager == null) return;
        
        PlayerData currentPlayer = turnManager.GetCurrentPlayer();
        bool isHuman = currentPlayer != null && !currentPlayer.IsAI();
        
        // End Turn button - only for human players
        if (endTurnButton != null)
        {
            endTurnButton.gameObject.SetActive(!hideEndTurnForAI || isHuman);
            endTurnButton.interactable = turnManager.CanEndTurn();
            
            // Change button text based on state
            TextMeshProUGUI buttonText = endTurnButton.GetComponentInChildren<TextMeshProUGUI>();
            if (buttonText != null)
            {
                if (!isHuman)
                {
                    buttonText.text = "AI Thinking...";
                    endTurnButton.interactable = false;
                }
                else if (turnManager.autoEndTurnWhenDone)
                {
                    buttonText.text = "End Turn (Auto)";
                }
                else
                {
                    buttonText.text = "End Turn";
                }
            }
        }
        
        // Undo button
        if (undoMoveButton != null)
        {
            undoMoveButton.gameObject.SetActive(isHuman && conditionalUndo);
            undoMoveButton.interactable = canUndo;
        }
        
        // Pause button - always available during gameplay
        if (pauseButton != null)
        {
            TextMeshProUGUI pauseText = pauseButton.GetComponentInChildren<TextMeshProUGUI>();
            if (pauseText != null)
            {
                pauseText.text = isPaused ? "Resume" : "Pause";
            }
        }
        
        // Concede button - only in competitive modes
        if (concedeButton != null)
        {
            bool showConcede = isHuman && 
                (turnManager.currentGameMode == GameMode.Versus || 
                 turnManager.currentGameMode == GameMode.TeamBattle);
            concedeButton.gameObject.SetActive(showConcede);
        }
        
        // Auto-play button - for testing
        if (autoPlayButton != null)
        {
            autoPlayButton.gameObject.SetActive(allowAutoPlay && isHuman);
        }
    }
    
    void UpdateConditionalButtons()
    {
        // Dynamic button state based on game state
        if (gameState != null && gameState.GetSelectedUnit() != null)
        {
            Unit selected = gameState.GetSelectedUnit();
            
            // Track for undo
            if (selected == lastMovedUnit && selected.hasMoved && !selected.hasAttacked)
            {
                canUndo = true;
            }
        }
        
        // Update undo button state
        if (undoMoveButton != null)
        {
            undoMoveButton.interactable = canUndo && lastMovedUnit != null && !lastMovedUnit.hasAttacked;
            
            // Visual feedback
            if (undoMoveButton.interactable)
            {
                ColorBlock colors = undoMoveButton.colors;
                colors.normalColor = Color.yellow;
                undoMoveButton.colors = colors;
            }
            else
            {
                ColorBlock colors = undoMoveButton.colors;
                colors.normalColor = Color.gray;
                undoMoveButton.colors = colors;
            }
        }
    }
    
    // Button click handlers
    void OnEndTurnClicked()
    {
        if (turnManager != null && turnManager.CanEndTurn())
        {
            // Optional: Confirm dialog for important turns
            if (gameState != null)
            {
                // Check if any units haven't acted
                Unit[] allUnits = FindObjectsByType<Unit>(FindObjectsSortMode.None);
                var currentPlayerUnits = allUnits.Where(u => 
                    u.GetOwner() == turnManager.GetCurrentPlayer().playerID && 
                    u.currentHealth > 0);
                
                int unmovedUnits = currentPlayerUnits.Count(u => !u.hasMoved);
                int unattackedUnits = currentPlayerUnits.Count(u => !u.hasAttacked);
                
                if (unmovedUnits > 0 || unattackedUnits > 0)
                {
                    // Show warning
                    string warning = $"Warning: {unmovedUnits} units haven't moved, {unattackedUnits} haven't attacked.";
                    Debug.Log(warning);
                    
                    // In a full implementation, show a confirmation dialog
                    // For now, just proceed
                }
            }
            
            turnManager.EndCurrentTurn();
        }
    }
    
    void OnUndoClicked()
    {
        if (canUndo && lastMovedUnit != null && lastUnitTile != null)
        {
            // Undo the last move
            lastMovedUnit.transform.position = lastUnitPosition;
            lastMovedUnit.hasMoved = false;
            
            // Update tile occupancy
            Tile currentTile = lastMovedUnit.GetCurrentTile();
            if (currentTile != null)
            {
                currentTile.SetUnit(null);
            }
            lastUnitTile.SetUnit(lastMovedUnit);
            
            canUndo = false;
            
            Debug.Log($"Undid move for {lastMovedUnit.name}");
            
            // Refresh game state
            if (gameState != null)
            {
                gameState.SelectUnit(lastMovedUnit);
            }
            
            // Visual feedback
            StartCoroutine(FlashUnit(lastMovedUnit));
        }
    }
    
    void OnPauseClicked()
    {
        isPaused = !isPaused;
        
        if (isPaused)
        {
            Time.timeScale = 0f;
            Debug.Log("Game Paused");
            // TODO: Show pause menu UI
        }
        else
        {
            Time.timeScale = 1f;
            Debug.Log("Game Resumed");
            // TODO: Hide pause menu UI
        }
        
        UpdateButtonStates();
    }
    
    void OnConcedeClicked()
    {
        // Concede confirmation
        Debug.Log("Concede button clicked - showing confirmation");
        
        // In a full implementation, show a confirmation dialog
        // For now, just log
        if (turnManager != null)
        {
            PlayerData currentPlayer = turnManager.GetCurrentPlayer();
            Debug.Log($"{currentPlayer.playerName} wants to concede!");
            
            // TODO: Show confirmation dialog
            // If confirmed: turnManager.EndGame();
        }
    }
    
    void OnAutoPlayClicked()
    {
        // Auto-play current turn (for testing)
        Debug.Log("Auto-play activated for current turn");
        
        // TODO: Implement basic auto-play logic for testing
        // This would make reasonable moves for the human player
    }
    
    void OnTeamVictory(TeamData winningTeam)
    {
        Debug.Log($"Team {winningTeam.teamName} wins!");
        
        // Update UI for victory
        if (currentPlayerText != null)
        {
            currentPlayerText.text = $"🏆 {winningTeam.teamName} Victory! 🏆";
            currentPlayerText.color = winningTeam.teamColor;
        }
        
        // Disable all buttons except pause
        DisableGameButtons();
    }
    
    void OnGameEnd()
    {
        Debug.Log("Game has ended");
        
        // Update UI
        if (phaseText != null)
        {
            phaseText.text = "Game Over";
            phaseText.color = Color.white;
        }
        
        DisableGameButtons();
    }
    
    void OnPlayerTurnEnd(PlayerData player)
    {
        // Clean up any turn-specific UI
        canUndo = false;
        lastMovedUnit = null;
    }
    
    void DisableGameButtons()
    {
        if (endTurnButton != null) endTurnButton.interactable = false;
        if (undoMoveButton != null) undoMoveButton.interactable = false;
        if (concedeButton != null) concedeButton.interactable = false;
        if (autoPlayButton != null) autoPlayButton.interactable = false;
    }
    
    // Visual feedback coroutines
    System.Collections.IEnumerator AnimateTurnTransition(PlayerData newPlayer)
    {
        // Simple turn transition animation
        if (turnInfoPanel != null)
        {
            // Fade out
            CanvasGroup canvasGroup = turnInfoPanel.GetComponent<CanvasGroup>();
            if (canvasGroup == null)
                canvasGroup = turnInfoPanel.AddComponent<CanvasGroup>();
            
            for (float t = 1f; t > 0; t -= Time.deltaTime * 2)
            {
                canvasGroup.alpha = t;
                yield return null;
            }
            
            // Update content (already done in OnPlayerTurnStart)
            
            // Fade in
            for (float t = 0; t < 1f; t += Time.deltaTime * 2)
            {
                canvasGroup.alpha = t;
                yield return null;
            }
            
            canvasGroup.alpha = 1f;
        }
    }
    
    System.Collections.IEnumerator FlashUnit(Unit unit)
    {
        if (unit == null) yield break;
        
        SpriteRenderer sprite = unit.GetComponent<SpriteRenderer>();
        if (sprite == null) yield break;
        
        Color originalColor = sprite.color;
        
        // Flash yellow
        for (int i = 0; i < 3; i++)
        {
            sprite.color = Color.yellow;
            yield return new WaitForSeconds(0.1f);
            sprite.color = originalColor;
            yield return new WaitForSeconds(0.1f);
        }
    }
}
