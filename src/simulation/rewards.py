"""Centralized reward calculation."""

from dataclasses import dataclass

from src.app.config import WorldConfig


@dataclass(frozen=True, slots=True)
class StepEvents:
    invalid_action: bool = False
    ate_food: bool = False
    predator_hit: bool = False
    died: bool = False
    discovered_cells: int = 0


def calculate_reward(events: StepEvents, config: WorldConfig) -> float:
    """Return the additive reward for a transition."""
    # Compose reward from transition events.
    reward = config.step_reward
    if events.invalid_action:
        reward += config.invalid_reward
    if events.ate_food:
        reward += config.food_reward
    if events.predator_hit:
        reward += config.predator_hit_reward
    if events.died:
        reward += config.death_reward
    reward += events.discovered_cells * config.discovery_reward
    return float(reward)
