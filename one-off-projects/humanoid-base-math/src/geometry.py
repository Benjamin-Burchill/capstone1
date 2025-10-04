"""
Core Geometry Functions - Mathematical primitives for mesh generation
"""

import numpy as np
from scipy.interpolate import splprep, splev, CubicSpline
from typing import Tuple, List, Optional
import warnings
warnings.filterwarnings('ignore', category=RuntimeWarning)


def generate_spline_curve(points: np.ndarray, num_samples: int = 50, closed: bool = False) -> np.ndarray:
    """
    Create a smooth B-spline curve through given control points.
    
    Args:
        points: Nx2 or Nx3 array of control points
        num_samples: Number of points to sample along curve
        closed: Whether to close the curve (for profiles)
        
    Returns:
        Smooth curve as array of points
    """
    if closed:
        # Add first point to end to close the loop
        points = np.vstack([points, points[0:1]])
    
    if points.shape[0] < 4:
        # Not enough points for spline, use linear interpolation
        t = np.linspace(0, 1, num_samples)
        indices = np.linspace(0, len(points) - 1, num_samples)
        return np.array([
            np.interp(indices, np.arange(len(points)), points[:, i])
            for i in range(points.shape[1])
        ]).T
    
    try:
        # Fit B-spline
        if points.shape[1] == 2:
            tck, u = splprep([points[:, 0], points[:, 1]], s=0, k=min(3, len(points) - 1))
        else:
            tck, u = splprep([points[:, 0], points[:, 1], points[:, 2]], s=0, k=min(3, len(points) - 1))
        
        # Sample curve
        u_fine = np.linspace(0, 1, num_samples)
        smooth_points = np.array(splev(u_fine, tck)).T
        return smooth_points
    
    except Exception as e:
        print(f"Spline fitting failed: {e}, using linear interpolation")
        # Fallback to linear
        t = np.linspace(0, 1, num_samples)
        indices = np.linspace(0, len(points) - 1, num_samples)
        return np.array([
            np.interp(indices, np.arange(len(points)), points[:, i])
            for i in range(points.shape[1])
        ]).T


def create_ellipse_profile(width: float, depth: float, segments: int = 16) -> np.ndarray:
    """
    Create an elliptical cross-section profile.
    
    Args:
        width: Width (left-right, X-axis)
        depth: Depth (front-back, Z-axis)
        segments: Number of points around ellipse
        
    Returns:
        Nx2 array of (x, z) coordinates
    """
    theta = np.linspace(0, 2 * np.pi, segments + 1)[:-1]  # Exclude duplicate endpoint
    x = (width / 2) * np.cos(theta)
    z = (depth / 2) * np.sin(theta)
    return np.column_stack([x, z])


def loft_profile_along_curve(profile: np.ndarray, 
                             spine_curve: np.ndarray,
                             scale_along_spine: Optional[np.ndarray] = None) -> Tuple[np.ndarray, np.ndarray]:
    """
    Loft a 2D profile along a 3D spine curve to create a surface.
    
    Args:
        profile: Nx2 array of (x, z) coordinates in cross-section
        spine_curve: Mx3 array of (x, y, z) points defining the sweep path
        scale_along_spine: Optional M array of scale factors (1.0 = no scaling)
        
    Returns:
        Tuple of (vertices, faces) arrays
    """
    n_profile = len(profile)
    n_spine = len(spine_curve)
    
    if scale_along_spine is None:
        scale_along_spine = np.ones(n_spine)
    
    # Generate vertices by sweeping profile along spine
    vertices = []
    for i, spine_pt in enumerate(spine_curve):
        scale = scale_along_spine[i]
        
        # Transform profile to this position
        # Profile is in XZ plane, extrude along Y (spine)
        for prof_pt in profile:
            x = spine_pt[0] + prof_pt[0] * scale
            y = spine_pt[1]
            z = spine_pt[2] + prof_pt[1] * scale
            vertices.append([x, y, z])
    
    vertices = np.array(vertices)
    
    # Generate quad faces connecting rings
    faces = []
    for i in range(n_spine - 1):
        for j in range(n_profile):
            # Indices of quad corners
            v0 = i * n_profile + j
            v1 = i * n_profile + (j + 1) % n_profile
            v2 = (i + 1) * n_profile + (j + 1) % n_profile
            v3 = (i + 1) * n_profile + j
            
            # Split quad into two triangles
            faces.append([v0, v1, v2])
            faces.append([v0, v2, v3])
    
    return vertices, np.array(faces)


