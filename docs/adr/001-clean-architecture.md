# ADR 001 — Clean Architecture

**Date:** 2026-05-15
**Status:** Accepted

---

## Context

Django's default approach co-locates business rules with HTTP views and ORM models. As the application grows, this makes logic harder to test in isolation: tests require a running database, and changing persistence details leaks into domain code. The team wanted a structure where financial rules (budget plans, savings projections, transaction reversal) could be exercised without spinning up Django at all.

---

## Decision

Adopt a 4-layer Clean Architecture:

```
domain/          # Entities, value objects, domain exceptions — zero external deps
application/     # Use cases, DTOs, command/query objects — depends only on domain
adapters/        # Django Ninja routers, schemas — depends on application
infrastructure/  # Django ORM models, repositories, DI wiring — depends on all layers
```

Dependency arrows point inward only. Outer layers may import inner layers; inner layers never import outer layers.

---

## Consequences

**Positive:**
- Domain logic and use cases are fully unit-testable without a database or HTTP stack.
- Swapping Django ORM for another storage backend requires changes only in `infrastructure/`.
- Clear boundaries make it obvious where new code belongs.

**Negative:**
- More files and directories than a standard Django project.
- Developers unfamiliar with Clean Architecture face an initial learning curve.
- Simple CRUD operations require more ceremony (entity → use case → repository → ORM model).
