# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Revolution Idle — INF1040 - 2026.1 - Grupo 2. A procedural Python incremental game with two front-ends (terminal and pygame). Requires Python 3.10+; pygame is the only non-stdlib dependency (for `main_pygame.py`).

## Commands

```bash
# Run (terminal mode, turn-based)
python main_console.py

# Run (pygame GUI, real-time at 60 fps)
python main_pygame.py

# Run individual test suites (each prints "Falhou: 0" on success)
python test_economia.py
python test_upgrades.py
python test_progresso.py
python test_display.py
```

## Architecture

All game state is **pure-functional**: every TAD function takes state as input and returns `(codigo, novo_estado)` — no mutation, no globals. The `main_console.py` / `main_pygame.py` files are the only orchestrators; they hold references to the three live state dicts (`eco`, `upg`, `prog`) and pass them between TAD calls each tick.

### TAD modules (no side effects, no I/O)

| Module | Responsibility |
|--------|---------------|
| `economia.py` | Points, generators, revolution/ascension multipliers |
| `upgrades.py` | Upgrade catalog and per-generator factors |
| `progresso.py` | Level, milestones, victory condition |
| `display.py` | Number/string formatting only |
| `constantes.py` | All numeric constants and catalogs (40 generators, 120 upgrades, 13 milestones) |

### I/O boundary

`persistencia.py` is the **only** module allowed to read/write files. It serializes/deserializes the three state dicts to `saves/save.json`.

### pygame front-end (`main_pygame.py`)

`main_pygame.py` is self-contained. It imports `processar_comando` from `main_console.py` to reuse tested command logic. Internally it has three sections: **ui_estado** (scroll, buttons, particles, flash — pure state, no pygame calls), **renderizador** (all drawing logic), and **loop principal** (event loop + orchestration). The `interface_pygame/` package is obsolete and can be deleted.

### Return code convention

TAD functions return `(0, ...)` on success and `(non-zero, ...)` on error. The orchestrators check `codigo` before using updated state.
