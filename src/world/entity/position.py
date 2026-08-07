"""Position and orientation types."""

from dataclasses import dataclass
from enum import IntEnum


class Orientation(IntEnum):
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3

    @property
    def delta(self) -> tuple[int, int]:
        return ((-1, 0), (0, 1), (1, 0), (0, -1))[int(self)]

    def left(self) -> "Orientation":
        return Orientation((int(self) - 1) % 4)

    def right(self) -> "Orientation":
        return Orientation((int(self) + 1) % 4)


@dataclass(frozen=True, slots=True, order=True)
class Position:
    row: int
    col: int

    def moved(self, delta: tuple[int, int]) -> "Position":
        return Position(self.row + delta[0], self.col + delta[1])
