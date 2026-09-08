"""
main.py

'Beyond the Forest' -- pygame edition.

This is a visual, animated front end built on top of the ORIGINAL
game_engine.py logic (unchanged, so test_game.py still passes against it).
All the game rules -- movement, combat odds, win/lose conditions -- are
identical to the text version. What's new is a real scene for each
location, an animated player and monsters, a health bar, floating combat
text, and screen transitions.

Run with:
    python main.py

Controls:
    Click the direction buttons (or press Arrow Keys / WASD) to move.
    Click Fight / Run during an encounter (or press F / R).
    Click Use Medkit (or press U) to heal.
    Press Esc to quit.

Drop your own pixel art into assets/images/ -- see assets.py for the
exact filenames expected. The game works with generated placeholder art
until then.
"""

import math
import sys
import pygame

import game_engine as ge
import assets
from ui import Button, TextInputBox, FloatingText, Fader, draw_text, draw_health_bar

# ---------------------------------------------------------------- constants

SCREEN_W, SCREEN_H = 960, 600
FPS = 60

STATE_NAME_ENTRY = "name_entry"
STATE_EXPLORE = "explore"
STATE_ENCOUNTER = "encounter"
STATE_RESULT = "result"      # shows outcome text of fight/run/use before returning
STATE_WIN = "win"
STATE_GAMEOVER = "gameover"

LOCATION_BG_KEY = {
    "Forest Entrance": "bg_forest_entrance",
    "Deep Forest": "bg_deep_forest",
    "Riverbank": "bg_riverbank",
}

MONSTER_KEY = {
    "Goblin": "monster_goblin",
    "Wolf": "monster_wolf",
    "Giant Spider": "monster_giant_spider",
    "Bandit": "monster_bandit",
}

DIRECTIONS = ["north", "south", "east", "west"]


