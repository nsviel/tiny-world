"""Observation types and construction for TinyWorld."""

from dataclasses import dataclass

import numpy as np

from src.world.entity import Agent, Position, Predator
from src.world.environment.tile import Tile


OBSERVATION_CHANNELS = ("obstacles", "food", "predator", "agent")
SCALAR_FEATURES = ("energy_norm", "orientation_norm", "food", "time_norm")


@dataclass(frozen=True, slots=True)
class Observation:
    """An observation containing exactly one spatial and one scalar array.

    ``local_grid`` is a world-aligned float32 tensor shaped
    ``(4, view_size, view_size)``. Its binary channels are obstacles (water,
    trees and out-of-map cells), food, predator and agent. The agent channel is
    set at the centre.

    ``scalar_features`` is float32 and ordered as ``energy / max_energy``,
    ``orientation / 3`` (N=0, E=1/3, S=2/3, W=1), cumulative food collected,
    and elapsed time divided by ``max_steps``. When no time limit is configured,
    time uses the bounded transform ``time / (time + 1)``.
    """

    local_grid: np.ndarray
    scalar_features: np.ndarray

    def as_dict(self) -> dict[str, np.ndarray]:
        return {"local_grid": self.local_grid, "scalar_features": self.scalar_features}


def make_observation(
    tiles: np.ndarray,
    agent: Agent,
    predator: Predator,
    time: int,
    view_size: int,
    max_energy: float,
    max_steps: int | None,
) -> Observation:
    radius = view_size // 2
    # Channels stay world-aligned around the agent.
    local = np.zeros((4, view_size, view_size), dtype=np.float32)
    height, width = tiles.shape
    for vr, row in enumerate(range(agent.position.row - radius, agent.position.row + radius + 1)):
        for vc, col in enumerate(range(agent.position.col - radius, agent.position.col + radius + 1)):
            if not (0 <= row < height and 0 <= col < width):
                # Treat unseen map edges as obstacles.
                local[0, vr, vc] = 1.0
                continue
            tile = Tile(int(tiles[row, col]))
            if tile in (Tile.WATER, Tile.TREE):
                local[0, vr, vc] = 1.0
            elif tile == Tile.FOOD:
                local[1, vr, vc] = 1.0
            if predator.position == Position(row, col):
                local[2, vr, vc] = 1.0
    local[3, radius, radius] = 1.0

    time_norm = time / max_steps if max_steps is not None else time / (time + 1.0)
    scalars = np.asarray(
        (
            np.clip(agent.energy / max_energy, 0.0, 1.0),
            int(agent.orientation) / 3.0,
            agent.food_eaten,
            time_norm,
        ),
        dtype=np.float32,
    )
    return Observation(local_grid=local, scalar_features=scalars)
