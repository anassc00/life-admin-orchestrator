---
command: /update-docs
description: >
  Synchronize project documentation (CLAUDE.md and README.md) with the current source code structure,
  modules, and configuration for clean-personal-erp. Triggers automatically when /new-feature
  completes, a new folder or module is created inside src/, or the user asks to update, sync,
  or regenerate documentation.
---

# doc-sync

Synchronize project documentation (`CLAUDE.md` and `README.md`) with the current source code
structure, agent modules, and configuration for `clean-personal-erp`.

## Trigger

Activate this skill when:
- The `/new-feature` command completes successfully
- A new folder or module is created inside `src/`
- The user asks to "update documentation", "sync docs", "actualizar la documentación", or similar
- The user invokes `/update-docs` manually

## Process

### Step 1 — Scan Source Structure

Run a recursive scan of `src/` to build a complete map of existing modules and their internal folders:

```bash
find src/ -type d | sort
```

Identify each layer (`domain/`, `application/`, `adapters/`, `infrastructure/`) and the modules
within each. Also check for:
- `src/infrastructure/django_app/` — the Django application (models, admin, urls, api)
- `src/infrastructure/celery/` — Celery task definitions
- `src/infrastructure/di.py` — the dependency injection wiring module

### Step 2 — Read Architecture Levels

Check `docs/technical_report.md §3` (Layered Responsibility Analysis) to confirm the architecture
level of each module:

| Level | Meaning |
|-------|---------|
| **Full** | All 4 layers: domain, application, adapters, infrastructure |
| **Light** | Infrastructure only (cross-cutting concerns: auth, config, logging) |

If `docs/technical_report.md` does not exist, infer the level from the folder structure detected in Step 1.

### Step 3 — Update CLAUDE.md

Open `CLAUDE.md` and update the following sections. Do NOT modify sections outside of these:

#### 3a — Folder Structure Section
Regenerate the folder tree to reflect the **current** state of `src/`. Use the same indented tree
format already present in the file. Include all modules with their internal layer folders and key
files (e.g., `entities.py`, `ports.py`, `use_cases.py`, `repositories.py`, `tasks.py`).

#### 3b — Module Conventions Section
If a new module follows a structure that differs from the documented Full/Light convention, add a
note or update the description to reflect the supported patterns.

#### 3c — Agent Catalog Section
If a new agent module was added, update the agent catalog table with:
- Agent name
- Trigger mechanism (Scheduled / Event-driven / Manual)
- Primary use cases
- External dependencies (APIs, connectors)

Reference: `docs/technical_report.md §5.3`.

### Step 4 — Update README.md

Open `README.md` and synchronize:

- **Project description**: Ensure it matches the current scope of the system.
- **Tech stack table**: Verify all dependencies listed are still in `pyproject.toml`. Add any new
  significant dependencies (e.g., new external API connector packages). Remove any that were removed.
  Core stack to always verify:
  - `django` / `django-ninja` / `pydantic` / `langgraph` / `celery` / `redis` / `psycopg`

- **Useful commands**: Ensure commands listed are accurate:
  ```
  uv run pytest tests/                         # run all tests
  uv run pytest tests/unit/                    # run unit tests only
  uv run pytest tests/integration/             # run integration tests only
  uv run ruff check src/                       # lint
  uv run mypy src/                             # type check
  python manage.py runserver                   # start Django dev server
  python manage.py migrate                     # apply database migrations
  python manage.py createsuperuser             # create admin user
  celery -A src.infrastructure.celery worker   # start Celery worker
  ```

- **Available API endpoints**: If there is an endpoints section, update it to reflect current
  Django Ninja routers and route decorators found in `src/adapters/*/controllers.py`.

- **Django Admin**: Confirm which models are registered in Django admin
  (`src/infrastructure/django_app/admin.py`).

### Step 5 — Validate Consistency

Cross-check the following between `CLAUDE.md`, `README.md`, and the actual code:

1. **Django Ninja docs URL**: Confirm the documented API docs path matches `docs_url` in the
   `NinjaAPI(...)` constructor (default: `/api/docs`).
2. **Base API routes**: Verify documented routes match the actual `@router.get/post/...`
   decorators in `src/adapters/*/controllers.py`.
3. **Django admin URL**: Confirm the admin URL is documented (default: `/admin/`).
4. **Python version**: Confirm the documented Python version matches `requires-python` in `pyproject.toml`.
5. **Celery broker**: Confirm the documented broker (Redis) matches the `CELERY_BROKER_URL`
   configuration in Django settings.
6. **Database**: Confirm PostgreSQL is documented and matches `DATABASES` in Django settings.

If any inconsistency is found, fix it in the documentation.

### Step 6 — Report

Present a short summary to the user:

```
Documentation sync complete:
- Agent modules detected  : [list with levels]
- CLAUDE.md sections updated: [list]
- README.md sections updated: [list]
- Inconsistencies fixed   : [list or "none"]
```
