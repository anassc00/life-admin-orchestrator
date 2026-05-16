# Mejoras pendientes — Life Admin Orchestrator

Auditoría técnica realizada el 2026-05-15 (segunda revisión, post-sprint de correcciones).
Los módulos Calendar, Contacts y Documents fueron eliminados. Las mejoras F1–F6 y U1–U5 fueron implementadas.

---

## Leyenda de prioridad

- 🔴 **CRÍTICO** — bug de seguridad o corrupción de datos
- 🟠 **ALTO** — funcionalidad incompleta o incorrecto visible al usuario
- 🟡 **MEDIO** — feature con impacto directo en usabilidad o coherencia de datos
- 🟢 **BAJO** — mejora técnica, calidad interna o UX refinada

---

## 1. Seguridad y Datos

| ID | Prioridad | Problema | Archivo |
|----|-----------|----------|---------|
| S1 | 🔴 | `InvoiceModel` no tiene `user_id`. Cualquier usuario autenticado puede ver, procesar o eliminar facturas de otros usuarios. Mismo patrón que D1/C1 ya corregidos en entidades previas. | `infrastructure/django_app/models/finance.py`, `domain/entities/finance.py` |
| S2 | 🔴 | `ExpenseModel` no tiene `user_id`. Las entidades `Expense` y `ExpenseModel` son compartidas por todos los usuarios. | `infrastructure/django_app/models/finance.py`, `domain/entities/finance.py` |
| S3 | 🟠 | `ProcessInvoice` no verifica que la factura pertenezca al usuario que la procesa antes de marcarla como pagada. Aunque no haya endpoint público para listar facturas ajenas, un UUID conocido es suficiente para explotarlo. | `application/use_cases/finance/process_invoice.py` |
| S4 | 🟠 | `CreateInvoice` / `ProcessInvoice` no tienen validación de que la cuenta destino pertenezca al usuario. Un usuario puede registrar un gasto sobre la cuenta de otro usuario. | `application/use_cases/finance/process_invoice.py` |

---

## 2. Finance — Lógica y Endpoints

### Bugs / Lógica incompleta

| ID | Prioridad | Problema | Archivo |
|----|-----------|----------|---------|
| F1 | 🟠 | `GetTransactionsByUser` no tiene paginación ni límite. Para un usuario con historial largo, la respuesta puede ser enorme e impacta rendimiento de base de datos. | `application/use_cases/finance/get_transactions_by_user.py` |
| F2 | 🟠 | `RegisterExpense` no acepta cuenta (`account_id`). El gasto se registra sin asociarlo a ninguna cuenta, lo que rompe el balance de cuentas. El endpoint de ingreso sí recibe `account_id`; el de gastos debe tener la misma interfaz. | `application/use_cases/finance/register_expense.py`, `adapters/api/finance/views.py` |
| F3 | 🟡 | `GetSavingsGoals` llama a `SavingsDepositRepository.get_total_deposited_usd(goal_id)` que suma todos los depósitos sin filtrar por moneda USD. `EditSavingsGoal` sí filtra. El progreso mostrado al usuario puede ser incorrecto si hay depósitos en USDT. | `application/use_cases/finance/get_savings_goals.py` |
| F4 | 🟡 | Solo se puede tener un ingreso marcado como `is_base_salary` por período, pero no existe validación ni restricción de base de datos que lo garantice. Si se registran dos salarios en el mismo mes, el resumen financiero duplica la base salarial. | `application/use_cases/finance/register_income.py` |
| F5 | 🟡 | `EditTransaction` no permite cambiar la categoría (`category_id`) de un gasto. Solo permite editar notas, descripción, monto, tasa y fecha. Una corrección de categorización requiere borrar y recrear la transacción. | `application/use_cases/finance/edit_transaction.py` |

### Funcionalidades faltantes

