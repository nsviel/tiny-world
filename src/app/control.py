"""Interactive application input controls."""

from dataclasses import dataclass
from typing import Any

import pygame

from src.rendering.engine.control import CameraControl


@dataclass(frozen=True, slots=True)
class ControlCommands:
    restart: bool = False
    toggle_auto_loop: bool = False
    selected_agent: str | None = None
    new_seed: int | None = None


class Controls:
    """Translate input events into application commands."""

    def __init__(self, speed: float = 8.0) -> None:
        self.running = True
        self.paused = False
        self.show_observation = False
        self.speed = speed
        self.camera = CameraControl()

    def update(
        self,
        renderer: Any,
        env: Any,
        state: Any,
        dt: float,
    ) -> ControlCommands:
        restart = False
        toggle_auto_loop = False
        selected_agent: str | None = None
        new_seed: int | None = None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif self.camera.handle_event(event, renderer, env):
                continue
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if renderer.panel.contains_seed(event.pos):
                    state.seed_input_active = True
                    state.seed_input = "" if state.seed is None else str(state.seed)
                else:
                    state.seed_input_active = False
                    toggle_auto_loop = renderer.panel.contains_auto_loop(event.pos)
            elif event.type == pygame.KEYDOWN:
                if state.seed_input_active:
                    if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        if state.seed_input:
                            new_seed = int(state.seed_input)
                        state.seed_input_active = False
                    elif event.key == pygame.K_ESCAPE:
                        state.seed_input_active = False
                    elif event.key == pygame.K_BACKSPACE:
                        state.seed_input = state.seed_input[:-1]
                    elif event.unicode.isdigit() and len(state.seed_input) < 18:
                        state.seed_input += event.unicode
                    continue
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif event.key == pygame.K_r:
                    restart = True
                elif event.key == pygame.K_o:
                    self.show_observation = not self.show_observation
                elif event.key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
                    self.speed = min(60.0, self.speed * 1.5)
                elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    self.speed = max(0.5, self.speed / 1.5)
                elif event.key == pygame.K_1:
                    selected_agent = "random"
                elif event.key == pygame.K_2:
                    selected_agent = "rule"

        self.camera.update(renderer, dt)
        return ControlCommands(
            restart=restart,
            toggle_auto_loop=toggle_auto_loop,
            selected_agent=selected_agent,
            new_seed=new_seed,
        )
