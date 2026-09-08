"""
assets.py

Central place that loads every image the game needs.

HOW TO DROP IN YOUR OWN PIXEL ART
----------------------------------
Save your files with these EXACT names into assets/images/ and they will be
picked up automatically the next time the game runs -- no code changes needed.

    Backgrounds (recommended size: 960x540, but any size is scaled to fit):
        bg_forest_entrance.png
        bg_deep_forest.png
        bg_riverbank.png

    Player (recommended: 64x64, transparent background):
        player.png

    Monsters (recommended: 96x96, transparent background):
        monster_goblin.png
        monster_wolf.png
        monster_giant_spider.png
        monster_bandit.png

    Icons (recommended: 32x32):
        icon_medkit.png
        icon_heart.png

Until a file exists, a generated placeholder pixel-art sprite is used instead
so the game is fully playable right away.
"""

import os
import random
import pygame

IMAGES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "images")

# Deterministic colors so placeholders stay visually consistent across runs.
_PLACEHOLDER_PALETTES = {
    "bg_forest_entrance": [(24, 40, 24), (34, 58, 34), (46, 74, 46)],
    "bg_deep_forest":     [(12, 22, 16), (18, 34, 22), (26, 46, 30)],
    "bg_riverbank":       [(18, 34, 46), (24, 48, 64), (40, 72, 92)],
    "player":             [(64, 130, 220)],
    "monster_goblin":     [(72, 140, 60)],
    "monster_wolf":       [(120, 120, 130)],
    "monster_giant_spider": [(90, 40, 90)],
    "monster_bandit":     [(120, 90, 50)],
    "icon_medkit":        [(220, 60, 60)],
    "icon_heart":         [(220, 40, 60)],
}

_cache = {}


def _placeholder_background(key, size):
    """Generate a simple layered pixel-art-style background as a fallback."""
    w, h = size
    small_w, small_h = 48, 27
    surf = pygame.Surface((small_w, small_h))
    palette = _PLACEHOLDER_PALETTES.get(key, [(40, 40, 40)])
    rng = random.Random(key)  # deterministic per-location noise
    base = palette[0]
    surf.fill(base)
    # Rows of "terrain" bands using the palette
    for row in range(small_h):
        color = palette[min(row // max(1, small_h // len(palette)), len(palette) - 1)]
        pygame.draw.line(surf, color, (0, row), (small_w, row))
    # Sprinkle some noise pixels (trees / pebbles / reeds depending on scene)
    accent = tuple(min(255, c + 40) for c in palette[-1])
    for _ in range(int(small_w * small_h * 0.06)):
        x = rng.randint(0, small_w - 1)
        y = rng.randint(small_h // 3, small_h - 1)
        surf.set_at((x, y), accent)
    scaled = pygame.transform.scale(surf, (w, h))
    return scaled.convert()


def _placeholder_sprite(key, size):
    """Generate a small blocky 'pixel art' creature/icon as a fallback."""
    w, h = size
    grid = 16
    surf = pygame.Surface((grid, grid), pygame.SRCALPHA)
    color = _PLACEHOLDER_PALETTES.get(key, [(200, 200, 200)])[0]
    dark = tuple(max(0, c - 60) for c in color)
    light = tuple(min(255, c + 60) for c in color)
    rng = random.Random(key)

    # Simple humanoid/creature blob silhouette
    body_rect = pygame.Rect(4, 6, 8, 8)
    head_rect = pygame.Rect(6, 2, 4, 4)
    pygame.draw.rect(surf, color, body_rect)
    pygame.draw.rect(surf, color, head_rect)
    pygame.draw.rect(surf, dark, body_rect, 1)
    pygame.draw.rect(surf, dark, head_rect, 1)
    # A couple of random highlight pixels for texture
    for _ in range(4):
        x = rng.randint(body_rect.left, body_rect.right - 1)
        y = rng.randint(body_rect.top, body_rect.bottom - 1)
        surf.set_at((x, y), light)
    # eyes
    surf.set_at((7, 3), (0, 0, 0))
    surf.set_at((8, 3), (0, 0, 0))

    scaled = pygame.transform.scale(surf, (w, h))
    return scaled


def _placeholder_icon(key, size):
    w, h = size
    surf = pygame.Surface((size[0], size[1]), pygame.SRCALPHA)
    color = _PLACEHOLDER_PALETTES.get(key, [(255, 255, 255)])[0]
    if key == "icon_heart":
        r = w // 4
        pygame.draw.circle(surf, color, (w // 2 - r // 2, h // 3), r)
        pygame.draw.circle(surf, color, (w // 2 + r // 2, h // 3), r)
        pygame.draw.polygon(surf, color, [(2, h // 3), (w - 2, h // 3), (w // 2, h - 2)])
    else:  # medkit-style cross in a box
        pygame.draw.rect(surf, color, (2, 2, w - 4, h - 4), border_radius=3)
        pygame.draw.rect(surf, (255, 255, 255), (w // 2 - 2, 5, 4, h - 10))
        pygame.draw.rect(surf, (255, 255, 255), (5, h // 2 - 2, w - 10, 4))
    return surf


def load_image(key, size, kind="sprite"):
    """
    Load assets/images/{key}.png at the given size, or synthesize a
    placeholder pixel-art image of the right kind if the file is missing.
    kind: "background" | "sprite" | "icon"
    """
    cache_key = (key, size, kind)
    if cache_key in _cache:
        return _cache[cache_key]

    path = os.path.join(IMAGES_DIR, f"{key}.png")
    image = None
    if os.path.isfile(path):
        try:
            raw = pygame.image.load(path)
            image = pygame.transform.smoothscale(raw.convert_alpha(), size)
        except Exception:
            image = None

    if image is None:
        if kind == "background":
            image = _placeholder_background(key, size)
        elif kind == "icon":
            image = _placeholder_icon(key, size)
        else:
            image = _placeholder_sprite(key, size)

    _cache[cache_key] = image
    return image


def has_real_asset(key):
    """True if the user has already dropped in their own art for this key."""
    return os.path.isfile(os.path.join(IMAGES_DIR, f"{key}.png"))
