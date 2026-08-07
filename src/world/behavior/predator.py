"""Predator movement behavior."""

import numpy as np

from ..entity import Position
from ..environment.config import WorldConfig
from ..environment.map import WorldMap


def update_predator(world: WorldMap, config: WorldConfig, target: Position) -> Position:
    """Pursue a nearby target or wander using the world's random stream."""
    current = world.predator.position
    options = []
    for delta in ((-1, 0), (0, 1), (1, 0), (0, -1)):
        candidate = current.moved(delta)
        if world.is_walkable(candidate):
            options.append(candidate)
    if not options:
        return current

    distance = abs(current.row - target.row) + abs(current.col - target.col)
    if distance <= config.predator_detection_radius:
        distances = np.asarray(
            [abs(p.row - target.row) + abs(p.col - target.col) for p in options]
        )
        best = np.flatnonzero(distances == distances.min())
        choice = int(world.rng.choice(best))
        world.predator.position = options[choice]
    else:
        world.predator.position = options[int(world.rng.integers(len(options)))]
    return world.predator.position
