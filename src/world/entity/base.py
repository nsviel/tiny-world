"""Base world entity."""

from dataclasses import dataclass

from .position import Position


@dataclass(slots=True)
class Entity:
    position: Position
