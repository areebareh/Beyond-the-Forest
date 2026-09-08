"""
ui.py

Small reusable UI helpers: buttons, text input box, floating combat text,
and a fade transition -- kept dependency-free (just pygame) so the game
stays easy to hack on.
"""

import pygame

FONT_CACHE = {}


def get_font(size, bold=False):
    key = (size, bold)
    if key not in FONT_CACHE:
        f = pygame.font.SysFont("Consolas,Menlo,monospace", size, bold=bold)
        FONT_CACHE[key] = f
    return FONT_CACHE[key]


class Button:
    def __init__(self, rect, label, callback, enabled=True, color=(58, 92, 58),
                 hover_color=(80, 124, 80), text_color=(240, 240, 230)):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.callback = callback
        self.enabled = enabled
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self._hover = False

    def handle_event(self, event):
        if not self.enabled:
            return
        if event.type == pygame.MOUSEMOTION:
            self._hover = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.callback()

    def draw(self, surf):
        color = self.color if self.enabled else (50, 50, 50)
        if self._hover and self.enabled:
            color = self.hover_color
        pygame.draw.rect(surf, color, self.rect, border_radius=6)
        pygame.draw.rect(surf, (15, 15, 15), self.rect, 2, border_radius=6)
        font = get_font(20, bold=True)
        text_color = self.text_color if self.enabled else (120, 120, 120)
        text = font.render(self.label, True, text_color)
        surf.blit(text, text.get_rect(center=self.rect.center))


class TextInputBox:
    def __init__(self, rect, placeholder="", max_len=16):
        self.rect = pygame.Rect(rect)
        self.text = ""
        self.placeholder = placeholder
        self.max_len = max_len
        self.active = True
        self._cursor_timer = 0
        self._cursor_visible = True

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key not in (pygame.K_RETURN, pygame.K_KP_ENTER):
                if event.unicode.isprintable() and len(self.text) < self.max_len:
                    self.text += event.unicode

    def update(self, dt):
        self._cursor_timer += dt
        if self._cursor_timer > 500:
            self._cursor_timer = 0
            self._cursor_visible = not self._cursor_visible

    def draw(self, surf):
        pygame.draw.rect(surf, (20, 20, 20), self.rect, border_radius=4)
        pygame.draw.rect(surf, (200, 200, 190), self.rect, 2, border_radius=4)
        font = get_font(24)
        shown = self.text if self.text else self.placeholder
        color = (240, 240, 230) if self.text else (120, 120, 110)
        text_surf = font.render(shown, True, color)
        surf.blit(text_surf, (self.rect.x + 10, self.rect.centery - text_surf.get_height() // 2))
        if self.text and self._cursor_visible:
            cursor_x = self.rect.x + 10 + text_surf.get_width() + 2
            pygame.draw.line(surf, (240, 240, 230),
                              (cursor_x, self.rect.y + 8), (cursor_x, self.rect.bottom - 8), 2)


class FloatingText:
    """A small piece of text that drifts upward and fades out (damage numbers etc.)."""

    def __init__(self, text, pos, color=(255, 90, 90), lifetime=900):
        self.text = text
        self.x, self.y = pos
        self.color = color
        self.lifetime = lifetime
        self.age = 0

    def update(self, dt):
        self.age += dt
        self.y -= dt * 0.03
        return self.age < self.lifetime

    def draw(self, surf):
        alpha = max(0, 255 - int(255 * (self.age / self.lifetime)))
        font = get_font(22, bold=True)
        text_surf = font.render(self.text, True, self.color)
        text_surf.set_alpha(alpha)
        surf.blit(text_surf, (self.x, self.y))


class Fader:
    """Simple fade-to-black-and-back transition, used between scenes."""

    def __init__(self, duration=350):
        self.duration = duration
        self.timer = 0
        self.active = False
        self.on_mid = None
        self._fired_mid = False

    def start(self, on_mid=None):
        self.active = True
        self.timer = 0
        self.on_mid = on_mid
        self._fired_mid = False

    def update(self, dt):
        if not self.active:
            return
        self.timer += dt
        if not self._fired_mid and self.timer >= self.duration and self.on_mid:
            self.on_mid()
            self._fired_mid = True
        if self.timer >= self.duration * 2:
            self.active = False

    def draw(self, surf):
        if not self.active:
            return
        half = self.duration
        if self.timer < half:
            alpha = int(255 * (self.timer / half))
        else:
            alpha = int(255 * (1 - (self.timer - half) / half))
        alpha = max(0, min(255, alpha))
        overlay = pygame.Surface(surf.get_size())
        overlay.fill((0, 0, 0))
        overlay.set_alpha(alpha)
        surf.blit(overlay, (0, 0))


def draw_text(surf, text, pos, size=20, color=(235, 235, 225), bold=False, center=False, shadow=True):
    font = get_font(size, bold=bold)
    if shadow:
        shadow_surf = font.render(text, True, (0, 0, 0))
        offset = (pos[0] + 2, pos[1] + 2)
        if center:
            surf.blit(shadow_surf, shadow_surf.get_rect(center=offset))
        else:
            surf.blit(shadow_surf, offset)
    text_surf = font.render(text, True, color)
    if center:
        surf.blit(text_surf, text_surf.get_rect(center=pos))
    else:
        surf.blit(text_surf, pos)


def draw_health_bar(surf, rect, ratio, label=""):
    ratio = max(0.0, min(1.0, ratio))
    pygame.draw.rect(surf, (20, 20, 20), rect, border_radius=5)
    inner = pygame.Rect(rect.x + 3, rect.y + 3, int((rect.width - 6) * ratio), rect.height - 6)
    color = (90, 200, 90) if ratio > 0.5 else (220, 190, 60) if ratio > 0.25 else (210, 70, 70)
    pygame.draw.rect(surf, color, inner, border_radius=4)
    pygame.draw.rect(surf, (230, 230, 220), rect, 2, border_radius=5)
    if label:
        draw_text(surf, label, (rect.x, rect.y - 20), size=16)
