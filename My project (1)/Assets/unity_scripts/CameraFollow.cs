using UnityEngine;

/// <summary>
/// Third-person camera that follows the player smoothly
/// Attach this script to the Main Camera
/// </summary>
public class CameraFollow : MonoBehaviour
{
    [Header("Target Settings")]
    [Tooltip("The player transform to follow")]
    public Transform target;
    
    [Header("Camera Position")]
    [Tooltip("Offset from target position")]
    public Vector3 offset = new Vector3(0, 10, -10);
    
    [Tooltip("How smoothly the camera follows (lower = smoother)")]
    public float followSpeed = 2f;
    
    [Tooltip("How smoothly the camera rotates to look at target")]
    public float lookSpeed = 3f;
    
    [Header("Camera Bounds")]
    [Tooltip("Minimum height above ground")]
    public float minHeight = 2f;
    
    [Tooltip("Maximum distance from target")]
    public float maxDistance = 50f;
    
    [Header("Advanced Settings")]
    [Tooltip("Use smooth damping instead of lerp")]
    public bool useSmoothDamping = true;
    
    [Tooltip("Damping time for smooth follow")]
    public float dampTime = 0.3f;
    
    // Private state
    private Vector3 velocity = Vector3.zero;
    private Vector3 currentOffset;
    
    void Start()
    {
        // Find player if not assigned
        if (target == null)
        {
            GameObject player = GameObject.FindWithTag("Player");
            if (player != null)
            {
                target = player.transform;
                Debug.Log("Camera found player automatically");
            }
            else
            {
                Debug.LogError("CameraFollow: No target assigned and no GameObject with 'Player' tag found!");
            }
        }
        
        currentOffset = offset;
    }
    
    void LateUpdate()
    {
        if (target == null) return;
        
        // Calculate desired position
        Vector3 desiredPosition = target.position + currentOffset;
        
        // Enforce height constraint
        desiredPosition.y = Mathf.Max(desiredPosition.y, minHeight);
        
        // Enforce max distance constraint
        Vector3 targetToCamera = desiredPosition - target.position;
        if (targetToCamera.magnitude > maxDistance)
        {
            targetToCamera = targetToCamera.normalized * maxDistance;
            desiredPosition = target.position + targetToCamera;
        }
        
        // Move camera smoothly
        if (useSmoothDamping)
        {
            transform.position = Vector3.SmoothDamp(
                transform.position, 
                desiredPosition, 
                ref velocity, 
                dampTime
            );
        }
        else
        {
            transform.position = Vector3.Lerp(
                transform.position, 
                desiredPosition, 
                followSpeed * Time.deltaTime
            );
        }
        
        // Look at target smoothly
        Vector3 lookDirection = target.position - transform.position;
        if (lookDirection != Vector3.zero)
        {
            Quaternion targetRotation = Quaternion.LookRotation(lookDirection);
            transform.rotation = Quaternion.Slerp(
                transform.rotation, 
                targetRotation, 
                lookSpeed * Time.deltaTime
            );
        }
    }
    
    // Public methods for camera control
    public void SetOffset(Vector3 newOffset)
    {
        currentOffset = newOffset;
    }
    
    public void ShakeCamera(float intensity, float duration)
    {
        // Could implement camera shake here
        StartCoroutine(CameraShake(intensity, duration));
    }
    
    System.Collections.IEnumerator CameraShake(float intensity, float duration)
    {
        Vector3 originalOffset = currentOffset;
        float elapsed = 0f;
        
        while (elapsed < duration)
        {
            float x = Random.Range(-1f, 1f) * intensity;
            float y = Random.Range(-1f, 1f) * intensity;
            
            currentOffset = originalOffset + new Vector3(x, y, 0);
            
            elapsed += Time.deltaTime;
            yield return null;
        }
        
        currentOffset = originalOffset;
    }
    
    // Debug visualization
    void OnDrawGizmos()
    {
        if (target == null) return;
        
        // Draw camera target line
        Gizmos.color = Color.cyan;
        Gizmos.DrawLine(transform.position, target.position);
        
        // Draw offset position
        Gizmos.color = Color.yellow;
        Gizmos.DrawWireSphere(target.position + offset, 1f);
        
        // Draw max distance sphere
        Gizmos.color = Color.red;
        Gizmos.DrawWireSphere(target.position, maxDistance);
    }
}
