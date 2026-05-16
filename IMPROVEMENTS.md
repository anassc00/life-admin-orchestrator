# Mejoras pendientes — Life Admin Orchestrator

Auditoría técnica realizada el 2026-05-15. Cada ítem tiene un ID único para referenciarlo al implementar.

---

## Leyenda de prioridad

- 🔴 **CRÍTICO** — bug o brecha de seguridad que puede producir datos corruptos o fugas entre usuarios
- 🟠 **ALTO** — funcionalidad incompleta o con comportamiento incorrecto visible
- 🟡 **MEDIO** — feature faltante con impacto directo en usabilidad
- 🟢 **BAJO** — mejora técnica o de calidad interna

---

## Finance

### Bugs / Lógica rota

| ID | Prioridad | Problema | Archivo |
|----|-----------|----------|---------|
| F1 | 🔴 | `EditTransaction` no actualiza la transacción relacionada en intercambios de divisa. Si se edita el `amount` o `exchange_rate` de un lado del par `EXCHANGE_IN/OUT`, el otro lado queda desincronizado y el balance se corrompe. | `application/use_cases/finance/edit_transaction.py` |
| F2 | 🔴 | `DepositToSavings` guarda el depósito y la transacción en dos operaciones separadas sin atomicidad. Si la segunda falla, queda un depósito registrado sin transacción correspondiente. Solución: usar `UnitOfWork` o una transacción de base de datos. | `application/use_cases/finance/deposit_to_savings.py` |
| F3 | 🟠 | `GetSavingsGoals` calcula el total depositado sin filtrar por moneda USD, pero `EditSavingsGoal._calculate_deposited_usd()` sí filtra. El progreso del goal mostrado al usuario es incorrecto. | `application/use_cases/finance/get_savings_goals.py` |
| F4 | 🟠 | `GetSavingsGoalContributions` no verifica que el goal pertenezca al usuario solicitante. Cualquier usuario autenticado puede ver las contribuciones de goals ajenos pasando un UUID arbitrario. | `application/use_cases/finance/get_savings_goal_contributions.py` |
| F5 | 🟠 | `ProcessInvoice` marca la factura como pagada pero no crea la transacción de gasto ni actualiza el balance de la cuenta. El flujo factura → gasto está roto. | `application/use_cases/finance/process_invoice.py` |
| F6 | 🟡 | `SavingsGoal` tiene el campo `is_completed` pero ningún use case lo activa automáticamente cuando los depósitos alcanzan `target_amount_usd`. El goal nunca se marca como completado. | `application/use_cases/finance/deposit_to_savings.py` |

### Funcionalidades faltantes

| ID | Prioridad | Feature | Descripción |
|----|-----------|---------|-------------|
| F7 | 🟠 | Endpoint POST para crear cuentas | `RegisterAccountUseCase` existe pero no hay ruta `POST /api/finance/accounts`. Los usuarios no pueden crear cuentas desde la API. | 
| F8 | 🟡 | Budget vs. real | `BudgetPlanCommand` y la entidad existen en domain pero no hay use cases para crear un presupuesto, consultarlo ni compararlo con el gasto real del mes. |
| F9 | 🟡 | Reporte mensual desglosado | Reporte que muestra gasto real por categoría vs. monto presupuestado, con flag de desvío. |
| F10 | 🟡 | Transacciones recurrentes | Poder definir una transacción periódica (ej. renta mensual el día 1) y que se genere automáticamente vía Celery. |
| F11 | 🟡 | Reversión de transacción | Use case que crea una transacción compensatoria (mismo monto, signo contrario) en lugar de eliminar o editar. |
| F12 | 🟢 | Onboarding de usuario nuevo | Al registrarse, crear cuentas, categorías de gasto y meta de ahorro por defecto para que el dashboard no esté vacío. |

---

## Calendar

### Bugs / Lógica rota

| ID | Prioridad | Problema | Archivo |
|----|-----------|----------|---------|
| C1 | 🔴 | Las citas no tienen `user_id`. Todos los usuarios ven, modifican y eliminan las citas de todos. Bug multi-tenant crítico. | `domain/entities/calendar.py`, `infrastructure/django_app/models/calendar.py` |
| C2 | 🟠 | `SendReminderUseCase` devuelve `sent=True` sin hacer nada real. No existe integración con ningún canal de notificación (email, push, SMS). | `application/use_cases/calendar/send_reminder.py` |
| C3 | 🟠 | Al reencuadrar una cita no se puede excluir la propia cita del chequeo de conflictos. El parámetro `exclude_id` existe en el DTO pero el endpoint de la API nunca lo pasa, haciendo imposible el reschedule sin falso conflicto. | `adapters/api/calendar/views.py` |
| C4 | 🟠 | El `CalendarAgent` siempre reporta `has_conflict=False` porque `_parse_event()` está hardcodeado a devolver `None`. La integración LLM es un stub. | `application/agents/calendar_agent.py` |

### Funcionalidades faltantes

| ID | Prioridad | Feature | Descripción |
|----|-----------|---------|-------------|
| C5 | 🟠 | Cancelar / eliminar cita | `AppointmentRepository.delete()` existe pero no hay use case ni endpoint. |
| C6 | 🟡 | Listar citas por rango de fechas | Endpoint `GET /api/calendar/appointments?from=&to=` filtrado por usuario. |
| C7 | 🟡 | Confirmar cita | `Appointment.confirm()` existe en la entidad pero no hay use case ni endpoint para invocarlo. |
| C8 | 🟡 | Actualizar cita (reschedule) | Use case que re-verifica conflictos excluyendo la propia cita. |
| C9 | 🟢 | Importar eventos desde ICS/iCal | Parsear archivo de calendario externo y crear citas en bulk. |

