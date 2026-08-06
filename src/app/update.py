"""Per-frame application update orchestration."""

from src.rendering.control import Controls
from src.rendering.renderer import Renderer
from src.world.env import TinyWorldEnv

from .restart import restart_episode
from .state import ApplicationState


def update_application(
    state: ApplicationState,
    env: TinyWorldEnv,
    renderer: Renderer,
    controls: Controls,
    dt: float,
) -> None:
    """Process controls and advance the interactive simulation when needed."""
    commands = controls.update(renderer, env, dt)

    if commands.selected_agent is not None:
        state.agent_name = commands.selected_agent

    if commands.selected_agent is not None or commands.restart:
        restart_episode(state, env, renderer)

    if not controls.paused and not state.game_over:
        # Convert variable frame time into fixed simulation steps.
        state.accumulator += dt * controls.speed
        while state.accumulator >= 1.0 and not state.game_over:
            state.accumulator -= 1.0
            state.last_action = state.policy.act(state.observation)
            state.observation, reward, terminated, truncated, _ = env.step(
                state.last_action
            )
            state.recorder.record(env, state.last_action, reward)
            state.total_reward += reward
            state.game_over = terminated or truncated

    state.paused = controls.paused
    state.show_observation = controls.show_observation
    state.frame_dt = dt
