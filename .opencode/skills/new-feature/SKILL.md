---
name: new-feature
description: Full-cycle feature orchestrator for Clean Architecture. Automates Red-Green-Refactor TDD cycle coordinating architecture validation, test generation, implementation, and verification.
---

# new-feature

Full-cycle feature orchestrator for Clean Architecture. Automates the complete Red-Green-Refactor TDD cycle, coordinating architecture validation, test generation, implementation, and verification.

## Trigger

Activate this skill automatically when:
- The user says "create a new feature", "implement a requirement", "build new functionality"
- The user describes a feature they want developed end-to-end
- The user invokes this skill manually

## Process

### Step1 — Capture Requirements

Ask the user two questions:
1. **Feature**: "Describe the feature you want to implement."
2. **Module**: "Which module does this feature belong to? (`finance`, `calendar`, `document`, `contact`, or a new cross-cutting concern)"

Output:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FEATURE ORCHESTRATOR - INIT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Feature : <description>
Module  : <module name>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Starting pipeline...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Step2 — Architecture Validation

Validate the module's structure:
- Confirm it's Full (all 4 layers) for agent modules or Light (infrastructure only) for cross-cutting concerns
- Validate folder structure exists: `domain/{module}/`, `application/{module}/`, `adapters/api/{module}/`, `infrastructure/{module}/`
- Confirm naming conventions and import boundary rules

**Gate**: If any violation, **STOP**. Fix the structure before proceeding.

```
[Step 2/6] ✓ Architecture validated
```

### Step3 — Phase RED: Generate Tests (TDD)

Generate the `test_*.py` file in the correct path:
- Identify correct layer (Domain or Application)
- Include at least 1 happy path and 1 error case
- Use proper mocks via `unittest.mock`

```
[Step 3/6] ✓ Test file created — <path>
```

### Step4 — Phase RED: Verify Tests Fail

```bash
uv run pytest <path> -v --no-header
```

**Gate**: Tests **MUST fail**. If they PASS, investigate why.

```
[Step 4/6] ✓ RED phase confirmed — Tests fail as expected
```

### Step5 — Phase GREEN: Implement the Code

Write implementation to make tests pass:

- **Domain layer** → `domain/{module}/entities.py`, `repositories/` (ports), `exceptions/`
- **Application layer** → `application/use_cases/{module}/`, `dtos/`, `agents/`
- **Adapters layer** → `adapters/api/{module}/views.py`, `schemas.py`
- **Infrastructure layer** → `infrastructure/repositories/`, `django_app/models/`, `tasks/`

**Implementation rules:**
- `domain/` must have **zero external imports** (no django, celery, langgraph)
- `application/` may only import from `domain/` (plus `langgraph` for agents)
- Domain entities must be **frozen Pydantic models**
- Repository implementations must convert ORM models to domain entities
- Never raise generic `Exception` — use typed domain exceptions

After writing, run tests again:

```bash
uv run pytest <path> -v --no-header
```

**Gate**: Tests **MUST pass**. Repeat until all pass.

```
[Step 5/6] ✓ GREEN phase confirmed — All tests pass
```

### Step6 — Phase REFACTOR and Verify

#### 6a. Run Linter and Formatter
```bash
uv run ruff check . --fix
uv run ruff format .
```

#### 6b. Run Type Checker
```bash
uv run mypy .
```

#### 6c. Final Full Test Run
```bash
uv run pytest tests/ -v --no-header
```

#### 6d. Django Migration Check
If `infrastructure/django_app/models/` was modified:
```bash
uv run python manage.py makemigrations
uv run python manage.py migrate --plan
```
Do NOT run `migrate` automatically.

### Step7 — Pipeline Summary

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FEATURE ORCHESTRATOR - COMPLETE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Feature      : <description>
Module       : <module name>
Level        : Full | Light
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Architecture : Validated
Test file    : <path>
Impl files   : <paths>
Tests        : All passing (<count> tests)
Linter       : Clean (ruff)
Types        : Clean (mypy)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TDD Cycle    : RED → GREEN → REFACTOR
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```
