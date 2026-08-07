"""Agent entity state."""

from dataclasses import dataclass

from .base import Entity
from .position import Orientation


@dataclass(slots=True)
class Agent(Entity):
    orientation: Orientation = Orientation.NORTH
    energy: float = 100.0
    food_eaten: int = 0
    alive: bool = True
