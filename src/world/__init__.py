"""World entities, generation, and the headless environment."""

from typing import TYPE_CHECKING, Any

from .entity import Agent, Orientation, Position, Predator
from .environment import Tile, WorldConfig, WorldMap

# Compatibility alias for the former public name.
World = WorldMap

if TYPE_CHECKING:
    from .environment.env import TinyWorldEnv


def __getattr__(name: str) -> Any:
    """Load the environment lazily to avoid a cycle with game observations."""
    if name == "TinyWorldEnv":
        from .environment.env import TinyWorldEnv

        return TinyWorldEnv
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    "Agent",
    "Orientation",
    "Position",
    "Predator",
    "Tile",
    "TinyWorldEnv",
    "World",
    "WorldConfig",
    "WorldMap",
]
