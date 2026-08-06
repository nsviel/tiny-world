"""State containers used by the interactive application."""

from dataclasses import dataclass

from src.agents import BaseAgent
from src.simulation.actions import Action
from src.simulation.observations import Observation

from .replay import ReplayRecorder


@dataclass(slots=True)
class EngineState:
    observation: Observation
    policy: BaseAgent
    recorder: ReplayRecorder
    game_over: bool = False
    accumulator: float = 0.0
    total_reward: float = 0.0
    last_action: Action | None = None
