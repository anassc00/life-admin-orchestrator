# life-admin-orchestrator

Personal ERP powered by AI agents, built with Clean Architecture for maximum modularity and data control.

## Architecture

```
[domain/]  ←  [application/]  ←  [adapters/]  ←  [infrastructure/]
Pure Python    Use Cases          Django Ninja      Django ORM
Pydantic       DTOs               Controllers       Celery Tasks
No imports     Agent Graphs       Schemas           Repositories
               (LangGraph)                          DI Container
```

**Dependency rule:** dependencies point inward only. `infrastructure/` knows about `domain/`; `domain/` knows nothing about `infrastructure/`.

## Agents

| Agent | Trigger | Primary Use Cases |
|---|---|---|
| `FinanceAgent` | Document upload / scheduled | CreateInvoice, ProcessInvoice, CategorizeExpense, GenerateMonthlyReport |
| `CalendarAgent` | Event detection / LLM prompt | ScheduleAppointment, DetectConflict, SendReminder |
| `DocumentAgent` | File system event | RegisterDocument, ClassifyDocument, ExtractMetadata, ArchiveDocument |
| `ContactAgent` | Inbound communication | UpdateContactRecord, LogInteraction |

## Stack

- **Django 5.x** — ORM, admin panel, auth (infrastructure only)
- **Django Ninja 1.x** — API layer with native Pydantic v2
- **LangGraph 0.x** — Stateful agent graph execution
- **Pydantic v2** — Domain entities and DTOs
- **Celery 5.x + Redis** — Async task queue for agent dispatch
- **PostgreSQL 16** — Persistence (JSONB for agent state, ArrayField for tags/attendees)

## Quick start

```bash
# 1. Copy environment file
cp .env.example .env
# Edit .env with your credentials

# 2. Start infrastructure services
docker compose up db redis -d

# 3. Install dependencies
pip install -e ".[dev]"

# 4. Run migrations
python manage.py migrate

# 5. Create superuser
python manage.py createsuperuser

# 6. Start the API
python manage.py runserver

# 7. Start Celery worker (separate terminal)
celery -A config worker --loglevel=info
```

API docs available at `http://localhost:8000/api/docs`.

## Running tests

```bash
# Unit tests (no database required)
USE_SQLITE=true pytest tests/unit/ -v

# All tests (requires PostgreSQL)
pytest -v
```

## Project structure

```
life-admin-orchestrator/
├── domain/                # Entities, repository interfaces, exceptions
├── application/           # Use cases, DTOs, LangGraph agent orchestrators
├── adapters/api/          # Django Ninja schemas + thin HTTP controllers
├── infrastructure/
│   ├── django_app/        # Django ORM models, admin, migrations
│   ├── repositories/      # Concrete repository implementations
│   ├── tasks/             # Celery tasks (agent dispatch)
│   └── di.py              # Dependency injection wiring
├── config/                # Django settings, urls, wsgi, celery
└── tests/
    ├── fakes/             # In-memory repositories for unit testing
    ├── unit/              # Domain and use case tests (no DB)
    └── integration/       # Django ORM integration tests
```