| ID | Prioridad | Feature | Descripción |
|----|-----------|---------|-------------|
| F6 | 🟠 | Endpoint `DELETE /api/finance/accounts/{id}` | `Account.delete()` no existe. Los usuarios no pueden eliminar cuentas. Definir comportamiento: bloquear si tiene transacciones o migrarlas a una cuenta "archivada". |
| F7 | 🟠 | `GET /api/finance/transactions` debe soportar filtros adicionales | Actualmente solo filtra por año/mes. Agregar filtros: `account_id`, `type`, `category_id`, `min_amount`, `max_amount`. Necesario para la vista de transacciones del dashboard. |
| F8 | 🟡 | Endpoint `GET /api/finance/accounts/{id}/balance-history` | Historial de balance de una cuenta por mes (últimos N meses). Sirve para la gráfica de evolución de cuenta en el dashboard. |
| F9 | 🟡 | Reversión de transacción (`POST /api/finance/transactions/{id}/reverse`) | Use case que crea una transacción compensatoria (mismo monto, signo contrario) sin borrar el registro original. Preserva el historial contable. |
| F10 | 🟢 | Transacciones recurrentes | Definir una transacción periódica (ej. renta mensual el día 1) y generarla automáticamente vía Celery beat. Requiere nueva entidad `RecurringTransaction`. |
| F11 | 🟢 | Onboarding de usuario nuevo | Al registrarse, crear cuentas, categorías de gasto y una meta de ahorro por defecto para que el dashboard no esté vacío en el primer uso. |

---

## 3. Presupuesto y Planificación Mensual

> **Contexto**: El dominio tiene entidades `BudgetPlan` y `PlannedItem`, y existe la página `/finance/planning/`, pero no hay ningún use case, endpoint ni repositorio implementado para este módulo. El módulo completo está pendiente.

### Repositorios y acceso a datos (bloqueantes)

| ID | Prioridad | Tarea | Descripción |
|----|-----------|-------|-------------|
| B1 | 🔴 | Implementar `BudgetRepository` y `PlannedItemRepository` | Las interfaces en `domain/repositories/finance.py` deben definir: `create`, `get_by_user_year_month`, `get_by_id`, `list_by_user`, `delete`. Sin esto, ningún use case de presupuesto puede funcionar. |

### Use cases del módulo

| ID | Prioridad | Feature | Descripción |
|----|-----------|---------|-------------|
| B2 | 🟠 | `CreateBudgetPlanUseCase` | Crear el plan mensual (`year`, `month`, `budget_usd`). Solo puede existir uno por (user, year, month); lanzar error si ya existe. |
| B3 | 🟠 | `GetBudgetPlanUseCase` | Devolver el plan del mes con todos sus ítems planeados, el gasto real por categoría y el desvío (planeado vs real). Columnas: `category`, `planned_usd`, `actual_usd`, `deviation_usd`, `deviation_pct`. |
| B4 | 🟠 | `SetPlannedItemUseCase` | Agregar o actualizar el monto planeado para una categoría dentro de un plan. Idempotente: si ya existe el ítem para esa categoría, lo actualiza. |
| B5 | 🟡 | `DeletePlannedItemUseCase` | Remover una categoría del plan. No afecta transacciones reales. |
| B6 | 🟡 | `CopyBudgetPlanUseCase` | Copiar el plan del mes anterior al mes actual como punto de partida. Operación de conveniencia muy común en gestión financiera personal. |
| B7 | 🟡 | `GetBudgetVsActualSummaryUseCase` | Versión resumida para el dashboard: total planeado, total real, % ejecutado, categorías que superaron el presupuesto. |

### Lógica de planificación salarial

