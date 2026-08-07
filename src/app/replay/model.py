"""Replay step model and dictionary conversion."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from src.simulation.actions import Action
from src.world.entity import Orientation, Position

JSONValue = None | bool | int | float | str | list["JSONValue"] | dict[str, "JSONValue"]


def _position_to_dict(position: Position) -> dict[str, JSONValue]:
    return {"row": int(position.row), "col": int(position.col)}


def _position_from_dict(value: Mapping[str, Any]) -> Position:
    return Position(row=int(value["row"]), col=int(value["col"]))


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
