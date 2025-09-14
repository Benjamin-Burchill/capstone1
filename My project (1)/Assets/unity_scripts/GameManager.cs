using UnityEngine;
using UnityEngine.UI;
using System.Collections.Generic;

/// <summary>
/// Main game manager for the Goblin RPG
/// Handles spawning, game state, UI, and overall coordination
/// </summary>
public class GameManager : MonoBehaviour
{
    [Header("Game Settings")]
    [Tooltip("Number of goblin packs to spawn")]
    public int goblinPackCount = 5;
    
    [Tooltip("Goblins per pack (min-max)")]
    public Vector2Int goblinsPerPack = new Vector2Int(2, 4);
    
    [Tooltip("Number of mammoths to spawn")]
    public int mammothCount = 2;
    
    [Tooltip("World size (300x300m)")]
    public float worldSize = 300f;
    
    [Header("Prefabs")]
    [Tooltip("Player prefab")]
    public GameObject playerPrefab;
    
    [Tooltip("Goblin prefab")]
    public GameObject goblinPrefab;
    
    [Tooltip("Mammoth prefab")]
    public GameObject mammothPrefab;
    
    [Tooltip("Ground plane prefab")]
    public GameObject groundPrefab;
    
    [Header("UI")]
    [Tooltip("Main game UI canvas")]
    public Canvas gameUI;
    
    [Tooltip("Status text element")]
    public Text statusText;
    
    [Tooltip("Game over panel")]
    public GameObject gameOverPanel;
    
    // Game state
    private GameObject player;
    private List<GameObject> goblins = new List<GameObject>();
    private int goblinsKilled = 0;
    private float gameTime = 0f;
    private bool gameActive = true;
    
    void Start()
    {
        InitializeGame();
    }
    
    void Update()
    {
        if (!gameActive) return;
        
        gameTime += Time.deltaTime;
        UpdateUI();
        CheckWinCondition();
    }
    
    void InitializeGame()
    {
        Debug.Log("Initializing Goblin RPG...");
        
        // Create ground
        if (groundPrefab != null)
        {
            GameObject ground = Instantiate(groundPrefab);
            ground.transform.localScale = new Vector3(worldSize / 10f, 1, worldSize / 10f);
            ground.name = "Ground";
        }
        
        // Spawn player
        SpawnPlayer();
        
        // Spawn goblins
        SpawnGoblins();
        
        // Spawn mammoths
        SpawnMammoths();
        
        // Setup camera
        SetupCamera();
        
        Debug.Log($"Game initialized: {goblins.Count} goblins and {mammothCount} mammoths spawned");
    }
    
    void SpawnPlayer()
    {
        if (playerPrefab != null)
        {
            player = Instantiate(playerPrefab, Vector3.up, Quaternion.identity);
            player.name = "Player";
            player.tag = "Player";
            
            // Add health system if not present
            if (player.GetComponent<HealthSystem>() == null)
            {
                HealthSystem health = player.AddComponent<HealthSystem>();
                health.maxHealth = 100;
                health.OnDeath += OnPlayerDeath;
            }
        }
        else
        {
            Debug.LogError("No player prefab assigned!");
        }
    }
    
    void SpawnGoblins()
    {
        if (goblinPrefab == null)
        {
            Debug.LogError("No goblin prefab assigned!");
            return;
        }
        
        float spawnRadius = worldSize * 0.4f; // Spawn within 40% of world size
        
        for (int pack = 0; pack < goblinPackCount; pack++)
        {
            // Random pack center
            Vector2 packCenter = Random.insideUnitCircle * spawnRadius;
            Vector3 packPosition = new Vector3(packCenter.x, 0, packCenter.y);
            
            // Spawn goblins in this pack
            int packSize = Random.Range(goblinsPerPack.x, goblinsPerPack.y + 1);
            
            for (int i = 0; i < packSize; i++)
            {
                // Random offset within pack
                Vector2 offset = Random.insideUnitCircle * 8f;
                Vector3 goblinPos = packPosition + new Vector3(offset.x, 0, offset.y);
                
                // Spawn goblin
                GameObject goblin = Instantiate(goblinPrefab, goblinPos + Vector3.up * 0.5f, Quaternion.identity);
                goblin.name = $"Goblin_{goblins.Count}";
                goblin.tag = "Enemy";
                
                // Setup goblin AI
                GoblinAI ai = goblin.GetComponent<GoblinAI>();
                if (ai != null && player != null)
                {
                    ai.player = player.transform;
                }
                
                // Setup health system
                HealthSystem health = goblin.GetComponent<HealthSystem>();
                if (health == null)
                {
                    health = goblin.AddComponent<HealthSystem>();
                }
                health.maxHealth = 30;
                health.OnDeath += () => OnGoblinDeath(goblin);
                
                goblins.Add(goblin);
            }
        }
    }
    
