"""TinyWorld AI: a small deterministic, headless survival environment."""

from .app.config import WorldConfig
from .simulation import (
    OBSERVATION_CHANNELS,
    SCALAR_FEATURES,
    Action,
    Observation,
    StepEvents,
    calculate_reward,
)
from .world import Agent, Orientation, Position, Predator, Tile, TinyWorldEnv, World

__all__ = [
    "Action",
    "Agent",
    "OBSERVATION_CHANNELS",
    "Observation",
    "Orientation",
    "Position",
    "Predator",
    "SCALAR_FEATURES",
    "StepEvents",
    "Tile",
    "TinyWorldEnv",
    "World",
    "WorldConfig",
    "calculate_reward",
]
