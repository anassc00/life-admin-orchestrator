# Arquitectura del Proyecto

## Clean Architecture (Arquitectura Limpia)

Las dependencias apuntan solo hacia adentro: `infrastructure/` → `domain/`, `domain/` no conoce nada externo.

### Capa de Dominio (`domain/`)

Entidades Pydantic inmutables (`frozen=True`), interfaces de repositorios abstractas (puertos), excepciones específicas.

**Entidades principales:**
- `finance.py`: Account, Transaction, Invoice, Expense, SavingsGoal, BudgetPlan, MonthlyFinancialSummary
- `calendar.py`: Appointment
- `document.py`: Document
- `contact.py`: Contact, Interaction

**Repositorios abstractos:** Definidos en `domain/repositories/` (ej: `AccountRepository`, `TransactionRepository`)

### Capa de Aplicación (`application/`)

Casos de uso que encapsulan lógica de aplicación, DTOs con Pydantic, agentes LangGraph.

**Casos de uso (16 en finance, varios en otros módulos):**
- Finance: `register_income`, `register_expense`, `process_invoice`, `register_currency_exchange`, etc.
- Calendar: `schedule_appointment`, `detect_conflict`, `send_reminder`
- Document: `register_document`, `classify_document`
- Contact: `update_contact_record`, `log_interaction`

**Agentes LangGraph:**
- `finance_agent.py`: extract_data → validate_and_persist
- `calendar_agent.py`: parse_event → detect_conflict → schedule
- `document_agent.py`, `contact_agent.py`

### Capa de Adaptadores (`adapters/`)

API REST con Django Ninja. Views y schemas por módulo.

### Capa de Infraestructura (`infrastructure/`)

Implementaciones concretas: modelos Django ORM, repositorios Django, tareas Celery, contenedor DI.

**Inyección de Dependencias:** `infrastructure/di.py` (224 líneas) - factory functions que crean casos de uso con sus dependencias.

## Patrones de Diseño

- **Repository Pattern:** Interfaces abstractas → implementaciones Django
- **Dependency Injection:** DI container en `di.py`
- **Use Case Pattern:** Clases con método `execute()`
- **DTO Pattern:** Commands y Responses con Pydantic
- **Unit of Work:** Interfaz abstracta para transacciones
- **Entity Pattern:** Inmutable (Pydantic `frozen=True`)

## Base de Datos

- **Producción:** PostgreSQL 16 (soporta JSONB, ArrayField)
- **Desarrollo:** SQLite3 (con `USE_SQLITE=true`)
- Configuración vía `DATABASE_URL` o variables individuales

## Procesamiento Asíncrono

- **Celery + Redis:** Cola de tareas
- Tareas en `infrastructure/tasks/`
- Celery beat para tareas periódicas (recordatorios)
