# Life Admin Orchestrator

ERP personal de finanzas construido con Clean Architecture en Django. Controla ingresos, gastos, ahorros, presupuestos y facturas en un solo lugar, con soporte multi-moneda (USD / USDT / VES / MXN).

---

## Stack

| Capa | Tecnología |
|------|-----------|
| API | Django 5.2 + Django Ninja (Pydantic v2) |
| Base de datos | PostgreSQL 16 |
| Cola de tareas | Celery 5 + Redis |
| Frontend | Django Templates + Vanilla JS (sin frameworks) |
| Tests | pytest + pytest-django |

---

## Arquitectura

Clean Architecture con 4 capas. Las dependencias apuntan siempre hacia adentro:

```
infrastructure/ → adapters/ → application/ → domain/
   ORM / DI        Ninja API     Use Cases    Entities + ABCs
```

```
life-admin-orchestrator/
├── domain/                  # Entidades Pydantic (frozen), ABCs de repos, excepciones
│   ├── entities/finance.py
│   ├── repositories/finance.py
│   └── exceptions/finance.py
├── application/
│   ├── use_cases/finance/   # Un archivo por use case (~30 use cases)
│   └── dtos/finance.py      # Commands / Response DTOs
├── adapters/api/finance/
│   ├── views.py             # ~50 endpoints Django Ninja
│   └── schemas.py           # Schemas de entrada/salida
├── infrastructure/
│   ├── django_app/
│   │   ├── models/finance.py     # Django ORM models
│   │   ├── migrations/           # Migraciones hand-written
│   │   ├── templates/            # HTML templates (12 páginas)
│   │   └── views.py              # Thin view functions (solo render)
│   ├── repositories/finance.py   # Implementaciones ORM
│   └── di.py                     # Inyección de dependencias (factory functions)
├── config/
│   ├── settings/development.py
│   └── urls.py
└── tests/
    ├── fakes/repositories.py     # In-memory fakes para unit tests
    └── unit/application/         # ~118 unit tests (sin DB)
```

---

## Cómo correr el proyecto

### Prerrequisitos

- Python 3.12+
- Docker (para PostgreSQL + Redis locales)

### 1. Instalar dependencias

```bash
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Iniciar servicios

```bash
docker compose up db redis -d
```

### 3. Aplicar migraciones

```bash
.venv/bin/python manage.py migrate
```

### 4. Correr el servidor

```bash
.venv/bin/python manage.py runserver
```

Abrir `http://localhost:8000/` — registrar un usuario y explorar el dashboard.

### 5. (Opcional) Worker Celery

```bash
.venv/bin/celery -A config worker --loglevel=info
```

---

## Tests

Los tests unitarios no necesitan base de datos — usan repositorios en memoria.

```bash
# Unit tests (rápidos, sin DB)
.venv/bin/pytest tests/unit/ -q

# Suite completa (necesita DB corriendo)
.venv/bin/pytest -q
```

---

## Páginas disponibles

| URL | Descripción |
|-----|-------------|
| `/` | Landing page |
| `/register/` | Registro de usuario |
| `/login/` | Inicio de sesión |
| `/dashboard/` | Dashboard principal con KPIs, gráficos y widgets |
| `/finance/accounts/` | Gestión de cuentas (crear, editar, eliminar) |
| `/finance/income/` | Registrar ingresos |
| `/finance/expenses/` | Registrar gastos con categorías |
| `/finance/exchange/` | Cambio de divisas entre cuentas |
| `/finance/transactions/` | Historial con filtros, edición y reversión |
| `/finance/savings/` | Metas de ahorro con proyecciones y aportes |
| `/finance/planning/` | Presupuesto mensual (plan vs real, regla 50/30/20) |
| `/finance/invoices/` | Facturas pendientes y pagadas |
| `/finance/reports/` | Reporte anual con gráfico de barras |
| `/finance/cashflow/` | Calendario de flujo de caja mensual |
| `/profile/` | Perfil de usuario |
| `/api/docs` | Swagger UI — documentación interactiva de la API |

---

## API — endpoints principales

### Autenticación (`/api/auth/`)

