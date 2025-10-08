# Repository Guidelines

## Project Structure & Module Organization
- Game source lives in `robotron_remix/`; `main.py` defines gameplay loop, sprites, and helpers.
- Persistent data such as `high_scores.json` sits alongside the module; keep schema (initials, score) intact when modifying.
- Root-level `requirements.txt` tracks Python dependencies; keep optional assets or docs in clearly named top-level folders (e.g., `docs/`).

## Build, Test, and Development Commands
- `python -m venv .venv && source .venv/bin/activate` creates an isolated interpreter for local work.
- `pip install -r requirements.txt` installs pygame and any additional runtime packages.
- `python -m robotron_remix.main` launches the game window; pass `PYGAME_HIDE_SUPPORT_PROMPT=1` if you prefer a quiet startup.

## Coding Style & Naming Conventions
- Target Python 3.11; use type hints and dataclasses as in `main.py` for new state containers.
- Follow 4-space indentation, lowercase_with_underscores for module- and function-names, UpperCamelCase for sprite classes.
- Keep module-level constants uppercase (e.g., `PLAYER_SPEED`), and encapsulate new behaviors inside lightweight classes or helper functions.
- Run `python -m compileall robotron_remix` or `ruff check` (if installed) before PRs to catch syntax or lint issues.

## Testing Guidelines
- Favor `pytest` for any automated coverage; place suites in `tests/` mirroring module names (`tests/test_high_scores.py`).
- Isolate logic from rendering so unit tests can validate score handling, spawning, and timers without pygame surfaces.
- For manual QA, run `python -m robotron_remix.main` and verify high-score persistence, spawn pacing, and input latency after each change.

## Commit & Pull Request Guidelines
- Use short, imperative commit titles similar to `Add persistent high score screen`; include a blank line before body details.
- Reference issues with `Fixes #123` when applicable and limit commits to a focused concern (gameplay, UI, build).
- PRs should describe the gameplay impact, list testing evidence (commands run, screenshots/GIFs for visual tweaks), and call out save-file migrations or balance shifts.

## Security & Configuration Tips
- Do not ship personal `high_scores.json` data; reset or mock it before publishing releases.
- Guard new file I/O with `Path` APIs and validate payloads the way `HighScoreManager.load` filters malformed entries.
- When introducing config toggles, prefer environment variables (`ROBOTRON_DIFFICULTY=hard python -m robotron_remix.main`) over hard-coded constants.
