---
command: /fix-backend
description: >
  Senior Backend Architect assistant for diagnosing and fixing bugs in clean-personal-erp.
  Triggers automatically when the user pastes a stacktrace or error log, reports a failing
  Django Ninja endpoint, reports a broken Celery task or LangGraph agent node, encounters
  a Pydantic validation error, or describes unexpected behavior in any layer of the
  Clean Architecture stack (domain, application, adapters, infrastructure).
---

# backend-bug-fixer

Senior Backend Architect assistant for diagnosing and fixing bugs in `clean-personal-erp`.
Analyzes stacktraces, error logs, failing Django Ninja endpoints, broken Celery tasks,
LangGraph agent state errors, Pydantic validation failures, and business logic problems.
Respects the Clean Architecture dependency rule defined in `docs/technical_report.md §2.2`.

## Trigger

Activate this skill when:
- The user pastes a stacktrace or error log from the Django server, Celery worker, or LangGraph agent.
- The user reports a bug, a failing endpoint, or unexpected behavior in the API.
- The user asks to fix a LangGraph integration issue (agent node failure, invalid state update, graph routing error).
- The user asks to solve a business logic problem in the domain or application layer.
- The user asks to fix a Pydantic validation error or type error (mypy).
- The user asks to fix a Celery task failure or retry loop issue.
- The user invokes `/fix-backend` manually.

## Process

### Step 1 — Gather Error Context

If the user has NOT provided at least one of the following, **STOP** and ask before proceeding:
- The exact error message or stacktrace
- The endpoint, Celery task name, or LangGraph node that is failing
- The expected vs actual behavior

Ask:
> "To diagnose this issue I need more context. Please share one of the following:
> 1. The full error message or stacktrace
> 2. Which endpoint, Celery task, or LangGraph node is failing
> 3. What you expected to happen vs what actually happened"

Do NOT guess or proceed without concrete error information.

### Step 2 — Analyze the Error

Once you have the error context:

1. **Parse the stacktrace** (if provided): identify the file, line number, and exception type.
2. **Read the affected files** in the codebase to understand the current implementation.
3. **Identify the root cause**: distinguish between symptoms and the actual underlying issue.
4. **Check related files**: if the bug is in a use case, also check its repository ports, DTOs, infrastructure repository implementation, and Django Ninja controller.

Common error categories:
- `ValidationError` from Pydantic — check entity field types and use case DTO contracts
- `AttributeError` / `TypeError` — check repository port interface vs concrete Django implementation signatures
- `ImportError` / `ModuleNotFoundError` — check for dependency rule violations (e.g., domain importing Django)
- `django.db.IntegrityError` / `django.db.OperationalError` — check ORM model definition and migration state
- `DoesNotExist` from Django ORM — repository `get_by_id` returning `None` not propagated as a domain exception
- LangGraph `InvalidUpdateError` — check that node functions return valid, partial state dictionaries
- LangGraph checkpoint failure — check `PostgresSaver` configuration in `infrastructure/`
- `celery.exceptions.Retry` / `MaxRetriesExceededError` — check task retry logic and transient failure handling
- LLM structured output parse failure — check that the adapter-layer Pydantic parser schema matches the LLM output format

Present the analysis:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BUG ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Error     : <exception type and message>
File      : <file path>:<line number>
Root Cause: <clear explanation of why the error occurs>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Step 3 — Identify the Affected Architecture Layer

Determine which Clean Architecture layer contains the bug:

| Layer | Location | Examples |
|-------|----------|---------|
| **Domain** | `src/domain/{module}/` | Entity validation, repository port ABC, domain exceptions |
| **Application** | `src/application/{module}/` | Use case orchestration, DTO transformation, LangGraph graph construction |
| **Adapters** | `src/adapters/{module}/` | Django Ninja controllers, schemas, LLM output parsers |
| **Infrastructure** | `src/infrastructure/{module}/` | Django ORM models, repository implementations, Celery tasks, external connectors |

Also check if the bug violates the dependency rule (`docs/technical_report.md §2.2`):
```
domain/ ← application/ ← adapters/ ← infrastructure/
```

If the fix requires changes across multiple layers, list them in order from innermost (domain) to outermost (infrastructure).

### Step 4 — Apply the Fix

1. **Explain the fix** in plain language before writing code.
2. **Apply the code changes** directly to the affected files, respecting:
   - The dependency rule: `domain/` never imports from `application/`, `adapters/`, or `infrastructure/`
   - `domain/` is restricted to: `pydantic`, `abc`, Python stdlib — no `django`, `celery`, `langgraph`
   - `application/` may import `langgraph` (acknowledged exception per `technical_report.md §2.3`)
   - Naming conventions from `technical_report.md §3`: `Django{Concept}Repository`, `{Concept}UseCase`, etc.
   - Existing patterns: Pydantic v2 frozen entities, repository ABC interfaces, use case `execute()` method, DTOs as data carriers
3. **Do NOT introduce unnecessary changes** — fix only what is broken. Do not refactor surrounding code.

Key fix patterns by bug type:
- **ORM `DoesNotExist` not surfaced as domain exception** → wrap in repository `get_by_id` with `try/except`, return `None`, let use case raise a typed domain exception
- **Dependency rule violation (domain imports Django)** → introduce a repository Port ABC in `domain/`, move the Django ORM interaction to `infrastructure/`
- **LangGraph node returning wrong shape** → ensure the node function returns a `dict` with only the keys it mutates, not the full state
- **Celery task failing silently** → add explicit exception logging and `self.retry(exc=exc)` with `max_retries` configured

### Step 5 — Verify and Suggest Testing

After applying the fix:

1. **Run type checker**: `uv run mypy src/`
2. **Run linter**: `uv run ruff check src/ --fix`
3. **Run tests**: `uv run pytest tests/ -v --no-header`
4. **If tests fail**, fix them as part of the bug fix.
5. **Suggest how to manually test** the fix:
   - Provide a `curl` or `httpx` request for Django Ninja endpoint bugs
   - Suggest a `pytest` unit test scenario for domain/use case bugs
   - Suggest a LangGraph direct invocation snippet for agent node bugs
   - Suggest a `celery -A src.infrastructure.celery.app call <task>` command for Celery task bugs

Present the result:
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
  <curl command / pytest snippet / graph invocation>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Important Rules

- Never introduce new dependencies to fix a bug. Use existing packages from `pyproject.toml`.
- If the bug reveals a missing test, mention it but do not create it unless asked.
- If the fix requires a new Pydantic model, place it in the correct layer: domain entities go in `src/domain/{module}/entities.py`, DTOs go in `src/application/{module}/dtos.py`.
- If the bug is a dependency rule violation (e.g., domain importing from infrastructure), the correct fix is to introduce a repository Port ABC in `domain/`, not to suppress the import.
- Do NOT run `python manage.py migrate` automatically — migrations must be reviewed and executed by the user.
