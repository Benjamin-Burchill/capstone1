using UnityEngine;
using UnityEngine.UI;
using TMPro;
using System.Collections.Generic;
using System.Linq;

/// <summary>
/// Manages the settings UI interface for key bindings and game options
/// Creates top and bottom panels accessible via ESC key
/// </summary>
public class SettingsUI : MonoBehaviour
{
    [Header("Settings Panels")]
    [Tooltip("Main settings panel (parent of all settings UI)")]
    public GameObject settingsPanel;
    
    [Tooltip("Top panel for main settings content")]
    public GameObject topPanel;
    
    [Tooltip("Bottom panel for action buttons")]
    public GameObject bottomPanel;
    
    [Header("Key Binding UI")]
    [Tooltip("Parent object for key binding controls")]
    public Transform keyBindingContainer;
    
    [Tooltip("Prefab for individual key binding rows")]
    public GameObject keyBindingRowPrefab;
    
    [Header("UI Elements")]
    [Tooltip("Title text for settings")]
    public TextMeshProUGUI settingsTitle;
    
    [Tooltip("Button to close settings")]
    public Button closeButton;
    
    [Tooltip("Button to reset to defaults")]
    public Button resetDefaultsButton;
    
    [Tooltip("Button to apply/save settings")]
    public Button applyButton;
    
    [Header("Audio Volume")]
    [Tooltip("Slider for master volume")]
    public Slider masterVolumeSlider;
    
    [Tooltip("Text showing current volume value")]
    public TextMeshProUGUI volumeText;
    
    // Key binding UI elements
    private List<GameObject> keyBindingRows = new List<GameObject>();
    private InputManager inputManager;
    private bool isSettingsOpen = false;
    private string currentlyRebindingAction = null;
    
    void Start()
    {
        // Get InputManager reference
        inputManager = InputManager.Instance;
        if (inputManager == null)
        {
            Debug.LogError("SettingsUI: InputManager instance not found!");
            return;
        }
        
        // Subscribe to input manager events
        inputManager.OnSettingsToggle += ToggleSettings;
        
        // Setup UI elements
        InitializeUI();
        SetupEventListeners();
        
        // Hide settings panel initially
        if (settingsPanel != null)
        {
            settingsPanel.SetActive(false);
        }
        
        Debug.Log("SettingsUI initialized");
    }
    
    void InitializeUI()
    {
        // Create settings panel structure if not assigned
        if (settingsPanel == null)
        {
            CreateSettingsPanelStructure();
        }
        
        // Set up title
        if (settingsTitle != null)
        {
            settingsTitle.text = "Game Settings";
        }
        
        // Load current volume setting
        if (masterVolumeSlider != null)
        {
            float currentVolume = AudioListener.volume;
            masterVolumeSlider.value = currentVolume;
            UpdateVolumeText(currentVolume);
        }
        
        // Create key binding rows
        CreateKeyBindingUI();
    }
    
    void CreateSettingsPanelStructure()
    {
        // This method helps create the basic structure if it doesn't exist
        // In Unity, you'd typically set this up in the editor, but this provides fallback
        
        Canvas canvas = FindFirstObjectByType<Canvas>();
        if (canvas == null)
        {
            Debug.LogError("No Canvas found for SettingsUI!");
            return;
        }
        
        // Create main settings panel
        GameObject settingsObj = new GameObject("SettingsPanel");
        settingsObj.transform.SetParent(canvas.transform, false);
        
        // Add Panel component
        Image panelImage = settingsObj.AddComponent<Image>();
        panelImage.color = new Color(0, 0, 0, 0.8f); // Semi-transparent black
        
        // Make it full screen
        RectTransform rectTransform = settingsObj.GetComponent<RectTransform>();
        rectTransform.anchorMin = Vector2.zero;
        rectTransform.anchorMax = Vector2.one;
        rectTransform.offsetMin = Vector2.zero;
        rectTransform.offsetMax = Vector2.zero;
        
        settingsPanel = settingsObj;
    }
    
    void SetupEventListeners()
    {
        if (closeButton != null)
        {
            closeButton.onClick.AddListener(CloseSettings);
        }
        
        if (resetDefaultsButton != null)
        {
            resetDefaultsButton.onClick.AddListener(ResetToDefaults);
        }
        
        if (applyButton != null)
        {
            applyButton.onClick.AddListener(ApplySettings);
        }
        
        if (masterVolumeSlider != null)
        {
            masterVolumeSlider.onValueChanged.AddListener(OnVolumeChanged);
        }
    }
    
