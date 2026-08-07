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
    seed_input: str = ""
    seed_input_active: bool = False
    observation: Observation | None = None
    total_reward: float = 0.0
    last_action: Action | None = None
    paused: bool = False
    game_over: bool = False
    auto_loop: bool = True
    auto_loop_delay: float = 0.5
    auto_loop_timer: float = 0.0
    show_observation: bool = False
    frame_dt: float = 0.0


@dataclass(slots=True, kw_only=True)
class ApplicationState(RenderState):
    observation: Observation
    policy: BaseAgent
    recorder: ReplayRecorder
    accumulator: float = 0.0
