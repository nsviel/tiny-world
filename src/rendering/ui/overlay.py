"""Pause and episode-end overlay rendering."""

import pygame


class Overlay:
    """Draw a dark veil with centered status text."""

    def __init__(
        self,
        screen: pygame.Surface,
        font: pygame.font.Font,
        title_font: pygame.font.Font,
    ) -> None:
        self.screen = screen
        self.font = font
        self.title_font = title_font

    def draw(
        self,
        title: str,
        subtitle: str,
        viewport: tuple[int, int],
    ) -> None:
        width, height = viewport
        veil = pygame.Surface((width, height), pygame.SRCALPHA)
        veil.fill((7, 13, 14, 165))
        self.screen.blit(veil, (0, 0))

        title_image = self.title_font.render(title, True, (250, 235, 179))
        subtitle_image = self.font.render(subtitle, True, (210, 220, 207))
        self.screen.blit(
            title_image,
            title_image.get_rect(center=(width // 2, height // 2 - 18)),
        )
        self.screen.blit(
            subtitle_image,
            subtitle_image.get_rect(center=(width // 2, height // 2 + 30)),
        )
