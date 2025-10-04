"""
Mesh Assembly - Combines geometric primitives into complete humanoid
"""

import numpy as np
import trimesh
from typing import Tuple, Optional
from .params import HumanoidParams
from .geometry import (
    create_sphere,
    create_tapered_cylinder,
    create_ellipse_profile,
    loft_profile_along_curve,
    create_anatomical_torso_profile,
    mirror_vertices_x,
    smooth_vertices_laplacian
)


class HumanoidMeshBuilder:
    """
    Builds a complete humanoid mesh from parameters using mathematical primitives.
    """
    
    def __init__(self, params: HumanoidParams):
        """
        Initialize builder with parameters.
        
        Args:
            params: HumanoidParams defining the character
        """
        self.params = params
        self.all_vertices = []
        self.all_faces = []
        self.vertex_offset = 0
        
    def add_component(self, vertices: np.ndarray, faces: np.ndarray):
        """
        Add a component to the mesh with proper index offsetting.
        
        Args:
            vertices: Component vertices
            faces: Component faces (will be offset)
        """
        self.all_vertices.append(vertices)
        # Offset face indices
        offset_faces = faces + self.vertex_offset
        self.all_faces.append(offset_faces)
        self.vertex_offset += len(vertices)
    
    def build_head(self) -> Tuple[np.ndarray, np.ndarray]:
        """Generate head as UV sphere."""
        head_height = self.params.height * self.params.head_ratio
        head_radius = head_height * self.params.head_width_ratio / 2
        
        # Create sphere
        vertices, faces = create_sphere(
            radius=head_radius,
            lat_segments=6,
            lon_segments=self.params.radial_segments
        )
        
        # Position at top of body
        neck_height = self.params.height * self.params.neck_ratio
        torso_height = self.params.height * self.params.torso_ratio
        y_offset = neck_height + torso_height + head_radius
        
        vertices[:, 1] += y_offset
        
        return vertices, faces
    
    def build_neck(self) -> Tuple[np.ndarray, np.ndarray]:
        """Generate neck connecting head to torso."""
        neck_height = self.params.height * self.params.neck_ratio
        torso_height = self.params.height * self.params.torso_ratio
        
        neck_radius_top = self.params.height * self.params.head_ratio * 0.2
        neck_radius_bottom = self.params.height * self.params.shoulder_width_ratio * 0.15
        
        vertices, faces = create_tapered_cylinder(
            length=neck_height,
            radius_start=neck_radius_bottom,
            radius_end=neck_radius_top,
            segments=self.params.radial_segments,
            rings=2
        )
        
        # Position on top of torso
        vertices[:, 1] += torso_height
        
        return vertices, faces
    
    def build_torso(self) -> Tuple[np.ndarray, np.ndarray]:
        """Generate torso with anatomical curves."""
        torso_height = self.params.height * self.params.torso_ratio
        
        # Create anatomical profiles
        profiles = create_anatomical_torso_profile(
            height=self.params.height,
            stockiness=self.params.stockiness,
            segments=self.params.radial_segments
        )
        
        # Create spine curve (vertical line with slight S-curve)
        n_profiles = len(profiles)
        y_positions = np.linspace(0, torso_height, n_profiles)
        
        # Add slight forward curve for realism
        z_curve = np.array([0.0, -0.01, -0.02, -0.01, 0.0, 0.01]) * self.params.height
        
        spine = np.column_stack([
            np.zeros(n_profiles),
            y_positions,
            z_curve[:n_profiles]
        ])
        
        # Loft profiles along spine
        # Stack all profile points with proper offsets
        all_verts = []
        all_faces = []
        
        for i in range(n_profiles - 1):
            # Loft between two profiles
            profile1 = profiles[i]
            profile2 = profiles[i + 1]
            
            # Create mini-spine between two heights
            mini_spine = np.array([spine[i], spine[i + 1]])
            
            # Loft
            verts, faces = loft_profile_along_curve(profile1, mini_spine)
            
            # Offset faces and add
            if all_verts:
                faces = faces + len(np.vstack(all_verts))
            
            all_verts.append(verts)
            all_faces.append(faces)
        
        vertices = np.vstack(all_verts)
        faces = np.vstack(all_faces)
        
        return vertices, faces
    
    def build_arm(self, side: str = 'right') -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate arm (upper arm + forearm + hand).
        
        Args:
            side: 'right' or 'left'
        """
        arm_length = self.params.height * self.params.arm_length_ratio
        upper_arm_length = arm_length * 0.45
        forearm_length = arm_length * 0.45
        hand_length = arm_length * 0.10
        
        # Upper arm
        upper_arm_verts, upper_arm_faces = create_tapered_cylinder(
            length=upper_arm_length,
            radius_start=self.params.height * self.params.upper_arm_thickness,
            radius_end=self.params.height * self.params.upper_arm_thickness * 0.9,
            segments=self.params.radial_segments // 2,
            rings=self.params.limb_segments // 2
        )
        
        # Forearm
        forearm_verts, forearm_faces = create_tapered_cylinder(
            length=forearm_length,
            radius_start=self.params.height * self.params.forearm_thickness,
            radius_end=self.params.height * self.params.forearm_thickness * 0.8,
            segments=self.params.radial_segments // 2,
            rings=self.params.limb_segments // 2
        )
        forearm_verts[:, 1] += upper_arm_length
        forearm_faces += len(upper_arm_verts)
        
        # Hand (simple tapered end)
        hand_verts, hand_faces = create_tapered_cylinder(
            length=hand_length,
            radius_start=self.params.height * self.params.forearm_thickness * 0.6,
            radius_end=self.params.height * self.params.forearm_thickness * 0.4,
            segments=self.params.radial_segments // 2,
            rings=2
        )
        hand_verts[:, 1] += upper_arm_length + forearm_length
        hand_faces += len(upper_arm_verts) + len(forearm_verts)
        
        # Combine arm parts
        arm_verts = np.vstack([upper_arm_verts, forearm_verts, hand_verts])
        arm_faces = np.vstack([upper_arm_faces, forearm_faces, hand_faces])
        
        # Position at shoulder
        shoulder_width = self.params.height * self.params.shoulder_width_ratio
        torso_height = self.params.height * self.params.torso_ratio
        shoulder_y = torso_height * 0.95
        
        # Rotate arm downward
        angle = np.radians(-10)  # Slight downward angle
        rotation = np.array([
            [np.cos(angle), -np.sin(angle), 0],
            [np.sin(angle), np.cos(angle), 0],
            [0, 0, 1]
        ])
        
        arm_verts = arm_verts @ rotation.T
        
        # Position
        x_offset = shoulder_width / 2 if side == 'right' else -shoulder_width / 2
        arm_verts[:, 0] += x_offset
        arm_verts[:, 1] += shoulder_y
        
        return arm_verts, arm_faces
    
    def build_leg(self, side: str = 'right') -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate leg (thigh + calf + foot).
        
        Args:
            side: 'right' or 'left'
        """
        leg_length = self.params.height * self.params.leg_length_ratio
        thigh_length = leg_length * 0.48
        calf_length = leg_length * 0.48
        foot_length = leg_length * 0.04
        
        # Thigh
        thigh_verts, thigh_faces = create_tapered_cylinder(
            length=thigh_length,
            radius_start=self.params.height * self.params.thigh_thickness,
            radius_end=self.params.height * self.params.thigh_thickness * 0.85,
            segments=self.params.radial_segments // 2,
            rings=self.params.limb_segments // 2
        )
        
        # Calf
        calf_verts, calf_faces = create_tapered_cylinder(
            length=calf_length,
            radius_start=self.params.height * self.params.calf_thickness,
            radius_end=self.params.height * self.params.calf_thickness * 0.7,
            segments=self.params.radial_segments // 2,
            rings=self.params.limb_segments // 2
        )
        calf_verts[:, 1] += thigh_length
        calf_faces += len(thigh_verts)
        
        # Foot (simple)
        foot_verts, foot_faces = create_tapered_cylinder(
            length=foot_length,
            radius_start=self.params.height * self.params.calf_thickness * 0.6,
            radius_end=self.params.height * self.params.calf_thickness * 0.5,
            segments=self.params.radial_segments // 2,
            rings=2
        )
        foot_verts[:, 1] += thigh_length + calf_length
        foot_faces += len(thigh_verts) + len(calf_verts)
        
        # Combine leg parts
        leg_verts = np.vstack([thigh_verts, calf_verts, foot_verts])
        leg_faces = np.vstack([thigh_faces, calf_faces, foot_faces])
        
        # Flip upside down (legs go downward)
        leg_verts[:, 1] *= -1
        
        # Position at hip
        hip_width = self.params.height * self.params.hip_width_ratio
        x_offset = hip_width / 2 if side == 'right' else -hip_width / 2
        leg_verts[:, 0] += x_offset
        
        return leg_verts, leg_faces
    
    def build(self, apply_symmetry: bool = True, apply_smoothing: bool = True) -> trimesh.Trimesh:
        """
        Build the complete humanoid mesh.
        
        Args:
            apply_symmetry: Mirror across X axis for bilateral symmetry
            apply_smoothing: Apply Laplacian smoothing
            
        Returns:
            Complete trimesh.Trimesh object
        """
        # Reset builder
        self.all_vertices = []
        self.all_faces = []
        self.vertex_offset = 0
        
        # Build components
        print(f"Building humanoid: {self.params.height:.2f}m tall, {self.params.stockiness:.2f}x stockiness")
        
        # Central components
        head_v, head_f = self.build_head()
        self.add_component(head_v, head_f)
        
        neck_v, neck_f = self.build_neck()
        self.add_component(neck_v, neck_f)
        
        torso_v, torso_f = self.build_torso()
        self.add_component(torso_v, torso_f)
        
        # Right side only (will mirror if symmetry=True)
        right_arm_v, right_arm_f = self.build_arm('right')
        self.add_component(right_arm_v, right_arm_f)
        
        right_leg_v, right_leg_f = self.build_leg('right')
        self.add_component(right_leg_v, right_leg_f)
        
        # Combine all
        vertices = np.vstack(self.all_vertices)
        faces = np.vstack(self.all_faces)
        
        print(f"Base mesh: {len(vertices)} vertices, {len(faces)} faces")
        
        # Apply symmetry
        if apply_symmetry:
            # Note: This is simplified - proper symmetry needs center vertex detection
            # For now, just manually add left arm/leg
            left_arm_v, left_arm_f = self.build_arm('left')
            left_leg_v, left_leg_f = self.build_leg('left')
            
            left_arm_f += len(vertices)
            left_leg_f += len(vertices) + len(left_arm_v)
            
            vertices = np.vstack([vertices, left_arm_v, left_leg_v])
            faces = np.vstack([faces, left_arm_f, left_leg_f])
            
            print(f"After symmetry: {len(vertices)} vertices, {len(faces)} faces")
        
        # Create mesh
        mesh = trimesh.Trimesh(vertices=vertices, faces=faces, process=False)
        
        # Apply smoothing if requested
        if apply_smoothing:
            vertices = smooth_vertices_laplacian(
                mesh.vertices,
                mesh.faces,
                iterations=1,
                factor=0.3
            )
            mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
            print("Smoothing applied")
        
        # Clean up mesh
        mesh.remove_duplicate_faces()
        mesh.remove_degenerate_faces()
        mesh.fix_normals()
        
        print(f"Final mesh: {len(mesh.vertices)} vertices, {len(mesh.faces)} faces")
        print(f"Watertight: {mesh.is_watertight}")
        print(f"Bounds: {mesh.bounds}")
        
        return mesh