# ---------------------------------------------------------------- game app

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Beyond the Forest")
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        self.clock = pygame.time.Clock()

        self.state = STATE_NAME_ENTRY
        self.fader = Fader(300)
        self.floating_texts = []
        self.log_lines = []

        self.player_bob = 0.0
        self.monster_bob = 0.0
        self.shake = 0.0

        self.current_monster = None
        self.pending_result_text = ""
        self.pending_next_state = STATE_EXPLORE
        self.result_ok_button = None

        ge.reset_game()
        self._build_name_entry_widgets()

    # ---------------------------------------------------------- widgets

    def _build_name_entry_widgets(self):
        self.name_box = TextInputBox((SCREEN_W // 2 - 160, SCREEN_H // 2, 320, 44),
                                      placeholder="Type your name...")
        self.name_error = ""
        self.name_confirm_button = Button(
            (SCREEN_W // 2 - 90, SCREEN_H // 2 + 60, 180, 46),
            "Begin", self._confirm_name)

    def _confirm_name(self):
        name = self.name_box.text.strip()
        if not name:
            self.name_error = "Name cannot be empty."
            return
        ge.set_player_name(name)
        self.log_lines = [f"Welcome, {name}! Find your way to safety."]
        self._enter_explore()

    def _build_explore_widgets(self):
        self.direction_buttons = []
        valid_dirs = ge.locations[ge.current_location]
        btn_w, btn_h = 150, 44
        start_x = SCREEN_W - btn_w - 30
        y = 140
        for d in DIRECTIONS:
            enabled = d in valid_dirs
            btn = Button((start_x, y, btn_w, btn_h), f"Move {d.capitalize()}",
                         (lambda dir=d: self._do_move(dir)), enabled=enabled)
            self.direction_buttons.append(btn)
            y += btn_h + 12

        has_medkit = "Medkit" in ge.inventory
        self.use_item_button = Button((start_x, y + 10, btn_w, btn_h),
                                       "Use Medkit", self._do_use_item,
                                       enabled=has_medkit)

    def _build_encounter_widgets(self):
        btn_w, btn_h = 170, 50
        cx = SCREEN_W // 2
        self.fight_button = Button((cx - btn_w - 15, SCREEN_H - 100, btn_w, btn_h),
                                    "Fight (F)", self._do_fight, color=(120, 50, 50),
                                    hover_color=(160, 70, 70))
        self.run_button = Button((cx + 15, SCREEN_H - 100, btn_w, btn_h),
                                  "Run (R)", self._do_run, color=(50, 80, 120),
                                  hover_color=(70, 105, 160))

    # ---------------------------------------------------------- transitions

    def _enter_explore(self):
        self.state = STATE_EXPLORE
        self._build_explore_widgets()

    def _start_fade(self, on_mid):
        self.fader.start(on_mid=on_mid)

    # ---------------------------------------------------------- actions

    def _do_move(self, direction):
        if self.state != STATE_EXPLORE:
            return

        def after():
            msg = ge.move(direction)
            self.log_lines.append(msg)

            if ge.has_won():
                self.state = STATE_WIN
                return

            monster = ge.encounter_monster()
            if monster:
                self.current_monster = monster
                self.log_lines.append(f"A wild {monster} appears!")
                self._build_encounter_widgets()
                self.state = STATE_ENCOUNTER
            else:
                self._build_explore_widgets()
                self.state = STATE_EXPLORE

        self._start_fade(after)

    def _do_use_item(self):
        msg = ge.use_item()
        self.log_lines.append(msg)
        color = (100, 220, 100) if "restored" in msg else (220, 120, 120)
        self.floating_texts.append(FloatingText(msg.split(".")[0], (SCREEN_W // 2 - 100, SCREEN_H // 2), color))
        self._build_explore_widgets()

    def _do_fight(self):
        monster = self.current_monster
        health_before = ge.player_health
        outcome = ge.fight(monster)
        self.log_lines.append(outcome)
        self.shake = 12
        damage = health_before - ge.player_health
        if damage > 0:
            self.floating_texts.append(
                FloatingText(f"-{damage}", (SCREEN_W // 2 - 20, SCREEN_H // 2 - 40), (230, 70, 70)))
        else:
            self.floating_texts.append(
                FloatingText("Victory!", (SCREEN_W // 2 - 40, SCREEN_H // 2 - 40), (110, 230, 110)))
        self._go_to_result(outcome)

    def _do_run(self):
        monster = self.current_monster
        health_before = ge.player_health
        outcome = ge.run(monster)
        self.log_lines.append(outcome)
        damage = health_before - ge.player_health
        if damage > 0:
            self.shake = 8
            self.floating_texts.append(
                FloatingText(f"-{damage}", (SCREEN_W // 2 - 20, SCREEN_H // 2 - 40), (230, 70, 70)))
        else:
            self.floating_texts.append(
                FloatingText("Escaped!", (SCREEN_W // 2 - 40, SCREEN_H // 2 - 40), (140, 200, 240)))
        self._go_to_result(outcome)

    def _go_to_result(self, outcome_text):
        self.pending_result_text = outcome_text
        if not ge.is_alive():
            self.pending_next_state = STATE_GAMEOVER
        else:
            self.pending_next_state = STATE_EXPLORE
        self.state = STATE_RESULT
        self.result_ok_button = Button((SCREEN_W // 2 - 90, SCREEN_H - 100, 180, 46),
                                        "Continue", self._resolve_result)

    def _resolve_result(self):
        self.current_monster = None
        if self.pending_next_state == STATE_EXPLORE:
            self._build_explore_widgets()
        self.state = self.pending_next_state

    def restart(self):
        ge.reset_game()
        self.state = STATE_NAME_ENTRY
        self.log_lines = []
        self.floating_texts = []
        self._build_name_entry_widgets()

    # ---------------------------------------------------------- update/draw

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit(0)

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            pygame.quit()
            sys.exit(0)

        if self.state == STATE_NAME_ENTRY:
            self.name_box.handle_event(event)
            self.name_confirm_button.handle_event(event)
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self._confirm_name()

        elif self.state == STATE_EXPLORE:
            for btn in self.direction_buttons:
                btn.handle_event(event)
            self.use_item_button.handle_event(event)
            if event.type == pygame.KEYDOWN:
                key_dir = {pygame.K_UP: "north", pygame.K_w: "north",
                           pygame.K_DOWN: "south", pygame.K_s: "south",
                           pygame.K_RIGHT: "east", pygame.K_d: "east",
                           pygame.K_LEFT: "west", pygame.K_a: "west"}.get(event.key)
                if key_dir and key_dir in ge.locations[ge.current_location]:
                    self._do_move(key_dir)
                elif event.key == pygame.K_u and "Medkit" in ge.inventory:
                    self._do_use_item()

        elif self.state == STATE_ENCOUNTER:
            self.fight_button.handle_event(event)
            self.run_button.handle_event(event)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:
                    self._do_fight()
                elif event.key == pygame.K_r:
                    self._do_run()

        elif self.state == STATE_RESULT:
            self.result_ok_button.handle_event(event)
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._resolve_result()

        elif self.state in (STATE_WIN, STATE_GAMEOVER):
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.restart()
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.restart()

    def update(self, dt):
        self.fader.update(dt)
        self.player_bob += dt * 0.004
        self.monster_bob += dt * 0.006
        if self.shake > 0:
            self.shake = max(0.0, self.shake - dt * 0.03)
        self.floating_texts = [t for t in self.floating_texts if t.update(dt)]
        if self.state == STATE_NAME_ENTRY:
            self.name_box.update(dt)

    def _draw_scene_background(self):
        bg_key = LOCATION_BG_KEY.get(ge.current_location, "bg_forest_entrance")
        bg = assets.load_image(bg_key, (SCREEN_W, SCREEN_H), kind="background")
        offset = (math.sin(self.shake) * self.shake) if self.shake else 0
        self.screen.blit(bg, (offset, 0))

    def _draw_hud(self):
        draw_health_bar(self.screen, pygame.Rect(20, 20, 240, 26),
                         ge.player_health / 100.0, label=f"{ge.player_name or 'Hero'}'s Health")
        draw_text(self.screen, f"{max(0, ge.player_health)}/100", (270, 22), size=18)
        draw_text(self.screen, f"Location: {ge.current_location}", (20, 60), size=18)
        inv_text = ", ".join(ge.inventory) if ge.inventory else "Empty"
        draw_text(self.screen, f"Inventory: {inv_text}", (20, 88), size=18)

        # log panel (last 4 lines)
        log_y = SCREEN_H - 110
        panel = pygame.Rect(15, log_y - 10, 560, 100)
        overlay = pygame.Surface(panel.size, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 130))
        self.screen.blit(overlay, panel.topleft)
        for i, line in enumerate(self.log_lines[-4:]):
            draw_text(self.screen, line, (panel.x + 10, panel.y + 8 + i * 22), size=16, shadow=False)

    def _draw_player(self):
        bob = math.sin(self.player_bob) * 6
        size = (96, 96)
        img = assets.load_image("player", size, kind="sprite")
        x = 120
        y = SCREEN_H - 220 + bob
        self.screen.blit(img, (x, y))

    def _draw_name_entry(self):
        self.screen.fill((16, 24, 16))
        bg = assets.load_image("bg_forest_entrance", (SCREEN_W, SCREEN_H), kind="background")
        bg.set_alpha(120)
        self.screen.blit(bg, (0, 0))
        draw_text(self.screen, "Beyond the Forest", (SCREEN_W // 2, SCREEN_H // 2 - 120),
                  size=44, bold=True, center=True)
        draw_text(self.screen, "You wake up alone in a dark forest with no memory of how you got here.",
                  (SCREEN_W // 2, SCREEN_H // 2 - 70), size=18, center=True, color=(210, 210, 200))
        draw_text(self.screen, "Find your way to safety before the monsters find you.",
                  (SCREEN_W // 2, SCREEN_H // 2 - 45), size=18, center=True, color=(210, 210, 200))
        self.name_box.draw(self.screen)
        self.name_confirm_button.draw(self.screen)
        if self.name_error:
            draw_text(self.screen, self.name_error, (SCREEN_W // 2, SCREEN_H // 2 + 130),
                      size=16, center=True, color=(230, 100, 100))

    def _draw_explore(self):
        self._draw_scene_background()
        self._draw_player()
        self._draw_hud()
        for btn in self.direction_buttons:
            btn.draw(self.screen)
        self.use_item_button.draw(self.screen)
        draw_text(self.screen, "Choose where to go:", (SCREEN_W - 200, 110), size=16)

    def _draw_encounter(self):
        self._draw_scene_background()
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 70))
        self.screen.blit(overlay, (0, 0))

        self._draw_player()

        bob = math.sin(self.monster_bob) * 8
        m_key = MONSTER_KEY.get(self.current_monster, "monster_goblin")
        m_img = assets.load_image(m_key, (140, 140), kind="sprite")
        shake_x = math.sin(self.shake) * self.shake if self.shake else 0
        self.screen.blit(m_img, (SCREEN_W - 260 + shake_x, SCREEN_H - 300 + bob))

        draw_text(self.screen, f"A wild {self.current_monster} blocks your path!",
                  (SCREEN_W // 2, 90), size=26, bold=True, center=True)
        self._draw_hud()
        self.fight_button.draw(self.screen)
        self.run_button.draw(self.screen)

    def _draw_result(self):
        self._draw_scene_background()
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        self.screen.blit(overlay, (0, 0))
        panel = pygame.Rect(SCREEN_W // 2 - 300, SCREEN_H // 2 - 90, 600, 160)
        pygame.draw.rect(self.screen, (30, 30, 30), panel, border_radius=10)
        pygame.draw.rect(self.screen, (200, 200, 190), panel, 2, border_radius=10)
        # wrap text simply
        words = self.pending_result_text.split(" ")
        lines, cur = [], ""
        for w in words:
            trial = (cur + " " + w).strip()
            if len(trial) > 60:
                lines.append(cur)
                cur = w
            else:
                cur = trial
        if cur:
            lines.append(cur)
        for i, line in enumerate(lines):
            draw_text(self.screen, line, (SCREEN_W // 2, panel.y + 35 + i * 26), size=18, center=True)
        self._draw_hud()
        self.result_ok_button.draw(self.screen)

    def _draw_win(self):
        self.screen.fill((14, 30, 18))
        bg = assets.load_image("bg_riverbank", (SCREEN_W, SCREEN_H), kind="background")
        bg.set_alpha(150)
        self.screen.blit(bg, (0, 0))
        draw_text(self.screen, "You made it to safety!", (SCREEN_W // 2, SCREEN_H // 2 - 40),
                  size=42, bold=True, center=True, color=(140, 230, 140))
        draw_text(self.screen, f"{ge.player_name} survived Beyond the Forest with a Medkit in hand.",
                  (SCREEN_W // 2, SCREEN_H // 2 + 10), size=18, center=True)
        draw_text(self.screen, "Click or press Enter to play again.",
                  (SCREEN_W // 2, SCREEN_H // 2 + 60), size=16, center=True, color=(190, 190, 180))

    def _draw_gameover(self):
        self.screen.fill((30, 12, 12))
        bg = assets.load_image(LOCATION_BG_KEY.get(ge.current_location, "bg_deep_forest"),
                                (SCREEN_W, SCREEN_H), kind="background")
        bg.set_alpha(90)
        self.screen.blit(bg, (0, 0))
        draw_text(self.screen, "You have died.", (SCREEN_W // 2, SCREEN_H // 2 - 40),
                  size=42, bold=True, center=True, color=(230, 110, 110))
        draw_text(self.screen, "The forest claims another wanderer.",
                  (SCREEN_W // 2, SCREEN_H // 2 + 10), size=18, center=True)
        draw_text(self.screen, "Click or press Enter to try again.",
                  (SCREEN_W // 2, SCREEN_H // 2 + 60), size=16, center=True, color=(190, 190, 180))

    def draw(self):
        if self.state == STATE_NAME_ENTRY:
            self._draw_name_entry()
        elif self.state == STATE_EXPLORE:
            self._draw_explore()
        elif self.state == STATE_ENCOUNTER:
            self._draw_encounter()
        elif self.state == STATE_RESULT:
            self._draw_result()
        elif self.state == STATE_WIN:
            self._draw_win()
        elif self.state == STATE_GAMEOVER:
            self._draw_gameover()

        for t in self.floating_texts:
            t.draw(self.screen)

        self.fader.draw(self.screen)
        pygame.display.flip()

    def run(self):
        while True:
            dt = self.clock.tick(FPS)
            for event in pygame.event.get():
                self.handle_event(event)
            self.update(dt)
            self.draw()


if __name__ == "__main__":
    Game().run()
