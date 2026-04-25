# Technical Report: clean-personal-erp

**Version:** 1.0  
**Status:** Approved for Implementation  
**Author:** AI Solutions Architecture  
**Date:** 2026-04-25

---

## 1. Executive Summary

`clean-personal-erp` is a personal administrative system whose core design principle is the strict inversion of dependencies between business logic and infrastructure concerns. The system is driven by AI agents that automate domain workflows — financial tracking, appointment scheduling, document processing — while remaining entirely agnostic to the specific persistence or delivery mechanisms in use.

The architecture enforces a single non-negotiable constraint: **no domain or application-layer code shall import, reference, or depend on Django, LangGraph, PostgreSQL, or any other infrastructure component directly.** All such dependencies flow inward via abstract interfaces defined at the domain boundary.

Django is adopted as an operational convenience for its mature ORM, admin panel, and authentication subsystem. It is treated as a replaceable plug-in, not a foundational dependency. This distinction is not cosmetic — it has direct implications for testability, maintainability, and the long-term ability to swap infrastructure components without touching business logic.

The net outcome is a system where the personal domain model (bills, events, documents, contacts) is expressed purely in Python and Pydantic, while Django, Celery, LangGraph, and external API connectors are implementation details confined to the outermost layers of the architecture.

---

## 2. Decoupled Architecture (The Clean Approach to Django)

### 2.1 The Core Argument: Django as a Plug-in

Robert C. Martin's Clean Architecture establishes that frameworks are details. A framework should serve the application; the application must not serve the framework. In practice, Django projects frequently invert this relationship: domain logic ends up embedded in `models.py`, business rules are expressed as ORM queries, and `settings.py` becomes a load-bearing structural dependency.

This project rejects that pattern entirely.

Django is introduced at the `infrastructure/` boundary exclusively. Its role is confined to:

- **Persistence** — ORM models as database-mapped representations of domain entities.
- **Administration** — The Django admin panel as a rapid operational interface.
- **Authentication** — User session management via `django.contrib.auth`.
- **HTTP routing** — URL dispatch, delegated immediately to Django Ninja controllers.

Nothing above the `infrastructure/` layer is permitted to reference `django.*` namespaces. Violations of this boundary are treated as architectural defects, not style preferences.

### 2.2 The Dependency Rule in Practice

```
[domain/]  <──  [application/]  <──  [adapters/]  <──  [infrastructure/]
   ↑                  ↑                   ↑                     ↑
Pure Python       Uses Domain          Translates            Django, LangGraph,
Pydantic          Interfaces           DTOs ↔ Domain         Celery, PostgreSQL
No imports        No Django            Entities              External APIs
```

Dependencies point inward only. `infrastructure/` knows about `domain/`; `domain/` knows nothing about `infrastructure/`.

### 2.3 The DTO Bridge

Communication across layer boundaries is mediated exclusively by **Data Transfer Objects (DTOs)**. DTOs are plain Pydantic models with no behavior — they carry structured data between layers without exposing internal representations.

Three categories of DTOs exist in this system:

| Category | Direction | Description |
|---|---|---|
| `CommandDTO` | Inbound to Application | Carries intent from an adapter to a use case (e.g., `ProcessInvoiceCommand`) |
| `QueryDTO` | Inbound to Application | Carries query parameters to a use case (e.g., `GetExpensesByPeriodQuery`) |
| `ResponseDTO` | Outbound from Application | Carries results from a use case back to the adapter (e.g., `InvoiceProcessedResponse`) |

A Django ORM model instance is **never** passed across a layer boundary. The infrastructure repository implementation maps ORM records to domain entities before returning them to the application layer. The application layer maps domain entities to ResponseDTOs before returning them to adapters.

---

## 3. Layered Responsibility Analysis

### 3.1 `domain/` — The Invariant Core

This layer contains the sole source of truth for what the system **is**, independent of what it **does** or **uses**.

**Contents:**

- **Entities** — Pydantic v2 `BaseModel` subclasses representing core business objects.

  ```python
  # domain/entities/finance.py
  from pydantic import BaseModel, Field
  from decimal import Decimal
  from datetime import date
  from uuid import UUID

  class Invoice(BaseModel):
      id: UUID
      vendor: str
      amount: Decimal
      currency: str = "MXN"
      due_date: date
      is_paid: bool = False

      def mark_as_paid(self) -> "Invoice":
          return self.model_copy(update={"is_paid": True})
  ```

- **Repository Interfaces** — Abstract Base Classes defining persistence contracts. No SQL, no ORM, no Django.

  ```python
  # domain/repositories/finance.py
  from abc import ABC, abstractmethod
  from uuid import UUID
  from domain.entities.finance import Invoice

  class InvoiceRepository(ABC):

      @abstractmethod
      def get_by_id(self, invoice_id: UUID) -> Invoice | None: ...

      @abstractmethod
      def save(self, invoice: Invoice) -> None: ...

      @abstractmethod
      def list_unpaid(self) -> list[Invoice]: ...
  ```

