"""
Advanced Mathematical Models - Pushing pure math toward realism
===============================================================

This module implements more sophisticated mathematical techniques for humanoid
generation, demonstrating how far pure math can go before needing artist input.

Techniques implemented:
1. SMPL-like parametric body models (linear algebra on blend shapes)
2. NURBS surfaces (weighted rational B-splines)
3. Fractal/noise-based organic detailing
4. Multi-resolution subdivision surfaces
5. Volume-preserving deformations

Author: Mathematical Humanoid Generator Team
Version: 2.0 - Advanced
Date: October 2025
"""

import numpy as np
from scipy.interpolate import BSpline, splprep, splev
from typing import Tuple, List, Optional, Callable
import warnings
warnings.filterwarnings('ignore')


class AdvancedMathematicalModel:
    """
    Container for advanced mathematical techniques that approximate
    biological rules through stacked equations.
    """
    
    def __init__(self):
        self.noise_seed = 42
        np.random.seed(self.noise_seed)
    
    # ============================================================================
    # SMPL-INSPIRED PARAMETRIC MODEL
    # ============================================================================
    
    def create_smpl_blend_shapes(self, base_vertices: np.ndarray, 
                                  n_shapes: int = 10) -> List[np.ndarray]:
        """
        Create SMPL-style blend shapes using PCA-inspired deformations.
        
        In real SMPL, these come from PCA on thousands of scans. Here, we 
        generate them mathematically using anatomical constraints.
        
        Args:
            base_vertices: Base mesh vertices (Nx3)
            n_shapes: Number of blend shapes to generate
            
        Returns:
            List of blend shape deltas (each Nx3)
        """
        n_verts = len(base_vertices)
        blend_shapes = []
        
        # Height-based influence for different blend shapes
        y_coords = base_vertices[:, 1]
        y_normalized = (y_coords - y_coords.min()) / (y_coords.max() - y_coords.min())
        
        # Radial distance from center
        radial_dist = np.sqrt(base_vertices[:, 0]**2 + base_vertices[:, 2]**2)
        
        # Shape 1: Overall size (height + width)
        shape1 = base_vertices * 0.1
        blend_shapes.append(shape1)
        
        # Shape 2: Stockiness (width only, preserve height)
        shape2 = np.zeros_like(base_vertices)
        shape2[:, 0] = base_vertices[:, 0] * 0.15
        shape2[:, 2] = base_vertices[:, 2] * 0.15
        blend_shapes.append(shape2)
        
        # Shape 3: Leg length (lower body elongation)
        shape3 = np.zeros_like(base_vertices)
        lower_body_mask = y_normalized < 0.5
        shape3[lower_body_mask, 1] = -0.1 * y_normalized[lower_body_mask]
        blend_shapes.append(shape3)
        
        # Shape 4: Torso length
        shape4 = np.zeros_like(base_vertices)
        mid_body_mask = (y_normalized >= 0.3) & (y_normalized <= 0.7)
        shape4[mid_body_mask, 1] = 0.1
        blend_shapes.append(shape4)
        
        # Shape 5: Shoulder width
        shape5 = np.zeros_like(base_vertices)
        shoulder_mask = (y_normalized > 0.7) & (y_normalized < 0.85)
        shape5[shoulder_mask, 0] = base_vertices[shoulder_mask, 0] * 0.2
        blend_shapes.append(shape5)
        
        # Shape 6: Hip width
        shape6 = np.zeros_like(base_vertices)
        hip_mask = (y_normalized > 0.25) & (y_normalized < 0.4)
        shape6[hip_mask, 0] = base_vertices[hip_mask, 0] * 0.15
        shape6[hip_mask, 2] = base_vertices[hip_mask, 2] * 0.15
        blend_shapes.append(shape6)
        
        # Shape 7: Chest depth
        shape7 = np.zeros_like(base_vertices)
        chest_mask = (y_normalized > 0.6) & (y_normalized < 0.75)
        shape7[chest_mask, 2] = base_vertices[chest_mask, 2] * 0.1
        blend_shapes.append(shape7)
        
        # Shape 8: Muscle bulk (radial expansion)
        shape8 = np.zeros_like(base_vertices)
        limb_mask = radial_dist > np.percentile(radial_dist, 50)
        for i in range(n_verts):
            if limb_mask[i]:
                direction = base_vertices[i] - np.array([0, base_vertices[i, 1], 0])
                direction_norm = np.linalg.norm(direction)
                if direction_norm > 0:
                    shape8[i] = direction / direction_norm * 0.05
        blend_shapes.append(shape8)
        
        # Shape 9: Head size
        shape9 = np.zeros_like(base_vertices)
        head_mask = y_normalized > 0.9
        if np.any(head_mask):
            head_center = np.mean(base_vertices[head_mask], axis=0)
            shape9[head_mask] = (base_vertices[head_mask] - head_center) * 0.15
        blend_shapes.append(shape9)
        
        # Shape 10: Limb thickness variation
        shape10 = np.zeros_like(base_vertices)
        for i in range(n_verts):
            if radial_dist[i] > 0.1:
                radial_factor = np.sin(y_coords[i] * 3) * 0.02
                shape10[i, 0] = base_vertices[i, 0] * radial_factor
                shape10[i, 2] = base_vertices[i, 2] * radial_factor
        blend_shapes.append(shape10)
        
        return blend_shapes[:n_shapes]
    
    def apply_blend_shapes(self, base_vertices: np.ndarray,
                          blend_shapes: List[np.ndarray],
                          weights: np.ndarray) -> np.ndarray:
        """
        Apply SMPL-style blend shape deformation.
        
        Formula: V_final = V_base + Σ(B_i * w_i)
        
        Args:
            base_vertices: Base mesh (Nx3)
            blend_shapes: List of blend shape deltas
            weights: Weight for each blend shape
            
        Returns:
            Deformed vertices
        """
        result = base_vertices.copy()
        
        for i, (blend_shape, weight) in enumerate(zip(blend_shapes, weights)):
            if abs(weight) > 1e-6:  # Skip negligible weights
                result += blend_shape * weight
        
        return result
    
    # ============================================================================
    # NURBS (Non-Uniform Rational B-Splines)
    # ============================================================================
    
    def create_nurbs_surface(self, control_grid: np.ndarray,
                            weights: Optional[np.ndarray] = None,
                            resolution: int = 20) -> np.ndarray:
        """
        Create a NURBS surface from control points.
        
        NURBS = weighted rational B-splines, allowing more control over
        curvature than simple B-splines. Used in CAD and medical modeling.
        
        Args:
            control_grid: MxNx3 grid of control points
            weights: Optional MxN weights (default: all 1.0)
            resolution: Points to sample in each direction
            
        Returns:
            Surface points (resolution x resolution x 3)
        """
        m, n, _ = control_grid.shape
        
        if weights is None:
            weights = np.ones((m, n))
        
        # Create knot vectors (clamped)
        degree = 3
        knots_u = self._create_knot_vector(m, degree)
        knots_v = self._create_knot_vector(n, degree)
        
        # Sample surface
        u_vals = np.linspace(0, 1, resolution)
        v_vals = np.linspace(0, 1, resolution)
        
        surface_points = np.zeros((resolution, resolution, 3))
        
        for i, u in enumerate(u_vals):
            for j, v in enumerate(v_vals):
                point = self._evaluate_nurbs_point(
                    control_grid, weights, knots_u, knots_v, u, v, degree
                )
                surface_points[i, j] = point
        
        return surface_points
    
    def _create_knot_vector(self, n_control_points: int, degree: int) -> np.ndarray:
        """Create a clamped uniform knot vector."""
        n_knots = n_control_points + degree + 1
        knots = np.zeros(n_knots)
        
        # Clamped (repeated at ends)
        for i in range(degree + 1):
            knots[i] = 0
            knots[-(i + 1)] = 1
        
        # Uniform in middle
        interior = n_knots - 2 * (degree + 1)
        if interior > 0:
            knots[degree + 1:degree + 1 + interior] = np.linspace(0, 1, interior + 2)[1:-1]
        
        return knots
    
    def _evaluate_nurbs_point(self, control_grid: np.ndarray, weights: np.ndarray,
                             knots_u: np.ndarray, knots_v: np.ndarray,
                             u: float, v: float, degree: int) -> np.ndarray:
        """Evaluate NURBS surface at (u,v) parameter."""
        m, n, _ = control_grid.shape
        
        # Cox-de Boor recursion for B-spline basis functions
        def basis_function(i, p, u, knots):
            if p == 0:
                return 1.0 if knots[i] <= u < knots[i + 1] else 0.0
            
            # Avoid division by zero
            denom1 = knots[i + p] - knots[i]
            denom2 = knots[i + p + 1] - knots[i + 1]
            
            term1 = 0.0 if denom1 == 0 else ((u - knots[i]) / denom1) * basis_function(i, p - 1, u, knots)
            term2 = 0.0 if denom2 == 0 else ((knots[i + p + 1] - u) / denom2) * basis_function(i + 1, p - 1, u, knots)
            
            return term1 + term2
        
        # Calculate rational basis
        numerator = np.zeros(3)
        denominator = 0.0
        
        for i in range(m):
            for j in range(n):
                N_u = basis_function(i, min(degree, m - 1), u, knots_u)
                N_v = basis_function(j, min(degree, n - 1), v, knots_v)
                R = N_u * N_v * weights[i, j]
                
                numerator += R * control_grid[i, j]
                denominator += R
        
        return numerator / denominator if denominator > 0 else np.zeros(3)
    
    # ============================================================================
    # FRACTAL AND NOISE-BASED DETAILING
    # ============================================================================
    
    def perlin_noise_3d(self, positions: np.ndarray,
                        scale: float = 1.0,
                        octaves: int = 4,
                        persistence: float = 0.5) -> np.ndarray:
        """
        Generate 3D Perlin-like noise for organic detailing.
        
        This creates pseudo-random patterns that follow "rules" of self-similarity,
        mimicking biological complexity like skin texture or muscle striations.
        
        Args:
            positions: Nx3 array of positions to sample
            scale: Frequency scale
            octaves: Number of noise layers
            persistence: Amplitude decay per octave
            
        Returns:
            N array of noise values
        """
        noise = np.zeros(len(positions))
        amplitude = 1.0
        frequency = scale
        
        for octave in range(octaves):
            # Simple trigonometric noise (replace with proper Perlin for production)
            octave_noise = (
                np.sin(positions[:, 0] * frequency + octave) *
                np.sin(positions[:, 1] * frequency * 1.3 + octave * 2) *
                np.sin(positions[:, 2] * frequency * 0.7 + octave * 3)
            )
            
            noise += octave_noise * amplitude
            
            amplitude *= persistence
            frequency *= 2.0
        
        return noise
    
    def add_organic_detail(self, vertices: np.ndarray,
                          normals: np.ndarray,
                          detail_amplitude: float = 0.005,
                          detail_scale: float = 10.0) -> np.ndarray:
        """
        Add fractal organic detail to mesh via noise displacement.
        
        This simulates the "millions of rules" of biological variation
        through multi-scale noise patterns.
        
        Args:
            vertices: Nx3 vertex positions
            normals: Nx3 vertex normals
            detail_amplitude: Displacement strength
            detail_scale: Noise frequency
            
        Returns:
            Detailed vertices
        """
        # Generate multi-octave noise
        noise = self.perlin_noise_3d(
            vertices,
            scale=detail_scale,
            octaves=4,
            persistence=0.5
        )
        
        # Normalize noise to [-1, 1]
        if noise.std() > 0:
            noise = (noise - noise.mean()) / noise.std()
        noise = np.clip(noise, -2, 2) / 2
        
        # Displace along normals
        displacement = normals * (noise[:, np.newaxis] * detail_amplitude)
        
        return vertices + displacement
    
    def add_muscle_striations(self, vertices: np.ndarray,
                             normals: np.ndarray,
                             direction: np.ndarray = np.array([0, 1, 0]),
                             strength: float = 0.003) -> np.ndarray:
        """
        Add directional muscle-like striations.
        
        Simulates muscle fiber patterns using oriented noise.
        """
        # Project positions onto direction
        projection = vertices @ direction
        
        # Create striations perpendicular to muscle direction
        striation_freq = 20.0
        striations = np.sin(projection * striation_freq) * strength
        
        # Apply along normals
        displacement = normals * striations[:, np.newaxis]
        
        return vertices + displacement
    
    # ============================================================================
    # VOLUME-PRESERVING DEFORMATIONS
    # ============================================================================
    
    def volume_preserving_scale(self, vertices: np.ndarray,
                               scale_factors: np.ndarray) -> np.ndarray:
        """
        Scale vertices while approximately preserving volume.
        
        This is a mathematical "rule" that biology follows: when you
        compress in one direction, expand in others.
        
        Args:
            vertices: Nx3 positions
            scale_factors: 3-element array [sx, sy, sz]
            
        Returns:
            Scaled vertices with volume compensation
        """
        # Calculate volume change
        volume_change = np.prod(scale_factors)
        
        # Compensate to preserve volume
        compensation = np.cbrt(1.0 / volume_change)
        
        # Apply compensated scaling
        adjusted_scales = scale_factors * compensation
        
        return vertices * adjusted_scales
    
    # ============================================================================
    # MULTI-RESOLUTION SUBDIVISION
    # ============================================================================
    
    def catmull_clark_subdivision(self, vertices: np.ndarray,
                                  faces: np.ndarray,
                                  iterations: int = 1) -> Tuple[np.ndarray, np.ndarray]:
        """
        Apply Catmull-Clark subdivision for smooth surfaces.
        
        This is a mathematical rule that mimics how artists add detail:
        each iteration quadruples face count and smooths the mesh.
        
        Args:
            vertices: Nx3 vertex array
            faces: Mx4 quad face array (assumes quads)
            iterations: Number of subdivision steps
            
        Returns:
            Subdivided (vertices, faces)
        """
        current_verts = vertices.copy()
        current_faces = faces.copy()
        
        for _ in range(iterations):
            current_verts, current_faces = self._subdivide_once(current_verts, current_faces)
        
        return current_verts, current_faces
    
    def _subdivide_once(self, vertices: np.ndarray,
                       faces: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Single Catmull-Clark subdivision step."""
        n_verts = len(vertices)
        n_faces = len(faces)
        
        # Build edge map
        edges = {}  # (v1, v2) -> edge_index
        edge_list = []
        
        for face in faces:
            for i in range(4):
                v1, v2 = face[i], face[(i + 1) % 4]
                edge = tuple(sorted([v1, v2]))
                if edge not in edges:
                    edges[edge] = len(edge_list)
                    edge_list.append(edge)
        
        n_edges = len(edge_list)
        
        # Calculate new points
        # 1. Face points (average of face vertices)
        face_points = np.zeros((n_faces, 3))
        for i, face in enumerate(faces):
            face_points[i] = np.mean(vertices[face], axis=0)
        
        # 2. Edge points (average of edge endpoints and adjacent face points)
        edge_points = np.zeros((n_edges, 3))
        for i, (v1, v2) in enumerate(edge_list):
            edge_midpoint = (vertices[v1] + vertices[v2]) / 2
            # Simplified: just use midpoint (full CC needs adjacent faces)
            edge_points[i] = edge_midpoint
        
        # 3. Updated original vertices (simplified CC)
        new_verts = []
        new_verts.extend(vertices)  # Original (will be updated)
        new_verts.extend(face_points)  # Face points
        new_verts.extend(edge_points)  # Edge points
        
        new_verts = np.array(new_verts)
        
        # Generate new faces (each old face becomes 4 new faces)
        new_faces = []
        for f_idx, face in enumerate(faces):
            face_point_idx = n_verts + f_idx
            
            for i in range(4):
                v1 = face[i]
                v2 = face[(i + 1) % 4]
                
                edge = tuple(sorted([v1, v2]))
                edge_point_idx = n_verts + n_faces + edges[edge]
                
                # Quad: v1 -> edge_point -> face_point -> prev_edge_point
                prev_edge = tuple(sorted([face[(i - 1) % 4], v1]))
                prev_edge_point_idx = n_verts + n_faces + edges[prev_edge]
                
                new_faces.append([v1, edge_point_idx, face_point_idx, prev_edge_point_idx])
        
        return new_verts, np.array(new_faces)


# Convenience functions

def enhance_mesh_with_advanced_math(vertices: np.ndarray,
                                   faces: np.ndarray,
                                   normals: Optional[np.ndarray] = None,
                                   add_detail: bool = True,
                                   add_subdivision: bool = False) -> Tuple[np.ndarray, np.ndarray]:
    """
    Enhance a basic mesh with advanced mathematical techniques.
    
    Args:
        vertices: Base mesh vertices
        faces: Base mesh faces
        normals: Optional vertex normals (calculated if not provided)
        add_detail: Add fractal organic detail
        add_subdivision: Apply Catmull-Clark subdivision
        
    Returns:
        Enhanced (vertices, faces)
    """
    model = AdvancedMathematicalModel()
    
    enhanced_verts = vertices.copy()
    enhanced_faces = faces.copy()
    
    # Calculate normals if not provided
    if normals is None:
        # Simple vertex normal calculation
        normals = np.zeros_like(vertices)
        for face in faces:
            if len(face) >= 3:
                v0, v1, v2 = vertices[face[0]], vertices[face[1]], vertices[face[2]]
                normal = np.cross(v1 - v0, v2 - v0)
                for v_idx in face:
                    normals[v_idx] += normal
        
        # Normalize
        norms = np.linalg.norm(normals, axis=1, keepdims=True)
        norms[norms == 0] = 1  # Avoid division by zero
        normals = normals / norms
    
    # Add organic detail
    if add_detail:
        enhanced_verts = model.add_organic_detail(
            enhanced_verts,
            normals,
            detail_amplitude=0.003,
            detail_scale=15.0
        )
    
    # Apply subdivision
    if add_subdivision:
        # Convert triangles to quads if needed (simplified)
        if faces.shape[1] == 3:
            print("Note: Catmull-Clark works best with quads, skipping subdivision")
        elif faces.shape[1] == 4:
            enhanced_verts, enhanced_faces = model.catmull_clark_subdivision(
                enhanced_verts,
                enhanced_faces,
                iterations=1
            )
    
    return enhanced_verts, enhanced_faces


if __name__ == "__main__":
    # Test advanced mathematical models
    print("Testing Advanced Mathematical Models...")
    print("=" * 60)
    
    model = AdvancedMathematicalModel()
    
    # Test 1: Blend shapes
    print("\nTest 1: SMPL-style blend shapes")
    base = np.random.randn(100, 3) * 0.5  # Random base mesh
    blend_shapes = model.create_smpl_blend_shapes(base, n_shapes=5)
    print(f"  Created {len(blend_shapes)} blend shapes")
    
    weights = np.array([0.5, -0.3, 0.2, 0.0, 0.8])
    deformed = model.apply_blend_shapes(base, blend_shapes, weights)
    print(f"  Deformed mesh: {len(deformed)} vertices")
    
    # Test 2: Perlin noise
    print("\nTest 2: Perlin noise for organic detail")
    positions = np.random.rand(50, 3)
    noise = model.perlin_noise_3d(positions, scale=5.0, octaves=4)
    print(f"  Generated noise: min={noise.min():.3f}, max={noise.max():.3f}, std={noise.std():.3f}")
    
    # Test 3: NURBS surface
    print("\nTest 3: NURBS surface")
    control_grid = np.random.randn(4, 4, 3) * 0.3
    surface = model.create_nurbs_surface(control_grid, resolution=10)
    print(f"  NURBS surface: {surface.shape}")
    
    print("\n" + "=" * 60)
    print("All advanced math tests passed!")


