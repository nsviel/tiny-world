"""High-level interactive application object."""

from os import PathLike
from pathlib import Path

from src.rendering.engine.config import RenderingConfig
from src.rendering.engine.control import Controls
from src.rendering.renderer import Renderer
from src.world.env import TinyWorldEnv

from .replay import save_application_replay
from .restart import create_application_state
from .state import ApplicationState
from .update import update_application


class App:
    """Own the interactive session and coordinate one frame at a time."""

    def __init__(
        self,
        agent_name: str = "rule",
        seed: int = 42,
        rendering_config: RenderingConfig | None = None,
    ) -> None:
        self.env = TinyWorldEnv(seed=seed)
        self.renderer = Renderer(config=rendering_config)
        self.controls = Controls()
        self.state: ApplicationState = create_application_state(
            self.env,
            self.renderer,
            agent_name,
            seed,
        )

    def tick(self) -> float:
        return self.renderer.display.tick()

    @property
    def running(self) -> bool:
        return self.controls.running

    def update(self, dt: float) -> None:
        """Process input, advance the simulation, and draw one frame."""
        # Keep orchestration outside rendering and simulation.
        update_application(
            self.state,
            self.env,
            self.renderer,
            self.controls,
            dt,
        )
        self.renderer.draw(self.env, self.state)

    def replay(self, path: str | PathLike[str]) -> Path:
        """Save the replay recorded during the current session."""
        return save_application_replay(self.state, path)

    def close(self) -> None:
        self.renderer.close()