| ID | Prioridad | Feature | Descripción |
|----|-----------|---------|-------------|
| B8 | 🟡 | Modelo de asignación de ingreso | Agregar al `BudgetPlan` el campo `income_usd` (ingreso esperado del mes) y calcular automáticamente: `gastos_fijos`, `gastos_variables`, `ahorros` como porcentaje del ingreso. Regla 50/30/20 como configuración por defecto. |
| B9 | 🟢 | Alertas de desvío de presupuesto | Endpoint o lógica en `GetBudgetPlanUseCase` que marque con `over_budget: true` las categorías que superaron el 100% de lo planeado. El frontend puede mostrar estas alertas en el dashboard sin lógica adicional. |

### Endpoints requeridos

```
POST   /api/finance/budget                        → CreateBudgetPlan
GET    /api/finance/budget?year=&month=            → GetBudgetPlan (con vs real)
PUT    /api/finance/budget/{plan_id}               → UpdateBudgetPlan (total budget_usd)
POST   /api/finance/budget/{plan_id}/items         → SetPlannedItem
DELETE /api/finance/budget/{plan_id}/items/{cat_id} → DeletePlannedItem
POST   /api/finance/budget/{plan_id}/copy-from-previous → CopyBudgetPlan
GET    /api/finance/budget/summary?year=&month=    → GetBudgetVsActualSummary
```

---

## 4. Ahorro — Distribución y Proyecciones

> **Contexto**: El módulo de ahorro funciona a nivel de depósitos individuales pero le falta la capa de planificación: ¿cuánto ahorro esta persona el mes que viene? ¿Cómo distribuye ese ahorro entre múltiples metas? ¿Cuándo va a alcanzar cada meta?

### Use cases nuevos

| ID | Prioridad | Feature | Descripción |
|----|-----------|---------|-------------|
| SA1 | 🟠 | `GetSavingsProjectionUseCase` | Para cada meta activa, calcular: `deposited_usd`, `remaining_usd`, `months_to_completion` (basado en `expected_monthly_contribution`), `projected_completion_date`. Si `expected_monthly_contribution` es cero, reportar `null`. |
| SA2 | 🟠 | `GetSavingsDashboardUseCase` | Endpoint `/api/finance/savings/dashboard` que devuelve para el mes actual: total ahorrado en el mes, distribución por meta (nombre, progreso %, monto), resumen de todas las metas activas con proyección. Endpoint único para el widget de ahorros del dashboard. |
| SA3 | 🟡 | `CreateMonthlySavingsDistributionUseCase` | Permitir definir un plan de distribución mensual: "este mes quiero ahorrar $500 distribuidos así: $300 → Meta A, $150 → Meta B, $50 → Meta C". El plan genera las contribuciones esperadas y puede compararse con lo realmente depositado. |
| SA4 | 🟡 | `GetSavingsRateUseCase` | Calcular la tasa de ahorro mensual: `savings_usd / income_usd * 100`. Devolver histórico de los últimos 6 meses. Métrica clave para salud financiera personal. |
| SA5 | 🟢 | Prioridad de metas de ahorro | Agregar campo `priority` (int) a `SavingsGoal` para ordenar metas en el dashboard y en la distribución sugerida. |
| SA6 | 🟢 | Sugerir distribución automática | Use case que toma el `expected_monthly_contribution` de todas las metas activas y sugiere una distribución proporcional basada en urgencia (fecha objetivo más cercana primero). |

### Mejoras al modelo de datos de ahorro

| ID | Prioridad | Cambio | Descripción |
|----|-----------|--------|-------------|
| SA7 | 🟡 | Agregar `deadline` a `SavingsGoal` | Campo opcional de fecha objetivo. Junto con `target_amount_usd` y los depósitos actuales, permite calcular la contribución mensual necesaria para llegar a tiempo. |
| SA8 | 🟡 | Agregar `category` a `SavingsGoal` | Enum: `EMERGENCY_FUND`, `TRAVEL`, `EDUCATION`, `INVESTMENT`, `OTHER`. Permite filtrar y presentar metas agrupadas en el dashboard. |
| SA9 | 🟢 | Proteger FK savings_deposits con `PROTECT` | Actualmente `CASCADE` borra todos los depósitos al eliminar un goal. Cambiar a `PROTECT` (lanzar error si tiene depósitos) o `SET_NULL` con un flag de `archived`. | 