    void CreateKeyBindingUI()
    {
        if (inputManager == null || keyBindingContainer == null) return;
        
        // Clear existing rows
        ClearKeyBindingRows();
        
        // Get all action names
        List<string> actionNames = inputManager.GetAllActionNames();
        
        foreach (string actionName in actionNames)
        {
            CreateKeyBindingRow(actionName);
        }
    }
    
    void CreateKeyBindingRow(string actionName)
    {
        GameObject row;
        
        if (keyBindingRowPrefab != null)
        {
            row = Instantiate(keyBindingRowPrefab, keyBindingContainer);
        }
        else
        {
            // Create a simple row structure
            row = new GameObject($"KeyBinding_{actionName}");
            row.transform.SetParent(keyBindingContainer, false);
            
            // Add horizontal layout
            HorizontalLayoutGroup layout = row.AddComponent<HorizontalLayoutGroup>();
            layout.childAlignment = TextAnchor.MiddleLeft;
            layout.spacing = 10f;
            
            // Add content size fitter
            ContentSizeFitter fitter = row.AddComponent<ContentSizeFitter>();
            fitter.horizontalFit = ContentSizeFitter.FitMode.Unconstrained;
            fitter.verticalFit = ContentSizeFitter.FitMode.PreferredSize;
        }
        
        // Setup row components
        SetupKeyBindingRowComponents(row, actionName);
        keyBindingRows.Add(row);
    }
    
    void SetupKeyBindingRowComponents(GameObject row, string actionName)
    {
        KeyBinding binding = inputManager.GetKeyBinding(actionName);
        if (binding == null) return;
        
        // Action name label
        GameObject labelObj = new GameObject("ActionLabel");
        labelObj.transform.SetParent(row.transform, false);
        TextMeshProUGUI label = labelObj.AddComponent<TextMeshProUGUI>();
        label.text = actionName;
        label.fontSize = 16;
        
        // Primary key button
        GameObject primaryBtnObj = new GameObject("PrimaryKeyButton");
        primaryBtnObj.transform.SetParent(row.transform, false);
        Button primaryBtn = primaryBtnObj.AddComponent<Button>();
        Image primaryBtnImage = primaryBtnObj.AddComponent<Image>();
        primaryBtnImage.color = Color.white;
        
        GameObject primaryTextObj = new GameObject("PrimaryKeyText");
        primaryTextObj.transform.SetParent(primaryBtnObj.transform, false);
        TextMeshProUGUI primaryText = primaryTextObj.AddComponent<TextMeshProUGUI>();
        primaryText.text = InputManager.GetKeyDisplayName(binding.keyCode);
        primaryText.fontSize = 14;
        primaryText.color = Color.black;
        primaryText.alignment = TextAlignmentOptions.Center;
        
        // Alternative key button
        GameObject altBtnObj = new GameObject("AltKeyButton");
        altBtnObj.transform.SetParent(row.transform, false);
        Button altBtn = altBtnObj.AddComponent<Button>();
        Image altBtnImage = altBtnObj.AddComponent<Image>();
        altBtnImage.color = Color.gray;
        
        GameObject altTextObj = new GameObject("AltKeyText");
        altTextObj.transform.SetParent(altBtnObj.transform, false);
        TextMeshProUGUI altText = altTextObj.AddComponent<TextMeshProUGUI>();
        altText.text = InputManager.GetKeyDisplayName(binding.alternativeKey);
        altText.fontSize = 14;
        altText.color = Color.black;
        altText.alignment = TextAlignmentOptions.Center;
        
        // Add button listeners
        primaryBtn.onClick.AddListener(() => StartRebinding(actionName, true, primaryText));
        altBtn.onClick.AddListener(() => StartRebinding(actionName, false, altText));
        
        // Store references for updates
        KeyBindingRowData rowData = row.AddComponent<KeyBindingRowData>();
        rowData.actionName = actionName;
        rowData.primaryKeyText = primaryText;
        rowData.altKeyText = altText;
    }
    
    void StartRebinding(string actionName, bool isPrimary, TextMeshProUGUI buttonText)
    {
        if (currentlyRebindingAction != null) return; // Already rebinding something
        
        currentlyRebindingAction = $"{actionName}|{isPrimary}";
        buttonText.text = "Press Key...";
        buttonText.color = Color.red;
        
        Debug.Log($"Started rebinding: {actionName} ({(isPrimary ? "Primary" : "Alternative")})");
    }
    
    void Update()
    {
        // Handle key rebinding
        if (currentlyRebindingAction != null && isSettingsOpen)
        {
            HandleRebindingInput();
        }
    }
    
