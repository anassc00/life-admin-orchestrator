# life-admin-orchestrator - Documentación para OpenCode

## Resumen del Proyecto

Personal ERP impulsado por agentes de IA para gestión integral de vida administrativa personal.

**Tecnologías principales:** Python 3.12+, Django 5.x, Django Ninja, Pydantic v2, LangGraph, Celery, PostgreSQL

## Estructura de Capas (Clean Architecture)

```
domain/          → Lógica de negocio pura (entidades Pydantic, repositorios abstractos)
application/     → Casos de uso, DTOs, agentes LangGraph
adapters/        → API REST (Django Ninja)
infrastructure/  → Django ORM, tareas Celery, inyección de dependencias
config/          → Configuración Django, Celery, URLs
tests/           → Unitarios (sin BD) e integración
```

## Módulos Funcionales

- **Finance:** Cuentas multi-moneda, ingresos/gastos, facturas, intercambio de divisas, objetivos de ahorro, presupuestos
- **Calendar:** Citas, detección de conflictos, recordatorios, procesamiento en lenguaje natural
- **Documents:** Registro, clasificación automática con IA, extracción de metadatos
- **Contacts:** Gestión de contactos, registro de interacciones, etiquetado

## Comandos Rápidos

```bash
uv sync --extra dev                          # Instalar dependencias
uv run python manage.py migrate              # Migraciones BD
uv run python manage.py runserver            # Servidor desarrollo
uv run pytest tests/unit/ -v                 # Tests unitarios
uv run pytest tests/ -v --cov                # Tests con cobertura
uv run celery -A config worker --loglevel=info  # Worker Celery
```

## URLs

- `http://localhost:8000/` → Landing/registro
- `http://localhost:8000/api/docs` → Swagger UI
- `http://localhost:8000/admin/` → Admin Django

## Documentación Adicional

- [Arquitectura detallada](./architecture.md)
- [Workflow de desarrollo](./workflow.md)
- [Convenciones de código](./conventions.md)
