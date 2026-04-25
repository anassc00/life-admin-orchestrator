---
command: /test-gen
description: >
  TDD test generator for clean-personal-erp Clean Architecture. Triggers automatically when the
  user requests a new feature, new functionality, business logic implementation, use case, or
  domain entity. Generates unit test files (test_*.py) BEFORE the implementation code, following
  TDD methodology. Respects the module's architecture level (Full or Light) as defined in
  docs/technical_report.md and enforces layer isolation and dependency rules in test code.
---

# tdd-tester

Generates unit test files (`test_*.py`) **before** implementation code, following a strict TDD
approach. Tests are tailored to the module's Clean Architecture level (Full or Light) as defined
in `docs/technical_report.md §3`.

## Auto-Trigger Conditions

Activate this skill automatically when:
- The user requests a "new feature", "new functionality", or "business logic"
- The user describes a use case, domain rule, or entity to implement
- The user invokes `/test-gen` manually

## Process

### Step 1 — Consult Architecture Reference

Read `docs/technical_report.md §3` to identify the target module and its layer structure.

All agent modules (`finance`, `calendar`, `document`, `contact`) are **Full-level**: they span
all four layers. Cross-cutting concerns are **Light-level**: infrastructure only.

Output:
```
Module: <name>
Architecture level: Full | Light
Source: technical_report.md §3
```

---

### Step 2 — Identify Target Layer

Based on the feature description, determine which layer the test belongs to:

| Feature type | Target layer | Test location |
|---|---|---|
| Domain invariants, entity validation, frozen model transitions, domain exceptions | **Domain** | `tests/unit/domain/{module}/` |
| Use case orchestration, repository port coordination, DTO transformation | **Application** | `tests/unit/application/{module}/` |
| Django Ninja schema validation, controller request mapping | **Adapters** | `tests/unit/adapters/{module}/` |

**Rule**: If the module is **Light**, there is no domain or application layer.
Tests go in `tests/unit/infrastructure/{module}/` and are treated as integration-boundary tests.

**Rule for application layer agent tests**: The `{Module}AgentOrchestrator` is tested by
mocking the use cases it invokes, NOT by mocking LangGraph internals.

---

### Step 3 — Determine File Path

Build the test file path following naming conventions from `technical_report.md §3`:

**Domain test:**
`tests/unit/domain/{module}/test_{module}_{artifact}.py`
Example: `tests/unit/domain/finance/test_finance_entities.py`

**Application use case test:**
`tests/unit/application/{module}/test_{module}_{verb}_{concept}_use_case.py`
Example: `tests/unit/application/finance/test_finance_process_invoice_use_case.py`

**Application agent orchestrator test:**
`tests/unit/application/{module}/test_{module}_agent.py`
Example: `tests/unit/application/finance/test_finance_agent.py`

Output the planned path before creating:
```
Test file: tests/unit/<layer>/<module>/test_<name>.py
```

---

### Step 4 — Generate Test with Proper Isolation

Create the test file using **pytest** with the following rules:

#### Mocking Strategy
- Mock all **repository Port interfaces** (ABCs) using `unittest.mock.MagicMock(spec=PortClass)`
- Never instantiate real infrastructure implementations (`DjangoInvoiceRepository`, `GoogleCalendarConnector`, etc.)
- Never use Django's test database or ORM in unit tests — that belongs in `tests/integration/`
- Inject mocked ports into use case constructors (constructor injection pattern)
- Use `spec=PortClass` when creating mocks to enforce interface contracts: `MagicMock(spec=InvoiceRepository)`

#### Golden Rule for Domain Tests
Domain layer tests must **NEVER** import:
- `django`, `celery`, `langgraph`, `requests`, or any third-party framework
- Anything from `src/adapters/` or `src/infrastructure/`

Domain tests should only import:
- The entity/exception/port being tested (from `src/domain/{module}/`)
- Python stdlib (`pytest`, `unittest.mock`)
- `pydantic` (for constructing test entities)

#### Golden Rule for Application Tests
Application layer tests must **NEVER** import:
- Concrete infrastructure implementations (`DjangoInvoiceRepository`, `GoogleCalendarConnector`)
- `django`, `celery`, or any infrastructure framework

Application tests may import:
- The use case or orchestrator being tested (from `src/application/{module}/`)
- Domain entities and repository port interfaces for mock spec (from `src/domain/{module}/`)
- `unittest.mock.MagicMock`, `pytest`

---

### Step 5 — Test Structure

Every generated test file must follow this structure:

```python
import pytest
from unittest.mock import MagicMock
from uuid import uuid4
from decimal import Decimal
from datetime import date

from src.domain.{module}.ports import {ConceptRepository}     # for mock spec
from src.domain.{module}.entities import {Concept}
from src.domain.{module}.exceptions import {ConceptError}
from src.application.{module}.use_cases import {VerbConceptUseCase}
from src.application.{module}.dtos import {VerbConceptCommand}, {ConceptResponse}


class Test{VerbConceptUseCase}:
    def setup_method(self):
        """Initialize mocks and SUT before each test."""
        self.mock_repo = MagicMock(spec={ConceptRepository})
        self.sut = {VerbConceptUseCase}({concept}_repo=self.mock_repo)

    # --- Happy Path ---

    def test_should_{expected_happy_path_behavior}(self):
        # Arrange
        existing_{concept} = {Concept}(
            id=uuid4(),
            # ... field values
        )
        self.mock_repo.get_by_id.return_value = existing_{concept}
        command = {VerbConceptCommand}(...)

        # Act
        result = self.sut.execute(command)

        # Assert
        assert result.{field} == {expected_value}
        self.mock_repo.save.assert_called_once()

    # --- Error Cases ---

    def test_should_raise_{error}_when_{condition}(self):
        # Arrange
        self.mock_repo.get_by_id.return_value = None
        command = {VerbConceptCommand}(...)

        # Act & Assert
        with pytest.raises({ConceptError}):
            self.sut.execute(command)
```

**Requirements:**
- Always include at least **1 happy path** test
- Always include at least **1 error case** raising a domain-specific typed exception
- Use `self.sut` (System Under Test) as the variable name for the class being tested
- Use **Arrange / Act / Assert** pattern with comments in every test
- Use `spec=PortClass` on every mock to catch interface violations at test time
- Use descriptive `test_should_*` method names that describe expected behavior
- Build domain entities directly with `{Concept}(...)` — never via Django ORM factories

---

### Step 6 — Compliance Report

After generating the test file, output a compliance summary:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TDD-TESTER REPORT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Module       : <name>
Level        : Full | Light
Layer        : Domain | Application | Adapters
Test file    : <path>
Happy paths  : <count>
Error cases  : <count>
Mocks        : <list of mocked repository port interfaces>
Domain purity: ✓ No infrastructure imports | ✗ <violation>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Next step    : Run `uv run pytest <path> -v` — it should FAIL (RED phase)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Remind the user: **"Tests are ready. Run them to confirm RED, then implement the code to make them pass."**