    void HandleRebindingInput()
    {
        // Check for any key press
        foreach (KeyCode keyCode in System.Enum.GetValues(typeof(KeyCode)))
        {
            if (Input.GetKeyDown(keyCode))
            {
                CompleteRebinding(keyCode);
                break;
            }
        }
    }
    
    void CompleteRebinding(KeyCode newKey)
    {
        if (currentlyRebindingAction == null) return;
        
        string[] parts = currentlyRebindingAction.Split('|');
        string actionName = parts[0];
        bool isPrimary = bool.Parse(parts[1]);
        
        KeyBinding binding = inputManager.GetKeyBinding(actionName);
        if (binding != null)
        {
            if (isPrimary)
            {
                inputManager.SetKeyBinding(actionName, newKey, binding.alternativeKey);
            }
            else
            {
                inputManager.SetKeyBinding(actionName, binding.keyCode, newKey);
            }
        }
        
        // Update UI
        UpdateKeyBindingDisplay(actionName);
        
        currentlyRebindingAction = null;
        Debug.Log($"Completed rebinding: {actionName} = {newKey}");
    }
    
    void UpdateKeyBindingDisplay(string actionName)
    {
        KeyBinding binding = inputManager.GetKeyBinding(actionName);
        if (binding == null) return;
        
        // Find the row for this action
        foreach (GameObject row in keyBindingRows)
        {
            KeyBindingRowData rowData = row.GetComponent<KeyBindingRowData>();
            if (rowData != null && rowData.actionName == actionName)
            {
                rowData.primaryKeyText.text = InputManager.GetKeyDisplayName(binding.keyCode);
                rowData.primaryKeyText.color = Color.black;
                
                rowData.altKeyText.text = InputManager.GetKeyDisplayName(binding.alternativeKey);
                rowData.altKeyText.color = Color.black;
                break;
            }
        }
    }
    
    void ClearKeyBindingRows()
    {
        foreach (GameObject row in keyBindingRows)
        {
            if (row != null)
            {
                DestroyImmediate(row);
            }
        }
        keyBindingRows.Clear();
    }
    
    public void ToggleSettings()
    {
        if (settingsPanel != null)
        {
            isSettingsOpen = !settingsPanel.activeInHierarchy;
            settingsPanel.SetActive(isSettingsOpen);
            
            if (isSettingsOpen)
            {
                // Pause game or show cursor
                Time.timeScale = 0f; // Pause the game when settings are open
                Cursor.lockState = CursorLockMode.None;
                Cursor.visible = true;
            }
            else
            {
                // Resume game
                Time.timeScale = 1f;
                currentlyRebindingAction = null; // Cancel any ongoing rebinding
            }
            
            Debug.Log($"Settings panel {(isSettingsOpen ? "opened" : "closed")}");
        }
    }
    
    public void CloseSettings()
    {
        if (settingsPanel != null)
        {
            settingsPanel.SetActive(false);
            isSettingsOpen = false;
            Time.timeScale = 1f; // Resume game
            currentlyRebindingAction = null;
        }
    }
    
    void OnVolumeChanged(float volume)
    {
        AudioListener.volume = volume;
        UpdateVolumeText(volume);
        PlayerPrefs.SetFloat("MasterVolume", volume);
    }
    
    void UpdateVolumeText(float volume)
    {
        if (volumeText != null)
        {
            volumeText.text = $"Volume: {Mathf.RoundToInt(volume * 100)}%";
        }
    }
    
    public void ResetToDefaults()
    {
        if (inputManager != null)
        {
            inputManager.ResetToDefaults();
            CreateKeyBindingUI(); // Refresh the UI
        }
        
        // Reset volume
        if (masterVolumeSlider != null)
        {
            masterVolumeSlider.value = 1f;
            OnVolumeChanged(1f);
        }
        
        Debug.Log("Settings reset to defaults");
    }
    
    public void ApplySettings()
    {
        // Save any pending changes
        PlayerPrefs.Save();
        Debug.Log("Settings applied and saved");
    }
    
    void OnDestroy()
    {
        // Unsubscribe from events
        if (inputManager != null)
        {
            inputManager.OnSettingsToggle -= ToggleSettings;
        }
        
        // Ensure game is unpaused
        Time.timeScale = 1f;
    }
}

/// <summary>
/// Helper component to store key binding row data
/// </summary>
public class KeyBindingRowData : MonoBehaviour
{
    public string actionName;
    public TextMeshProUGUI primaryKeyText;
    public TextMeshProUGUI altKeyText;
}

