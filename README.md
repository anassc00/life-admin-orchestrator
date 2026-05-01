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

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) — `pip install uv`
- Docker (only for the local DB option)

---

### Option A — Neon (cloud PostgreSQL, recommended)

```bash
# 1. Clone and enter the project
git clone <repo-url>
cd life-admin-orchestrator

# 2. Copy the environment template and fill in your Neon credentials
cp .env.example .env
# Set DATABASE_URL=postgresql://<user>:<password>@<host>/<db>?sslmode=require

# 3. Install all dependencies (including dev tools)
uv sync --extra dev

# 4. Apply migrations
uv run python manage.py migrate

# 5. Start the API
uv run python manage.py runserver
```

---

### Option B — Local Docker (PostgreSQL + Redis)

```bash
# 1. Clone and enter the project
git clone <repo-url>
cd life-admin-orchestrator

# 2. Start database and Redis
docker compose up db redis -d

# 3. Copy the environment template
cp .env.example .env
# Leave DATABASE_URL commented out; the individual DB_* defaults point to localhost

# 4. Install all dependencies
uv sync --extra dev

# 5. Apply migrations
uv run python manage.py migrate

# 6. Start the API
uv run python manage.py runserver

# 7. (Optional) Start Celery worker — required for agent tasks
uv run celery -A config worker --loglevel=info
```

---

Once running, open:

| URL | Description |
|---|---|
| `http://localhost:8000/` | Home — register or log in |
| `http://localhost:8000/api/docs` | Interactive API docs (Swagger UI) |
| `http://localhost:8000/admin/` | Django admin panel |

## Running tests

Unit tests run with **no database** — domain and application logic is tested with in-memory fakes.

```bash
# Unit tests only (fast, no DB required)
uv run pytest tests/unit/ -v

# Full suite
uv run pytest tests/ -v
```

## API endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/auth/register` | Create a new admin user |
| `POST` | `/api/auth/login` | Authenticate and return user info |
| `POST` | `/api/finance/invoices` | Create invoice |
| `POST` | `/api/finance/invoices/{id}/process` | Mark invoice as paid |
| `POST` | `/api/calendar/appointments` | Schedule appointment |
| `POST` | `/api/documents/` | Register document |
| `POST` | `/api/contacts/` | Create contact |

## Project structure

```
life-admin-orchestrator/
├── domain/                # Entities, repository interfaces, exceptions
│   ├── entities/          # User, Invoice, Appointment, Document, Contact
│   ├── repositories/      # Abstract ports (UserRepository, PasswordHasher, …)
│   └── exceptions/        # Typed domain exceptions
├── application/
│   ├── use_cases/         # RegisterUser, AuthenticateUser, ProcessInvoice, …
│   ├── dtos/              # Command / Response DTOs per module
│   └── agents/            # LangGraph orchestrators (Finance, Calendar, …)
├── adapters/api/          # Django Ninja schemas + thin HTTP controllers
├── infrastructure/
│   ├── django_app/
│   │   ├── models/        # Django ORM models (UserModel, InvoiceModel, …)
│   │   ├── migrations/    # Auto-generated Django migrations
│   │   ├── templates/     # home.html (register + login frontend)
│   │   └── views.py       # Template-based view (serves home.html at /)
│   ├── repositories/      # Concrete ORM + hasher implementations
│   ├── tasks/             # Celery tasks (agent dispatch)
│   └── di.py              # Dependency injection wiring
├── config/                # Django settings (base / dev / prod), urls, celery
└── tests/
    ├── fakes/             # In-memory repositories for unit testing
    ├── unit/              # Domain and use case tests (no DB)
    └── integration/       # Django ORM integration tests
```
