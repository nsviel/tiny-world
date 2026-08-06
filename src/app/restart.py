"""Interactive episode setup and restart logic."""

from dataclasses import asdict

from src.agents import BaseAgent, RandomAgent, RuleBasedAgent
from src.engine.renderer import Renderer
from src.world.env import TinyWorldEnv

from .replay import ReplayRecorder
from .state import ApplicationState


def _create_agent(name: str, seed: int) -> BaseAgent:
    if name == "rule":
        return RuleBasedAgent(seed)
    if name == "random":
        return RandomAgent(seed)
    raise ValueError(f"unknown agent {name!r}")


def create_application_state(
    env: TinyWorldEnv,
    renderer: Renderer,
    agent_name: str,
    seed: int,
) -> ApplicationState:
    """Create the initial state, then initialize its first episode."""
    observation, _ = env.reset(seed)
    policy = _create_agent(agent_name, seed)
    policy.reset(seed)
    state = ApplicationState(
        agent_name=agent_name,
        seed=seed,
        observation=observation,
        policy=policy,
        recorder=ReplayRecorder(seed, asdict(env.config), {"agent": agent_name}),
    )
    renderer.reset_effects()
    renderer.center_on_agent(env)
    return state


def restart_episode(
    state: ApplicationState,
    env: TinyWorldEnv,
    renderer: Renderer,
) -> None:
    """Reset all episode-specific values in an existing application state."""
    observation, _ = env.reset(state.seed)
    policy = _create_agent(state.agent_name, state.seed)
    policy.reset(state.seed)

    state.observation = observation
    state.policy = policy
    state.recorder = ReplayRecorder(
        state.seed,
        asdict(env.config),
        {"agent": state.agent_name},
    )
    state.game_over = False
    state.accumulator = 0.0
    state.total_reward = 0.0
    state.last_action = None

    renderer.reset_effects()
    renderer.center_on_agent(env)
