"""JSON replay recording for TinyWorld, with no rendering dependencies."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict, dataclass, is_dataclass
from enum import Enum
import json
from os import PathLike
from pathlib import Path
import time
from typing import TYPE_CHECKING, Any

from src.app.config import WorldConfig
from src.simulation.actions import Action
from src.world.entities import Orientation, Position

if TYPE_CHECKING:
    from .state import ApplicationState

JSONValue = None | bool | int | float | str | list["JSONValue"] | dict[str, "JSONValue"]


def _position_to_dict(position: Position) -> dict[str, JSONValue]:
    return {"row": int(position.row), "col": int(position.col)}


def _position_from_dict(value: Mapping[str, Any]) -> Position:
    return Position(row=int(value["row"]), col=int(value["col"]))


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


@dataclass(frozen=True, slots=True)
class ReplayStep:
    """Complete observable game state after one action."""

    time: int
    agent_position: Position
    predator_position: Position
    orientation: Orientation
    action: Action
    reward: float
    energy: float
    food_collected: int

    def to_dict(self) -> dict[str, JSONValue]:
        return {
            "time": self.time,
            "agent_position": _position_to_dict(self.agent_position),
            "predator_position": _position_to_dict(self.predator_position),
            "orientation": self.orientation.name,
            "action": self.action.name,
            "reward": self.reward,
            "energy": self.energy,
            "food_collected": self.food_collected,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "ReplayStep":
        return cls(
            time=int(data["time"]),
            agent_position=_position_from_dict(data["agent_position"]),
            predator_position=_position_from_dict(data["predator_position"]),
            orientation=Orientation[data["orientation"]],
            action=Action[data["action"]],
            reward=float(data["reward"]),
            energy=float(data["energy"]),
            food_collected=int(data["food_collected"]),
        )


class ReplayRecorder:
    """Record, save and load a TinyWorld trajectory.

    ``record`` is convenient directly after ``env.step(action)``.  The explicit
    ``record_step`` form is useful to frontends and tests that already own the
    individual state values.
    """

    FORMAT_VERSION = 1

    def __init__(
        self,
        seed: int | None = None,
        config: WorldConfig | Mapping[str, Any] | None = None,
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
        destination = Path(path)
        destination.write_text(
            json.dumps(self.to_dict(), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        return destination

    @classmethod
    def load(cls, path: str | PathLike[str]) -> "ReplayRecorder":
        source = Path(path)
        data = json.loads(source.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("replay JSON root must be an object")
        return cls.from_dict(data)


def main(argv: list[str] | None = None) -> int:
    """Play a recorded trajectory with the standard Pygame renderer."""
    import argparse
    import time

    parser = argparse.ArgumentParser(description="Lire un replay TinyWorld AI")
    parser.add_argument("path", type=Path)
    parser.add_argument("--fps", type=float, default=8.0)
    args = parser.parse_args(argv)
    if args.fps <= 0:
        parser.error("--fps doit être positif")

    replay = ReplayRecorder.load(args.path)
    if not replay.steps:
        parser.error("le replay ne contient aucune étape")

    # Keep headless replay recording free of Pygame.
    import pygame
    from src.world.env import TinyWorldEnv

    from src.engine.control import ReplayControls
    from src.engine.renderer import Renderer

    from .state import RenderState

    config_fields = WorldConfig.__dataclass_fields__
    config_values: dict[str, Any] = {
        key: value for key, value in replay.config.items() if key in config_fields
    }
    config = WorldConfig(**config_values)
    env = TinyWorldEnv(config, replay.seed)
    renderer = Renderer(f"TinyWorld Replay — {args.path.name}")
    renderer.center_on_agent(env)
    clock = pygame.time.Clock()
    index = 0
    controls = ReplayControls()
    render_state = RenderState(
        agent_name=str(replay.metadata.get("agent", "replay")),
        seed=replay.seed,
    )
    accumulator = 0.0
    total_reward = 0.0
    while controls.running:
        dt = min(clock.tick(60) / 1000.0, .1)
        commands = controls.update(renderer, env)
        if commands.restart:
            index = 0
            total_reward = 0.0
        if not controls.paused:
            # Decouple replay cadence from render frames.
            accumulator += dt * args.fps
            if accumulator >= 1.0:
                accumulator -= 1.0
                step = replay.steps[index]
                env.elapsed_steps = step.time
                env.agent.position = step.agent_position
                env.agent.orientation = step.orientation
                env.agent.energy = step.energy
                env.agent.food_eaten = step.food_collected
                env.world.predator.position = step.predator_position
                total_reward += step.reward
                index = (index + 1) % len(replay.steps)
                if index == 0:
                    time.sleep(.25); total_reward = 0.0
        current = replay.steps[index - 1]
        render_state.total_reward = total_reward
        render_state.last_action = current.action
        render_state.paused = controls.paused
        render_state.frame_dt = dt
        renderer.draw(env, render_state)
    renderer.close()
    return 0


def save_application_replay(
    state: "ApplicationState",
    path: str | PathLike[str],
) -> Path:
    """Add save metadata and persist the current application replay."""
    state.recorder.metadata["saved_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    destination = state.recorder.save(path)
    print(f"Replay saved to: {destination}")
    return destination


__all__ = ["ReplayRecorder", "ReplayStep", "save_application_replay"]


if __name__ == "__main__":
    raise SystemExit(main())
