"""Procedural world generation."""

from collections import deque

import numpy as np

from ..entity import Position, Predator
from .config import WorldConfig
from .map import WorldMap
from .tile import Tile
from .validation import validate_world_config


def smooth_noise(noise: np.ndarray, passes: int) -> np.ndarray:
    """Average each cell with its neighbourhood for a number of passes."""
    for _ in range(passes):
        padded = np.pad(noise, 1, mode="edge")
        neighbourhoods = [
            padded[dr : dr + noise.shape[0], dc : dc + noise.shape[1]]
            for dr in range(3)
            for dc in range(3)
        ]
        noise = np.mean(np.stack(neighbourhoods), axis=0)
    return noise


def ground_components(world: WorldMap) -> list[list[Position]]:
    """Return all connected ground components in scan order."""
    seen: set[Position] = set()
    components: list[list[Position]] = []
    height, width = world.shape
    for row in range(height):
        for col in range(width):
            start = Position(row, col)
            if start in seen or Tile(int(world.tiles[row, col])) != Tile.GROUND:
                continue
            component: list[Position] = []
            queue = deque([start])
            seen.add(start)
            while queue:
                current = queue.popleft()
                component.append(current)
                for delta in ((-1, 0), (0, 1), (1, 0), (0, -1)):
                    nxt = current.moved(delta)
                    if (
                        nxt not in seen
                        and world.in_bounds(nxt)
                        and Tile(int(world.tiles[nxt.row, nxt.col])) == Tile.GROUND
                    ):
                        seen.add(nxt)
                        queue.append(nxt)
            components.append(component)
    return components


def generate_world(config: WorldConfig, seed: int | None = None) -> WorldMap:
    """Generate terrain and entities from one seeded random stream."""
    validate_world_config(config)
    rng = np.random.default_rng(seed)
    tiles = np.empty((config.height, config.width), dtype=np.uint8)
    world = WorldMap(tiles, Position(0, 0), Predator(Position(0, 0)), rng)

    # Smooth noise creates broad, readable biomes.
    water_noise = smooth_noise(rng.random((config.height, config.width)), passes=4)
    forest_noise = smooth_noise(rng.random((config.height, config.width)), passes=3)
    tiles.fill(Tile.GROUND)
    if config.water_ratio > 0:
        tiles[water_noise <= np.quantile(water_noise, config.water_ratio)] = Tile.WATER
    if config.tree_ratio > 0:
        available = tiles == Tile.GROUND
        threshold = np.quantile(forest_noise[available], 1.0 - config.tree_ratio)
        tiles[available & (forest_noise >= threshold)] = Tile.TREE
    tiles[[0, -1], :] = Tile.WATER
    tiles[:, [0, -1]] = Tile.WATER

    components = ground_components(world)
    if not components:
        raise RuntimeError("world generation produced no traversable ground")
    land = max(components, key=len)
    land_set = set(land)
    # Seal unusable isolated pockets with trees.
    for component in components:
        if component is not land:
            for pos in component:
                tiles[pos.row, pos.col] = Tile.TREE

    candidates = sorted(land_set)
    needed = config.food_count + 2
    if len(candidates) < needed:
        raise ValueError(f"not enough connected ground for {config.food_count} food items")
    chosen = rng.choice(len(candidates), size=needed, replace=False)
    world.spawn_position = candidates[int(chosen[0])]
    world.predator = Predator(candidates[int(chosen[1])])
    for index in chosen[2:]:
        pos = candidates[int(index)]
        tiles[pos.row, pos.col] = Tile.FOOD
    return world
