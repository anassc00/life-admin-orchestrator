# ADR 004 — Pydantic Frozen Domain Entities

**Date:** 2026-05-15
**Status:** Accepted

---

## Context

Domain entities represent the core state of the system (accounts, transactions, savings goals). When entities are mutable, it is easy to accidentally modify one inside a use case or repository method without realizing it, leading to subtle bugs where the in-memory object no longer reflects what was persisted — or vice versa. Mutable state also complicates reasoning in tests, since a single entity instance can change between assertions.

The application already uses Pydantic v2 for entities, which provides a straightforward mechanism to enforce immutability.

---

## Decision

All domain entities are defined with:

```python
model_config = ConfigDict(frozen=True)
```

This makes every entity instance immutable after construction. When a use case needs to produce a modified version of an entity (e.g., marking an invoice as paid), it uses Pydantic's `model_copy(update={...})` method, which returns a new instance with the specified fields replaced.

Example:

```python
paid_invoice = invoice.model_copy(update={"status": InvoiceStatus.PAID})
```

---

## Consequences

**Positive:**
- Accidental mutation of domain entities raises a `ValidationError` at runtime, catching bugs early.
- Entities are safe to pass across layer boundaries without defensive copying.
- Easy to serialize: frozen Pydantic models can be converted to dicts or JSON without hidden side effects.
- Explicit mutation via `model_copy` makes state changes visible and searchable in code review.

**Negative:**
- Developers accustomed to mutable ORM models must remember to use `model_copy` instead of attribute assignment.
- `model_copy` creates a new object on every change, which has a small memory overhead for high-frequency operations (negligible in this application).
- Frozen models cannot use `__setattr__` patterns common in some Python libraries.
