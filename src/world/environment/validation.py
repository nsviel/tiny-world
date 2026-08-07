"""Validation helpers for world configuration."""

from .config import WorldConfig


def validate_world_config(config: WorldConfig) -> None:
    """Raise ``ValueError`` when a world configuration is inconsistent."""
    if config.width < 11 or config.height < 11:
        raise ValueError("width and height must both be at least 11")

    if not 0 <= config.water_ratio < 1 or not 0 <= config.tree_ratio < 1:
        raise ValueError("terrain ratios must be in [0, 1)")
    if config.water_ratio + config.tree_ratio >= 0.75:
        raise ValueError("terrain ratios leave too little traversable ground")
    if config.food_count < 0:
        raise ValueError("food_count cannot be negative")
    if config.initial_energy <= 0 or config.max_energy <= 0:
        raise ValueError("energy limits must be positive")

    if config.predator_detection_radius < 0:
        raise ValueError("predator_detection_radius cannot be negative")