- **Domain Exceptions** — Typed exceptions expressing business rule violations (`InvoiceDueDateExceededError`, `DuplicateEventError`).

- **Domain Services** — Stateless functions operating exclusively on domain entities for logic that does not belong to a single entity.

**Hard constraint:** Zero imports from `django`, `langgraph`, `celery`, `sqlalchemy`, or any external library except `pydantic` and the Python standard library.

---

### 3.2 `application/` — Use Cases and Agent Orchestration

This layer expresses what the system **does**. It orchestrates domain objects to fulfill specific user or agent intents.

**Contents:**

- **Use Cases** — Each use case is a single Python class with an `execute` method. It accepts a CommandDTO, operates on domain entities via repository interfaces, and returns a ResponseDTO.

  ```python
  # application/use_cases/finance/process_invoice.py
  from domain.repositories.finance import InvoiceRepository
  from application.dtos.finance import ProcessInvoiceCommand, InvoiceProcessedResponse

  class ProcessInvoiceUseCase:

      def __init__(self, invoice_repo: InvoiceRepository) -> None:
          self._repo = invoice_repo

      def execute(self, command: ProcessInvoiceCommand) -> InvoiceProcessedResponse:
          invoice = self._repo.get_by_id(command.invoice_id)
          if invoice is None:
              raise InvoiceNotFoundError(command.invoice_id)
          paid_invoice = invoice.mark_as_paid()
          self._repo.save(paid_invoice)
          return InvoiceProcessedResponse(invoice_id=paid_invoice.id, status="paid")
  ```

- **Agent Orchestration Services** — High-level services that construct and invoke LangGraph graphs. These services depend on the `langgraph` library, making this the only application-layer exception to the "no framework imports" rule. This is an acknowledged trade-off: LangGraph is treated as an orchestration primitive, not a business dependency.

  ```python
  # application/agents/finance_agent.py
  from langgraph.graph import StateGraph
  from application.use_cases.finance.process_invoice import ProcessInvoiceUseCase

  class FinanceAgentOrchestrator:
      def __init__(self, process_invoice_uc: ProcessInvoiceUseCase) -> None:
          self._graph = self._build_graph(process_invoice_uc)

      def _build_graph(self, uc: ProcessInvoiceUseCase) -> StateGraph:
          # Graph node definitions reference use cases, not Django or SQL
          ...
  ```

- **DTOs** — All `CommandDTO`, `QueryDTO`, and `ResponseDTO` definitions.

---

### 3.3 `adapters/` — Translation Layer

This layer is responsible for one task: translating between the external world's representation of data and the application's representation.

**Contents:**

- **Django Ninja Schemas** — Pydantic models that map HTTP request/response payloads to and from application DTOs.

  ```python
  # adapters/api/finance/schemas.py
  from ninja import Schema
  from uuid import UUID

  class ProcessInvoiceRequest(Schema):
      invoice_id: UUID

  class InvoiceProcessedResponseSchema(Schema):
      invoice_id: UUID
      status: str
  ```

- **Django Ninja Controllers** — Thin HTTP handlers. They deserialize the request into a CommandDTO, invoke the use case, serialize the ResponseDTO back to an HTTP response. No business logic lives here.

  ```python
  # adapters/api/finance/views.py
  from ninja import Router
  from adapters.api.finance.schemas import ProcessInvoiceRequest, InvoiceProcessedResponseSchema
  from infrastructure.di import get_process_invoice_use_case

  router = Router()

  @router.post("/invoices/process", response=InvoiceProcessedResponseSchema)
  def process_invoice(request, payload: ProcessInvoiceRequest):
      uc = get_process_invoice_use_case()
      return uc.execute(payload.to_command())
  ```

- **LLM Output Parsers** — Structured parsers (using Pydantic) that transform raw LLM completions into typed domain objects or DTOs for downstream use case invocation.

---

### 3.4 `infrastructure/` — External Dependencies

This is the only layer that is allowed to import Django, Celery, LangGraph clients, and third-party API SDKs.

**Contents:**

- **Django ORM Models** — Persistence-only representations. They carry no domain logic. A `models.py` invoice model is a schema mapping to the `invoices` table; nothing more.

  ```python
  # infrastructure/django_app/models.py
  from django.db import models
  import uuid

  class InvoiceModel(models.Model):
      id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
      vendor = models.CharField(max_length=255)
      amount = models.DecimalField(max_digits=12, decimal_places=2)
      currency = models.CharField(max_length=3, default="MXN")
      due_date = models.DateField()
      is_paid = models.BooleanField(default=False)

      class Meta:
          db_table = "invoices"
  ```

