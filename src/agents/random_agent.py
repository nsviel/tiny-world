"""Uniform random baseline agent."""

import random

from src.simulation.actions import Action
from src.simulation.observations import Observation

from .base import BaseAgent


class RandomAgent(BaseAgent):
    """Choose uniformly among all actions exposed by :class:`Action`.

    An observation cannot reveal whether every action will succeed (for example,
    eating depends on the current tile). Therefore "valid" means every member of
    the public action enum. Supplying a seed makes action sequences reproducible;
    calling :meth:`reset` without a new seed restarts the original sequence.
    """

    def __init__(self, seed: int | None = None) -> None:
        self._seed = seed
        self._rng = random.Random(seed)
        self._actions = tuple(Action)

    def reset(self, seed: int | None = None) -> None:
        if seed is not None:
            self._seed = seed
        # Restart the deterministic action stream.
        self._rng.seed(self._seed)

    def act(self, observation: Observation) -> Action:
        del observation
        return self._rng.choice(self._actions)
