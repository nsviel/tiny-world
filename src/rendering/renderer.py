"""Pygame renderer; importing the headless engine never imports this module."""

from typing import Any

from src.app.state import RenderState

from .effect import ParticleSystem
from .world import WorldRenderer

from .engine.assets import AssetStore
from .engine.camera import Camera
from .engine.config import RenderingConfig
from .engine.display import Display
from .ui import Overlay, Panel



class Renderer:
    """Draw an environment state without owning simulation logic."""

    def __init__(self, title: str = "TinyWorld AI", config: RenderingConfig | None = None) -> None:
        self.config = config or RenderingConfig()
        self.display = Display(self.config, title)
        self.screen = self.display.screen
        self.assets = AssetStore(self.config.assets_root)
        self.panel = Panel(
            self.screen,
            self.config,
            self.display.font,
            self.display.small_font,
        )
        self.overlay = Overlay(
            self.screen,
            self.display.font,
            self.display.title_font,
        )
        self.camera = Camera(self.screen, self.config)
        self.effects = ParticleSystem(self.screen, self.camera, self.config)
        self.world_renderer = WorldRenderer(
            self.screen,
            self.camera,
            self.config,
            self.assets,
        )



    def reset_effects(self) -> None:
        """Clear transient visual state for a new episode."""
        self.effects.reset()



    def draw(self, env: Any, state: RenderState) -> None:
        if state.auto_loop_timer > 0.0:
            self.overlay.draw_black()
            self.display.present()
            return

        self.effects.update(env, state.frame_dt)
        self.screen.fill((17, 28, 29))
        self.world_renderer.draw(env, self.camera.viewport)
        self.effects.draw()
        if state.show_observation and state.observation is not None:
            self.world_renderer.draw_observation(env, state.observation)
        self.panel.draw(env, state)
        if state.paused or state.game_over:
            self.overlay.draw(
                "ÉPISODE TERMINÉ" if state.game_over else "PAUSE",
                "R : recommencer" if state.game_over else "Espace : reprendre",
                self.camera.viewport,
            )
        self.display.present()

    def close(self) -> None:
        self.display.close()
