---
command: /new-feature
description: >
  Full-cycle feature orchestrator for clean-personal-erp Clean Architecture. Triggers automatically
  when the user wants to create a new feature, implement a requirement, build new functionality,
  or develop a new use case for any personal admin agent (finance, calendar, document, contact).
  Automates the complete Red-Green-Refactor TDD cycle, coordinating architecture validation
  (/check-arch), test generation (/test-gen), implementation, and test verification.
  Ensures Clean Architecture compliance at every step.
---

# feature-orchestrator

Automates the complete development cycle of a feature following **Red-Green-Refactor TDD**,
ensuring compliance with the Clean Architecture and dependency rules defined in
`docs/technical_report.md`. Orchestrates the other skills (`/check-arch`, `/test-gen`) as
part of the pipeline.

## Auto-Trigger Conditions

Activate this skill automatically when:
- The user says "create a new feature", "implement a requirement", "build new functionality"
- The user describes a feature they want developed end-to-end
- The user invokes `/new-feature` manually

## Process

### Step 1 — Capture Requirements

Ask the user two questions before proceeding:

1. **Feature**: "Describe the feature you want to implement."
2. **Module**: "Which agent module does this feature belong to? (`finance`, `calendar`, `document`, `contact`, or a new cross-cutting concern)"

Wait for both answers. Do not proceed until both are provided.

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

---

### Step 2 — Architecture Validation (Sentinel)

Invoke the **`/check-arch`** skill logic to:
- Confirm the module's level (Full for agent modules, Light for cross-cutting concerns)
- Validate that the folder structure exists and is correct for that level (`docs/technical_report.md §3`)
- Confirm naming conventions (§3 per-layer sections) and import boundary rules (§2.2)

**Gate**: If `/check-arch` reports any violation, **STOP** the pipeline. Fix the structural issue first before proceeding. Do not generate tests or implementation code on an invalid structure.

Output after passing:
```
[Step 2/6] ✓ Architecture validated — Level: Full | Light
```

---

### Step 3 — Phase RED: Generate Tests (TDD)

Invoke the **`/test-gen`** skill logic to:
- Identify the correct layer (Domain or Application) based on the feature description
- Generate the `test_*.py` file in the correct path following naming conventions from `technical_report.md §3`
- Include at least 1 happy path and 1 error case with proper mocks via `unittest.mock`

Output after generation:
```
[Step 3/6] ✓ Test file created — <path/to/test_file.py>
```

---

### Step 4 — Phase RED: Verify Tests Fail

Run the generated test to confirm it fails (RED phase of TDD):

```bash
uv run pytest <path/to/test_file.py> -v --no-header
```

**Gate**: The test **MUST fail**. This confirms the tests are valid and the implementation does not exist yet.

- If tests **FAIL** — proceed to Step 5
- If tests **PASS** — something is wrong. Investigate why the tests pass without implementation and fix the test file before continuing.

Output:
```
[Step 4/6] ✓ RED phase confirmed — Tests fail as expected
```

---

### Step 5 — Phase GREEN: Implement the Code

Write the implementation code to make the tests pass:

- **Domain layer** — create or update `entities.py`, `ports.py`, or `exceptions.py` inside `src/domain/{module}/`
- **Application layer** — create or update `use_cases.py` and `dtos.py` inside `src/application/{module}/`
  - If the feature involves agent orchestration, also update the `{Module}AgentOrchestrator` in `src/application/{module}/agents.py`
- **Adapters layer** — create or update `schemas.py` and `controllers.py` in `src/adapters/{module}/`
- **Infrastructure layer** — create or update `models.py`, `repositories.py`, or `tasks.py` in `src/infrastructure/{module}/`

**Implementation rules:**
- `src/domain/` must have **zero external imports**: no `django`, no `celery`, no `langgraph`, no external API SDKs
- `src/domain/` allowed imports: `pydantic`, `abc`, Python stdlib (`uuid`, `datetime`, `decimal`, `typing`)
- `src/application/` may only import from `src/domain/` (plus `langgraph` as an acknowledged exception per `technical_report.md §2.3`)
- `src/adapters/` uses Django Ninja `Schema` (Pydantic-based) for request/response schemas
- `src/infrastructure/` is the only layer that touches `django.db.models`, `celery`, and external API clients
- Domain entities must be **frozen Pydantic models** (`model_config = ConfigDict(frozen=True)`) — state transitions via `model_copy(update={...})`
- Repository implementations (`Django{Concept}Repository`) must convert ORM model instances to domain entities before returning — never pass `{Concept}Model` instances across layer boundaries
- Never raise generic `Exception` in domain — define typed exceptions as subclasses of `Exception` in `src/domain/{module}/exceptions.py`

After writing the implementation, run the test again:

```bash
uv run pytest <path/to/test_file.py> -v --no-header
```

**Gate (CRITICAL)**: Tests **MUST pass**. This is a hard gate.

- If tests **PASS** — proceed to Step 6
- If tests **FAIL** — analyze the error output, fix the implementation, and re-run. **Repeat until all tests pass.** Do NOT advance to Step 6 with failing tests.

Output:
```
[Step 5/6] ✓ GREEN phase confirmed — All tests pass
```

---

### Step 6 — Phase REFACTOR and Verify

Once tests are green, perform cleanup:

#### 6a. Run Linter and Formatter
```bash
uv run ruff check src/ --fix
uv run ruff format src/
```

Fix any linting issues. Re-run tests after to confirm nothing broke.

#### 6b. Run Type Checker
```bash
uv run mypy src/
```

Resolve any type errors. All new code must pass mypy with no errors.

#### 6c. Final Full Test Run

Run the complete test suite to ensure no regressions:
```bash
uv run pytest tests/ -v --no-header
```

#### 6d. Django Migration Check (if infrastructure models were added or modified)

If `src/infrastructure/{module}/models.py` was created or modified, remind the user to generate and review a migration:
```bash
python manage.py makemigrations
python manage.py migrate --plan
```

Do NOT run `migrate` automatically — let the user review the plan first.

---

### Step 7 — Pipeline Summary

Output the final report:

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
