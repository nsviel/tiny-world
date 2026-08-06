"""A reactive, observation-only policy for TinyWorld."""

import random

import numpy as np

from src.simulation.actions import Action
from src.simulation.observations import Observation
from src.world.entities import Orientation

from .base import BaseAgent


class RuleBasedAgent(BaseAgent):
    """Prioritize eating, fleeing, visible food, then safe exploration.

    The local grid is world-aligned. The policy consequently tracks an internal
    cardinal orientation, resynchronizing it from ``scalar_features`` on every
    decision. It never relies on environment internals.
    """

    _PREDATOR_DISTANCE = 2

    def __init__(self, seed: int | None = None) -> None:
        self._seed = seed
        self._rng = random.Random(seed)
        self._orientation = Orientation.NORTH

    def reset(self, seed: int | None = None) -> None:
        if seed is not None:
            self._seed = seed
        self._rng.seed(self._seed)
        self._orientation = Orientation.NORTH

    def act(self, observation: Observation) -> Action:
        """Return a single action selected from the observable local state."""
        grid = observation.local_grid
        if grid.ndim != 3 or grid.shape[0] < 3:
            raise ValueError("local_grid must have at least obstacle, food, and predator channels")
        if observation.scalar_features.size < 2:
            raise ValueError("scalar_features must contain orientation_norm")

        # Recover heading without reading environment state.
        self._orientation = Orientation(
            round(float(observation.scalar_features[1]) * 3.0) % 4
        )
        centre = (grid.shape[1] // 2, grid.shape[2] // 2)

        if grid[1, centre[0], centre[1]] > 0.5:
            return Action.EAT

        # Channel indices follow the observation contract.
        predators = self._positions(grid[2])
        nearby = [
            position
            for position in predators
            if self._manhattan(position, centre) <= self._PREDATOR_DISTANCE
        ]
        if nearby:
            desired = self._escape_orientation(grid, centre, nearby)
            if desired is not None:
                return self._steer(desired)

        food = self._positions(grid[1])
        if food:
            target = min(food, key=lambda position: self._manhattan(position, centre))
            desired = self._food_orientation(grid, centre, target)
            if desired is not None:
                return self._steer(desired)

        return self._explore(grid, centre)

    @staticmethod
    def _positions(channel: np.ndarray) -> list[tuple[int, int]]:
        return [(int(row), int(col)) for row, col in np.argwhere(channel > 0.5)]

    @staticmethod
    def _manhattan(first: tuple[int, int], second: tuple[int, int]) -> int:
        return abs(first[0] - second[0]) + abs(first[1] - second[1])

    @staticmethod
    def _destination(
        centre: tuple[int, int], orientation: Orientation
    ) -> tuple[int, int]:
        delta_row, delta_col = orientation.delta
        return centre[0] + delta_row, centre[1] + delta_col

    @classmethod
    def _walkable(
        cls, grid: np.ndarray, centre: tuple[int, int], orientation: Orientation
    ) -> bool:
        row, col = cls._destination(centre, orientation)
        return (
            0 <= row < grid.shape[1]
            and 0 <= col < grid.shape[2]
            and grid[0, row, col] <= 0.5
            and grid[2, row, col] <= 0.5
        )

    def _escape_orientation(
        self,
        grid: np.ndarray,
        centre: tuple[int, int],
        predators: list[tuple[int, int]],
    ) -> Orientation | None:
        candidates = [
            orientation
            for orientation in Orientation
            if self._walkable(grid, centre, orientation)
        ]
        if not candidates:
            return None
        scores = {
            orientation: min(
                self._manhattan(self._destination(centre, orientation), predator)
                for predator in predators
            )
            for orientation in candidates
        }
        best_score = max(scores.values())
        return self._rng.choice(
            [orientation for orientation, score in scores.items() if score == best_score]
        )

    def _food_orientation(
        self,
        grid: np.ndarray,
        centre: tuple[int, int],
        target: tuple[int, int],
    ) -> Orientation | None:
        candidates = [
            orientation
            for orientation in Orientation
            if self._walkable(grid, centre, orientation)
        ]
        if not candidates:
            return None
        best_distance = min(
            self._manhattan(self._destination(centre, orientation), target)
            for orientation in candidates
        )
        best = [
            orientation
            for orientation in candidates
            if self._manhattan(self._destination(centre, orientation), target) == best_distance
        ]
        return min(best, key=self._turn_distance)

    def _explore(self, grid: np.ndarray, centre: tuple[int, int]) -> Action:
        if self._walkable(grid, centre, self._orientation) and self._rng.random() < 0.75:
            return Action.MOVE_FORWARD
        choices = [
            orientation
            for orientation in Orientation
            if self._walkable(grid, centre, orientation)
        ]
        if not choices:
            return Action.IDLE
        return self._steer(self._rng.choice(choices))

    def _turn_distance(self, desired: Orientation) -> int:
        difference = (int(desired) - int(self._orientation)) % 4
        return min(difference, 4 - difference)

    def _steer(self, desired: Orientation) -> Action:
        difference = (int(desired) - int(self._orientation)) % 4
        if difference == 0:
            return Action.MOVE_FORWARD
        if difference == 1:
            return Action.TURN_RIGHT
        if difference == 3:
            return Action.TURN_LEFT
        return self._rng.choice((Action.TURN_LEFT, Action.TURN_RIGHT))