- **Repository Implementations** — Concrete implementations of the domain's repository interfaces using the Django ORM.

  ```python
  # infrastructure/repositories/finance.py
  from domain.repositories.finance import InvoiceRepository
  from domain.entities.finance import Invoice
  from infrastructure.django_app.models import InvoiceModel
  from uuid import UUID

  class DjangoInvoiceRepository(InvoiceRepository):

      def get_by_id(self, invoice_id: UUID) -> Invoice | None:
          try:
              record = InvoiceModel.objects.get(pk=invoice_id)
              return self._to_entity(record)
          except InvoiceModel.DoesNotExist:
              return None

      def save(self, invoice: Invoice) -> None:
          InvoiceModel.objects.update_or_create(
              pk=invoice.id,
              defaults=self._to_record(invoice),
          )

      def list_unpaid(self) -> list[Invoice]:
          return [
              self._to_entity(r)
              for r in InvoiceModel.objects.filter(is_paid=False)
          ]

      @staticmethod
      def _to_entity(record: InvoiceModel) -> Invoice:
          return Invoice(
              id=record.id,
              vendor=record.vendor,
              amount=record.amount,
              currency=record.currency,
              due_date=record.due_date,
              is_paid=record.is_paid,
          )

      @staticmethod
      def _to_record(invoice: Invoice) -> dict:
          return {
              "vendor": invoice.vendor,
              "amount": invoice.amount,
              "currency": invoice.currency,
              "due_date": invoice.due_date,
              "is_paid": invoice.is_paid,
          }
  ```

- **Celery Tasks** — Async wrappers that invoke application-layer use cases or agent orchestrators.
- **External API Connectors** — Clients for Google Calendar, banking APIs, document OCR services.
- **Dependency Injection Container** — A `di.py` module (or lightweight container) that wires concrete infrastructure implementations to abstract interfaces before injecting them into use cases.

---

## 4. Technology Stack & Infrastructure Drivers

| Component | Technology | Architectural Justification |
|---|---|---|
| **Framework Base** | Django 5.x | Provides a production-grade ORM, a functional admin panel for operational visibility, robust authentication/permissions, and a mature middleware ecosystem. Confined entirely to `infrastructure/`. |
| **API Layer** | Django Ninja 1.x | Native Pydantic v2 integration eliminates the schema duplication problem present in DRF. Request/response schemas are Pydantic models, directly compatible with the DTO layer. Async support aligns with agent invocation patterns. |
| **Agent Orchestration** | LangGraph 0.x | Provides stateful, cyclic graph execution for multi-step agent workflows. Its node/edge model maps cleanly to the use-case decomposition of the application layer. State is managed as typed Pydantic models, maintaining type consistency across the stack. |
| **Domain Entities** | Pydantic v2 | Immutable by default (with `model_config = ConfigDict(frozen=True)`), schema-validated, and serializable without ORM coupling. Serves as the universal data contract across all layer boundaries. |
| **Task Queue** | Celery 5.x + Redis | Decouples long-running agent executions from synchronous HTTP request cycles. Agent graph runs are dispatched as Celery tasks, preventing HTTP timeout violations and enabling retry logic for transient LLM or API failures. |
| **Database** | PostgreSQL 16 | JSONB support for semi-structured agent state snapshots. Mature full-text search for document retrieval use cases. Native UUID primary key support. |
| **Dependency Injection** | Manual wiring via `di.py` | Avoids framework-specific DI containers that would introduce additional infrastructure coupling. Repository implementations are instantiated and injected at the `infrastructure/` boundary. |
| **Testing** | pytest + pytest-django | Use cases are tested in complete isolation by injecting in-memory repository implementations (fakes) that satisfy the domain interface contracts. Django ORM is never exercised in unit tests. |

---

## 5. Personal Admin Agent Workflow (Orchestration Design)

### 5.1 Finance Agent — End-to-End Request Flow

The following describes the complete execution path for an agent-initiated invoice processing workflow, illustrating how each layer participates without violating dependency boundaries.

```
[Celery Task] ──► [FinanceAgentOrchestrator] ──► [LangGraph Graph Execution]
                                                          │
                              ┌───────────────────────────┤
                              ▼                           ▼
                    [Node: ExtractInvoiceData]   [Node: ValidateAndPersist]
                              │                           │
                    LLM call via tool use        ProcessInvoiceUseCase.execute()
                    Returns: InvoiceDTO                   │
                                               DjangoInvoiceRepository.save()
                                                          │
                                               PostgreSQL INSERT/UPDATE
```

**Step-by-step breakdown:**

1. **Trigger** — A Celery task in `infrastructure/tasks/finance.py` is dispatched (scheduled or event-driven). The task constructs the `FinanceAgentOrchestrator` with its dependencies wired by the DI module.

