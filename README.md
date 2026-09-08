# Beyond the Forest — Pygame Edition

A visual, animated version of the original text-based survival game. Same
rules, same odds, same win condition — now with real scenes, an animated
player and monsters, a health bar, screen transitions, and slots for your
own pixel art.

## ▶ Run it

```
pip install -r requirements.txt
python main.py
```

## 🎮 Controls

| Action        | Mouse            | Keyboard              |
|---------------|------------------|------------------------|
| Move          | Direction button | Arrow keys / WASD      |
| Fight         | Fight button     | F                      |
| Run           | Run button       | R                      |
| Use Medkit    | Use Medkit button| U                      |
| Continue      | Continue button  | Enter / Space          |
| Quit          | —                | Esc                    |

## 🖼 Adding your own pixel art

Drop PNG files into `assets/images/` using these **exact filenames**.
Nothing else needs to change — the game checks for each file at startup
and instantly swaps out the generated placeholder art for yours.

**Backgrounds** (any size — auto-scaled to fill the 960×600 window; pixel-art
scenes around 240×135 or 320×180 upscale nicely):
- `bg_forest_entrance.png`
- `bg_deep_forest.png`
- `bg_riverbank.png`

**Player** (recommended 64–96px square, transparent background):
- `player.png`

**Monsters** (recommended 96–140px square, transparent background):
- `monster_goblin.png`
- `monster_wolf.png`
- `monster_giant_spider.png`
- `monster_bandit.png`

**Icons** (recommended 32px square — not yet drawn on screen by default,
reserved for a future inventory panel, but already wired up in `assets.py`):
- `icon_medkit.png`
- `icon_heart.png`

Until a given file exists, `assets.py` generates a small deterministic
pixel-art-style placeholder for it (blocky sprite for characters/monsters,
banded/textured tile for backgrounds), so the game is fully playable right
now and will automatically look better as you finish each piece of art —
no code edits required.

## 📦 Project structure

```
beyond_the_forest/
├── main.py           # pygame app: states, scenes, input, animation
├── game_engine.py     # original game logic/state — unchanged, still covered by test_game.py
├── assets.py           # image loading + placeholder pixel-art generator
├── ui.py                 # buttons, text box, floating damage text, fade transitions
├── test_game.py     # original unit tests (all still pass)
├── requirements.txt
└── assets/
    └── images/          # <- put your .png files here
```

## 🧠 How it fits together

`game_engine.py` is untouched from the original text version — it still
owns all state (`player_health`, `inventory`, `current_location`) and all
rules (`move`, `fight`, `run`, `use_item`, `has_won`, `is_alive`). `main.py`
is purely a presentation layer: it calls those same functions and turns
their return values into animated scenes, floating combat text, and fades
between locations. That separation means:

- `test_game.py` keeps testing the real rules with zero changes.
- You can reskin, retheme, or completely redesign the visuals in `main.py`
  / `assets.py` without ever touching the game's actual logic.

## 🌱 Ideas for extending it further

- Add more locations/monsters in `game_engine.py`'s `locations` / `monsters`
  dicts — `main.py` and `assets.py` will pick up new locations automatically
  as long as you add a matching `bg_<location_key>.png` and extend
  `LOCATION_BG_KEY` in `main.py`.
- Add a `sounds/` folder and hook `pygame.mixer` into `_do_fight` /
  `_do_move` for footsteps, hits, and a win/lose jingle.
- Add an inventory bar along the HUD using the `icon_medkit` / `icon_heart`
  assets that are already loaded and ready to draw.
