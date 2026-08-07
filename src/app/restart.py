"""Interactive episode setup and restart logic."""

from dataclasses import asdict

from src.agents import BaseAgent, RandomAgent, RuleBasedAgent
from src.rendering.renderer import Renderer
from src.world.env import TinyWorldEnv

from .replay import ReplayRecorder
from .state import ApplicationState


def _config_dict(env: TinyWorldEnv) -> dict[str, object]:
    return {
        "world": asdict(env.world_config),
        "simulation": asdict(env.simulation_config),
    }


def _create_agent(name: str, seed: int | None) -> BaseAgent:
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
        recorder=ReplayRecorder(seed, _config_dict(env), {"agent": agent_name}),
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
    # Reuse the seed for an identical episode.
    observation, _ = env.reset(state.seed)
    policy = _create_agent(state.agent_name, state.seed)
    policy.reset(state.seed)

    state.observation = observation
    state.policy = policy
    state.seed_input = "" if state.seed is None else str(state.seed)
    state.seed_input_active = False
    state.recorder = ReplayRecorder(
        state.seed,
        _config_dict(env),
        {"agent": state.agent_name},
    )
    state.game_over = False
    state.auto_loop_timer = 0.0
    state.accumulator = 0.0
    state.total_reward = 0.0
    state.last_action = None

    renderer.reset_effects()
    renderer.center_on_agent(env)
