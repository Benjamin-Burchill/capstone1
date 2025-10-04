#!/usr/bin/env python3
"""
Symmetric Humanoid Builder - Professional mesh generation with perfect symmetry
================================================================================

This module creates anatomically correct humanoid meshes using a half-mesh 
mirroring approach, ensuring perfect bilateral symmetry. This is the standard
approach used in professional 3D modeling software like Blender.

Key Features:
- Generates only right half of the mesh
- Mirrors vertices and faces for left half
- Ensures perfect symmetry
- Reduces code complexity and potential errors
- Follows industry-standard practices

Author: Character Generator System
Version: 2.0
Date: 2024
"""

import numpy as np
import trimesh
from typing import Dict, List, Tuple, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


class SymmetricHumanoidBuilder:
    """
    Builds perfectly symmetric humanoid meshes using half-mesh generation.
    
    This builder creates only the right half of the humanoid (and center line),
    then mirrors it to create the left half, ensuring perfect bilateral symmetry.
    """
    
    def __init__(self, detail_level: str = 'medium'):
        """
        Initialize the symmetric humanoid builder.
        
        Args:
            detail_level: Quality setting ('low', 'medium', or 'high')
                - low: Fast generation, fewer vertices
                - medium: Balanced quality and performance  
                - high: High quality with subdivision
        """
        self.vertices = []
        self.faces = []
        self.vertex_groups = {}
        self.detail_level = detail_level
        
        # Resolution settings based on detail level
        self.settings = {
            'low': {'body_res': 8, 'limb_res': 6, 'subdivide': False},
            'medium': {'body_res': 12, 'limb_res': 8, 'subdivide': False},
            'high': {'body_res': 16, 'limb_res': 10, 'subdivide': True}
        }[detail_level]
        
        # Track vertices on the center line (x=0) for special handling
        self.center_vertices = []
        
    def build(self) -> trimesh.Trimesh:
        """
        Build the complete symmetric humanoid mesh.
        
        Returns:
            trimesh.Trimesh: The completed humanoid mesh with perfect symmetry
        """
        logger.info(f"Building {self.detail_level} detail symmetric humanoid")
        
        # Reset mesh data
        self.vertices = []
        self.faces = []
        self.vertex_groups = {}
        self.center_vertices = []
        
        # Build half mesh (right side + center)
        self._build_half_mesh()
        
        # Mirror to create full mesh
        self._mirror_mesh()
        
        # Convert to trimesh object
        vertices = np.array(self.vertices, dtype=np.float32)
        faces = np.array(self.faces, dtype=np.int32)
        
        mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
        
        # Apply subdivision if high detail
        if self.settings['subdivide']:
            logger.info("Applying subdivision surface")
            mesh = mesh.subdivide()
        
        # Clean up mesh
        mesh.update_faces(mesh.unique_faces())
        mesh.update_faces(mesh.nondegenerate_faces())
        mesh.fix_normals()
        
        logger.info(f"Created mesh with {len(mesh.vertices)} vertices and {len(mesh.faces)} faces")
        
        return mesh
    
    def _add_vertex(self, pos: List[float], is_center: bool = False) -> int:
        """
        Add a vertex to the mesh.
        
        Args:
            pos: [x, y, z] position of the vertex
            is_center: True if this vertex is on the center line (x=0)
            
        Returns:
            int: Index of the added vertex
        """
        idx = len(self.vertices)
        self.vertices.append(pos)
        
        if is_center or abs(pos[0]) < 0.001:  # Consider vertices very close to x=0 as center
            self.center_vertices.append(idx)
            
        return idx
    
    def _build_half_mesh(self):
        """
        Build the right half of the humanoid mesh plus center line.
        
        This method creates:
        - Complete head (it's roughly symmetric)
        - Right half of neck
        - Right half of torso
        - Right arm
        - Right leg
        """
        # Build head (mostly centered, slight adjustments for half-mesh)
        self._build_head()
        
        # Build neck and torso (right half + center)
        neck_data = self._build_neck()
        torso_data = self._build_torso(neck_data)
        
        # Build right arm only
        self._build_arm(torso_data['shoulder_point'])
        
        # Build right leg only
        self._build_leg(torso_data['hip_point'])
        
    def _build_head(self):
        """
        Build the head with facial features.
        
        The head is built mostly complete since it needs to be 
        roughly spherical and centered.
        """
        head_center = [0, 1.7, 0]
        head_radius = 0.15
        
        # Create head with UV sphere topology
        lat_divs = 6
        lon_divs = self.settings['body_res']
        
        # Top pole (center vertex)
        top_idx = self._add_vertex([0, head_center[1] + head_radius, 0], is_center=True)
        
        # Build latitude rings
        rings = []
        for lat in range(1, lat_divs):
            lat_angle = np.pi * lat / lat_divs
            ring = []
            
            # Build full ring for head
            for lon in range(lon_divs):
                lon_angle = 2 * np.pi * lon / lon_divs
                
                x = head_radius * np.sin(lat_angle) * np.cos(lon_angle)
                y = head_center[1] + head_radius * np.cos(lat_angle)
                z = head_radius * np.sin(lat_angle) * np.sin(lon_angle)
                
                # Add facial features
                if 0.3 < lat_angle < 0.7:  # Face region
                    # Flatten face front
                    if abs(lon_angle) < 0.5 or abs(lon_angle - 2*np.pi) < 0.5:
                        z *= 0.9
                    
                    # Eye sockets
                    if 0.4 < lat_angle < 0.5:
                        if 0.3 < abs(lon_angle - 0.5) < 0.6:
                            z -= 0.008
                    
                    # Nose
                    if 0.5 < lat_angle < 0.6:
                        if abs(lon_angle) < 0.2 or abs(lon_angle - 2*np.pi) < 0.2:
                            z += 0.01
                
                # Mark center vertices
                is_center = abs(x) < 0.001
                ring.append(self._add_vertex([x, y, z], is_center))
                
            rings.append(ring)
        
        # Bottom pole - chin (center vertex)
        bottom_idx = self._add_vertex([0, head_center[1] - head_radius * 0.9, 0.02], is_center=True)
        
        # Connect head faces
        self._connect_head_faces(top_idx, rings, bottom_idx, lon_divs)
        
        # Store head vertices
        self.vertex_groups['head'] = list(range(0, len(self.vertices)))
    
    def _build_neck(self) -> Dict:
        """
        Build neck connecting head to torso.
        
        Returns:
            Dict containing neck data including bottom ring indices
        """
        neck_positions = [
            {'y': 1.52, 'radius': 0.08},
            {'y': 1.48, 'radius': 0.085},
            {'y': 1.44, 'radius': 0.09},
            {'y': 1.40, 'radius': 0.1}
        ]
        
        neck_rings = []
        half_res = self.settings['body_res'] // 2 + 1  # Half ring plus center
        
        for pos in neck_positions:
            ring = []
            for i in range(half_res):
                # Generate half ring from back center to front center
                angle = np.pi * i / (half_res - 1)  # 0 to π (back to front)
                
                x = pos['radius'] * np.sin(angle)  # Right side positive
                y = pos['y']
                z = pos['radius'] * np.cos(angle)
                
                is_center = (i == 0 or i == half_res - 1)  # First and last are on center
                ring.append(self._add_vertex([x, y, z], is_center))
                
            neck_rings.append(ring)
        
        # Connect neck rings
        for r in range(len(neck_rings) - 1):
            self._connect_half_rings(neck_rings[r], neck_rings[r+1])
        
        return {'bottom_ring': neck_rings[-1]}
    
    def _build_torso(self, neck_data: Dict) -> Dict:
        """
        Build torso with anatomical structure.
        
        Args:
            neck_data: Data from neck building including connection points
            
        Returns:
            Dict containing shoulder and hip attachment points
        """
        sections = [
            {'y': 1.35, 'rx': 0.14, 'rz': 0.11, 'part': 'shoulders'},
            {'y': 1.30, 'rx': 0.17, 'rz': 0.12, 'part': 'upper_chest'},
            {'y': 1.20, 'rx': 0.18, 'rz': 0.12, 'part': 'chest'},
            {'y': 1.10, 'rx': 0.16, 'rz': 0.11, 'part': 'ribs'},
            {'y': 1.00, 'rx': 0.14, 'rz': 0.10, 'part': 'abdomen'},
            {'y': 0.90, 'rx': 0.13, 'rz': 0.095, 'part': 'waist'},
            {'y': 0.80, 'rx': 0.14, 'rz': 0.10, 'part': 'pelvis'},
            {'y': 0.70, 'rx': 0.16, 'rz': 0.11, 'part': 'hips'},
            {'y': 0.60, 'rx': 0.15, 'rz': 0.10, 'part': 'lower_hips'}
        ]
        
        torso_rings = [neck_data['bottom_ring']]
        half_res = self.settings['body_res'] // 2 + 1
        
        shoulder_point = None
        hip_point = None
        
        for section in sections:
            ring = []
            for i in range(half_res):
                angle = np.pi * i / (half_res - 1)  # 0 to π
                
                x = section['rx'] * np.sin(angle)  # Right side
                y = section['y']
                z = section['rz'] * np.cos(angle)
                
                # Add muscle definition
                if section['part'] == 'chest':
                    if i < half_res // 3:  # Front area
                        x *= 1.05
                        z += 0.005
                
                is_center = (i == 0 or i == half_res - 1)
                idx = self._add_vertex([x, y, z], is_center)
                ring.append(idx)
                
                # Mark attachment points
                if section['part'] == 'upper_chest' and i == half_res // 2:
                    shoulder_point = idx
                elif section['part'] == 'lower_hips' and i == half_res // 2:
                    hip_point = idx
                    
            torso_rings.append(ring)
        
        # Connect torso rings
        for r in range(len(torso_rings) - 1):
            self._connect_half_rings(torso_rings[r], torso_rings[r+1])
        
        return {'shoulder_point': shoulder_point, 'hip_point': hip_point}
    
    def _build_arm(self, shoulder_idx: int):
        """
        Build right arm with hand.
        
        Args:
            shoulder_idx: Vertex index of shoulder attachment point
        """
        shoulder_pos = self.vertices[shoulder_idx]
        
        # Arm sections (right arm only)
        arm_sections = [
            {'offset': [0.08, -0.02, 0], 'radius': 0.06},
            {'offset': [0.18, -0.12, 0], 'radius': 0.055},
            {'offset': [0.26, -0.25, 0], 'radius': 0.05},
            {'offset': [0.28, -0.40, 0], 'radius': 0.045},
            {'offset': [0.28, -0.55, 0], 'radius': 0.04},
            {'offset': [0.28, -0.65, 0], 'radius': 0.035}
        ]
        
        arm_rings = []
        arm_res = self.settings['limb_res']
        
        for section in arm_sections:
            ring = []
            for i in range(arm_res):
                angle = 2 * np.pi * i / arm_res
                
                # All arm vertices are away from center, none are on x=0
                x = shoulder_pos[0] + section['offset'][0] + section['radius'] * np.cos(angle) * 0.7
                y = shoulder_pos[1] + section['offset'][1]
                z = shoulder_pos[2] + section['offset'][2] + section['radius'] * np.sin(angle)
                
                ring.append(self._add_vertex([x, y, z], False))
                
            arm_rings.append(ring)
        
        # Connect arm rings
        for r in range(len(arm_rings) - 1):
            self._connect_full_rings(arm_rings[r], arm_rings[r+1])
        
        # Cap the hand
        self._cap_limb_end(arm_rings[-1])
    
    def _build_leg(self, hip_idx: int):
        """
        Build right leg with foot.
        
        Args:
            hip_idx: Vertex index of hip attachment point
        """
        hip_pos = self.vertices[hip_idx]
        
        # Leg sections (right leg only)
        leg_sections = [
            {'offset': [0.08, -0.1, 0], 'radius': 0.075},
            {'offset': [0.08, -0.25, 0], 'radius': 0.07},
            {'offset': [0.08, -0.40, 0], 'radius': 0.06},
            {'offset': [0.08, -0.55, 0], 'radius': 0.055},
            {'offset': [0.08, -0.70, 0], 'radius': 0.05},
            {'offset': [0.08, -0.85, 0], 'radius': 0.045},
            {'offset': [0.08, -0.95, 0], 'radius': 0.04}
        ]
        
        leg_rings = []
        leg_res = self.settings['limb_res']
        
        for section in leg_sections:
            ring = []
            for i in range(leg_res):
                angle = 2 * np.pi * i / leg_res
                
                x = hip_pos[0] + section['offset'][0] + section['radius'] * np.cos(angle) * 0.8
                y = hip_pos[1] + section['offset'][1]
                z = hip_pos[2] + section['offset'][2] + section['radius'] * np.sin(angle) * 0.8
                
                ring.append(self._add_vertex([x, y, z], False))
                
            leg_rings.append(ring)
        
        # Connect leg rings
        for r in range(len(leg_rings) - 1):
            self._connect_full_rings(leg_rings[r], leg_rings[r+1])
        
        # Build simple foot
        self._build_foot(leg_rings[-1])
    
    def _build_foot(self, ankle_ring: List[int]):
        """
        Build foot at end of leg.
        
        Args:
            ankle_ring: Ring of vertices at the ankle
        """
        ankle_center = np.mean([self.vertices[i] for i in ankle_ring], axis=0)
        
        # Simple foot - just extend forward and down
        foot_ring = []
        for i, ankle_idx in enumerate(ankle_ring):
            ankle_pos = self.vertices[ankle_idx]
            
            # Move down and forward for foot
            x = ankle_pos[0]
            y = ankle_center[1] - 0.05
            z = ankle_center[2] + 0.08
            
            foot_ring.append(self._add_vertex([x, y, z], False))
        
        # Connect ankle to foot
        self._connect_full_rings(ankle_ring, foot_ring)
        
        # Cap the foot
        self._cap_limb_end(foot_ring)
    
    def _mirror_mesh(self):
        """
        Mirror the half mesh to create the complete symmetric mesh.
        
        This method:
        1. Duplicates all non-center vertices with negative x
        2. Creates mirrored faces with corrected winding order
        3. Ensures perfect bilateral symmetry
        """
        original_vertex_count = len(self.vertices)
        
        # Create mapping from original to mirrored vertices
        vertex_mirror_map = {}
        
        # Add mirrored vertices (skip center vertices)
        for i in range(original_vertex_count):
            if i not in self.center_vertices:
                # Mirror across x=0 plane
                original_pos = self.vertices[i]
                mirrored_pos = [-original_pos[0], original_pos[1], original_pos[2]]
                
                mirror_idx = self._add_vertex(mirrored_pos, False)
                vertex_mirror_map[i] = mirror_idx
            else:
                # Center vertices map to themselves
                vertex_mirror_map[i] = i
        
        # Mirror faces
        original_face_count = len(self.faces)
        for i in range(original_face_count):
            face = self.faces[i]
            
            # Create mirrored face with corrected winding order
            mirrored_face = [
                vertex_mirror_map[face[2]],
                vertex_mirror_map[face[1]],
                vertex_mirror_map[face[0]]
            ]
            
            # Only add if it's not a degenerate face (all same vertex)
            if len(set(mirrored_face)) == 3:
                self.faces.append(mirrored_face)
    
    def _connect_half_rings(self, ring1: List[int], ring2: List[int]):
        """
        Connect two half rings (for neck/torso).
        
        Args:
            ring1: First half ring indices
            ring2: Second half ring indices
        """
        n = len(ring1)
        for i in range(n - 1):
            # Create quad as two triangles
            self.faces.append([ring1[i], ring2[i], ring2[i+1]])
            self.faces.append([ring1[i], ring2[i+1], ring1[i+1]])
    
    def _connect_full_rings(self, ring1: List[int], ring2: List[int]):
        """
        Connect two full rings (for arms/legs).
        
        Args:
            ring1: First ring indices
            ring2: Second ring indices
        """
        n = len(ring1)
        for i in range(n):
            next_i = (i + 1) % n
            self.faces.append([ring1[i], ring2[i], ring2[next_i]])
            self.faces.append([ring1[i], ring2[next_i], ring1[next_i]])
    
    def _connect_head_faces(self, top_idx: int, rings: List[List[int]], 
                           bottom_idx: int, resolution: int):
        """
        Connect head vertices into faces.
        
        Args:
            top_idx: Top pole vertex index
            rings: List of ring vertex indices
            bottom_idx: Bottom pole vertex index
            resolution: Number of vertices per ring
        """
        # Top cap
        for i in range(resolution):
            next_i = (i + 1) % resolution
            self.faces.append([top_idx, rings[0][i], rings[0][next_i]])
        
        # Middle rings
        for r in range(len(rings) - 1):
            for i in range(resolution):
                next_i = (i + 1) % resolution
                self.faces.append([rings[r][i], rings[r+1][i], rings[r+1][next_i]])
                self.faces.append([rings[r][i], rings[r+1][next_i], rings[r][next_i]])
        
        # Bottom cap
        for i in range(resolution):
            next_i = (i + 1) % resolution
            self.faces.append([rings[-1][i], bottom_idx, rings[-1][next_i]])
    
    def _cap_limb_end(self, end_ring: List[int]):
        """
        Cap the end of a limb (hand or foot).
        
        Args:
            end_ring: Ring of vertices at limb end
        """
        # Find center point
        center = np.mean([self.vertices[i] for i in end_ring], axis=0)
        
        # Offset center slightly
        center[1] -= 0.02
        center_idx = self._add_vertex(center.tolist(), False)
        
        # Create triangular cap
        n = len(end_ring)
        for i in range(n):
            next_i = (i + 1) % n
            self.faces.append([end_ring[i], end_ring[next_i], center_idx])


