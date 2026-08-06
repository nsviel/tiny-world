"""State containers used by the application and renderer."""

from dataclasses import dataclass

from src.agents import BaseAgent
from src.simulation.actions import Action
from src.simulation.observations import Observation

from .replay import ReplayRecorder


@dataclass(slots=True, kw_only=True)
class RenderState:
    agent_name: str
    seed: int | None
    observation: Observation | None = None
    total_reward: float = 0.0
    last_action: Action | None = None
    paused: bool = False
    game_over: bool = False
    show_observation: bool = False
    frame_dt: float = 0.0


@dataclass(slots=True, kw_only=True)
class ApplicationState(RenderState):
    observation: Observation
    policy: BaseAgent
    recorder: ReplayRecorder
    accumulator: float = 0.0
