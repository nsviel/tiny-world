"""World tile types."""

from enum import IntEnum


class Tile(IntEnum):
    GROUND = 0
    WATER = 1
    TREE = 2
    FOOD = 3
