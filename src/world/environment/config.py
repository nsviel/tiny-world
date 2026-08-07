"""Configuration values for TinyWorld generation and entities."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class WorldConfig:
    """World generation, energy, and predator parameters."""

    width: int = 40
    height: int = 40
    initial_energy: float = 100.0
    max_energy: float = 100.0
    food_energy: float = 20.0  # Energy restored
    food_count: int = 35
    water_ratio: float = 0.12  # Map coverage
    tree_ratio: float = 0.16  # Map coverage
    predator_damage: float = 25.0  # Energy lost
    predator_detection_radius: int = 8  # Manhattan cells
