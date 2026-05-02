---
name: fix-backend
description: Senior Backend Architect assistant for diagnosing and fixing bugs in Clean Architecture stack including Django Ninja endpoints, Celery tasks, LangGraph agents, and Pydantic validation errors.
---

# fix-backend

Senior Backend Architect assistant for diagnosing and fixing bugs in the Clean Architecture stack (domain, application, adapters, infrastructure), including Django Ninja endpoints, Celery tasks, LangGraph agents, and Pydantic validation errors.

## Trigger

Activate this skill when:
- The user pastes a stacktrace or error log
- The user reports a failing endpoint, broken Celery task, or LangGraph agent issue
- The user encounters a Pydantic validation error or type error
- The user asks to fix a bug or unexpected behavior in any layer
- The user invokes this skill manually

## Process

### Step1 — Gather Error Context

If the user has NOT provided at least one of the following, **STOP** and ask:

> "To diagnose this issue I need more context. Please share:
> 1. The full error message or stacktrace
> 2. Which endpoint, Celery task, or LangGraph node is failing
> 3. What you expected vs what actually happened"

### Step2 — Analyze the Error

1. **Parse the stacktrace**: identify file, line number, exception type
2. **Read affected files** to understand current implementation
3. **Identify root cause**: distinguish symptoms from underlying issue
4. **Check related files**: if bug is in a use case, check repositories, DTOs, infrastructure, and controllers

Common error categories:
- `ValidationError` from Pydantic → check entity field types and DTO contracts
- `AttributeError` / `TypeError` → check repository interface vs implementation
- `ImportError` / `ModuleNotFoundError` → check dependency rule violations
- `django.db.IntegrityError` → check ORM model and migration state
- `DoesNotExist` from Django ORM → repository should return `None`, use case raises domain exception
- LangGraph `InvalidUpdateError` → check node functions return valid partial state dicts
- Celery retry errors → check task retry logic

Present analysis:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BUG ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Error     : <exception type and message>
File      : <file path>:<line number>
Root Cause: <explanation>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Step3 — Identify Affected Architecture Layer

| Layer | Location |
|-------|----------|
| **Domain** | `domain/{module}/` |
| **Application** | `application/{module}/` |
| **Adapters** | `adapters/api/{module}/` |
| **Infrastructure** | `infrastructure/{module}/`, `infrastructure/django_app/`, `config/` |

Check for dependency rule violations:
```
domain/ ← application/ ← adapters/ ← infrastructure/
```

### Step4 — Apply the Fix

1. **Explain the fix** in plain language before writing code
2. **Apply changes** respecting:
   - `domain/` never imports from outer layers
   - `domain/` restricted to: `pydantic`, `abc`, Python stdlib
   - `application/` may import `langgraph` (exception for agents)
   - Naming conventions: `Django{Concept}Repository`, `{Verb}{Concept}UseCase`
   - Pydantic v2 frozen entities, repository ABC interfaces
3. **Do NOT introduce unnecessary changes** — fix only what's broken

Key fix patterns:
- **ORM `DoesNotExist` not surfaced** → wrap in repository with try/except, return `None`, let use case raise domain exception
- **Dependency rule violation** → introduce Port ABC in `domain/`, move Django interaction to `infrastructure/`
- **LangGraph node wrong shape** → ensure node returns `dict` with only keys it mutates
- **Celery task failing silently** → add logging and `self.retry(exc=exc)`

### Step5 — Verify and Suggest Testing

1. **Run type checker**: `uv run mypy .`
2. **Run linter**: `uv run ruff check . --fix`
3. **Run tests**: `uv run pytest tests/ -v`

Present result:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FIX APPLIED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Files Modified:
  - <file 1>
  - <file 2>

Type check : OK (mypy)
Linter     : OK (ruff)
Tests      : <N> passed, 0 failed

How to verify:
  <curl command / pytest snippet / celery command>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Important Rules

- Never introduce new dependencies without asking
- If bug reveals missing test, mention it but don't create unless asked
- Do NOT run `migrate` automatically — let user review