---

## 5. Dashboard y Reportes

> **Contexto**: Actualmente el dashboard dispara múltiples llamadas de API independientes. Para un dashboard fluido, el backend debe ofrecer endpoints agregados que devuelvan exactamente lo que cada widget necesita en una sola llamada.

### Endpoints de dashboard nuevos

| ID | Prioridad | Feature | Descripción |
|----|-----------|---------|-------------|
| DH1 | 🟠 | `GET /api/finance/dashboard` — Snapshot principal | Endpoint único que devuelve todos los datos del dashboard en una sola llamada. Campos: `net_worth_usd`, `monthly_summary` (income/expense/savings/balance), `budget_status` (% ejecutado), `top_expense_categories` (top 3), `savings_overview` (metas con progreso), `upcoming_invoices` (próximos 30 días). Reduce N llamadas a 1. |
| DH2 | 🟠 | `GET /api/finance/net-worth` — Patrimonio neto | Suma todos los balances de todas las cuentas del usuario convertidos a USD (usando el exchange_rate de la última transacción por divisa, o un rate configurable). Desglose: total en efectivo, total en banco, total en billetera digital. |
| DH3 | 🟠 | `GET /api/finance/trend?months=6` — Tendencia mensual | Devuelve los últimos N meses con: `income_usd`, `expenses_usd`, `savings_usd`, `balance_usd` para cada mes. Alimenta el gráfico de barras/línea del dashboard. |
| DH4 | 🟡 | `GET /api/finance/expenses/breakdown?year=&month=` | Desglose de gastos por categoría para un mes: `category_name`, `total_usd`, `transaction_count`, `pct_of_total`. Alimenta el gráfico de torta. |
| DH5 | 🟡 | `GET /api/finance/invoices/upcoming` | Facturas no pagadas ordenadas por `due_date` (próximas primero). Incluye: `vendor`, `amount`, `currency`, `due_date`, `days_until_due`, `is_overdue`. |
| DH6 | 🟡 | `GET /api/finance/transactions/recent?limit=10` | Últimas N transacciones del usuario con nombre de cuenta y categoría expandidos. Para el feed de actividad reciente del dashboard. |
| DH7 | 🟡 | `GET /api/finance/reports/annual?year=` | Reporte anual: totales por mes (income/expense/savings), mes con mayor gasto, mes con mayor ahorro, categoría de gasto dominante por trimestre. |
| DH8 | 🟢 | `GET /api/finance/cashflow/calendar?year=&month=` | Para cada día del mes: suma de ingresos, suma de gastos, balance del día. Alimenta un calendario de flujo de caja. |

### Mejoras al endpoint de resumen existente

| ID | Prioridad | Mejora | Descripción |
|----|-----------|--------|-------------|
| DH9 | 🟡 | `GET /api/finance/summary/current` — Extender respuesta | Agregar a la respuesta existente: `savings_rate_pct` (ahorro/ingreso), `budget_execution_pct` (gasto/presupuesto), `goals_active_count`, `goals_completed_this_month`. Sin cambiar el contrato actual, solo agregando campos. |
| DH10 | 🟡 | Soporte multi-moneda en reportes | Actualmente todos los reportes convierten a USD usando `exchange_rate` de la transacción. Agregar endpoint de configuración de rates de referencia del usuario (rate USD/VES del mes) para conversiones más precisas. |

---

## 6. Arquitectura e Infraestructura

