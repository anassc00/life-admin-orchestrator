---
name: test-gen
description: TDD test generator for Clean Architecture. Generates unit test files BEFORE implementation code following TDD methodology. Respects module architecture level and enforces layer isolation.
---

# test-gen

TDD test generator for Clean Architecture. Generates unit test files **before** implementation code, following TDD methodology. Respects the module's architecture level (Full or Light) and enforces layer isolation.

## Trigger

Activate this skill automatically when:
- The user requests a "new feature", "new functionality", or "business logic"
- The user describes a use case, domain rule, or entity to implement
- The user invokes this skill manually

## Process

### Step1 — Identify Target Module and Layer

Determine which module and layer the test belongs to:

| Feature type | Target layer | Test location |
|---|---|---|
| Domain invariants, entity validation, frozen model transitions | **Domain** | `tests/unit/domain/{module}/` |
| Use case orchestration, repository coordination, DTO transformation | **Application** | `tests/unit/application/{module}/` |
| Django Ninja schema validation, controller request mapping | **Adapters** | `tests/unit/adapters/{module}/` |

### Step2 — Determine File Path

**Domain test:** `tests/unit/domain/{module}/test_{module}_{artifact}.py`
Example: `tests/unit/domain/finance/test_finance_entities.py`

**Application use case test:** `tests/unit/application/{module}/test_{verb}_{concept}_use_case.py`
Example: `tests/unit/application/finance/test_register_income_use_case.py`

**Application agent test:** `tests/unit/application/{module}/test_{module}_agent.py`

### Step3 — Generate Test with Proper Isolation

#### Mocking Strategy
- Mock all repository interfaces using `unittest.mock.MagicMock(spec=PortClass)`
- Never instantiate real infrastructure implementations
- Never use Django's test database in unit tests
- Use `spec=PortClass` to enforce interface contracts

#### Golden Rule for Domain Tests
Domain layer tests must **NEVER** import:
- `django`, `celery`, `langgraph`, or any third-party framework
- Anything from `adapters/` or `infrastructure/`

Domain tests should only import:
- The entity/exception/port being tested (from `domain/{module}/`)
- Python stdlib (`pytest`, `unittest.mock`)
- `pydantic`

#### Golden Rule for Application Tests
Application layer tests must **NEVER** import:
- Concrete infrastructure implementations
- `django`, `celery`, or infrastructure frameworks

### Step4 — Test Structure

```python
import pytest
from unittest.mock import MagicMock
from uuid import uuid4
from decimal import Decimal
from datetime import date

from domain.{module}.repositories import {Concept}Repository
from domain.{module}.entities import {Concept}
from domain.{module}.exceptions import {Concept}Error
from application.use_cases.{module}.{action} import {VerbConcept}UseCase
from application.dtos.{module} import {VerbConcept}Command, {Concept}Response


class Test{VerbConcept}UseCase:
    def setup_method(self):
        self.mock_repo = MagicMock(spec={Concept}Repository)
        self.sut = {VerbConcept}UseCase({concept}_repo=self.mock_repo)

    def test_should_{expected_behavior}(self):
        # Arrange
        existing = {Concept}(id=uuid4(), ...)
        self.mock_repo.get_by_id.return_value = existing
        command = {VerbConcept}Command(...)

        # Act
        result = self.sut.execute(command)

        # Assert
        assert result.{field} == {expected_value}
        self.mock_repo.save.assert_called_once()

    def test_should_raise_{error}_when_{condition}(self):
        # Arrange
        self.mock_repo.get_by_id.return_value = None
        command = {VerbConcept}Command(...)

        # Act & Assert
        with pytest.raises({Concept}Error):
            self.sut.execute(command)
```

### Step5 — Compliance Report

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TDD-TESTER REPORT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Module       : <name>
Layer        : Domain | Application | Adapters
Test file    : <path>
Happy paths  : <count>
Error cases  : <count>
Mocks        : <list>
Domain purity: ✓ No infrastructure imports | ✗ <violation>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Next step    : Run `uv run pytest <path> -v` — it should FAIL (RED phase)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Remind the user: **"Tests are ready. Run them to confirm RED, then implement the code to make them pass."**
