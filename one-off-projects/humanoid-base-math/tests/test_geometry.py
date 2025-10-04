"""
Unit tests for geometry functions
"""

import pytest
import numpy as np
import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from geometry import (
    generate_spline_curve,
    create_ellipse_profile,
    create_tapered_cylinder,
    create_sphere,
    loft_profile_along_curve
)


class TestSplines:
    def test_spline_basic(self):
        """Test basic spline generation"""
        points = np.array([[0, 0], [1, 1], [2, 0]])
        curve = generate_spline_curve(points, num_samples=10)
        
        assert curve.shape == (10, 2)
        assert curve[0, 0] == pytest.approx(0, abs=0.1)  # Starts at first point
        assert curve[-1, 0] == pytest.approx(2, abs=0.1)  # Ends at last point
    
    def test_closed_spline(self):
        """Test closed spline (loop)"""
        points = np.array([[0, 0], [1, 0], [1, 1], [0, 1]])
        curve = generate_spline_curve(points, num_samples=20, closed=True)
        
        assert curve.shape == (20, 2)
        # First and last should be close (closed loop)
        assert np.allclose(curve[0], curve[-1], atol=0.2)


class TestProfiles:
    def test_ellipse_profile(self):
        """Test ellipse generation"""
        profile = create_ellipse_profile(width=2.0, depth=1.0, segments=12)
        
        assert profile.shape == (12, 2)
        
        # Check max width and depth
        assert np.max(np.abs(profile[:, 0])) == pytest.approx(1.0, abs=0.01)  # width/2
        assert np.max(np.abs(profile[:, 1])) == pytest.approx(0.5, abs=0.01)  # depth/2
    
    def test_circular_profile(self):
        """Test circular profile (equal width/depth)"""
        profile = create_ellipse_profile(1.0, 1.0, segments=16)
        
        # All points should be same distance from origin
        distances = np.linalg.norm(profile, axis=1)
        assert np.allclose(distances, 0.5, atol=0.01)


class TestCylinder:
    def test_straight_cylinder(self):
        """Test cylinder with no taper"""
        verts, faces = create_tapered_cylinder(
            length=2.0,
            radius_start=0.5,
            radius_end=0.5,
            segments=8,
            rings=3
        )
        
        # Check vertex count: rings * segments
        assert len(verts) == 3 * 8
        
        # Check face count: (rings-1) * segments * 2 triangles
        assert len(faces) == (3 - 1) * 8 * 2
    
    def test_tapered_cylinder(self):
        """Test tapered cylinder"""
        verts, faces = create_tapered_cylinder(
            length=1.0,
            radius_start=1.0,
            radius_end=0.5,
            segments=8,
            rings=2
        )
        
        assert len(verts) > 0
        assert len(faces) > 0
        
        # Bottom ring should be larger
        bottom_ring = verts[:8]
        top_ring = verts[8:16]
        
        bottom_radius = np.mean(np.linalg.norm(bottom_ring[:, [0, 2]], axis=1))
        top_radius = np.mean(np.linalg.norm(top_ring[:, [0, 2]], axis=1))
        
        assert bottom_radius > top_radius


class TestSphere:
    def test_sphere_basic(self):
        """Test sphere generation"""
        verts, faces = create_sphere(radius=1.0, lat_segments=4, lon_segments=6)
        
        # Check vertex count: 2 poles + (lat_seg - 1) * lon_seg
        expected_verts = 2 + (4 - 1) * 6
        assert len(verts) == expected_verts
        
        assert len(faces) > 0
    
    def test_sphere_radius(self):
        """Test sphere vertices are at correct radius"""
        verts, faces = create_sphere(radius=2.0, lat_segments=5, lon_segments=8)
        
        # All vertices should be distance ~2.0 from origin
        distances = np.linalg.norm(verts, axis=1)
        assert np.allclose(distances, 2.0, atol=0.01)


class TestLofting:
    def test_loft_basic(self):
        """Test basic lofting"""
        # Simple square profile
        profile = np.array([[0.5, 0.5], [0.5, -0.5], [-0.5, -0.5], [-0.5, 0.5]])
        
        # Straight spine
        spine = np.array([[0, 0, 0], [0, 1, 0], [0, 2, 0]])
        
        verts, faces = loft_profile_along_curve(profile, spine)
        
        # Vertex count: len(profile) * len(spine)
        assert len(verts) == len(profile) * len(spine)
        
        # Face count: (len(spine) - 1) * len(profile) * 2 triangles
        expected_faces = (len(spine) - 1) * len(profile) * 2
        assert len(faces) == expected_faces
    
    def test_loft_with_scaling(self):
        """Test lofting with scale variation"""
        profile = create_ellipse_profile(1.0, 1.0, segments=8)
        spine = np.array([[0, 0, 0], [0, 1, 0]])
        scales = np.array([1.0, 0.5])  # Taper to half size
        
        verts, faces = loft_profile_along_curve(profile, spine, scales)
        
        # Bottom ring should be larger than top
        bottom_ring = verts[:8]
        top_ring = verts[8:16]
        
        bottom_size = np.mean(np.linalg.norm(bottom_ring[:, [0, 2]], axis=1))
        top_size = np.mean(np.linalg.norm(top_ring[:, [0, 2]], axis=1))
        
        assert bottom_size > top_size


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, '-v'])