def create_tapered_cylinder(length: float,
                            radius_start: float,
                            radius_end: float,
                            segments: int = 12,
                            rings: int = 4) -> Tuple[np.ndarray, np.ndarray]:
    """
    Create a tapered cylinder (e.g., for limbs).
    
    Args:
        length: Length along Y axis
        radius_start: Radius at y=0
        radius_end: Radius at y=length
        segments: Number of vertices around circumference
        rings: Number of subdivision rings along length
        
    Returns:
        Tuple of (vertices, faces)
    """
    # Create spine (straight line)
    spine = np.column_stack([
        np.zeros(rings),
        np.linspace(0, length, rings),
        np.zeros(rings)
    ])
    
    # Create circular profile
    theta = np.linspace(0, 2 * np.pi, segments + 1)[:-1]
    profile = np.column_stack([
        np.cos(theta),
        np.sin(theta)
    ])
    
    # Scale factors for tapering
    scales = np.linspace(radius_start, radius_end, rings)
    
    return loft_profile_along_curve(profile, spine, scales)


def create_sphere(radius: float, lat_segments: int = 8, lon_segments: int = 12) -> Tuple[np.ndarray, np.ndarray]:
    """
    Create a UV sphere (for head).
    
    Args:
        radius: Sphere radius
        lat_segments: Latitude divisions
        lon_segments: Longitude divisions
        
    Returns:
        Tuple of (vertices, faces)
    """
    vertices = []
    
    # Top pole
    vertices.append([0, radius, 0])
    
    # Latitude rings
    for i in range(1, lat_segments):
        lat = np.pi * i / lat_segments - np.pi / 2  # -π/2 to π/2
        y = radius * np.sin(lat)
        r = radius * np.cos(lat)
        
        for j in range(lon_segments):
            lon = 2 * np.pi * j / lon_segments
            x = r * np.cos(lon)
            z = r * np.sin(lon)
            vertices.append([x, y, z])
    
    # Bottom pole
    vertices.append([0, -radius, 0])
    
    vertices = np.array(vertices)
    
    # Generate faces
    faces = []
    
    # Top cap
    for j in range(lon_segments):
        v1 = 0  # Top pole
        v2 = 1 + j
        v3 = 1 + (j + 1) % lon_segments
        faces.append([v1, v2, v3])
    
    # Middle quads
    for i in range(lat_segments - 2):
        for j in range(lon_segments):
            v0 = 1 + i * lon_segments + j
            v1 = 1 + i * lon_segments + (j + 1) % lon_segments
            v2 = 1 + (i + 1) * lon_segments + (j + 1) % lon_segments
            v3 = 1 + (i + 1) * lon_segments + j
            
            faces.append([v0, v1, v2])
            faces.append([v0, v2, v3])
    
    # Bottom cap
    bottom_pole = len(vertices) - 1
    bottom_ring_start = 1 + (lat_segments - 2) * lon_segments
    for j in range(lon_segments):
        v1 = bottom_ring_start + j
        v2 = bottom_ring_start + (j + 1) % lon_segments
        v3 = bottom_pole
        faces.append([v1, v2, v3])
    
    return vertices, np.array(faces)


def create_anatomical_torso_profile(height: float, 
                                    stockiness: float,
                                    segments: int = 16) -> List[np.ndarray]:
    """
    Create multiple cross-section profiles for realistic torso lofting.
    
    Returns list of profiles from bottom to top:
    - Pelvis (wide)
    - Lower waist
    - Upper waist (narrow)
    - Lower chest
    - Upper chest (broad)
    - Shoulders (widest)
    
    Args:
        height: Total body height
        stockiness: Width multiplier
        segments: Points per profile
        
    Returns:
        List of profile arrays
    """
    scale = height * stockiness
    
    profiles = []
    
    # Pelvis - wide and slightly flattened
    pelvis = create_ellipse_profile(0.18 * scale, 0.12 * scale, segments)
    profiles.append(pelvis)
    
    # Lower waist - transitional
    lower_waist = create_ellipse_profile(0.16 * scale, 0.11 * scale, segments)
    profiles.append(lower_waist)
    
    # Upper waist - narrowest point
    upper_waist = create_ellipse_profile(0.14 * scale, 0.10 * scale, segments)
    profiles.append(upper_waist)
    
    # Lower chest - expanding
    lower_chest = create_ellipse_profile(0.17 * scale, 0.11 * scale, segments)
    profiles.append(lower_chest)
    
    # Upper chest - broad
    upper_chest = create_ellipse_profile(0.19 * scale, 0.12 * scale, segments)
    profiles.append(upper_chest)
    
    # Shoulders - widest
    shoulders = create_ellipse_profile(0.22 * scale, 0.13 * scale, segments)
    profiles.append(shoulders)
    
    return profiles


