"""Mutable world map state."""

import numpy as np

from ..entity import Position, Predator
from .tile import Tile


class WorldMap:
    """Map state backed by a ``(height, width)`` uint8 array."""

    def __init__(
        self,
        tiles: np.ndarray,
        spawn_position: Position,
        predator: Predator,
        rng: np.random.Generator,
    ) -> None:
        self.tiles = tiles
        self.spawn_position = spawn_position
        self.predator = predator
        self.rng = rng

    @property
    def shape(self) -> tuple[int, int]:
        return self.tiles.shape

    def in_bounds(self, position: Position) -> bool:
        height, width = self.shape
        return 0 <= position.row < height and 0 <= position.col < width

    def is_walkable(self, position: Position) -> bool:
        return self.in_bounds(position) and Tile(int(self.tiles[position.row, position.col])) in (
            Tile.GROUND,
            Tile.FOOD,
        )
