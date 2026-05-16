# Mejoras pendientes — Life Admin Orchestrator

Auditoría técnica actualizada el 2026-05-15 (cuarta revisión, post-sprints 3–8 + endpoint DELETE deposits).
Los módulos Calendar, Contacts y Documents fueron eliminados.

**Backend completado:**
- ✅ **S1–S4** — `user_id` en Invoice/Expense, ownership checks en ProcessInvoice
- ✅ **U1–U5** — RBAC, profile update, change password, reset flow
- ✅ **F1–F9** — Paginación, filtros, base salary único, category_id en edit, delete account, balance history, reverse transaction
- ✅ **A2, A3** — Índices compuestos, BudgetPlanRepository
- ✅ **Sprint 3 (B2–B7)** — CRUD completo de presupuesto mensual con plan vs real
- ✅ **Sprint 4 (SA5, SA7, SA8, SA9)** — `deadline`, `priority`, `category` en SavingsGoal; FK PROTECT
- ✅ **Sprint 5 (SA1–SA6)** — Proyecciones, distribución, suggest, savings dashboard
- ✅ **Sprint 6 (DH1–DH6)** — net-worth, trend, expenses/breakdown, invoices/upcoming, transactions/recent, dashboard snapshot
- ✅ **Sprint 7 (DH7–DH9)** — Reporte anual, cashflow calendar, extended summary
- ✅ **Sprint 8 (B8, B9)** — `income_usd` en BudgetPlan + regla 50/30/20, flag `over_budget`
- ✅ **SD1** — `DELETE /api/finance/savings/deposits/{id}` — eliminar depósito con ownership check

---

## Leyenda de prioridad

- 🔴 **CRÍTICO** — bug de seguridad o datos incorrectos visibles al usuario
- 🟠 **ALTO** — funcionalidad con backend listo pero sin interfaz, o UX rota
- 🟡 **MEDIO** — mejora de usabilidad o coherencia visual
- 🟢 **BAJO** — refinamiento técnico o UX

---

## 1. Páginas de gestión faltantes (backend listo, frontend pendiente)

Estas funcionalidades tienen endpoints completos pero no tienen ninguna página en el frontend.

| ID | Prioridad | Feature | Endpoint(s) disponibles | Descripción |
|----|-----------|---------|--------------------------|-------------|
| V1 | 🔴 | **Página de presupuesto** (`/finance/planning/`) | `POST/GET /api/finance/budget`, `POST /budget/{id}/items`, `DELETE /budget/{id}/items/{cat}`, `POST /budget/{id}/copy-from-previous`, `GET /api/finance/budget/summary` | La página existe pero está vacía. Mostrar: formulario para crear plan, tabla editable de categorías con monto planeado vs real, botón "Copiar mes anterior", barra de progreso 50/30/20. |
| V2 | 🟠 | **Página de metas de ahorro** (`/finance/savings/`) | `GET /api/finance/savings/goals`, `POST /api/finance/savings/goals`, `PATCH /api/finance/savings/goals/{id}`, `POST /api/finance/savings/deposits`, `DELETE /api/finance/savings/deposits/{id}`, `GET /api/finance/savings/projection`, `GET /api/finance/savings/dashboard` | Actualmente no hay página de metas. Mostrar: lista de metas con progreso, formulario para crear/editar meta (incluir deadline, priority, category), botón para registrar y eliminar depósito, proyección de fecha de completación. |
| V3 | 🟠 | **Reporte anual** (`/finance/reports/annual/`) | `GET /api/finance/reports/annual?year=` | Tabla con totales mensuales (ingreso / gasto / ahorro / balance), highlight del mes con mayor gasto y mayor ahorro, categoría dominante por trimestre. |
| V4 | 🟡 | **Calendario de cashflow** (`/finance/cashflow/`) | `GET /api/finance/cashflow/calendar?year=&month=` | Vista de calendario mensual donde cada día muestra el balance del día (verde si ingreso neto, rojo si gasto neto). Navegación prev/next mes. |
| V5 | 🟡 | **Historial de balance de cuenta** | `GET /api/finance/accounts/{id}/balance-history` | Gráfico de línea por cuenta con evolución del balance mes a mes. Accesible desde la vista de cuentas o desde el dashboard de cuentas. |

---

## 2. Mejoras visuales al dashboard existente

El dashboard (`/dashboard/`) ya carga 10 secciones pero le faltan estos refinamientos:

| ID | Prioridad | Mejora | Descripción |
|----|-----------|--------|-------------|
| D1 | 🟠 | **Widget de proyección de metas** | Agregar al dashboard el endpoint `GET /api/finance/savings/projection` para mostrar cuántos meses faltan para cada meta activa. Mostrar badge "En camino" / "Atrasada" según si la proyección llega antes o después del deadline. |
| D2 | 🟠 | **Gráfico de tasa de ahorro histórica** | Llamar `GET /api/finance/savings/rate?months=6` y dibujar una línea o barras simples con la tasa % de los últimos 6 meses en la sección de ahorros del dashboard. |
| D3 | 🟡 | **Visualización 50/30/20 en el dashboard** | Si el mes tiene un `BudgetPlan` con `income_usd`, mostrar los tres cubos (necesidades / deseos / ahorro) con la asignación recomendada vs la real. Endpoint: `GET /api/finance/budget/summary`. |
| D4 | 🟡 | **Botón "Eliminar depósito" en widget de metas** | Cada depósito listado en el widget de metas debería tener un botón de eliminar que llame `DELETE /api/finance/savings/deposits/{id}` y recargue el widget. Responde la pregunta que generó esta tarea. |
| D5 | 🟡 | **Estado vacío por sección** | Cuando un widget no tiene datos (sin metas, sin presupuesto, sin facturas) mostrar un mensaje de acción: "Crea tu primera meta →", "Define tu presupuesto →", etc. en lugar de simplemente vacío. |
| D6 | 🟢 | **Tasa de cambio y balance multi-moneda visible** | Mostrar en el widget de patrimonio neto el balance por moneda (USD, VES, MXN) antes de la conversión, no solo el total en USD. El endpoint `GET /api/finance/net-worth` ya devuelve el desglose. |