---

## Documents

### Bugs / Lógica rota

| ID | Prioridad | Problema | Archivo |
|----|-----------|----------|---------|
| D1 | 🔴 | Los documentos no tienen `user_id`. Todos los usuarios ven todos los documentos. | `domain/entities/document.py`, `infrastructure/django_app/models/document.py` |
| D2 | 🟠 | `ExtractMetadataUseCase` es referenciado por el `DocumentAgent` pero el archivo no existe. El agente falla en runtime al intentar ejecutar ese nodo. | `application/agents/document_agent.py:89` |
| D3 | 🟠 | `ArchiveDocumentUseCase` guarda un `storage_path` en la base de datos pero no escribe el archivo a disco ni a ningún storage backend (S3, etc.). El path apunta a un archivo inexistente. | `application/use_cases/document/archive_document.py` |
| D4 | 🟠 | `FinanceAgent._extract_data()` siempre devuelve `None` (stub). El procesamiento de facturas por LLM nunca funciona. | `application/agents/finance_agent.py` |

### Funcionalidades faltantes

| ID | Prioridad | Feature | Descripción |
|----|-----------|---------|-------------|
| D5 | 🟠 | Implementar `ExtractMetadataUseCase` | Crear el use case faltante que el agente espera. |
| D6 | 🟡 | Backend de almacenamiento real | Integrar almacenamiento de archivos (sistema de archivos local o S3) para que `ArchiveDocument` funcione. |
| D7 | 🟡 | Búsqueda de documentos | Endpoint para buscar por keyword, categoría o rango de fecha. |
| D8 | 🟡 | Eliminar documento | Use case y endpoint para borrar un documento y su archivo asociado. |

---

## Users / Auth

### Bugs / Lógica rota

| ID | Prioridad | Problema | Archivo |
|----|-----------|----------|---------|
| U1 | 🟠 | El endpoint de resumen financiero devuelve `200` con datos vacíos cuando el usuario no está autenticado, en lugar de `401 Unauthorized`. | `adapters/api/finance/views.py` |
| U2 | 🟡 | `is_admin` existe en la entidad `User` pero nunca se usa para controlar acceso en ningún use case ni endpoint. No hay RBAC efectivo. | `domain/entities/user.py` |

### Funcionalidades faltantes

| ID | Prioridad | Feature | Descripción |
|----|-----------|---------|-------------|
| U3 | 🟠 | Reset de contraseña | Flujo completo: solicitar reset → token por email → nueva contraseña. Sin esto, un usuario bloqueado no puede recuperar su cuenta. |
| U4 | 🟡 | Actualizar perfil | Use case y endpoint para cambiar nombre y email. |
| U5 | 🟡 | Cambiar contraseña (usuario autenticado) | Distinto al reset: el usuario conoce su contraseña actual y quiere cambiarla. |

---

## Contacts

### Bugs / Lógica rota

| ID | Prioridad | Problema | Archivo |
|----|-----------|----------|---------|
| CO1 | 🔴 | Los contactos no tienen `user_id`. Todos los usuarios comparten la misma lista de contactos. | `domain/entities/contact.py` |

### Funcionalidades faltantes

| ID | Prioridad | Feature | Descripción |
|----|-----------|---------|-------------|
| CO2 | 🟠 | CRUD completo de contactos | Solo existen `LogInteraction` y `UpdateContactRecord`. Faltan Create, Delete y List. |
| CO3 | 🟡 | Estadísticas de interacción | Último contacto, total de interacciones por canal, frecuencia. |
| CO4 | 🟢 | Importar contactos desde CSV/vCard | Creación en bulk desde archivo externo. |

---

## Infraestructura / Arquitectura

| ID | Prioridad | Problema | Archivo |
|----|-----------|----------|---------|
| I1 | 🟡 | `signals.py` registra un handler en `post_save`/`post_delete` que solo tiene `pass`. Código muerto que confunde sobre si el balance se recalcula o no. Debe eliminarse o implementarse (ej. invalidar caché). | `infrastructure/django_app/signals.py` |
| I2 | 🟡 | Faltan índices de base de datos en columnas críticas de consulta: índice compuesto `(user_id, date)` en `TransactionModel` e índice `(goal_id, currency)` en `SavingsDepositModel`. | `infrastructure/django_app/models/finance.py` |
| I3 | 🟢 | `SavingsGoalModel` usa `CASCADE` en la FK del goal. Borrar un goal elimina todo el historial de depósitos. Considerar `PROTECT` o `SET_NULL` según la política deseada. | `infrastructure/django_app/models/finance.py` |

---

## Resumen por prioridad

### 🔴 Críticos (6 ítems)
F1, F2, C1, D1, CO1 — bugs de integridad de datos o seguridad multi-tenant  
*(Nota: D1, C1, CO1 son el mismo patrón: agregar `user_id` a la entidad y migración)*

### 🟠 Altos (14 ítems)
F3, F4, F5, F7, C2, C3, C4, C5, D2, D3, D4, D5, U1, U3, CO2

### 🟡 Medios (12 ítems)
F6, F8, F9, F10, F11, C6, C7, C8, D6, D7, D8, U2, U4, U5, I1, I2

### 🟢 Bajos (4 ítems)
F12, C9, CO4, I3

---

*Para implementar un ítem, referenciar su ID (ej. "implementa F1 y F2").*
