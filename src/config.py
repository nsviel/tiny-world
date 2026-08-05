"""Configuration values for the headless TinyWorld environment."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class WorldConfig:
    """All gameplay and generation parameters.

    ``max_steps=None`` disables time-limit truncation. Energy values are kept as
    floats so experiments may use fractional action costs.
    """

    width: int = 40
    height: int = 40
    view_size: int = 11
    initial_energy: float = 100.0
    max_energy: float = 100.0
    food_energy: float = 20.0
    food_count: int = 35
    water_ratio: float = 0.12
    tree_ratio: float = 0.16
    max_steps: int | None = 500

    idle_cost: float = 0.1
    move_cost: float = 1.0
    turn_cost: float = 0.2
    eat_cost: float = 0.1
    predator_damage: float = 25.0
    predator_detection_radius: int = 8

    step_reward: float = -0.01
    food_reward: float = 10.0
    invalid_reward: float = -1.0
    predator_hit_reward: float = -5.0
    death_reward: float = -20.0
    discovery_reward: float = 0.02

    def __post_init__(self) -> None:
        if self.width < 11 or self.height < 11:
            raise ValueError("width and height must both be at least 11")
        if self.view_size < 3 or self.view_size % 2 == 0:
            raise ValueError("view_size must be an odd integer >= 3")
        if not 0 <= self.water_ratio < 1 or not 0 <= self.tree_ratio < 1:
            raise ValueError("terrain ratios must be in [0, 1)")
        if self.water_ratio + self.tree_ratio >= 0.75:
            raise ValueError("terrain ratios leave too little traversable ground")
        if self.food_count < 0:
            raise ValueError("food_count cannot be negative")
        if self.initial_energy <= 0 or self.max_energy <= 0:
            raise ValueError("energy limits must be positive")
        if self.max_steps is not None and self.max_steps <= 0:
            raise ValueError("max_steps must be positive or None")
        if self.predator_detection_radius < 0:
            raise ValueError("predator_detection_radius cannot be negative")