| Método | Ruta | Descripción |
|--------|------|-------------|
| `POST` | `/api/auth/register` | Registrar usuario |
| `POST` | `/api/auth/login` | Iniciar sesión |
| `POST` | `/api/auth/logout` | Cerrar sesión |
| `GET` | `/api/auth/me` | Perfil del usuario actual |
| `PATCH` | `/api/auth/me` | Actualizar perfil |
| `POST` | `/api/auth/me/change-password` | Cambiar contraseña |

### Cuentas (`/api/finance/accounts`)

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/api/finance/accounts` | Listar cuentas con saldo |
| `POST` | `/api/finance/accounts` | Crear cuenta |
| `PATCH` | `/api/finance/accounts/{id}` | Editar cuenta |
| `DELETE` | `/api/finance/accounts/{id}` | Eliminar cuenta |
| `GET` | `/api/finance/accounts/{id}/balance-history` | Historial de saldo mensual |

### Transacciones

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/api/finance/transactions` | Listar (filtros: año, mes, cuenta, tipo, categoría, montos) |
| `POST` | `/api/finance/income` | Registrar ingreso |
| `POST` | `/api/finance/expenses` | Registrar gasto |
| `POST` | `/api/finance/exchange` | Cambio de divisas |
| `PATCH` | `/api/finance/transactions/{id}` | Editar (requiere contraseña) |
| `DELETE` | `/api/finance/transactions/{id}` | Eliminar (requiere contraseña) |
| `POST` | `/api/finance/transactions/{id}/reverse` | Revertir (crea transacción compensatoria) |

### Presupuesto

| Método | Ruta | Descripción |
|--------|------|-------------|
| `POST` | `/api/finance/budget` | Crear plan mensual |
| `GET` | `/api/finance/budget` | Plan con comparación plan vs real |
| `POST` | `/api/finance/budget/{id}/items` | Agregar/actualizar ítem de categoría |
| `DELETE` | `/api/finance/budget/{id}/items/{cat_id}` | Eliminar ítem |
| `POST` | `/api/finance/budget/{id}/copy-from-previous` | Copiar mes anterior |
| `GET` | `/api/finance/budget/summary` | Resumen ejecutivo del mes |

### Ahorros

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/api/finance/savings/goals` | Listar metas |
| `POST` | `/api/finance/savings/goals` | Crear meta |
| `PUT` | `/api/finance/savings/goals/{id}` | Editar meta |
| `POST` | `/api/finance/savings/deposits` | Registrar aporte |
| `DELETE` | `/api/finance/savings/deposits/{id}` | Eliminar aporte |
| `GET` | `/api/finance/savings/projection` | Proyecciones por meta |
| `GET` | `/api/finance/savings/rate` | Tasa de ahorro histórica |
| `GET` | `/api/finance/savings/dashboard` | Resumen del widget de ahorros |

### Dashboard y Reportes

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/api/finance/net-worth` | Patrimonio neto por tipo de cuenta |
| `GET` | `/api/finance/trend` | Tendencia mensual (últimos N meses) |
| `GET` | `/api/finance/summary/current/extended` | Resumen del mes con tasa de ahorro y ejecución |
| `GET` | `/api/finance/expenses/breakdown` | Desglose de gastos por categoría |
| `GET` | `/api/finance/invoices/upcoming` | Facturas próximas a vencer |
| `GET` | `/api/finance/transactions/recent` | Últimas N transacciones |
| `GET` | `/api/finance/reports/annual` | Reporte anual por mes |
| `GET` | `/api/finance/cashflow/calendar` | Flujo de caja por día del mes |

---

## Patrones clave

- **Entidades:** Pydantic `frozen=True` — usar `model_copy(update={...})` para mutar
- **Repositorios:** ABC en `domain/`, implementación ORM en `infrastructure/repositories/`
- **DI:** funciones factory sin estado en `infrastructure/di.py` — `get_X_use_case()`
- **Auth:** sesión Django — `request.session.get("user_id")` devuelve UUID string
- **Migraciones:** hand-written en `infrastructure/django_app/migrations/`, app label `life_admin`
- **Fakes de test:** `tests/fakes/repositories.py` — deben implementar todos los métodos del ABC

---

## Variables de entorno

Copiar `.env.example` → `.env` y configurar:

```env
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:pass@localhost:5432/life_admin
REDIS_URL=redis://localhost:6379/0
DEBUG=True
```
