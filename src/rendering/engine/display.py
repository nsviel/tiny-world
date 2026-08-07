"""Pygame display lifecycle and frame timing."""

import pygame

from .config import RenderingConfig


class Display:
    """Own the window, fonts, clock, and Pygame lifecycle."""

    def __init__(self, config: RenderingConfig, title: str) -> None:
        pygame.init()
        pygame.display.set_caption(title)
        self.config = config
        self.screen = pygame.display.set_mode(config.window_size, pygame.RESIZABLE)
        self.font = pygame.font.SysFont(config.font_name, config.font_size)
        self.small_font = pygame.font.SysFont(config.font_name, config.small_font_size)
        self.title_font = pygame.font.SysFont(
            config.font_name,
            config.title_font_size,
            bold=True,
        )
        self.clock = pygame.time.Clock()

    def tick(self) -> float:
        """Return capped frame time in seconds."""
        elapsed = self.clock.tick(self.config.target_fps) / 1000.0
        return min(elapsed, self.config.max_frame_time)

    @staticmethod
    def present() -> None:
        pygame.display.flip()

    @staticmethod
    def close() -> None:
        pygame.quit()
