---
command: /standardize-responses
description: >
  Standardize all HTTP responses and error handling in the clean-personal-erp Django Ninja API.
  Creates a unified JSON payload format for both success (2xx) and error (4xx/5xx) responses using
  Pydantic schemas and Django Ninja exception handlers. Triggers automatically when the user asks to
  format errors, standardize HTTP responses, handle global exceptions, or structure JSON payloads
  in the Django Ninja layer. Also triggers when /new-feature completes and standard response
  formatting is needed.
---

# api-response-standardizer

Standardize all HTTP responses and error handling in the `clean-personal-erp` Django Ninja API.
Creates a unified JSON payload for success and error responses using Pydantic schemas and Django
Ninja's native exception handler registration. All schemas live in `src/adapters/shared/`.

## Trigger

Activate this skill when:
- The user asks to format errors, standardize HTTP responses, handle global exceptions, or structure JSON payloads in the Django Ninja API.
- The `/new-feature` command completes and standard response formatting is needed.
- The user invokes `/standardize-responses` manually.

## Input

No input required. The skill operates on the project at the current working directory.

Before starting, verify:
1. The project uses Django Ninja (check for `django-ninja` in `pyproject.toml`).
2. Read `src/infrastructure/django_app/` to locate the Django Ninja `NinjaAPI` instance (typically in `api.py` or `urls.py`).
3. Check if `src/adapters/shared/` already exists to avoid overwriting existing files.

## Process

### Step 1 — Create the Pydantic Response Schemas (`src/adapters/shared/schemas.py`)

Create standardized response schemas using Django Ninja's `Schema` (which is Pydantic v2 `BaseModel`):

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
# src/adapters/shared/schemas.py
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
    def build(
        cls,
        status_code: int,
        error: str,
        messages: list[str],
        path: str,
    ) -> "ApiErrorResponse":
        return cls(
            status_code=status_code,
            error=error,
            message=messages,
            timestamp=datetime.now(timezone.utc).isoformat(),
            path=path,
        )
```

### Step 2 — Create the Global Exception Handlers (`src/adapters/shared/exception_handlers.py`)

Create Django Ninja exception handlers using the `@api.exception_handler(ExceptionClass)` pattern.

**Handler categories:**

**1. Pydantic `ValidationError` (422):**
- Extract the list of validation error messages from `exc.errors()`
- Return a standardized `ApiErrorResponse` with the list in `message`

**2. Domain-specific exceptions:**
- Import domain exception classes from `src/domain/{module}/exceptions.py`
- Map each to an appropriate HTTP status code:

| Domain Exception | HTTP Status |
|---|---|
| `InvoiceNotFoundError` | 404 |
| `AppointmentNotFoundError` | 404 |
| `DocumentNotFoundError` | 404 |
| `ContactNotFoundError` | 404 |
| `DuplicateInvoiceError` | 409 |
| `DuplicateEventError` | 409 |
| `InvoiceDueDateExceededError` | 422 |
- Return a clean `ApiErrorResponse` without exposing internal details or stack traces

**3. Unhandled exceptions (500):**
- Log the full traceback server-side using Python's `logging` module
- Return a generic `ApiErrorResponse` with message `["Internal server error"]`
- Never expose stack traces or internal state to the client

```python
# src/adapters/shared/exception_handlers.py
import logging
from django.http import HttpRequest
from ninja import NinjaAPI
from pydantic import ValidationError

from src.adapters.shared.schemas import ApiErrorResponse
from src.domain.finance.exceptions import InvoiceNotFoundError, DuplicateInvoiceError
# ... import other domain exceptions

logger = logging.getLogger(__name__)


def register_exception_handlers(api: NinjaAPI) -> None:
    """Register all global exception handlers on the NinjaAPI instance."""

    @api.exception_handler(ValidationError)
    def handle_validation_error(request: HttpRequest, exc: ValidationError):
        messages = [f"{e['loc']}: {e['msg']}" for e in exc.errors()]
        return api.create_response(
            request,
            ApiErrorResponse.build(422, "Unprocessable Entity", messages, request.path),
            status=422,
        )

    @api.exception_handler(InvoiceNotFoundError)
    def handle_invoice_not_found(request: HttpRequest, exc: InvoiceNotFoundError):
        return api.create_response(
            request,
            ApiErrorResponse.build(404, "Not Found", [str(exc)], request.path),
            status=404,
        )

    @api.exception_handler(Exception)
    def handle_unhandled_exception(request: HttpRequest, exc: Exception):
        logger.exception("Unhandled exception at %s", request.path)
        return api.create_response(
            request,
            ApiErrorResponse.build(500, "Internal Server Error", ["Internal server error"], request.path),
            status=500,
        )
```

### Step 3 — Register Handlers on the NinjaAPI Instance

Locate the Django Ninja `NinjaAPI` instance (typically in `src/infrastructure/django_app/api.py` or `urls.py`). Apply the registration:

```python
# src/infrastructure/django_app/api.py
from ninja import NinjaAPI
from src.adapters.shared.exception_handlers import register_exception_handlers

api = NinjaAPI(
    title="clean-personal-erp API",
    version="1.0.0",
    docs_url="/docs",
)

register_exception_handlers(api)

# Register routers
from src.adapters.finance.controllers import router as finance_router
from src.adapters.calendar.controllers import router as calendar_router

api.add_router("/finance", finance_router)
api.add_router("/calendar", calendar_router)
```

### Step 4 — Apply `ApiSuccessResponse` to Existing Controllers

For each Django Ninja controller, add `response=ApiSuccessResponse[{ConceptResponse}]` to route decorators and wrap the use case result:

```python
# src/adapters/finance/controllers.py
from ninja import Router
from src.adapters.shared.schemas import ApiSuccessResponse
from src.adapters.finance.schemas import ProcessInvoiceRequest, InvoiceProcessedResponse
from src.infrastructure.di import get_process_invoice_use_case

router = Router()

@router.post(
    "/invoices/process",
    response={200: ApiSuccessResponse[InvoiceProcessedResponse]},
)
def process_invoice(request, payload: ProcessInvoiceRequest):
    uc = get_process_invoice_use_case()
    result = uc.execute(payload.to_command())
    return ApiSuccessResponse(status_code=200, message="OK", data=result)
```

### Step 5 — Show Summary

After creating all files, display:
- A list of all files created/modified
- An example success response (JSON)
- An example domain exception error response (JSON)
- An example validation error response (JSON)

## Validation

1. Run type checker: `uv run mypy src/adapters/shared/ src/infrastructure/django_app/`
2. Run linter: `uv run ruff check src/ --fix`
3. Confirm Django Ninja's `/api/docs` (Swagger UI) still generates valid OpenAPI schemas for all routes
4. Verify that domain exception classes remain in `src/domain/{module}/exceptions.py` — the handlers import from domain but do NOT leak domain details into HTTP responses
