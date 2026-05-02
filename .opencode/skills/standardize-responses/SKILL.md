---
name: standardize-responses
description: Standardize all HTTP responses and error handling in the Django Ninja API using Pydantic schemas and global exception handlers. Creates unified JSON payload format.
---

# standardize-responses

Standardize all HTTP responses and error handling in the Django Ninja API. Creates a unified JSON payload format for both success (2xx) and error (4xx/5xx) responses using Pydantic schemas and Django Ninja exception handlers.

## Trigger

Activate this skill when:
- The user asks to format errors, standardize HTTP responses, handle global exceptions, or structure JSON payloads
- A new feature completes and standard response formatting is needed
- The user invokes this skill manually

## Process

### Step1 — Create Pydantic Response Schemas (`adapters/api/shared/schemas.py`)

Create standardized response schemas using Django Ninja's `Schema`:

**Success response shape:**
```json
{
  "status_code": 200,
  "message": "OK",
  "data": { ... }
}
```

**Error response shape:**
```json
{
  "status_code": 400,
  "error": "Bad Request",
  "message": ["field: value is not valid"],
  "timestamp": "2025-01-01T00:00:00Z",
  "path": "/api/finance/invoices/process"
}
```

```python
from ninja import Schema
from typing import Generic, TypeVar
from datetime import datetime, timezone

T = TypeVar("T")

class ApiSuccessResponse(Schema, Generic[T]):
    status_code: int
    message: str
    data: T

class ApiErrorResponse(Schema):
    status_code: int
    error: str
    message: list[str]
    timestamp: str
    path: str

    @classmethod
    def build(cls, status_code: int, error: str, messages: list[str], path: str) -> "ApiErrorResponse":
        return cls(
            status_code=status_code,
            error=error,
            message=messages,
            timestamp=datetime.now(timezone.utc).isoformat(),
            path=path,
        )
```

### Step2 — Create Global Exception Handlers (`adapters/api/shared/exception_handlers.py`)

Create Django Ninja exception handlers using `@api.exception_handler(ExceptionClass)`.

Map domain exceptions to HTTP status codes:

| Domain Exception | HTTP Status |
|---|---|
| `*NotFoundError` | 404 |
| `Duplicate*Error` | 409 |
| `*DueDateExceededError` | 422 |

Always log unhandled exceptions server-side and return generic error to client.

### Step3 — Register Handlers on NinjaAPI Instance

Locate the Django Ninja `NinjaAPI` instance in `config/urls.py` or `adapters/api/__init__.py`:

```python
from ninja import NinjaAPI
from adapters.api.shared.exception_handlers import register_exception_handlers

api = NinjaAPI(
    title="life-admin-orchestrator API",
    version="1.0.0",
    docs_url="/api/docs",
)
register_exception_handlers(api)
```

### Step4 — Apply ApiSuccessResponse to Controllers

For each Django Ninja controller in `adapters/api/*/views.py`:

```python
from ninja import Router
from adapters.api.shared.schemas import ApiSuccessResponse
from adapters.api.finance.schemas import ProcessInvoiceRequest, InvoiceProcessedResponse

router = Router()

@router.post("/invoices/process", response={200: ApiSuccessResponse[InvoiceProcessedResponse]})
def process_invoice(request, payload: ProcessInvoiceRequest):
    # ... use case execution
    return ApiSuccessResponse(status_code=200, message="OK", data=result)
```

### Step5 — Show Summary

Display:
- Files created/modified
- Example success response (JSON)
- Example error response (JSON)

## Validation

```bash
uv run mypy adapters/ config/
uv run ruff check adapters/ --fix
# Verify /api/docs still generates valid OpenAPI schemas
```