2. **Graph Initialization** — `FinanceAgentOrchestrator` initializes a LangGraph `StateGraph`. The graph state is a typed Pydantic model (`FinanceAgentState`) containing extracted data, intermediate results, and error context.

3. **LLM Extraction Node** — The first graph node invokes an LLM with a structured tool-use schema to extract invoice fields (vendor, amount, due date) from a raw document. The LLM output is parsed by an adapter-layer parser into an `ExtractedInvoiceDTO`.

4. **Validation Node** — The second node invokes `ProcessInvoiceUseCase.execute()` with a `ProcessInvoiceCommand` constructed from the `ExtractedInvoiceDTO`. The use case operates entirely on domain entities and the `InvoiceRepository` interface.

5. **Persistence** — `DjangoInvoiceRepository` (the concrete implementation injected at startup) maps the domain `Invoice` entity to an `InvoiceModel` and executes the ORM write. **The domain entity has no awareness of this step.** The repository implementation absorbs the entire ORM interaction.

6. **State Transition** — On success, the graph transitions to a terminal state. On failure (duplicate invoice, LLM parse error, DB constraint violation), the graph transitions to an error-handling node that logs the failure and can trigger a retry or human-review notification.

### 5.2 Agent Boundary Enforcement

The `FinanceAgentOrchestrator` does not access the database, does not import Django models, and does not contain business logic. It is a coordination mechanism only. Each node in the graph is a thin wrapper that delegates to a use case. This design ensures:

- **Testability** — The entire graph can be tested by providing mock use cases that return controlled ResponseDTOs.
- **Replaceability** — LangGraph can be replaced with a different orchestration framework (CrewAI, a custom state machine) without modifying any use case or domain code.
- **Auditability** — LangGraph's built-in state checkpointing (configurable with a `PostgresSaver`) provides a complete audit trail of agent execution without requiring custom logging infrastructure.

### 5.3 Agent Catalog (Initial Scope)

| Agent | Trigger | Primary Use Cases | External Dependencies |
|---|---|---|---|
| `FinanceAgent` | Scheduled / document upload | `ProcessInvoice`, `CategorizeExpense`, `GenerateMonthlyReport` | Banking API, OCR service |
| `CalendarAgent` | Event detection / LLM prompt | `ScheduleAppointment`, `DetectConflict`, `SendReminder` | Google Calendar API |
| `DocumentAgent` | File system event | `ClassifyDocument`, `ExtractMetadata`, `ArchiveDocument` | OCR service, S3-compatible storage |
| `ContactAgent` | Inbound communication event | `UpdateContactRecord`, `LogInteraction` | Email / messaging gateway |

---

## 6. Data Integrity & Persistence Strategy

### 6.1 Entity Identity and Persistence Mapping

Domain entities use `UUID` as their primary identifier. UUIDs are generated at the domain layer, not delegated to the database. This removes the coupling between entity creation and database insertion — an entity can exist as a valid, fully-identified domain object before it is ever persisted.

The `InvoiceModel.id` field in Django is a `UUIDField` with `editable=False`. The ORM never generates this value.

### 6.2 Immutability and State Transitions

Domain entities are declared as frozen Pydantic models (`ConfigDict(frozen=True)`). State transitions produce new entity instances via `model_copy(update={...})`, never mutating in place. This enforces an append-oriented mental model at the domain level and aligns naturally with event sourcing patterns if adopted in the future.

### 6.3 Repository Contract and Transactional Integrity

The `InvoiceRepository.save()` interface accepts a single entity. For multi-entity transactional operations (e.g., splitting an invoice into line items), a Unit of Work pattern is introduced as a separate domain interface:

```python
# domain/repositories/unit_of_work.py
from abc import ABC, abstractmethod
from contextlib import AbstractContextManager

class UnitOfWork(ABC, AbstractContextManager):

    @abstractmethod
    def commit(self) -> None: ...

    @abstractmethod
    def rollback(self) -> None: ...
```

The Django implementation wraps `transaction.atomic()`. The domain interface remains agnostic.

### 6.4 LangGraph State Persistence

For agent workflows requiring fault tolerance and resumability, LangGraph's `PostgresSaver` checkpointer is configured in `infrastructure/`. This stores graph state snapshots in PostgreSQL between node executions. In the event of a Celery worker failure mid-graph, the workflow can be resumed from the last committed checkpoint rather than restarted from scratch.

The checkpoint table is managed independently of the application's domain schema. Domain migrations and agent state migrations are versioned separately.

### 6.5 Migration Strategy

Django migrations are restricted to `infrastructure/django_app/models.py` changes. Domain model changes (Pydantic entities) do not automatically produce migrations — a deliberate design choice that enforces explicit database schema management. When a domain entity field changes, the corresponding ORM model and its migration must be updated intentionally and separately, ensuring that schema changes are always a conscious infrastructure decision rather than a side effect of domain evolution.
