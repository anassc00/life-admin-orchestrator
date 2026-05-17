# Mejoras — Life Admin Orchestrator

Última actualización: 2026-05-15.

---

## Completado ✅

### Backend (sprints anteriores)
- ✅ **S1–S4** — `user_id` en Invoice/Expense, ownership checks
- ✅ **U1–U5** — RBAC, profile update, change password, reset flow
- ✅ **F1–F9** — Paginación, filtros, base salary único, category_id en edit, delete account, balance history, reverse transaction
- ✅ **A2, A3** — Índices compuestos, BudgetPlanRepository
- ✅ **Sprint 3 (B2–B7)** — CRUD completo de presupuesto mensual con plan vs real
- ✅ **Sprint 4 (SA5, SA7, SA8, SA9)** — `deadline`, `priority`, `category` en SavingsGoal; FK PROTECT
- ✅ **Sprint 5 (SA1–SA6)** — Proyecciones, distribución, suggest, savings dashboard
- ✅ **Sprint 6 (DH1–DH6)** — net-worth, trend, expenses/breakdown, invoices/upcoming, transactions/recent, dashboard snapshot
- ✅ **Sprint 7 (DH7–DH9)** — Reporte anual, cashflow calendar, extended summary
- ✅ **Sprint 8 (B8, B9)** — `income_usd` en BudgetPlan + regla 50/30/20, flag `over_budget`
- ✅ **SD1** — `DELETE /api/finance/savings/deposits/{id}` con ownership check
- ✅ **A6** — Eliminado código muerto en `signals.py`

### Frontend / UI (sprints 9–11)
- ✅ **V1** — Página de presupuesto completamente reescrita con API real (plan vs real, ítems editables inline, 50/30/20, copiar mes anterior)
- ✅ **V2** — Página de metas de ahorro mejorada (eliminar depósito, proyección por meta, campos deadline/priority/category)
- ✅ **V3** — Nueva página `/finance/reports/` — reporte anual con tabla y gráfico Canvas
- ✅ **V4** — Nueva página `/finance/cashflow/` — calendario de flujo de caja mensual
- ✅ **V5** — Gráfico de balance histórico por cuenta en `/finance/accounts/` (Canvas, línea, modal)
- ✅ **E1** — Filtros por cuenta y categoría en vista de transacciones
- ✅ **E2** — Botón eliminar cuenta con modal de confirmación
- ✅ **E3** — Nueva página `/finance/invoices/` — facturas pendientes/pagadas, crear y procesar pago
- ✅ **E4** — Botón "Revertir" por transacción en historial
- ✅ **D1** — Widget de proyección en dashboard (meses restantes + badge ⚠️ Atrasada)
- ✅ **D2** — Gráfico de tasa de ahorro histórica en dashboard (Canvas, línea morada)
- ✅ **D3** — Visualización 50/30/20 en tarjeta de presupuesto del dashboard
- ✅ **D4** — Link "Gestionar aportes →" en widget de ahorros del dashboard
- ✅ **D5** — Estados vacíos con CTA por widget en el dashboard
- ✅ **D6** — Desglose por tipo (cash/banco/wallet) ya presente en net-worth

### Backend técnico (sprint 10)
- ✅ **DH10** — `UserExchangeRate`: entidad, modelo, migración, CRUD (`GET/PUT /api/finance/exchange-rates`)
- ✅ **F10** — `RecurringTransaction`: entidad, modelo, migración, CRUD + Celery beat task (`GET/POST/DELETE /api/finance/recurring`, tarea `generate_recurring_transactions_task`)
- ✅ **F11** — Onboarding de usuario nuevo: `OnboardUserUseCase` crea 2 cuentas, 6 categorías y 1 meta al registrarse
- ✅ **A1** — Balance cache materializado en `AccountModel.balance_cache` (JSONField), actualizado en cada escritura de transacción; `POST /api/finance/accounts/refresh-balances` para recuperación manual
- ✅ **A4** — N/A: `GetMonthlyFinancialSummaryUseCase` y `GenerateMonthlyReportUseCase` usan repositorios completamente distintos; no hay duplicación real que extraer

### Documentación
- ✅ **DOC1** — README completamente reescrito con stack real, páginas y endpoints
- ✅ **DOC2** — Guía detallada de la API (`docs/api.md`) con los ~46 endpoints
- ✅ **DOC3** — 4 ADRs en `docs/adr/` (Clean Architecture, migraciones manuales, Ninja vs DRF, Pydantic v2 entities)

---

## Sin pendientes activos

Todos los ítems del backlog han sido implementados o descartados con justificación.
Para nuevas mejoras, abrir una sección "Pendiente" con el formato de tabla habitual.

---

*Para implementar un ítem, referenciarlo por ID (ej. "implementa V5").*
