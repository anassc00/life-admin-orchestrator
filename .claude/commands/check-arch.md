---
command: /check-arch
description: >
  Architecture sentinel for Clean Architecture compliance in clean-personal-erp. Triggers automatically
  when: creating a new feature, module, folder, or file inside src/; proposing a new use case, entity,
  repository port, or adapter; detecting an import that crosses architectural layers (e.g., Domain
  importing from Infrastructure); or when the user asks about module structure, layer dependencies,
  or naming conventions. Validates against the Clean Architecture rules defined in
  docs/technical_report.md §2 and §3.
---

# architect-sentinel

Guardian of Clean Architecture compliance for `clean-personal-erp`. Validates every new module,
file, or import against the dependency rule and layered responsibilities defined in
`docs/technical_report.md`.

## Auto-Trigger Conditions

Activate this skill automatically when:
- The user creates or proposes a new feature, module, or folder inside `src/`
- The user proposes creating a new use case, entity, repository port, or adapter class
- An import is detected (or proposed) that may cross architectural layers
- The user asks about where to place a class, how to structure a module, or which layer something belongs to

## Process

### Phase 1 — Module Classification

Before any file is created, classify the module against the agent catalog in `docs/technical_report.md §5.3`.

Core modules and their layer coverage:

| Module | Domain | Application | Adapters | Infrastructure |
|--------|--------|-------------|----------|---------------|
| `finance` | ✓ | ✓ | ✓ | ✓ |
| `calendar` | ✓ | ✓ | ✓ | ✓ |
| `document` | ✓ | ✓ | ✓ | ✓ |
| `contact` | ✓ | ✓ | ✓ | ✓ |

All core agent modules are **Full-level**: they span all four layers. Cross-cutting concerns
(auth, config, logging) are **Light-level**: they live only in `infrastructure/` with no
domain or application representation.

Output the classification result clearly:
```
Module: <name>
Assigned level: Full | Light
Reason: <brief justification referencing §5.3 or cross-cutting concern>
```

---

### Phase 2 — Structure Validation

Based on the assigned level, enforce the folder rules from `docs/technical_report.md §3`:

#### Full Level
```
src/
├── domain/{module}/
│   ├── __init__.py
│   ├── entities.py
│   ├── ports.py
│   └── exceptions.py
├── application/{module}/
│   ├── __init__.py
│   ├── use_cases.py
│   └── dtos.py
├── adapters/{module}/
│   ├── __init__.py
│   ├── controllers.py    # Django Ninja Router
│   └── schemas.py        # Django Ninja request/response schemas
└── infrastructure/{module}/
    ├── __init__.py
    ├── models.py          # Django ORM models
    └── repositories.py    # Concrete InvoiceRepository implementation
```

#### Light Level (cross-cutting concerns)
```
src/
└── infrastructure/{concern}/
    ├── __init__.py
    └── {concern}.py
```
**Rule**: Light modules MUST NOT have a `domain/{concern}/` or `application/{concern}/` folder.

---

### Phase 3 — Naming Convention Check

Verify that all proposed or created files and classes follow the conventions from
`docs/technical_report.md §3`:

**Files:**
| Artifact | Expected filename |
|---|---|
| Domain entities | `entities.py` |
| Domain repository port (interface) | `ports.py` |
| Domain exceptions | `exceptions.py` |
| Use case | `use_cases.py` |
| Application DTO | `dtos.py` |
| Django Ninja schemas | `schemas.py` |
| Django Ninja controller | `controllers.py` |
| LLM output parser | `parsers.py` |
| Django ORM model | `models.py` |
| Repository implementation | `repositories.py` |
| Celery tasks | `tasks.py` |
| External API connector | `connectors.py` |

**Classes:**
| Artifact | Pattern | Example |
|---|---|---|
| Domain entity | `{Concept}` | `Invoice`, `Appointment`, `Contact` |
| Repository port (ABC) | `{Concept}Repository` | `InvoiceRepository` |
| Domain exception | `{Concept}{Reason}Error` | `InvoiceDueDateExceededError` |
| Use case | `{Verb}{Concept}UseCase` | `ProcessInvoiceUseCase`, `ScheduleAppointmentUseCase` |
| Agent orchestrator | `{Module}AgentOrchestrator` | `FinanceAgentOrchestrator` |
| Django Ninja schema | `{Concept}Request` / `{Concept}Response` | `ProcessInvoiceRequest` |
| Django ORM model | `{Concept}Model` | `InvoiceModel`, `AppointmentModel` |
| Repository implementation | `Django{Concept}Repository` | `DjangoInvoiceRepository` |
| External API connector | `{Provider}{Concept}Connector` | `GoogleCalendarConnector` |

Flag any deviation and suggest the correct name.

---

### Phase 4 — Dependency Rule Check (§2.2)

Before any import is written, verify it complies with the **Dependency Rule** from §2.2:

```
domain/ ← application/ ← adapters/ ← infrastructure/
```

**Allowed:**
- `infrastructure/` can import from any layer
- `adapters/` can import from `application/` and `domain/`
- `application/` can import from `domain/` only
- `application/` may import `langgraph` (acknowledged exception — see §2.3 in report)
- `domain/` has zero external imports — no `django`, no `celery`, no `langgraph`, no external API SDKs
- `domain/` stdlib imports allowed: `abc`, `typing`, `datetime`, `uuid`, `decimal` — Pydantic v2 allowed

**Forbidden (flag immediately):**
- `domain/` importing from `application/`, `adapters/`, or `infrastructure/`
- `domain/` importing `django`, `celery`, `langgraph`, `requests`, or any third-party framework
- `application/` importing from `adapters/` or `infrastructure/`
- `adapters/` importing concrete repository classes from `infrastructure/` (only via DI container)
- `tests/unit/` importing any class from `infrastructure/`

When a violation is detected, output:
```
⚠ DEPENDENCY RULE VIOLATION (technical_report.md §2.2)
File: <file>
Illegal import: <import path>
Layer: <offending layer> → <target layer> is not allowed
Fix: Move the dependency to a Port ABC in domain/ or application/
```

---

### Phase 5 — Module Catalog Validation (§5.3)

Consult the Agent Catalog table in `docs/technical_report.md §5.3`.

If the module being created is in the catalog:
- Confirm its structure matches the Full-level layout (all 4 layers)
- If there is a mismatch, block the action and report:

```
⚠ MODULE STRUCTURE MISMATCH (technical_report.md §5.3)
Module: <name>
Expected level: Full (all 4 layers)
Proposed structure: <what is being created>
Action: Add the missing layer folders before proceeding.
```

---

### Phase 6 — Feedback Report

After running all phases, emit a structured compliance report before any code is written or edited:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ARCHITECT-SENTINEL REPORT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Module       : <name>
Level        : Full | Light
Structure    : ✓ Valid | ✗ <issue>
Naming       : ✓ Valid | ✗ <issue>
Dependencies : ✓ Valid | ✗ <issue>
Catalog      : ✓ Valid | ✗ <issue>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Reference    : technical_report.md §<section>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

If **any check fails**, do NOT proceed with code generation. Explain the violation with the exact section of `docs/technical_report.md` that applies, and suggest the corrective action.

If **all checks pass**, confirm clearance and proceed with implementation.
