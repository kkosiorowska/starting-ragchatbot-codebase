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
