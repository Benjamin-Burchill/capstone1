"""
Humanoid Parameters - Defines all adjustable characteristics
"""

from dataclasses import dataclass, field
from typing import Optional, Dict
import json


@dataclass
class HumanoidParams:
    """
    Parameters for mathematical humanoid generation.
    
    All ratios are relative to height. Stockiness affects width scaling.
    Based on Vitruvian proportions with adjustability for fantasy races.
    
    Attributes:
        height: Total height in meters (0.5 to 3.0)
        stockiness: Width multiplier (0.5=thin, 1.0=normal, 1.5=stocky)
        
        # Proportions (as fractions of height)
        head_ratio: Head height / total height (default: 0.125 = 1/8)
        torso_ratio: Torso height / total height (default: 0.375)
        arm_length_ratio: Arm length / total height (default: 0.375)
        leg_length_ratio: Leg length / total height (default: 0.5)
        
        # Body part details
        shoulder_width_ratio: Shoulder span / height (default: 0.25)
        hip_width_ratio: Hip width / height (default: 0.18)
        
        # Resolution (affects vertex count)
        body_segments: Vertical resolution for torso (8-16)
        limb_segments: Segments per limb (6-12)
        radial_segments: Vertices around circumference (8-16)
    """
    
    # Global parameters
    height: float = 1.75  # Average human height in meters
    stockiness: float = 1.0  # Width multiplier
    
    # Proportions (Vitruvian defaults)
    head_ratio: float = 0.125  # 1/8 of height
    neck_ratio: float = 0.05
    torso_ratio: float = 0.375  # 3/8 of height
    arm_length_ratio: float = 0.375
    leg_length_ratio: float = 0.5
    
    # Width ratios
    shoulder_width_ratio: float = 0.25  # Relative to height
    hip_width_ratio: float = 0.18
    waist_width_ratio: float = 0.15
    
    # Head details
    head_width_ratio: float = 0.66  # Relative to head height
    head_depth_ratio: float = 0.75  # Front-to-back
    
    # Limb details
    upper_arm_thickness: float = 0.06  # Relative to height
    forearm_thickness: float = 0.05
    hand_size: float = 0.10  # Length relative to height
    
    thigh_thickness: float = 0.08
    calf_thickness: float = 0.06
    foot_size: float = 0.12
    
    # Resolution settings
    body_segments: int = 12  # Vertical torso divisions
    limb_segments: int = 8   # Segments per limb section
    radial_segments: int = 12  # Vertices around circumference
    
    # Fantasy features (optional)
    ear_length: float = 0.0  # 0=human, 0.5=elf, 1.0=very long
    tail_length: float = 0.0  # As fraction of leg length
    horn_length: float = 0.0  # Relative to head size
    
    def __post_init__(self):
        """Validate parameters on creation."""
        assert 0.5 <= self.height <= 3.0, "Height must be 0.5-3.0 meters"
        assert 0.3 <= self.stockiness <= 2.0, "Stockiness must be 0.3-2.0"
        assert self.body_segments >= 4, "Need at least 4 body segments"
        assert self.radial_segments >= 6, "Need at least 6 radial segments"
        
        # Warn if proportions are unrealistic
        total_vertical = self.head_ratio + self.neck_ratio + self.torso_ratio + self.leg_length_ratio
        if total_vertical > 1.2 or total_vertical < 0.8:
            print(f"Warning: Vertical proportions sum to {total_vertical:.2f} (expected ~1.0)")
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON export."""
        return {
            k: v for k, v in self.__dict__.items() 
            if not k.startswith('_')
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'HumanoidParams':
        """Create from dictionary."""
        return cls(**data)
    
    def save(self, filepath: str):
        """Save parameters to JSON file."""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load(cls, filepath: str) -> 'HumanoidParams':
        """Load parameters from JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)


# Preset parameter sets for common body types
PRESETS = {
    'human_male': HumanoidParams(
        height=1.75,
        stockiness=1.0,
        shoulder_width_ratio=0.25,
        hip_width_ratio=0.18
    ),
    
    'human_female': HumanoidParams(
        height=1.65,
        stockiness=0.9,
        shoulder_width_ratio=0.22,
        hip_width_ratio=0.20
    ),
    
    'dwarf': HumanoidParams(
        height=1.2,
        stockiness=1.4,
        head_ratio=0.17,  # Proportionally larger head
        torso_ratio=0.4,
        leg_length_ratio=0.38,  # Shorter legs
        shoulder_width_ratio=0.30
    ),
    
    'elf': HumanoidParams(
        height=1.85,
        stockiness=0.85,
        torso_ratio=0.38,
        arm_length_ratio=0.40,  # Slightly longer limbs
        ear_length=0.6
    ),
    
    'orc': HumanoidParams(
        height=1.95,
        stockiness=1.3,
        shoulder_width_ratio=0.32,
        arm_length_ratio=0.42,  # Long arms
        head_ratio=0.14  # Larger head
    ),
    
    'goblin': HumanoidParams(
        height=1.0,
        stockiness=0.9,
        head_ratio=0.20,  # Large head for small body
        arm_length_ratio=0.40,  # Long arms
        leg_length_ratio=0.42,
        ear_length=0.8
    ),
    
    'child': HumanoidParams(
        height=1.2,
        stockiness=0.95,
        head_ratio=0.18,  # Larger head proportion
        limb_segments=6  # Simpler geometry
    ),
    
    'athletic': HumanoidParams(
        height=1.80,
        stockiness=1.05,
        shoulder_width_ratio=0.27,
        waist_width_ratio=0.14,  # Narrow waist
        upper_arm_thickness=0.065,
        thigh_thickness=0.085
    )
}


def get_preset(name: str) -> HumanoidParams:
    """
    Get a preset parameter set by name.
    
    Args:
        name: Preset name (e.g., 'human_male', 'dwarf', 'elf')
        
    Returns:
        HumanoidParams configured for that body type
    """
    if name not in PRESETS:
        raise ValueError(f"Unknown preset '{name}'. Available: {list(PRESETS.keys())}")
    return PRESETS[name]


if __name__ == "__main__":
    # Test parameter validation
    print("Testing HumanoidParams...")
    
    # Normal human
    human = HumanoidParams()
    print(f"Default human: {human.height}m tall, stockiness={human.stockiness}")
    
    # Test presets
    for preset_name in PRESETS:
        preset = get_preset(preset_name)
        print(f"{preset_name}: {preset.height}m, {preset.stockiness:.2f}x")
    
    # Test save/load
    human.save('test_params.json')
    loaded = HumanoidParams.load('test_params.json')
    assert loaded.height == human.height
    print("Save/load test passed!")
    
    print("\nAll parameter tests passed!")


