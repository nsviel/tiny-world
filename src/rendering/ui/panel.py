"""Side panel and minimap rendering."""

from typing import Any

import pygame

from src.app.state import RenderState
from src.world.entities import Tile

from ..engine.config import RenderingConfig


class Panel:
    """Draw metrics, energy, controls, and the minimap."""

    def __init__(
        self,
        screen: pygame.Surface,
        config: RenderingConfig,
        font: pygame.font.Font,
        small_font: pygame.font.Font,
    ) -> None:
        self.screen = screen
        self.config = config
        self.font = font
        self.small_font = small_font
        self.seed_rect = pygame.Rect(0, 0, 0, 0)
        self.auto_loop_rect = pygame.Rect(0, 0, 0, 0)

    def contains_seed(self, position: tuple[int, int]) -> bool:
        return self.seed_rect.collidepoint(position)

    def contains_auto_loop(self, position: tuple[int, int]) -> bool:
        return self.auto_loop_rect.collidepoint(position)

    def draw(self, env: Any, state: RenderState) -> None:
        width, height = self.screen.get_size()
        panel_width = self.config.panel_width
        left = width - panel_width
        pygame.draw.rect(self.screen, (24, 37, 39), (left, 0, panel_width, height))
        pygame.draw.line(self.screen, (56, 79, 76), (left, 0), (left, height), 2)
        self.screen.blit(
            self.font.render("TINY WORLD  AI", True, (237, 230, 196)),
            (left + 24, 24),
        )
        labels = [
            ("Agent", state.agent_name),
            ("Énergie", f"{env.agent.energy:.1f}"),
            ("Nourriture", str(env.agent.food_eaten)),
            ("Survie", str(env.elapsed_steps)),
            ("Récompense", f"{state.total_reward:.2f}"),
            ("Action", state.last_action.name if state.last_action else "—"),
        ]
        y = 72
        for label, value in labels:
            self.screen.blit(
                self.small_font.render(label.upper(), True, (132, 157, 148)),
                (left + 24, y),
            )
            self.screen.blit(
                self.font.render(value, True, (235, 239, 218)),
                (left + self.config.panel_value_offset, y - 3),
            )
            y += 34

        self.screen.blit(
            self.small_font.render("SEED", True, (132, 157, 148)),
            (left + 24, y),
        )
        value_x = left + self.config.panel_value_offset
        self.seed_rect = pygame.Rect(
            value_x - 4,
            y - 5,
            panel_width - self.config.panel_value_offset - 20,
            30,
        )
        border_color = (106, 190, 151) if state.seed_input_active else (56, 79, 76)
        pygame.draw.rect(self.screen, (17, 28, 29), self.seed_rect, border_radius=4)
        pygame.draw.rect(self.screen, border_color, self.seed_rect, 2, border_radius=4)
        seed_text = state.seed_input if state.seed_input_active else str(state.seed)
        if state.seed_input_active:
            seed_text += "|"
        self.screen.blit(
            self.font.render(seed_text, True, (235, 239, 218)),
            (self.seed_rect.x + 7, self.seed_rect.y + 2),
        )
        y += 34

        bar = pygame.Rect(left + 24, y + 4, panel_width - 48, 18)
        pygame.draw.rect(self.screen, (54, 65, 62), bar, border_radius=8)
        fill = bar.copy()
        fill.width = round(bar.width * max(0, env.agent.energy / env.world_config.max_energy))
        color = (72, 190, 112) if env.agent.energy > 30 else (218, 79, 67)
        pygame.draw.rect(self.screen, color, fill, border_radius=8)

        switch_y = y + 34
        self.screen.blit(
            self.small_font.render("AUTO LOOP", True, (132, 157, 148)),
            (left + 24, switch_y + 3),
        )
        self.auto_loop_rect = pygame.Rect(left + panel_width - 92, switch_y, 68, 24)
        switch_color = (72, 190, 112) if state.auto_loop else (78, 91, 88)
        pygame.draw.rect(self.screen, switch_color, self.auto_loop_rect, border_radius=12)
        knob_x = self.auto_loop_rect.right - 12 if state.auto_loop else self.auto_loop_rect.left + 12
        pygame.draw.circle(self.screen, (238, 239, 222), (knob_x, self.auto_loop_rect.centery), 9)

        minimap_size = panel_width - 48
        self._draw_minimap(
            env,
            pygame.Rect(left + 24, y + 72, minimap_size, minimap_size),
        )
        hints = "Espace pause · R reset · O vision\nMolette zoom · clic droit/glisser\nFlèches caméra · C recentrer"
        for index, line in enumerate(hints.splitlines()):
            self.screen.blit(
                self.small_font.render(line, True, (143, 158, 151)),
                (left + 24, height - 78 + index * 20),
            )

    def _draw_minimap(self, env: Any, rect: pygame.Rect) -> None:
        pygame.draw.rect(self.screen, (17, 28, 29), rect)
        scale_x = rect.width / env.world_config.width
        scale_y = rect.height / env.world_config.height
        colors = {
            Tile.GROUND: (70, 116, 70),
            Tile.WATER: (48, 112, 148),
            Tile.TREE: (29, 74, 42),
            Tile.FOOD: (178, 63, 75),
        }
        for row in range(env.world_config.height):
            for col in range(env.world_config.width):
                tile = Tile(int(env.world.tiles[row, col]))
                pygame.draw.rect(
                    self.screen,
                    colors[tile],
                    (
                        rect.x + col * scale_x,
                        rect.y + row * scale_y,
                        max(1, scale_x + 1),
                        max(1, scale_y + 1),
                    ),
                )

        agent = env.agent.position
        predator = env.world.predator.position
        pygame.draw.circle(
            self.screen,
            (255, 231, 104),
            (
                round(rect.x + (agent.col + 0.5) * scale_x),
                round(rect.y + (agent.row + 0.5) * scale_y),
            ),
            3,
        )
        pygame.draw.circle(
            self.screen,
            (238, 69, 66),
            (
                round(rect.x + (predator.col + 0.5) * scale_x),
                round(rect.y + (predator.row + 0.5) * scale_y),
            ),
            3,
        )
