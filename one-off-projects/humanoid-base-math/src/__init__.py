"""
Mathematical Humanoid Base Generator
====================================

A pure mathematical approach to generating humanoid base meshes from parametric equations.

This is an educational/research subproject exploring procedural generation
as an alternative to artist-created bases like MakeHuman.

Usage:
    from humanoid_base_math.src.mesh import generate_base_mesh
    from humanoid_base_math.src.params import HumanoidParams
    
    params = HumanoidParams(height=1.8, stockiness=1.2)
    mesh = generate_base_mesh(params)
    mesh.export('output.obj')

"""

__version__ = '0.1.0'
__author__ = 'MMORPG Character Creator Team'

from .params import HumanoidParams
from .mesh import generate_base_mesh

__all__ = ['HumanoidParams', 'generate_base_mesh']


