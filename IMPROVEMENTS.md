# Mejoras — Life Admin Orchestrator

Última actualización: 2026-05-17.

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

### Documentación
- ✅ **DOC1** — README completamente reescrito con stack real, páginas y endpoints

---

## Leyenda de prioridad

- 🔴 **CRÍTICO** — bug de seguridad o datos incorrectos
- 🟠 **ALTO** — impacto directo en usabilidad
- 🟡 **MEDIO** — mejora de coherencia o rendimiento
- 🟢 **BAJO** — refinamiento técnico o conveniencia

---

## Pendiente

### Frontend

| ID | Prioridad | Feature | Descripción |
|----|-----------|---------|-------------|
| V5 | 🟡 | **Historial de balance de cuenta** | Agregar gráfico de línea en `/finance/accounts/` mostrando la evolución del balance mes a mes por cuenta. Endpoint disponible: `GET /api/finance/accounts/{id}/balance-history`. |

### Backend técnico

| ID | Prioridad | Problema | Descripción |
|----|-----------|----------|-------------|
| DH10 | 🟡 | Rates de referencia multi-moneda | Endpoint de configuración de rates del usuario (USD/VES del mes) para conversiones más precisas en reportes. Actualmente usa el `exchange_rate` de la última transacción. |
| A1 | 🟡 | Balance cache en AccountModel | `AccountModel` recalcula el balance sumando todas las transacciones en cada request. Con historial grande se vuelve lento. Agregar `balance_cache` materializado actualizado en cada escritura. Requiere migración cuidadosa. |
| A4 | 🟡 | FinanceQueryService compartido | `GetMonthlyFinancialSummaryUseCase` y `GenerateMonthlyReportUseCase` calculan los mismos agregados de forma independiente. Extraer capa de consulta compartida para eliminar duplicación. |
| F11 | 🟢 | Onboarding de usuario nuevo | Al registrarse, crear cuentas por defecto, categorías de gasto y una meta de ahorro para que el dashboard no esté vacío en el primer uso. |
| F10 | 🟢 | Transacciones recurrentes | Definir transacciones periódicas (ej. renta mensual) y generarlas automáticamente vía Celery beat. Requiere nueva entidad `RecurringTransaction` y tarea programada. |

### Documentación

| ID | Prioridad | Tarea | Descripción |
|----|-----------|-------|-------------|
| DOC2 | 🟢 | Guía detallada de la API | Referencia completa de los ~50 endpoints: params, body, respuesta, casos de error. El Swagger en `/api/docs` cubre esto parcialmente. |
| DOC3 | 🟢 | ADR de decisiones de arquitectura | Documentar decisiones clave: Clean Architecture, hand-written migrations, Ninja vs DRF, Pydantic v2 frozen entities. Archivo `docs/adr/`. |

---

*Para implementar un ítem, referenciarlo por ID (ej. "implementa V5").*
