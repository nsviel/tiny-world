"""Per-frame application update orchestration."""

from src.rendering.engine.control import Controls
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
    commands = controls.update(renderer, env, state, dt)

    if commands.selected_agent is not None:
        state.agent_name = commands.selected_agent
    if commands.new_seed is not None:
        state.seed = commands.new_seed
    if commands.toggle_auto_loop:
        state.auto_loop = not state.auto_loop
        if not state.auto_loop:
            state.auto_loop_timer = 0.0

    if (
        commands.selected_agent is not None
        or commands.new_seed is not None
        or commands.restart
    ):
        restart_episode(state, env, renderer)

    if state.auto_loop_timer > 0.0:
        # Keep the transition responsive without advancing the world.
        state.auto_loop_timer = max(0.0, state.auto_loop_timer - dt)
        if state.auto_loop_timer == 0.0:
            restart_episode(state, env, renderer)
        state.paused = controls.paused
        state.show_observation = controls.show_observation
        state.frame_dt = dt
        return

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

    if state.game_over and state.auto_loop:
        state.auto_loop_timer = state.auto_loop_delay

    state.paused = controls.paused
    state.show_observation = controls.show_observation
    state.frame_dt = dt
