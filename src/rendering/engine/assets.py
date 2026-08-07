"""Optional image loading and scaling for the Pygame renderer."""

from pathlib import Path

import pygame


DEFAULT_ASSETS_ROOT = Path(__file__).resolve().parents[3] / "assets"


class AssetStore:
    """Load optional images once and cache their scaled variants."""

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or DEFAULT_ASSETS_ROOT
        self._images = {
            "tree": self._load_optional("trees/tree.png"),
            "food": self._load_optional("food/berries.png"),
        }
        self._scaled: dict[tuple[str, tuple[int, int]], pygame.Surface] = {}

    def get(self, name: str, size: tuple[int, int]) -> pygame.Surface | None:
        """Return a cached image scaled to the requested size."""
        source = self._images.get(name)
        if source is None:
            return None
        key = (name, size)
        if key not in self._scaled:
            self._scaled[key] = pygame.transform.smoothscale(source, size)
        return self._scaled[key]

    def _load_optional(self, relative_path: str) -> pygame.Surface | None:
        path = self.root / relative_path
        if not path.is_file():
            return None
        try:
            # Preserve PNG transparency.
            return pygame.image.load(path).convert_alpha()
        except pygame.error as error:
            raise RuntimeError(f"failed to load asset: {path}") from error
