"""Replay trajectory recording and portable dictionary conversion."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict, is_dataclass
from enum import Enum
from os import PathLike
from pathlib import Path
from typing import Any

from src.simulation.actions import Action
from src.world.entity import Orientation, Position

from .model import JSONValue, ReplayStep, _position_to_dict


def _json_value(value: Any) -> JSONValue:
    """Convert common engine values into portable JSON-compatible values."""
    # Preserve symbolic names before scalar coercion.
    if isinstance(value, Enum):
        return value.name
    if isinstance(value, Position):
        return _position_to_dict(value)
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if is_dataclass(value) and not isinstance(value, type):
        return _json_value(asdict(value))
    if isinstance(value, Mapping):
        return {str(key): _json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_value(item) for item in value]
    raise TypeError(f"{type(value).__name__} is not JSON serializable")


class ReplayRecorder:
    """Record, save and load a TinyWorld trajectory.

    ``record`` is convenient directly after ``env.step(action)``. The explicit
    ``record_step`` form is useful to frontends and tests that already own the
    individual state values.
    """

    FORMAT_VERSION = 1

    def __init__(
        self,
        seed: int | None = None,
        config: Mapping[str, Any] | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> None:
        self.seed = seed
        self.config: dict[str, JSONValue] = (
            {} if config is None else dict(_json_value(config))  # type: ignore[arg-type]
        )
        self.metadata: dict[str, JSONValue] = (
            {} if metadata is None else dict(_json_value(metadata))  # type: ignore[arg-type]
        )
        self.steps: list[ReplayStep] = []

    def __len__(self) -> int:
        return len(self.steps)

    def record(self, env: object, action: Action | int, reward: float) -> ReplayStep:
        """Record the current state of ``env`` after an action was applied."""
        agent = getattr(env, "agent")
        world = getattr(env, "world")
        return self.record_step(
            time=getattr(env, "elapsed_steps"),
            agent_position=agent.position,
            predator_position=world.predator.position,
            orientation=agent.orientation,
            action=action,
            reward=reward,
            energy=agent.energy,
            food_collected=agent.food_eaten,
        )

    def record_step(
        self,
        *,
        time: int,
        agent_position: Position,
        predator_position: Position,
        orientation: Orientation | int,
        action: Action | int,
        reward: float,
        energy: float,
        food_collected: int,
    ) -> ReplayStep:
        step = ReplayStep(
            time=int(time),
            agent_position=agent_position,
            predator_position=predator_position,
            orientation=Orientation(orientation),
            action=Action(action),
            reward=float(reward),
            energy=float(energy),
            food_collected=int(food_collected),
        )
        self.steps.append(step)
        return step

    def to_dict(self) -> dict[str, JSONValue]:
        # Version the portable replay schema.
        return {
            "version": self.FORMAT_VERSION,
            "seed": self.seed,
            "config": self.config,
            "metadata": self.metadata,
            "steps": [step.to_dict() for step in self.steps],
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "ReplayRecorder":
        version = int(data.get("version", 1))
        if version != cls.FORMAT_VERSION:
            raise ValueError(f"unsupported replay format version {version}")
        recorder = cls(
            seed=data.get("seed"),
            config=data.get("config", {}),
            metadata=data.get("metadata", {}),
        )
        recorder.steps.extend(ReplayStep.from_dict(item) for item in data.get("steps", []))
        return recorder

    def save(self, path: str | PathLike[str]) -> Path:
        """Save indented UTF-8 JSON and return its path."""
        from .storage import save_replay

        return save_replay(self, path)

    @classmethod
    def load(cls, path: str | PathLike[str]) -> "ReplayRecorder":
        from .storage import load_replay

        return load_replay(path)
