using UnityEngine;
using System.Collections.Generic;
using System;

/// <summary>
/// Manages all input for the game, including customizable key bindings
/// Provides a centralized input system that other scripts can use
/// </summary>
[System.Serializable]
public class KeyBinding
{
    public string actionName;
    public KeyCode keyCode;
    public KeyCode alternativeKey = KeyCode.None;
    
    public KeyBinding(string name, KeyCode key, KeyCode altKey = KeyCode.None)
    {
        actionName = name;
        keyCode = key;
        alternativeKey = altKey;
    }
    
    public bool IsPressed()
    {
        return Input.GetKey(keyCode) || (alternativeKey != KeyCode.None && Input.GetKey(alternativeKey));
    }
    
    public bool IsDown()
    {
        return Input.GetKeyDown(keyCode) || (alternativeKey != KeyCode.None && Input.GetKeyDown(alternativeKey));
    }
    
    public bool IsUp()
    {
        return Input.GetKeyUp(keyCode) || (alternativeKey != KeyCode.None && Input.GetKeyUp(alternativeKey));
    }
}

public class InputManager : MonoBehaviour
{
    [Header("Key Bindings")]
    [Tooltip("All customizable key bindings for the game")]
    public List<KeyBinding> keyBindings = new List<KeyBinding>();
    
    [Header("Settings")]
    [Tooltip("Whether to save/load key bindings to PlayerPrefs")]
    public bool persistKeyBindings = true;
    
    // Dictionary for fast lookup
    private Dictionary<string, KeyBinding> keyBindingMap = new Dictionary<string, KeyBinding>();
    
    // Events for input actions
    public System.Action OnSettingsToggle;
    public System.Action OnCameraMoveUp;
    public System.Action OnCameraMoveDown;
    public System.Action OnCameraMoveLeft;
    public System.Action OnCameraMoveRight;
    public System.Action OnCameraZoomIn;
    public System.Action OnCameraZoomOut;
    public System.Action<float> OnMouseScroll; // For scroll wheel
    
    // Singleton pattern
    public static InputManager Instance { get; private set; }
    
