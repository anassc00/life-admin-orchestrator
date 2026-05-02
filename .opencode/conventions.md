# Convenciones de Código

## Estructura de Archivos

- **Entidades:** `domain/entities/<module>.py` - Pydantic models con `frozen=True`
- **Repositorios abstractos:** `domain/repositories/<module>.py` - Protocol classes
- **Casos de uso:** `application/use_cases/<module>/<action>.py` - Clases con método `execute()`
- **DTOs:** `application/dtos/<module>.py` - Pydantic models para Commands y Responses
- **Agentes:** `application/agents/<module>_agent.py` - Grafos LangGraph
- **Repositorios Django:** `infrastructure/repositories/<module>.py` - Implementaciones concretas
- **Modelos Django:** `infrastructure/django_app/models/<module>.py`
- **API Views:** `adapters/api/<module>/views.py`
- **API Schemas:** `adapters/api/<module>/schemas.py`

## Naming Conventions

- **Entidades:** PascalCase singular (Account, Transaction, Invoice)
- **Casos de uso:** snake_case describiendo acción (register_income, schedule_appointment)
- **Repositorios:** PascalCase + "Repository" (AccountRepository, TransactionRepository)
- **DTOs:** Command/Response suffix (RegisterIncomeCommand, RegisterIncomeResponse)
- **Tests:** `test_<what_is_being_tested>.py`

## Inmutabilidad

Las entidades del dominio son inmutables:
```python
class Account(BaseEntity):
    model_config = {"frozen": True}
```

Para "modificar" una entidad, se retorna una nueva instancia con `model_copy()`:
```python
def update_field(self, value):
    return self.model_copy(update={"field": value})
```

## Inyección de Dependencias

Usar el contenedor DI en `infrastructure/di.py`. Los casos de uso reciben dependencias por constructor:
```python
class RegisterIncomeUseCase:
    def __init__(self, account_repo: AccountRepository, tx_repo: TransactionRepository):
        self._account_repo = account_repo
        self._tx_repo = tx_repo
```

## Manejo de Errores

Usar excepciones específicas del dominio en `domain/exceptions/`:
```python
from domain.exceptions.finance import AccountNotFoundError, InsufficientFundsError
```

## Testing

- Usar repositorios fake de `tests/fakes/repositories.py` para tests unitarios
- No usar base de datos en tests unitarios
- Fixtures en `tests/conftest.py`
- Patrón AAA: Arrange, Act, Assert

## Imports

Seguir la regla de dependencias de Clean Architecture:
- `domain/` no importa nada de capas exteriores
- `application/` solo importa de `domain/`
- `adapters/` importa de `application/` y `domain/`
- `infrastructure/` importa de todas las capas anteriores

## Type Hints

Usar type hints en todo el código. MyPy está configurado en modo estricto.

## Linting

Ruff se ejecuta automáticamente. Configuración en `pyproject.toml`:
- Line length: 100
- Python 3.12
- Reglas: E, F, I, N, UP
