---
name: check-arch
description: Architecture sentinel for Clean Architecture compliance. Validates module structure, naming conventions, and dependency rules against the project's established patterns.
---

# check-arch

Architecture sentinel for Clean Architecture compliance. Validates module structure, naming conventions, and dependency rules against the project's established patterns.

## Trigger

Activate this skill automatically when:
- Creating a new feature, module, folder, or file
- Proposing a new use case, entity, repository port, or adapter
- Detecting an import that may cross architectural layers
- The user asks about module structure, layer dependencies, or naming conventions
- The user invokes this skill manually

## Process

### Phase1 — Module Classification

Classify the module:

| Module | Domain | Application | Adapters | Infrastructure |
|--------|--------|-------------|----------|---------------|
| `finance` | ✓ | ✓ | ✓ | ✓ |
| `calendar` | ✓ | ✓ | ✓ | ✓ |
| `document` | ✓ | ✓ | ✓ | ✓ |
| `contact` | ✓ | ✓ | ✓ | ✓ |

All core modules are **Full-level** (all 4 layers). Cross-cutting concerns are **Light-level** (infrastructure only).

```
Module: <name>
Assigned level: Full | Light
```

### Phase2 — Structure Validation

#### Full Level (all 4 layers)
```
domain/{module}/
├── entities/
├── repositories/
└── exceptions/
application/{module}/
├── use_cases/
├── dtos/
└── agents/
adapters/api/{module}/
├── views.py
└── schemas.py
infrastructure/
├── repositories/
├── django_app/models/
└── tasks/
```

#### Light Level (infrastructure only)
```
infrastructure/{concern}/
└── {concern}.py
```

**Rule**: Light modules MUST NOT have `domain/{concern}/` or `application/{concern}/`.

### Phase3 — Naming Convention Check

**Files:**
| Artifact | Expected filename |
|---|---|
| Domain entities | `domain/entities/{module}.py` |
| Domain repositories (ports) | `domain/repositories/{module}.py` |
| Domain exceptions | `domain/exceptions/{module}.py` |
| Use cases | `application/use_cases/{module}/*.py` |
| Application DTOs | `application/dtos/{module}.py` |
| Django Ninja schemas | `adapters/api/{module}/schemas.py` |
| Django Ninja views | `adapters/api/{module}/views.py` |
| Django ORM models | `infrastructure/django_app/models/{module}.py` |
| Repository implementations | `infrastructure/repositories/{module}.py` |
| Celery tasks | `infrastructure/tasks/{module}.py` |

**Classes:**
| Artifact | Pattern | Example |
|---|---|---|
| Domain entity | `{Concept}` | `Account`, `Invoice`, `Appointment` |
| Repository port (ABC) | `{Concept}Repository` | `AccountRepository` |
| Domain exception | `{Concept}{Reason}Error` | `InvoiceNotFoundError` |
| Use case | `{Verb}{Concept}UseCase` | `RegisterIncomeUseCase` |
| Agent orchestrator | `{Module}Agent` | `FinanceAgent` |
| Django Ninja schema | `{Concept}Request/Response` | `ProcessInvoiceRequest` |
| Django ORM model | `{Concept}Model` | `InvoiceModel` |
| Repository implementation | `Django{Concept}Repository` | `DjangoInvoiceRepository` |

Flag deviations and suggest correct name.

### Phase4 — Dependency Rule Check

Verify the **Dependency Rule**:
```
domain/ ← application/ ← adapters/ ← infrastructure/
```

**Allowed:**
- `infrastructure/` can import from any layer
- `adapters/` can import from `application/` and `domain/`
- `application/` can import from `domain/` only (plus `langgraph` for agents)
- `domain/` has zero external imports (no django, celery, langgraph)

**Forbidden (flag immediately):**
- `domain/` importing from outer layers
- `domain/` importing `django`, `celery`, `langgraph`
- `application/` importing from `adapters/` or `infrastructure/`
- `adapters/` importing concrete infrastructure classes (use DI)

When violation detected:
```
⚠ DEPENDENCY RULE VIOLATION
File: <file>
Illegal import: <import path>
Layer: <offending> → <target> not allowed
Fix: Move dependency to Port ABC in domain/ or application/
```

### Phase5 — Feedback Report

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ARCHITECT-SENTINEL REPORT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Module       : <name>
Level        : Full | Light
Structure    : ✓ Valid | ✗ <issue>
Naming       : ✓ Valid | ✗ <issue>
Dependencies : ✓ Valid | ✗ <issue>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

If **any check fails**, do NOT proceed with code generation. Explain violation and suggest corrective action.

If **all checks pass**, confirm clearance.