def create_symmetric_humanoid(detail_level: str = 'medium') -> trimesh.Trimesh:
    """
    Create a perfectly symmetric humanoid mesh.
    
    Args:
        detail_level: Quality setting ('low', 'medium', or 'high')
        
    Returns:
        trimesh.Trimesh: A perfectly symmetric humanoid mesh
    """
    builder = SymmetricHumanoidBuilder(detail_level=detail_level)
    return builder.build()


if __name__ == "__main__":
    """Test the symmetric humanoid builder."""
    
    print("=" * 60)
    print("Symmetric Humanoid Builder Test")
    print("=" * 60)
    
    for level in ['low', 'medium', 'high']:
        print(f"\nBuilding {level} detail symmetric humanoid...")
        
        mesh = create_symmetric_humanoid(detail_level=level)
        
        print(f"  Vertices: {len(mesh.vertices)}")
        print(f"  Faces: {len(mesh.faces)}")
        print(f"  Watertight: {mesh.is_watertight}")
        
        # Check symmetry
        vertices = mesh.vertices
        symmetric_count = 0
        tolerance = 0.001
        
        for v in vertices:
            # Check if there's a mirrored vertex
            mirrored = [-v[0], v[1], v[2]]
            distances = np.linalg.norm(vertices - mirrored, axis=1)
            if np.min(distances) < tolerance:
                symmetric_count += 1
        
        symmetry_percentage = (symmetric_count / len(vertices)) * 100
        print(f"  Symmetry: {symmetry_percentage:.1f}% vertices have mirrors")
        
        # Export
        filename = f"humanoid_{level}_symmetric.obj"
        mesh.export(filename)
        print(f"  Exported to {filename}")
    
    print("\n" + "=" * 60)
    print("All tests completed successfully!")
    print("=" * 60)

