# ADR 003 — Django Ninja over Django REST Framework

**Date:** 2026-05-15
**Status:** Accepted

---

## Context

Django REST Framework (DRF) is the traditional choice for building Django APIs. However, DRF's `Serializer` classes are a parallel type system that must duplicate the shape of domain DTOs already defined with Pydantic. This means every data contract is defined twice: once as a Pydantic model (for use cases and domain entities) and once as a DRF serializer (for HTTP I/O). The duplication increases the maintenance surface and introduces opportunities for the two definitions to drift apart.

The team was already using Pydantic v2 for domain entities and application DTOs. A framework that used Pydantic natively for HTTP schemas would eliminate the duplication entirely.

---

## Decision

Use **Django Ninja** for all API endpoints.

Django Ninja uses Pydantic v2 schemas directly for request parsing and response serialization. This means the same Pydantic model can serve as a DTO in the application layer and as an HTTP schema in the adapter layer — or a thin adapter schema can extend a domain type with minimal boilerplate.

---

## Consequences

**Positive:**
- Swagger UI (OpenAPI 3) is generated automatically at `/api/docs` — no extra configuration.
- Request validation, response serialization, and OpenAPI documentation are all derived from a single Pydantic schema definition.
- Less boilerplate: no serializer `create()` / `update()` methods, no `Meta` classes.
- Type-safe path and query parameters via Python type annotations.

**Negative:**
- Django Ninja is a smaller ecosystem than DRF; some DRF third-party packages (e.g., `drf-spectacular`, viewsets) are not compatible.
- Team members familiar with DRF patterns need to learn Django Ninja's router-based approach.
- Django Ninja's support for DRF-style permissions and throttling requires manual integration.