| ID | Prioridad | Problema | Archivo |
|----|-----------|----------|---------|
| A1 | 🟠 | `AccountModel` recalcula el balance sumando todas las transacciones en cada request. Con un historial grande, esta consulta se vuelve lenta. Agregar un campo materializado `balance_cache` en `AccountModel` que se actualice en cada operación de escritura (income, expense, exchange, savings). | `infrastructure/repositories/finance.py` |
| A2 | 🟠 | Faltan índices de base de datos críticos: índice compuesto `(user_id, date)` en `TransactionModel` y `(user_id, year, month)` en `BudgetPlanModel`. Sin ellos, los reportes y el filtro por mes hacen full table scans. | `infrastructure/django_app/models/finance.py` |
| A3 | 🟡 | Los repositorios de `BudgetPlan` y `PlannedItem` no existen en `infrastructure/repositories/finance.py`. Se necesitan antes de implementar cualquier use case del módulo de presupuesto. | `infrastructure/repositories/finance.py` |
| A4 | 🟡 | `GetMonthlyFinancialSummaryUseCase` y `GenerateMonthlyReportUseCase` hacen queries similares de forma independiente. Extraer una capa de consulta compartida (`FinanceQueryService`) que calcule los agregados mensuales una sola vez y sea reutilizada por ambos use cases. | `application/use_cases/finance/` |
| A5 | 🟡 | El `di.py` instancia use cases manualmente. Si se agregan use cases de presupuesto y dashboard, el contenedor crece de forma no sostenible. Considerar organizar la inyección por módulo (`finance_container`, `budget_container`) o usar un micro-framework de DI (ej. `dependency-injector`). | `infrastructure/di.py` |
| A6 | 🟢 | `signals.py` tiene un handler `post_save`/`post_delete` con solo `pass`. Es código muerto que da la falsa impresión de que el balance se recalcula por señales. Eliminar o implementar (ej. invalidar cache). | `infrastructure/django_app/signals.py` |
| A7 | 🟢 | Introducir eventos de dominio básicos: `GoalCompleted`, `BudgetExceeded`, `DepositRegistered`. Los use cases los emiten y los handlers los procesan (notificación, log, etc.). No requiere un bus de eventos complejo; basta con un `list` de eventos en la entidad y un dispatcher simple en el use case. | `domain/entities/finance.py` |
| A8 | 🟢 | Agregar paginación estándar (`limit`/`offset` o cursor-based) a todos los endpoints de listado: transacciones, contribuciones de ahorro, facturas. La respuesta debe incluir `total`, `limit`, `offset`, `items`. | `adapters/api/finance/views.py` |

---

## Resumen por prioridad

### 🔴 Críticos (2 ítems)
S1, S2 — `InvoiceModel` y `ExpenseModel` sin `user_id` (fuga de datos multi-tenant)  
B1 — repositorios del módulo de presupuesto (bloqueante para todo el módulo)

### 🟠 Altos (15 ítems)
S3, S4, F1, F2, F6, F7, B2, B3, B4, SA1, SA2, DH1, DH2, DH3, A1, A2

### 🟡 Medios (18 ítems)
F3, F4, F5, F8, F9, B5, B6, B7, B8, SA3, SA4, SA7, SA8, DH4, DH5, DH6, DH7, DH9, DH10, A3, A4, A5

### 🟢 Bajos (7 ítems)
F10, F11, B9, SA5, SA6, SA9, DH8, A6, A7, A8

---

## Hoja de ruta sugerida

Para llegar a un dashboard funcional y una planificación mensual completa, el orden recomendado es:

1. **Sprint 1 — Cerrar brechas de seguridad**: S1, S2, S3, S4
2. **Sprint 2 — Fixes de lógica finance**: F2, F3, F4 + índices A2
3. **Sprint 3 — Módulo presupuesto (backend)**: B1 → B2 → B3 → B4 → B7
4. **Sprint 4 — Dashboard endpoints**: DH1 → DH2 → DH3 → DH4
5. **Sprint 5 — Proyecciones de ahorro**: SA1 → SA2 → SA7
6. **Sprint 6 — Distribución de ahorro y planning avanzado**: SA3 → SA4 → B6 → B8

*Para implementar un ítem, referenciar su ID (ej. "implementa B2 y B3").*
