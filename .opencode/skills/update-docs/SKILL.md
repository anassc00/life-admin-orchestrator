---
name: update-docs
description: Synchronize project documentation (README.md and .opencode/ docs) with current source code structure, modules, and configuration. Triggers when user asks to update docs or after new features.
---

# update-docs

Synchronize project documentation (`README.md` and `.opencode/README.md`) with the current source code structure, modules, and configuration for life-admin-orchestrator.

## Trigger

Activate this skill when:
- A new feature completes successfully
- A new folder or module is created inside `domain/`, `application/`, `adapters/`, or `infrastructure/`
- The user asks to "update documentation", "sync docs", "actualizar la documentación", or similar
- The user invokes this skill manually

## Process

### Step1 — Scan Source Structure

Run a recursive scan of the project to build a complete map of existing modules and their internal folders:

```bash
find domain/ application/ adapters/ infrastructure/ -type d 2>/dev/null | sort
```

Identify each layer and the modules within each:
- `domain/` — entities, repositories (ports), exceptions
- `application/` — use_cases, dtos, agents
- `adapters/` — api views and schemas
- `infrastructure/` — django_app/models, repositories, tasks, di.py

### Step2 — Read Architecture Levels

Check the module structure to determine if it's Full (all 4 layers) or Light (infrastructure only).

### Step3 — Update .opencode/README.md

Update `.opencode/README.md` to reflect the current state of the project:
- Folder structure section
- Module list
- Available commands

### Step4 — Update README.md

Open `README.md` and synchronize:

- **Project description**: Ensure it matches the current scope
- **Tech stack table**: Verify all dependencies in `pyproject.toml`
- **Useful commands**: Ensure accuracy
- **Available API endpoints**: Check Django Ninja routers in `adapters/api/*/views.py`
- **Django Admin**: Check registered models in `infrastructure/django_app/`

### Step5 — Validate Consistency

Cross-check between `.opencode/README.md`, `README.md`, and actual code:

1. **Django Ninja docs URL**: Confirm `/api/docs` in `config/urls.py`
2. **Base API routes**: Verify `@router.get/post/...` decorators in `adapters/api/*/views.py`
3. **Django admin URL**: Confirm `/admin/` in `config/urls.py`
4. **Python version**: Check `requires-python` in `pyproject.toml`
5. **Celery broker**: Check `CELERY_BROKER_URL` in `config/celery.py`
6. **Database**: Confirm PostgreSQL/SQLite in `config/settings/`

### Step6 — Report

Present a short summary:

```
Documentation sync complete:
- Modules detected    : [list with layers]
- README.md updated  : [sections]
- .opencode/ updated : [sections]
- Inconsistencies    : [list or "none"]
```
