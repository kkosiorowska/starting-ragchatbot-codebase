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
