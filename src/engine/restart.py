"""Interactive episode restart logic."""

from dataclasses import asdict

from src.agents import BaseAgent, RandomAgent, RuleBasedAgent
from src.world.env import TinyWorldEnv

from .renderer import Renderer
from .replay import ReplayRecorder
from .state import EngineState


def restart_episode(
    env: TinyWorldEnv,
    renderer: Renderer,
    agent_name: str,
    seed: int,
) -> EngineState:
    """Reset all state tied to the current interactive episode."""
    observation, _ = env.reset(seed)
    policy: BaseAgent
    if agent_name == "rule":
        policy = RuleBasedAgent(seed)
    elif agent_name == "random":
        policy = RandomAgent(seed)
    else:
        raise ValueError(f"unknown agent {agent_name!r}")
    policy.reset(seed)

    renderer.reset_effects()
    renderer.center_on_agent(env)
    recorder = ReplayRecorder(seed, asdict(env.config), {"agent": agent_name})
    return EngineState(observation=observation, policy=policy, recorder=recorder)
