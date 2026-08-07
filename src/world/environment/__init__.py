"""World configuration, generation, map state, and environment."""

from typing import TYPE_CHECKING, Any

from .config import WorldConfig
from .generation import generate_world
from .map import WorldMap
from .tile import Tile

if TYPE_CHECKING:
    from .env import TinyWorldEnv


def __getattr__(name: str) -> Any:
    """Load the environment lazily to avoid simulation import cycles."""
    if name == "TinyWorldEnv":
        from .env import TinyWorldEnv

        return TinyWorldEnv
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "Tile",
    "TinyWorldEnv",
    "WorldConfig",
    "WorldMap",
    "generate_world",
]
