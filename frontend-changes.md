# Frontend Changes: Dark/Light Theme Toggle

## Summary
Added a toggle button that lets users switch between the existing dark theme and a new light theme, with the preference persisted across visits.

## Files Changed

### `frontend/index.html`
- Added a `#themeToggle` button (fixed, top-right of the viewport, outside `.container` so it stays visible regardless of page content) containing inline SVG sun and moon icons.
- Button includes `aria-label`, `aria-pressed`, and `title` attributes for accessibility; it's a native `<button>` so it's keyboard-focusable and activates on Enter/Space by default.
- Bumped cache-busting query params for `style.css` and `script.js` from `v=9` to `v=10`.

### `frontend/style.css`
- Added a `:root[data-theme="light"]` block that overrides all existing CSS custom properties (`--background`, `--surface`, `--surface-hover`, `--text-primary`, `--text-secondary`, `--border-color`, `--user-message`, `--assistant-message`, `--shadow`, `--focus-ring`, `--welcome-bg`, `--welcome-border`) with a light palette that keeps AA-level contrast (e.g. `--text-primary: #0f172a` on `--background: #ffffff`, `--text-secondary: #475569`).
- Added a shared transition rule (`background-color`, `color`, `border-color`, 0.3s ease) across the main color-bearing containers (body, sidebar, chat area, message bubbles, stat items, etc.) so switching themes animates smoothly instead of snapping.
- Added `.theme-toggle` styles: a fixed circular button in the top-right corner using the existing surface/border/focus-ring variables so it matches the current design language, with hover/active/focus-visible states consistent with `#sendButton` and `.suggested-item`.
- Added icon-crossfade styles for `.theme-icon-sun` / `.theme-icon-moon` using `opacity`, `rotate`, and `scale` transitions so the sun and moon icons rotate/fade into each other when the theme changes.
- Added a small-screen rule (inside the existing `max-width: 768px` media query) to shrink the toggle button on mobile.

### `frontend/script.js`
- Added `themeToggle` to the cached DOM elements.
- Added `initializeTheme()`, called on load: reads `localStorage.getItem('theme')`, falling back to the `prefers-color-scheme: light` media query, then applies the resolved theme.
- Added `toggleTheme()`: flips between `'light'` and `'dark'` based on the current `data-theme` attribute.
- Added `applyTheme(theme)`: sets/removes `data-theme="light"` on `document.documentElement`, persists the choice to `localStorage`, and updates the toggle button's `aria-pressed`/`aria-label` to reflect the new state.
- Wired the toggle button's `click` listener in `setupEventListeners()`.

## Behavior
- Default/unset theme is the existing dark theme (no `data-theme` attribute).
- Clicking the button (or activating it via keyboard) toggles `data-theme="light"` on `<html>`, switching all CSS variables and animating the transition.
- Theme choice is remembered via `localStorage` and re-applied on next visit; if nothing is saved yet, the OS-level light/dark preference is used.

## Testing Notes
- Verified `script.js` parses with `node --check` and that `index.html` contains the new toggle markup.
- Served the frontend statically and confirmed `index.html`, `style.css`, and `script.js` all return HTTP 200.
- No browser automation tool was available in this environment, so the actual visual rendering/animation was not verified in a live browser — worth a manual spot-check (toggle click, icon crossfade, keyboard activation via Tab+Enter/Space, and contrast in light mode) before merging.
---

# Testing Framework Enhancements

> Note: this change is backend-only (test infrastructure for the RAG system's FastAPI app). No frontend files were touched. Logged here per the `/implement-feature` command's fixed convention.

## Summary

Added API testing infrastructure for the FastAPI backend under `backend/tests`, since none existed previously.

## Changes

### `pyproject.toml`
- Added a `dev` dependency group with `pytest` and `pytest-mock` (via `uv add --dev`).
- Added a `[tool.pytest.ini_options]` section:
  - `testpaths = ["backend/tests"]`
  - `pythonpath = ["backend"]` so backend modules import without path hacks
  - custom markers: `unit`, `api`, `integration`
  - `addopts = "-v --strict-markers"`

### `backend/tests/conftest.py` (new)
- `create_test_app(rag_system)`: builds a standalone FastAPI app that redefines the `/api/query`, `/api/courses`, and `/` routes from `backend/app.py`, backed by an injected `rag_system`.
  - This avoids importing `backend/app.py` directly, since it calls `app.mount("/", StaticFiles(directory="../frontend"), ...)` at import time, which throws if the `frontend` directory isn't present relative to the test working directory.
- `mock_rag_system` fixture: a `MagicMock` pre-wired with default return values for `query()`, `get_course_analytics()`, and `session_manager.create_session()`.
- `test_app` / `client` fixtures: the test app and a `TestClient` for it, built from `mock_rag_system`.
- `sample_lesson` / `sample_course` / `sample_course_chunk` fixtures: reusable sample domain objects (`Lesson`, `Course`, `CourseChunk`) for future unit tests.

### `backend/tests/test_api.py` (new)
API endpoint tests using the `client` fixture:
- `/api/query`: session creation vs. reuse, request validation (422 on missing `query`), error propagation (500 with the exception message), response schema shape.
- `/api/courses`: analytics response shape, error propagation.
- `/`: basic 200 response.

### `backend/tests/__init__.py` (new)
Empty marker file so `backend/tests` is a proper package.

## Running the tests

```bash
uv run pytest
```

9 tests pass.

---

# Code Quality Tooling

## Summary

Added `black` as the automatic code formatter for the project and created development scripts to run formatting/format-checking on demand. Reformatted the existing codebase to match `black`'s style so the baseline is consistent going forward.

Note: `black` formats Python code. This repo's `frontend/` directory is plain HTML/CSS/JS with no build tooling, so it has no files `black` applies to — the quality tooling and reformatting below apply to the Python codebase (`backend/`, `main.py`).

## Changes

- **`pyproject.toml`**: Added `black` as a dev dependency (via `uv add --dev black`) and configured it under `[tool.black]` (`line-length = 88`, `target-version = ["py313"]`).
- **`uv.lock`**: Updated to lock the new dev dependency.
- **`scripts/format.sh`** (new): Runs `black` against `backend` and `main.py` to auto-format the codebase.
- **`scripts/check.sh`** (new): Runs `black --check --diff` against `backend` and `main.py` to verify formatting without modifying files (suitable for CI).
- **`README.md`**: Added a "Development" section documenting the two new scripts.
- Reformatted with `black`: `backend/config.py`, `backend/models.py`, `backend/ai_generator.py`, `backend/app.py`, `backend/session_manager.py`, `backend/rag_system.py`, `backend/search_tools.py`, `backend/document_processor.py`, `backend/vector_store.py`. `main.py` was already compliant.

## Usage

```bash
./scripts/format.sh   # auto-format
./scripts/check.sh    # verify formatting, non-zero exit if issues found
```