def generate_base_mesh(params: HumanoidParams,
                       apply_symmetry: bool = True,
                       apply_smoothing: bool = True) -> trimesh.Trimesh:
    """
    Main entry point: Generate a humanoid base mesh from parameters.
    
    Args:
        params: HumanoidParams defining the character
        apply_symmetry: Apply bilateral symmetry
        apply_smoothing: Apply smoothing
        
    Returns:
        Complete humanoid mesh as trimesh.Trimesh
        
    Example:
        >>> from humanoid_base_math.src.params import HumanoidParams
        >>> from humanoid_base_math.src.mesh import generate_base_mesh
        >>> 
        >>> params = HumanoidParams(height=1.8, stockiness=1.2)
        >>> mesh = generate_base_mesh(params)
        >>> mesh.export('my_humanoid.obj')
    """
    builder = HumanoidMeshBuilder(params)
    return builder.build(apply_symmetry=apply_symmetry, apply_smoothing=apply_smoothing)


if __name__ == "__main__":
    # Test mesh generation
    from .params import get_preset
    
    print("Testing humanoid mesh generation...")
    print("=" * 60)
    
    # Test with human preset
    params = get_preset('human_male')
    mesh = generate_base_mesh(params)
    
    print("\nTest completed successfully!")
    print(f"Generated {len(mesh.vertices)} vertex humanoid mesh")


