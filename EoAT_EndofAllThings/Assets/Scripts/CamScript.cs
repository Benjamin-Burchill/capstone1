using UnityEngine;

public class CamScript : MonoBehaviour
{
    private Transform camTransform;
    private Vector2 position;
    private Camera mainCamera;
    private Map map;
    private InputManager inputManager;

    private void zoomCameraIn()
    {
        //zoom in, but only to a minimum of 5
        if (mainCamera.orthographicSize > 5)
        {
            mainCamera.orthographicSize -= 0.1f;
        }
        
    }

    private void zoomCameraOut() {
        //zoom out to a maximum of 30
        if (mainCamera.orthographicSize < 30){
            mainCamera.orthographicSize += 0.1f;
        }

        //if by zooming out the camera goes beyond the bounds of the map - move the camera
        if (camTransform.position.y + mainCamera.orthographicSize + map.tileSize.y * 0.5f > map.mapMaxDim.y)
        {
            moveCameraDown(0.1f);
        }
        else if (camTransform.position.y - mainCamera.orthographicSize - map.tileSize.y * 0.5f < 0)
        {
            moveCameraUp(0.1f);
        }
        else if (camTransform.position.x - mainCamera.orthographicSize * mainCamera.aspect < 0)
        {
            moveCameraRight(0.1f);
        }
        else if (camTransform.position.x + mainCamera.orthographicSize * mainCamera.aspect > map.mapMaxDim.x)
        {
            moveCameraLeft(0.1f);
        }
    }

    private void moveCameraUp(float speed=0.01f) {
        //move the camera upwards, but not if it would move the camera outside the map
        if (camTransform.position.y+mainCamera.orthographicSize+map.tileSize.y*0.5f<map.mapMaxDim.y) {
            camTransform.position = new Vector3(camTransform.position.x,
                                   camTransform.position.y + mainCamera.orthographicSize * speed, -10);
        }
    }

    private void moveCameraDown(float speed= 0.01f) {
        //move the camera downwards, but not if it would move the camera outside the map
        if (camTransform.position.y - mainCamera.orthographicSize - map.tileSize.y * 0.5f > 0){
            camTransform.position = new Vector3(camTransform.position.x,
                               camTransform.position.y - mainCamera.orthographicSize * speed, -10);
        }
    }

    private void moveCameraLeft(float speed= 0.01f) {
        //move the camera to the left, but not if it would move the camera outside the map
        if (camTransform.position.x - mainCamera.orthographicSize*mainCamera.aspect > 0){
            camTransform.position = new Vector3(camTransform.position.x - mainCamera.orthographicSize * speed,
                               camTransform.position.y, -10);
        }
    }

    private void moveCameraRight(float speed= 0.01f) {
        print(map.mapMaxDim.x);


        //move the camera to the right, but not if it would move the camera outside the map
        if (camTransform.position.x + mainCamera.orthographicSize * mainCamera.aspect < map.mapMaxDim.x){
            camTransform.position = new Vector3(camTransform.position.x + mainCamera.orthographicSize * speed,
                               camTransform.position.y, -10);
        }
    }

    void Start()
    {
        camTransform = gameObject.transform;//get the transform
        mainCamera = Camera.main;//get the camera component
        map = GameObject.Find("MapLoader").GetComponent<Map>();//get the map 
        
        // Get InputManager and subscribe to events
        inputManager = InputManager.Instance;
        if (inputManager != null)
        {
            inputManager.OnCameraMoveUp += () => moveCameraUp();
            inputManager.OnCameraMoveDown += () => moveCameraDown();
            inputManager.OnCameraMoveLeft += () => moveCameraLeft();
            inputManager.OnCameraMoveRight += () => moveCameraRight();
            inputManager.OnCameraZoomIn += () => zoomCameraIn();
            inputManager.OnCameraZoomOut += () => zoomCameraOut();
            inputManager.OnMouseScroll += HandleMouseScroll;
            
            Debug.Log("CamScript subscribed to InputManager events");
        }
        else
        {
            Debug.LogWarning("CamScript: InputManager not found! Using fallback input system.");
        }
    }

    void Update()
    {
        // Fallback input handling if InputManager is not available
        if (inputManager == null)
        {
            HandleFallbackInput();
        }
    }
    
    void HandleFallbackInput()
    {
        //check for camera movement inputs    
        if (Input.GetKey(KeyCode.KeypadPlus))
        {
            zoomCameraIn();
        }
        if (Input.GetKey(KeyCode.KeypadMinus))
        {
            zoomCameraOut();
        }
        
        // Scroll wheel zoom
        float scroll = Input.GetAxis("Mouse ScrollWheel");
        if (scroll > 0f)
        {
            zoomCameraIn();
        }
        else if (scroll < 0f)
        {
            zoomCameraOut();
        }
        
        if (Input.GetKey(KeyCode.UpArrow))
        {
            moveCameraUp();
        }
        if (Input.GetKey(KeyCode.DownArrow))
        {
            moveCameraDown();
        }
        if (Input.GetKey(KeyCode.LeftArrow))
        {
            moveCameraLeft();
        }
        if (Input.GetKey(KeyCode.RightArrow))
        {
            moveCameraRight();  
        }
    }
    
    void HandleMouseScroll(float scrollDelta)
    {
        if (scrollDelta > 0f)
        {
            zoomCameraIn();
        }
        else if (scrollDelta < 0f)
        {
            zoomCameraOut();
        }
    }
    
    void OnDestroy()
    {
        // Unsubscribe from events to prevent memory leaks
        if (inputManager != null)
        {
            inputManager.OnCameraMoveUp -= () => moveCameraUp();
            inputManager.OnCameraMoveDown -= () => moveCameraDown();
            inputManager.OnCameraMoveLeft -= () => moveCameraLeft();
            inputManager.OnCameraMoveRight -= () => moveCameraRight();
            inputManager.OnCameraZoomIn -= () => zoomCameraIn();
            inputManager.OnCameraZoomOut -= () => zoomCameraOut();
            inputManager.OnMouseScroll -= HandleMouseScroll;
        }
    }
}