    void SpawnMammoths()
    {
        if (mammothPrefab == null)
        {
            Debug.LogError("No mammoth prefab assigned!");
            return;
        }
        
        float spawnRadius = worldSize * 0.3f; // Spawn mammoths further from center
        
        for (int i = 0; i < mammothCount; i++)
        {
            // Random position, but not too close to player spawn
            Vector2 randomPos;
            do
            {
                randomPos = Random.insideUnitCircle * spawnRadius;
            }
            while (randomPos.magnitude < 30f); // At least 30 units from center
            
            Vector3 mammothPos = new Vector3(randomPos.x, 1f, randomPos.y); // Higher Y for large creature
            
            // Spawn mammoth
            GameObject mammoth = Instantiate(mammothPrefab, mammothPos, Quaternion.identity);
            mammoth.name = $"Mammoth_{i}";
            mammoth.tag = "Enemy";
            
            // Setup mammoth AI
            MammothAI ai = mammoth.GetComponent<MammothAI>();
            if (ai != null && player != null)
            {
                ai.target = player.transform;
            }
            
            // Setup health system
            HealthSystem health = mammoth.GetComponent<HealthSystem>();
            if (health == null)
            {
                health = mammoth.AddComponent<HealthSystem>();
            }
            health.maxHealth = 150;
            health.currentHealth = 150;
            health.OnDeath += () => OnMammothDeath(mammoth);
            
            // Make mammoth provoked when damaged
            health.OnDamageTaken += (damage) => {
                MammothAI mammothAI = mammoth.GetComponent<MammothAI>();
                if (mammothAI != null)
                {
                    mammothAI.BecomeProvoked($"Took {damage} damage!");
                }
            };
            
            Debug.Log($"Spawned {mammoth.name} at {mammothPos}");
        }
    }
    
    void OnMammothDeath(GameObject mammoth)
    {
        Debug.Log($"Mammoth {mammoth.name} was defeated! +50 XP bonus!");
        
        // Give bonus XP for killing mammoth
        if (player != null)
        {
            PlayerStats playerStats = player.GetComponent<PlayerStats>();
            if (playerStats != null)
            {
                playerStats.GainXP(50); // Bonus XP for tough enemy
            }
        }
    }
    
    void SetupCamera()
    {
        Camera mainCamera = Camera.main;
        if (mainCamera != null && player != null)
        {
            CameraFollow cameraFollow = mainCamera.GetComponent<CameraFollow>();
            if (cameraFollow == null)
            {
                cameraFollow = mainCamera.gameObject.AddComponent<CameraFollow>();
            }
            cameraFollow.target = player.transform;
        }
    }
    
    void UpdateUI()
    {
        if (statusText != null && player != null)
        {
            Vector3 playerPos = player.transform.position;
            int aliveGoblins = CountAliveGoblins();
            int chasingGoblins = CountChasingGoblins();
            
            statusText.text = $"Position: ({playerPos.x:F1}, {playerPos.z:F1})\n" +
                             $"Goblins: {aliveGoblins} alive, {chasingGoblins} chasing\n" +
                             $"Killed: {goblinsKilled}\n" +
                             $"Time: {gameTime:F1}s";
        }
    }
    
    void CheckWinCondition()
    {
        if (CountAliveGoblins() == 0)
        {
            WinGame();
        }
    }
    
    int CountAliveGoblins()
    {
        int count = 0;
        foreach (GameObject goblin in goblins)
        {
            if (goblin != null)
            {
                HealthSystem health = goblin.GetComponent<HealthSystem>();
                if (health != null && !health.IsDead())
                {
                    count++;
                }
            }
        }
        return count;
    }
    
    int CountChasingGoblins()
    {
        int count = 0;
        foreach (GameObject goblin in goblins)
        {
            if (goblin != null)
            {
                GoblinAI ai = goblin.GetComponent<GoblinAI>();
                if (ai != null && ai.currentState == GoblinAI.GoblinState.Chasing)
                {
                    count++;
                }
            }
        }
        return count;
    }
    
    void OnPlayerDeath()
    {
        Debug.Log("Player died! Game Over.");
        gameActive = false;
        
        if (gameOverPanel != null)
        {
            gameOverPanel.SetActive(true);
        }
    }
    
    void OnGoblinDeath(GameObject goblin)
    {
        Debug.Log($"Goblin {goblin.name} was defeated!");
        goblinsKilled++;
        
        // Remove from list
        goblins.Remove(goblin);
    }
    
    void WinGame()
    {
        Debug.Log("All goblins defeated! You win!");
        gameActive = false;
        
        // Could show victory screen here
    }
    
    // Public methods for external systems
    public void RestartGame()
    {
        UnityEngine.SceneManagement.SceneManager.LoadScene(
            UnityEngine.SceneManagement.SceneManager.GetActiveScene().name
        );
    }
    
    public void PauseGame()
    {
        Time.timeScale = 0f;
    }
    
    public void ResumeGame()
    {
        Time.timeScale = 1f;
    }
}
