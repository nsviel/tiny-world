"""Camera and replay input controls."""

from dataclasses import dataclass
from typing import Any

import pygame


class CameraControl:
    """Handle camera-only mouse and keyboard input."""

    def __init__(self) -> None:
        self._dragging = False

    def handle_event(self, event: pygame.event.Event, renderer: Any, env: Any) -> bool:
        if event.type == pygame.MOUSEWHEEL:
            renderer.camera.change_zoom(event.y, pygame.mouse.get_pos())
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            self._dragging = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 3:
            self._dragging = False
        elif event.type == pygame.MOUSEMOTION and self._dragging:
            renderer.camera.pan(-event.rel[0], -event.rel[1])
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_c:
            renderer.camera.center_on_agent(env)
        else:
            return False
        return True

    @staticmethod
    def update(renderer: Any, dt: float) -> None:
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


@dataclass(frozen=True, slots=True)
class ReplayCommands:
    restart: bool = False


class ReplayControls:
    """Handle replay playback and camera controls."""

    def __init__(self) -> None:
        self.running = True
        self.paused = False
        self.camera = CameraControl()

    def update(self, renderer: Any, env: Any, dt: float = 0.0) -> ReplayCommands:
        restart = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.paused = not self.paused
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                restart = True
            else:
                self.camera.handle_event(event, renderer, env)
        self.camera.update(renderer, dt)
        return ReplayCommands(restart=restart)
