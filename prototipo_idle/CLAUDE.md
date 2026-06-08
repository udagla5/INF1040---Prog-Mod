# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the Game

Three entry points exist — pick one:

```powershell
python main.py           # Turn-based terminal mode (press Enter to tick)
python gui.py            # Real-time terminal UI (auto-ticks every 500ms)
python main_pygame.py    # Graphical UI (requires pygame)
```

No external packages are required except `pygame` for the graphical mode.

## Running Tests

```powershell
python test_economia.py   # 39 tests — resource generation & management
python test_upgrades.py   # 22 tests — upgrade catalog & purchases
python test_progresso.py  # 28 tests — milestones, revolution, ascension
python test_display.py    # 27 tests — string formatting & rendering
```

All tests use Python's built-in `unittest`. CI runs all four on every push (Ubuntu, Python 3.11) via `.github/workflows/tests.yml`.

## Architecture

The project uses a **TAD (Abstract Data Type)** pattern with strict separation of concerns.

### Core Game Logic (pure Python — no I/O, no side effects)

- **`economia.py`** — resource state: points, generators, production rates, revolution/ascension multipliers
- **`upgrades.py`** — upgrade catalog and purchase logic
- **`progresso.py`** — progress tracking, revolution/ascension resets, victory condition
- **`display.py`** — formats all state into display strings (returns strings, never prints)
- **`constantes.py`** — all game constants: 40 generator definitions, 120 upgrades (auto-generated as 40×3), balance values
- **`persistencia.py`** — the **only** module that touches the filesystem; saves/loads `saves/save.json`

### UI/Orchestration Layer

- **`main.py`** — terminal orchestrator; exposes `processar_comando()` used by both terminal and pygame modes
- **`gui.py`** — real-time terminal UI using `curses` (Unix) or `threading` (Windows)
- **`main_pygame.py`** + **`interface_pygame/renderizador.py`** — pygame frontend; rendering reads TADs through their public interface only
- **`interface_pygame/ui_estado.py`** — UI-only state (scroll offsets, button registry); no game logic

### Key Design Rules

- All TAD functions return `(return_code, new_state)` tuples. Negative codes = errors (`-1` invalid param, `-2` insufficient resources, `-3` already purchased, `-4` locked).
- States are plain dicts. New states are created via `{**estado, 'key': value}` — never mutate in place.
- TADs have no I/O. Only `persistencia.py` reads/writes files.
- `display.py` returns strings; orchestrators decide how to render them.
- The upgrade catalog is generated programmatically in `constantes.py` (40 generators × ×2/×5/×10 multipliers).

## Game Mechanics Summary

- **Generators** (40 total): buy with points; cost scales ×1.15 per unit; production multiplied by upgrade factors
- **Upgrades** (120 total): one-time purchases that multiply a generator's output
- **Revolution**: soft reset — gain crystals (multiplicative production bonus)
- **Ascension**: requires 10 revolutions — gain fragments (exponential production bonus)
- **Victory**: reach 1×10⁵⁰ points (Ponto Ômega)
