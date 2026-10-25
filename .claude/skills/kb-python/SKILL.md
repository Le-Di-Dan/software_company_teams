---
name: kb-python
description: Python backend team conventions - FastAPI service layout, Pydantic v2, SQLAlchemy/Alembic, async patterns, AI/LLM orchestration, testing with pytest and Docker, tooling (uv, ruff, pyright) and pitfalls.
user-invocable: false
---

# Python backend conventions

## Setup
- Current stable Python 3; dependency management with `uv` (or pip-tools) and a committed lockfile; virtualenv per project (never global installs).
- `services/api/`: `app/main.py`, `app/api/v1/<domain>.py`, `app/services/`, `app/repositories/`, `app/schemas/` (Pydantic), `app/models/` (SQLAlchemy), `app/core/` (config, security, logging), `alembic/`, `tests/`, `Dockerfile`.

## Patterns
- FastAPI with Pydantic v2 models for request/response (OpenAPI generated automatically; keep it equal to the contract).
- SQLAlchemy 2.x (async engine) + Alembic migrations; Postgres.
- Settings via `pydantic-settings` from environment variables.
- AI orchestration: official provider SDKs (e.g. `anthropic`), structured outputs validated with Pydantic, timeouts/retries, streaming via SSE when the UX needs it, token/cost logging, evaluation scripts under `tests/evals/`.
- Background jobs: Celery/RQ/Arq or a managed queue per ADR.
- Logging: structlog or stdlib JSON logging with request ids.

## Quality commands
- `ruff check . && ruff format --check .`, `pyright` (or mypy), `pytest -q` (integration tests with docker-compose Postgres), `pip-audit`.

## Pitfalls
- Mixing sync DB calls inside async endpoints blocks the event loop.
- N+1 queries with lazy loading; use `selectinload`.
- Never log prompts/responses containing user PII.
