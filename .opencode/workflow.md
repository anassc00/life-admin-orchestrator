# Workflow de Desarrollo

## Configuración Inicial

```bash
# Instalar dependencias (incluye dev)
uv sync --extra dev

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus valores

# Ejecutar migraciones
uv run python manage.py migrate

# Iniciar servidor
uv run python manage.py runserver
```

## Variables de Entorno Clave

- `SECRET_KEY`: Clave secreta Django
- `DEBUG`: True/False
- `DATABASE_URL`: URL PostgreSQL (o usar DB_NAME, DB_USER, etc.)
- `USE_SQLITE`: true para desarrollo con SQLite
- `REDIS_URL`: URL de Redis
- `ANTHROPIC_API_KEY`: API key para modelos Claude

## Testing

```bash
# Tests unitarios (rápidos, sin BD, usan fakes in-memory)
uv run pytest tests/unit/ -v

# Toda la suite (incluye integración)
uv run pytest tests/ -v

# Con cobertura
uv run pytest tests/ -v --cov

# Tests específicos
uv run pytest tests/unit/domain/test_finance_entities.py -v
uv run pytest tests/unit/application/finance/test_register_income.py -v
```

### Estrategia de Testing

- **Unitarios:** En `tests/unit/`, usan repositorios fake (`tests/fakes/repositories.py`)
- **Integración:** En `tests/integration/`, usan BD real
- **Fixtures:** Definidos en `tests/conftest.py`

## Calidad de Código

```bash
# Linting y formateo (Ruff)
uv run ruff check .
uv run ruff format .

# Type checking (MyPy)
uv run mypy .
```

### Configuración de Herramientas

- **Ruff:** Line length 100, Python 3.12, reglas E, F, I, N, UP
- **MyPy:** Modo estricto, plugin Django
- **Pytest:** `DJANGO_SETTINGS_MODULE = "config.settings.development"`

## Docker

```bash
# Iniciar servicios (PostgreSQL, Redis)
docker compose up db redis -d

# Iniciar web, worker, beat
docker compose up web worker beat

# Construir e iniciar todo
docker compose up --build
```

## Agentes de IA

Los agentes usan LangGraph con estados tipados (`TypedDict`). Para modificar un agente:

1. Editar grafo en `application/agents/<module>_agent.py`
2. Implementar/modificar casos de uso en `application/use_cases/<module>/`
3. Actualizar repositorio si es necesario en `infrastructure/repositories/`
4. Exponer vía API en `adapters/api/<module>/views.py`

## Agregar Nueva Funcionalidad

1. **Dominio:** Definir entidades en `domain/entities/`, repositorios abstractos en `domain/repositories/`
2. **Aplicación:** Crear caso de uso en `application/use_cases/`, DTOs en `application/dtos/`
3. **Infraestructura:** Implementar repositorio en `infrastructure/repositories/`, modelo Django en `infrastructure/django_app/models/`
4. **Adaptadores:** Crear endpoint en `adapters/api/` con view y schema
5. **DI:** Registrar dependencias en `infrastructure/di.py`
6. **Tests:** Agregar tests unitarios en `tests/unit/`
