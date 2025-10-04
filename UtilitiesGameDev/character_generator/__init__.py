"""
Character Generator Package
A parametric 3D character generation system for MMORPG development
"""

__version__ = "1.0.0"
__author__ = "Character Generator Team"

from .character_generator import (
    CharacterGenerator,
    CharacterMesh,
    CharacterParameters,
    MorphTarget,
    CharacterPreset
)

__all__ = [
    'CharacterGenerator',
    'CharacterMesh',
    'CharacterParameters',
    'MorphTarget',
    'CharacterPreset'
]