    void Awake()
    {
        // Singleton setup with null check
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
            InitializeKeyBindings();
        }
        else if (Instance != this)
        {
            Destroy(gameObject);
            return;
        }
    }
    
    void InitializeKeyBindings()
    {
        // Initialize default key bindings
        if (keyBindings.Count == 0)
        {
            keyBindings.Add(new KeyBinding("Settings Toggle", KeyCode.Escape));
            keyBindings.Add(new KeyBinding("Camera Up", KeyCode.UpArrow, KeyCode.W));
            keyBindings.Add(new KeyBinding("Camera Down", KeyCode.DownArrow, KeyCode.S));
            keyBindings.Add(new KeyBinding("Camera Left", KeyCode.LeftArrow, KeyCode.A));
            keyBindings.Add(new KeyBinding("Camera Right", KeyCode.RightArrow, KeyCode.D));
            keyBindings.Add(new KeyBinding("Camera Zoom In", KeyCode.KeypadPlus, KeyCode.Plus));
            keyBindings.Add(new KeyBinding("Camera Zoom Out", KeyCode.KeypadMinus, KeyCode.Minus));
        }
        
        // Build lookup dictionary
        BuildKeyBindingMap();
        
        // Load saved key bindings
        if (persistKeyBindings)
        {
            LoadKeyBindings();
        }
        
        Debug.Log($"InputManager initialized with {keyBindings.Count} key bindings");
    }
    
    void BuildKeyBindingMap()
    {
        keyBindingMap.Clear();
        foreach (KeyBinding binding in keyBindings)
        {
            keyBindingMap[binding.actionName] = binding;
        }
    }
    
    void Update()
    {
        HandleInputActions();
        HandleMouseInput();
    }
    
    void HandleInputActions()
    {
        // Settings toggle
        if (IsActionDown("Settings Toggle"))
        {
            OnSettingsToggle?.Invoke();
        }
        
        // Camera movement (continuous input)
        if (IsActionPressed("Camera Up"))
        {
            OnCameraMoveUp?.Invoke();
        }
        if (IsActionPressed("Camera Down"))
        {
            OnCameraMoveDown?.Invoke();
        }
        if (IsActionPressed("Camera Left"))
        {
            OnCameraMoveLeft?.Invoke();
        }
        if (IsActionPressed("Camera Right"))
        {
            OnCameraMoveRight?.Invoke();
        }
        if (IsActionPressed("Camera Zoom In"))
        {
            OnCameraZoomIn?.Invoke();
        }
        if (IsActionPressed("Camera Zoom Out"))
        {
            OnCameraZoomOut?.Invoke();
        }
    }
    
    void HandleMouseInput()
    {
        // Mouse scroll wheel
        float scroll = Input.GetAxis("Mouse ScrollWheel");
        if (Mathf.Abs(scroll) > 0.01f)
        {
            OnMouseScroll?.Invoke(scroll);
        }
    }
    
    // Public methods to check input
    public bool IsActionPressed(string actionName)
    {
        return keyBindingMap.ContainsKey(actionName) && keyBindingMap[actionName].IsPressed();
    }
    
    public bool IsActionDown(string actionName)
    {
        return keyBindingMap.ContainsKey(actionName) && keyBindingMap[actionName].IsDown();
    }
    
    public bool IsActionUp(string actionName)
    {
        return keyBindingMap.ContainsKey(actionName) && keyBindingMap[actionName].IsUp();
    }
    
    public KeyBinding GetKeyBinding(string actionName)
    {
        keyBindingMap.TryGetValue(actionName, out KeyBinding binding);
        return binding;
    }
    
    public void SetKeyBinding(string actionName, KeyCode newKey, KeyCode newAltKey = KeyCode.None)
    {
        if (keyBindingMap.ContainsKey(actionName))
        {
            KeyBinding binding = keyBindingMap[actionName];
            binding.keyCode = newKey;
            binding.alternativeKey = newAltKey;
            
            // Update the list as well
            for (int i = 0; i < keyBindings.Count; i++)
            {
                if (keyBindings[i].actionName == actionName)
                {
                    keyBindings[i] = binding;
                    break;
                }
            }
            
            if (persistKeyBindings)
            {
                SaveKeyBindings();
            }
            
            Debug.Log($"Key binding updated: {actionName} = {newKey} / {newAltKey}");
        }
    }
    
    public List<string> GetAllActionNames()
    {
        List<string> actionNames = new List<string>();
        foreach (KeyBinding binding in keyBindings)
        {
            actionNames.Add(binding.actionName);
        }
        return actionNames;
    }
    
    void SaveKeyBindings()
    {
        foreach (KeyBinding binding in keyBindings)
        {
            string keyKey = "KeyBinding_" + binding.actionName + "_Key";
            string altKeyKey = "KeyBinding_" + binding.actionName + "_AltKey";
            
            PlayerPrefs.SetInt(keyKey, (int)binding.keyCode);
            PlayerPrefs.SetInt(altKeyKey, (int)binding.alternativeKey);
        }
        PlayerPrefs.Save();
        Debug.Log("Key bindings saved to PlayerPrefs");
    }
    
    void LoadKeyBindings()
    {
        foreach (KeyBinding binding in keyBindings)
        {
            string keyKey = "KeyBinding_" + binding.actionName + "_Key";
            string altKeyKey = "KeyBinding_" + binding.actionName + "_AltKey";
            
            if (PlayerPrefs.HasKey(keyKey))
            {
                binding.keyCode = (KeyCode)PlayerPrefs.GetInt(keyKey);
            }
            if (PlayerPrefs.HasKey(altKeyKey))
            {
                binding.alternativeKey = (KeyCode)PlayerPrefs.GetInt(altKeyKey);
            }
        }
        
        // Rebuild map after loading
        BuildKeyBindingMap();
        Debug.Log("Key bindings loaded from PlayerPrefs");
    }
    
    public void ResetToDefaults()
    {
        // Reset to default key bindings
        keyBindings.Clear();
        InitializeKeyBindings();
        
        if (persistKeyBindings)
        {
            SaveKeyBindings();
        }
        
        Debug.Log("Key bindings reset to defaults");
    }
    
    // Helper method to get key name for display
    public static string GetKeyDisplayName(KeyCode key)
    {
        if (key == KeyCode.None) return "None";
        
        return key switch
        {
            KeyCode.LeftArrow => "←",
            KeyCode.RightArrow => "→",
            KeyCode.UpArrow => "↑",
            KeyCode.DownArrow => "↓",
            KeyCode.KeypadPlus => "Num +",
            KeyCode.KeypadMinus => "Num -",
            KeyCode.Plus => "+",
            KeyCode.Minus => "-",
            KeyCode.Escape => "ESC",
            KeyCode.Space => "Space",
            KeyCode.LeftShift => "L Shift",
            KeyCode.RightShift => "R Shift",
            KeyCode.LeftControl => "L Ctrl",
            KeyCode.RightControl => "R Ctrl",
            _ => key.ToString()
        };
    }
}