def mirror_vertices_x(vertices: np.ndarray, faces: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Mirror mesh across X=0 plane for bilateral symmetry.
    
    Args:
        vertices: Nx3 vertex array
        faces: Mx3 face index array
        
    Returns:
        Tuple of (mirrored_vertices, mirrored_faces)
    """
    # Find center vertices (x ≈ 0)
    tolerance = 1e-6
    center_mask = np.abs(vertices[:, 0]) < tolerance
    center_indices = np.where(center_mask)[0]
    
    # Separate center and side vertices
    side_mask = ~center_mask
    side_vertices = vertices[side_mask]
    
    # Create mirrored side vertices
    mirrored_side = side_vertices.copy()
    mirrored_side[:, 0] *= -1  # Flip X coordinate
    
    # Combine: original + mirrored
    all_vertices = np.vstack([vertices, mirrored_side])
    
    # Create index mapping
    old_to_new = {}
    for i in range(len(vertices)):
        old_to_new[i] = i
    
    # Map mirrored vertices
    side_idx = 0
    for i, is_side in enumerate(side_mask):
        if is_side:
            old_to_new[i + len(vertices)] = len(vertices) + side_idx
            side_idx += 1
    
    # Mirror faces with flipped winding order
    mirrored_faces = []
    for face in faces:
        # Check if all vertices are on the side (not center)
        if all(not center_mask[v] for v in face):
            # Offset indices and flip winding
            new_face = [old_to_new.get(v + len(vertices), v) for v in face]
            mirrored_faces.append([new_face[0], new_face[2], new_face[1]])  # Flip winding
    
    all_faces = np.vstack([faces, mirrored_faces])
    
    return all_vertices, all_faces


def smooth_vertices_laplacian(vertices: np.ndarray, 
                               faces: np.ndarray,
                               iterations: int = 1,
                               factor: float = 0.5) -> np.ndarray:
    """
    Apply Laplacian smoothing to vertices.
    
    Args:
        vertices: Nx3 vertex array
        faces: Mx3 face index array
        iterations: Number of smoothing passes
        factor: Smoothing strength (0=none, 1=full)
        
    Returns:
        Smoothed vertex array
    """
    smoothed = vertices.copy()
    
    # Build vertex neighbors from faces
    neighbors = [set() for _ in range(len(vertices))]
    for face in faces:
        for i in range(3):
            v1 = face[i]
            v2 = face[(i + 1) % 3]
            neighbors[v1].add(v2)
            neighbors[v2].add(v1)
    
    for _ in range(iterations):
        new_positions = smoothed.copy()
        
        for i, vert in enumerate(smoothed):
            if len(neighbors[i]) == 0:
                continue
            
            # Average neighbor positions
            neighbor_avg = np.mean([smoothed[n] for n in neighbors[i]], axis=0)
            
            # Blend original with averaged
            new_positions[i] = vert * (1 - factor) + neighbor_avg * factor
        
        smoothed = new_positions
    
    return smoothed


if __name__ == "__main__":
    # Test geometry functions
    print("Testing geometry functions...")
    
    # Test spline
    points = np.array([[0, 0], [1, 1], [2, 0], [3, 1]])
    curve = generate_spline_curve(points, num_samples=20)
    print(f"Spline curve: {curve.shape}")
    
    # Test ellipse
    ellipse = create_ellipse_profile(1.0, 0.5, segments=12)
    print(f"Ellipse profile: {ellipse.shape}")
    
    # Test cylinder
    verts, faces = create_tapered_cylinder(2.0, 0.5, 0.3, segments=8, rings=4)
    print(f"Tapered cylinder: {len(verts)} verts, {len(faces)} faces")
    
    # Test sphere
    verts, faces = create_sphere(1.0, lat_segments=6, lon_segments=8)
    print(f"Sphere: {len(verts)} verts, {len(faces)} faces")
    
    print("\nAll geometry tests passed!")


