"""Validation helpers for simulation configuration."""

from .config import SimulationConfig


def validate_simulation_config(config: SimulationConfig) -> None:
    """Raise ``ValueError`` when a simulation configuration is inconsistent."""
    if config.view_size < 3 or config.view_size % 2 == 0:
        raise ValueError("view_size must be an odd integer >= 3")
    if config.max_steps is not None and config.max_steps <= 0:
        raise ValueError("max_steps must be positive or None")
    if min(config.idle_cost, config.move_cost, config.turn_cost, config.eat_cost) < 0:
        raise ValueError("action costs cannot be negative")
