"""Configuration values for TinyWorld simulation rules."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SimulationConfig:
    """Observation, episode, action cost, and reward parameters."""

    view_size: int = 11  # Local grid width
    max_steps: int | None = 500  # Episode limit
    idle_cost: float = 0.1  # Energy per action
    move_cost: float = 1.0  # Energy per action
    turn_cost: float = 0.2  # Energy per action
    eat_cost: float = 0.1  # Energy per action
    step_reward: float = -0.01  # Every transition
    food_reward: float = 10.0  # Successful eating
    invalid_reward: float = -1.0  # Blocked action
    predator_hit_reward: float = -5.0
    death_reward: float = -20.0
    discovery_reward: float = 0.02  # Per new cell
