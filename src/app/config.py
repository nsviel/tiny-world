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
