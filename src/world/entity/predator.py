"""Predator entity state."""

from dataclasses import dataclass

from .base import Entity


@dataclass(slots=True)
class Predator(Entity):
    pass
