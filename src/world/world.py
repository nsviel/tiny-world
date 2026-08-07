"""Procedural world generation and predator movement."""

from collections import deque

import numpy as np

from .config import WorldConfig

from .entities import Position, Predator, Tile
from .validation import validate_world_config


class World:
    """Mutable public world state backed by a ``(height, width)`` uint8 array."""

    def __init__(self, config: WorldConfig, seed: int | None = None) -> None:
        validate_world_config(config)
        self.config = config
        self.seed = seed
        # One seeded stream controls all world randomness.
        self.rng = np.random.default_rng(seed)
        self.tiles = np.empty((config.height, config.width), dtype=np.uint8)
        self.spawn_position = Position(0, 0)
        self.predator = Predator(Position(0, 0))
        self.generate()

    @property
    def shape(self) -> tuple[int, int]:
        return self.tiles.shape

    def in_bounds(self, position: Position) -> bool:
        return 0 <= position.row < self.config.height and 0 <= position.col < self.config.width

    def is_walkable(self, position: Position) -> bool:
        return self.in_bounds(position) and Tile(int(self.tiles[position.row, position.col])) in (
            Tile.GROUND,
            Tile.FOOD,
        )

    def generate(self) -> None:
        """Generate terrain, retaining one connected traversable land mass."""
        cfg = self.config
        # Smooth noise creates broad, readable biomes.
        water_noise = self._smooth_noise(self.rng.random((cfg.height, cfg.width)), passes=4)
        forest_noise = self._smooth_noise(self.rng.random((cfg.height, cfg.width)), passes=3)
        self.tiles.fill(Tile.GROUND)
        if cfg.water_ratio > 0:
            self.tiles[water_noise <= np.quantile(water_noise, cfg.water_ratio)] = Tile.WATER
        if cfg.tree_ratio > 0:
            available = self.tiles == Tile.GROUND
            threshold = np.quantile(forest_noise[available], 1.0 - cfg.tree_ratio)
            self.tiles[available & (forest_noise >= threshold)] = Tile.TREE
        self.tiles[[0, -1], :] = Tile.WATER
        self.tiles[:, [0, -1]] = Tile.WATER

        components = self._ground_components()
        if not components:
            raise RuntimeError("world generation produced no traversable ground")
        # Keep the largest connected ground component.
        land = max(components, key=len)
        land_set = set(land)
        # Seal unusable isolated pockets with trees.
        for component in components:
            if component is not land:
                for pos in component:
                    self.tiles[pos.row, pos.col] = Tile.TREE

        candidates = sorted(land_set)
        needed = cfg.food_count + 2
        if len(candidates) < needed:
            raise ValueError(f"not enough connected ground for {cfg.food_count} food items")
        chosen = self.rng.choice(len(candidates), size=needed, replace=False)
        self.spawn_position = candidates[int(chosen[0])]
        self.predator = Predator(candidates[int(chosen[1])])
        for index in chosen[2:]:
            pos = candidates[int(index)]
            self.tiles[pos.row, pos.col] = Tile.FOOD

    @staticmethod
    def _smooth_noise(noise: np.ndarray, passes: int) -> np.ndarray:
        for _ in range(passes):
            padded = np.pad(noise, 1, mode="edge")
            neighbourhoods = [
                padded[dr : dr + noise.shape[0], dc : dc + noise.shape[1]]
                for dr in range(3)
                for dc in range(3)
            ]
            noise = np.mean(np.stack(neighbourhoods), axis=0)
        return noise

    def _ground_components(self) -> list[list[Position]]:
        # Flood-fill every traversable component.
        seen: set[Position] = set()
        components: list[list[Position]] = []
        for row in range(self.config.height):
            for col in range(self.config.width):
                start = Position(row, col)
                if start in seen or Tile(int(self.tiles[row, col])) != Tile.GROUND:
                    continue
                component: list[Position] = []
                queue = deque([start])
                seen.add(start)
                while queue:
                    current = queue.popleft()
                    component.append(current)
                    for delta in ((-1, 0), (0, 1), (1, 0), (0, -1)):
                        nxt = current.moved(delta)
                        if nxt not in seen and self.in_bounds(nxt) and Tile(int(self.tiles[nxt.row, nxt.col])) == Tile.GROUND:
                            seen.add(nxt)
                            queue.append(nxt)
                components.append(component)
        return components

    def move_predator(self, target: Position) -> Position:
        """Pursue within detection range, otherwise wander randomly.

        Detection uses Manhattan distance. Both pursuit tie-breaking and random
        wandering consume this world's seeded NumPy generator, making complete
        trajectories reproducible for a seed and action sequence.
        """
        current = self.predator.position
        options = []
        for delta in ((-1, 0), (0, 1), (1, 0), (0, -1)):
            candidate = current.moved(delta)
            if self.is_walkable(candidate):
                options.append(candidate)
        if not options:
            return current

        distance = abs(current.row - target.row) + abs(current.col - target.col)
        if distance <= self.config.predator_detection_radius:
            distances = np.asarray(
                [abs(p.row - target.row) + abs(p.col - target.col) for p in options]
            )
            best = np.flatnonzero(distances == distances.min())
            choice = int(self.rng.choice(best))
            self.predator.position = options[choice]
        else:
            self.predator.position = options[int(self.rng.integers(len(options)))]
        return self.predator.position
