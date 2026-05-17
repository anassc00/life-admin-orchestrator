# ADR 002 — Hand-Written Migrations

**Date:** 2026-05-15
**Status:** Accepted

---

## Context

The application uses a custom Django app label `life_admin` (set in `AppConfig`) so that ORM models live under `infrastructure/django_app/models/` rather than in a top-level `models.py`. Django's `makemigrations` command uses the installed app's label to resolve foreign keys and references. When the app label differs from the folder name, auto-generated migrations frequently produce incorrect `app_label` references, missing `through` models, or skip custom SQL constraints entirely.

Additionally, some migrations include raw SQL (e.g., for partial indexes, check constraints, or triggers) that `makemigrations` cannot express.

---

## Decision

All database migrations are hand-written and stored in `infrastructure/django_app/migrations/`. The `makemigrations` command is not used to generate new migrations.

Each migration file is authored directly, specifying explicit `app_label` values and including any required raw SQL via `migrations.RunSQL`.

---

## Consequences

**Positive:**
- Full control over migration content — no surprises from auto-detection.
- Custom SQL constraints, indexes, and triggers are expressed exactly as intended.
- The `life_admin` app label resolves correctly in all `ForeignKey` and `ManyToMany` declarations.

**Negative:**
- Developers must write migration files manually, which is more verbose.
- Forgetting to create a migration after a model change will not be caught by `makemigrations --check`.
- Reviewers must verify migration correctness manually rather than relying on Django's diff engine.
