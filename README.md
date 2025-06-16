# Prince of Persia EDU

A **pygame 3.11** isometric platform‑action game created as a coursework project.\
You guide the prince through a series of floating dungeon paths, avoid traps, defeat enemies and climb the ladder at the end of each stage before the clock runs out.

---

## Gameplay loop

1. **Movement** – walk diagonally on isometric plates using **← → ↑ ↓**.
2. **Jump** – press **Space** to leap over gaps.
3. **Attack** – tap **G** to swing the scimitar (spammable, no hold).
4. **Goal** – reach the red ladder (`L`) to finish the level.
5. **Hazards** – spike pits (`^`), collapsible floors (`X`) and rotating blades (`O`) cause damage *only when your feet touch them*. Falling off the map kills you.
6. **Score** –
   - every enemy killed → `` (default `100`)
   - finish time tier awards ``\
     Final score is stored per level in *`save/scores.json`*.

---

## Controls

| Key       | Action           |
| --------- | ---------------- |
| ← ↑ ↓ →   | Move (isometric) |
| **Space** | Jump             |
| **G**     | Attack           |
| **Esc**   | Open pygame‑menu |

---

## How the project meets the coursework rubric

| Requirement                         | Implementation                                                                                                            |
| ----------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| **≥ 5 custom classes**              | `Player`, `Bandit`, `Skeleton`, `Level`, `HUD`, `SpikeTrap`, `FloorCollapse`, …                                           |
| **Inheritance (built‑in & custom)** | All entities inherit from `pygame.sprite.Sprite` and a custom `BaseEntity`; `Bandit` & `Skeleton` extend shared AI logic. |
| **Composition pattern**             | `Level` composes sprites groups (`world`, `enemies`, `traps`, …).                                                         |
| **Modular code**                    | Packages: `core/`, `entities/`, `levels/`, `ui/`, `utils/`, `assets/`.                                                    |
| **Start / end menu**                | `ui/menu.MainMenu` (interactive, animated bg) + high‑score sub‑menu.                                                      |
| **Graphics & animation**            | 8‑bit pixel‑art assets, animated sprite‑sheets, blinking invulnerability, camera edge‑scroll.                             |
| **Sound / music**                   | Background music loop, jump / attack / game‑over SFX, master‑volume slider.                                               |
| **Save system**                     | High‑scores persisted to `save/scores.json` as JSON.                                                                      |
| **Scoring, multiple levels**        | Three maps, scoring formula, time bonuses.                                                                                |
| **Simple AI**                       | Bandit & Skeleton patrol, detect, chase & attack player.                                                                  |
| **Design pattern**                  | **State Machine** controls game screens; singleton‑style `settings.py` holds constants.                                   |

The project therefore satisfies *good* grade requirements and multiple items for *very good*.

---

## Installation & Running

```bash
python -m venv .venv && source .venv/bin/activate  # optional
pip install -r requirements.txt                     # pygame==2.6+, pygame‑menu==4.5+
python -m src.core.game                             # launch
```

Windows users can double‑click `run.bat`.

---

## Repository layout

```
assets/         # graphics, sounds, level txt files
src/
 ├─ core/       # game loop, settings, state‑machine
 ├─ entities/   # sprites: player, enemies, traps
 ├─ levels/     # Level loader & logic
 ├─ ui/         # menu & HUD
 └─ utils/      # helpers: loader, save, audio
```

---

## Authors

*Arkadiusz Kowalczyk* (INF‑ASI2) – programming, art integration, documentation.

