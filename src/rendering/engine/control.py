"""Keyboard and mouse controls for the interactive renderer."""

from dataclasses import dataclass
from typing import Any

import pygame


@dataclass(frozen=True, slots=True)
class ControlCommands:
    """One-frame commands consumed by the application loop."""

    restart: bool = False
    toggle_auto_loop: bool = False
    selected_agent: str | None = None
    new_seed: int | None = None


@dataclass(frozen=True, slots=True)
class ReplayCommands:
    """One-frame commands used by the replay viewer."""

    restart: bool = False


class ReplayControls:
    """Own input handling for the replay viewer."""

    def __init__(self) -> None:
        self.running = True
        self.paused = False

    def update(self, renderer: Any, env: Any) -> ReplayCommands:
        restart = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.paused = not self.paused
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                restart = True
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_c:
                renderer.center_on_agent(env)
            elif event.type == pygame.MOUSEWHEEL:
                renderer.zoom(event.y, pygame.mouse.get_pos())
        return ReplayCommands(restart=restart)


class Controls:
    """Own the interactive input state and translate Pygame events into commands."""

    def __init__(self, speed: float = 8.0) -> None:
        self.running = True
        self.paused = False
        self.show_observation = False
        self.speed = speed
        self._dragging = False

    def update(self, renderer: Any, env: Any, state: Any, dt: float) -> ControlCommands:
        restart = False
        toggle_auto_loop = False
        selected_agent: str | None = None
        new_seed: int | None = None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEWHEEL:
                renderer.zoom(event.y, pygame.mouse.get_pos())
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if renderer.panel.contains_seed(event.pos):
                    state.seed_input_active = True
                    state.seed_input = "" if state.seed is None else str(state.seed)
                else:
                    state.seed_input_active = False
                    toggle_auto_loop = renderer.panel.contains_auto_loop(event.pos)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                self._dragging = True
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 3:
                self._dragging = False
            elif event.type == pygame.MOUSEMOTION and self._dragging:
                renderer.camera.pan(-event.rel[0], -event.rel[1])
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
                elif event.key == pygame.K_c:
                    renderer.center_on_agent(env)
                elif event.key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
                    self.speed = min(60.0, self.speed * 1.5)
                elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    self.speed = max(0.5, self.speed / 1.5)
                elif event.key == pygame.K_1:
                    selected_agent = "random"
                elif event.key == pygame.K_2:
                    selected_agent = "rule"

        self._move_camera(renderer, dt)
        return ControlCommands(
            restart=restart,
            toggle_auto_loop=toggle_auto_loop,
            selected_agent=selected_agent,
            new_seed=new_seed,
        )

    @staticmethod
    def _move_camera(renderer: Any, dt: float) -> None:
        keys = pygame.key.get_pressed()
        distance = renderer.config.camera_pan_speed * dt
        if keys[pygame.K_LEFT]:
            renderer.camera.pan(-distance, 0)
        if keys[pygame.K_RIGHT]:
            renderer.camera.pan(distance, 0)
        if keys[pygame.K_UP]:
            renderer.camera.pan(0, -distance)
        if keys[pygame.K_DOWN]:
            renderer.camera.pan(0, distance)
