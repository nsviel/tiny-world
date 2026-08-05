"""Common interface for agents interacting with TinyWorld."""

from abc import ABC, abstractmethod

from src.game.actions import Action
from src.game.observations import Observation


class BaseAgent(ABC):
    """Abstract policy interface used by TinyWorld examples and experiments."""

    @abstractmethod
    def reset(self, seed: int | None = None) -> None:
        """Reset episode-local state, optionally replacing the random seed."""

    @abstractmethod
    def act(self, observation: Observation) -> Action:
        """Choose one action from the current observation."""