---

## 3. Mejoras a vistas existentes

| ID | Prioridad | Vista | Mejora | Descripción |
|----|-----------|-------|--------|-------------|
| E1 | 🟠 | Transacciones | Filtros avanzados en la UI | El endpoint `GET /api/finance/transactions` ya soporta `account_id`, `type`, `category_id`, `min_amount`, `max_amount`. Agregar controles de filtro en la vista de transacciones. |
| E2 | 🟠 | Cuentas | Botón eliminar cuenta | El endpoint `DELETE /api/finance/accounts/{id}` existe. Agregar botón en la vista de cuentas con confirmación modal. Mostrar error si la cuenta tiene transacciones. |
| E3 | 🟡 | Facturas | Lista de facturas completa | Existe `GET /api/finance/invoices` pero no hay página de listado de todas las facturas. Solo se ven las próximas en el dashboard. Crear vista `/finance/invoices/` con tabla y acción "Marcar como pagada". |
| E4 | 🟡 | Transacciones | Acción "Revertir" en la UI | El endpoint `POST /api/finance/transactions/{id}/reverse` existe. Agregar botón en la fila de transacción con confirmación. |

---

## 4. Backend técnico pendiente

| ID | Prioridad | Problema | Descripción |
|----|-----------|----------|-------------|
| A1 | 🟡 | Balance cache en AccountModel | `AccountModel` recalcula el balance sumando todas las transacciones en cada request. Con historial grande se vuelve lento. Agregar `balance_cache` materializado que se actualiza en cada escritura. |
| A4 | 🟡 | FinanceQueryService compartido | `GetMonthlyFinancialSummaryUseCase` y `GenerateMonthlyReportUseCase` calculan los mismos agregados. Extraer una capa de consulta compartida para eliminar duplicación. |
| A6 | 🟢 | Eliminar signals.py muerto | `signals.py` tiene un handler `post_save`/`post_delete` con solo `pass`. Es código muerto. Eliminar. |
| F10 | 🟢 | Transacciones recurrentes | Definir una transacción periódica y generarla automáticamente vía Celery beat. Requiere nueva entidad `RecurringTransaction`. |
| F11 | 🟢 | Onboarding de usuario nuevo | Al registrarse, crear cuentas, categorías y una meta de ahorro por defecto para que el dashboard no esté vacío en el primer uso. |
| DH10 | 🟡 | Rates de referencia multi-moneda | Endpoint de configuración de rates del usuario (USD/VES del mes) para conversiones más precisas en reportes. |

---

## 5. Documentación final

| ID | Prioridad | Tarea | Descripción |
|----|-----------|-------|-------------|
| DOC1 | 🟡 | **README principal** | Actualizar `README.md` con: stack actual, comandos para correr el proyecto, estructura de carpetas con Clean Architecture, lista de endpoints disponibles con descripción breve. |
| DOC2 | 🟡 | **Guía de la API** | Generar o escribir una referencia de los ~50 endpoints actuales: método, ruta, params, respuesta, casos de error. Puede ser un Markdown o apuntar al Swagger que Django Ninja expone en `/api/docs`. |
| DOC3 | 🟢 | **ADR de decisiones de arquitectura** | Documentar las decisiones clave tomadas: por qué Clean Architecture, por qué mano a mano migrations, por qué Ninja vs DRF, por qué Pydantic v2 frozen entities. Un archivo `docs/adr/` con entradas cortas. |

---

## Hoja de ruta sugerida

### Sprint 9 — Páginas faltantes de alto impacto
> **Objetivo:** Dar acceso desde la UI a toda la funcionalidad de backend ya implementada.

| Orden | ID | Descripción |
|-------|----|-------------|
| 1 | V2 | Página de metas de ahorro (la más consultada) |
| 2 | D4 | Botón eliminar depósito en dashboard (responde el bug reportado hoy) |
| 3 | V1 | Página de presupuesto mensual |
| 4 | D1 | Widget de proyección de metas en dashboard |

### Sprint 10 — Reportes y refinamiento visual
> **Objetivo:** Páginas de análisis y mejoras de UX en el dashboard.

| Orden | ID | Descripción |
|-------|----|-------------|
| 1 | V3 | Página de reporte anual |
| 2 | V4 | Calendario de cashflow |
| 3 | D2 | Gráfico de tasa de ahorro histórica en dashboard |
| 4 | D5 | Estados vacíos por widget |

### Sprint 11 — Mejoras a vistas existentes
| Orden | ID | Descripción |
|-------|----|-------------|
| 1 | E1 | Filtros avanzados en transacciones |
| 2 | E2 | Botón eliminar cuenta |
| 3 | E3 | Lista completa de facturas |
| 4 | E4 | Acción revertir transacción |

### Sprint 12 — Documentación
| Orden | ID | Descripción |
|-------|----|-------------|
| 1 | DOC1 | README principal actualizado |
| 2 | DOC2 | Guía de la API |
| 3 | DOC3 | ADR de arquitectura |

---

*Para implementar un sprint, referenciar los IDs (ej. "implementa Sprint 9").*
