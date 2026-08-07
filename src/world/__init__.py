"""World entities, generation, and the headless environment."""

from typing import TYPE_CHECKING, Any

from .config import WorldConfig
from .entities import Agent, Orientation, Position, Predator, Tile
from .world import World

if TYPE_CHECKING:
    from .env import TinyWorldEnv


def __getattr__(name: str) -> Any:
    """Load the environment lazily to avoid a cycle with game observations."""
    if name == "TinyWorldEnv":
        from .env import TinyWorldEnv

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
]
