# API Reference — Life Admin Orchestrator

Base URL: `http://localhost:8000/api`
Auth: Session-based. Login first via `POST /auth/login`. All `/finance/*` endpoints require authentication (session cookie).
Interactive docs: `http://localhost:8000/api/docs` (Swagger UI)

---

## Auth (`/api/auth/`)

### POST /auth/register

Register a new user account. The very first registration is always allowed (bootstrap). All subsequent registrations require an active admin session.

**Auth required:** No (first user) / Yes, admin (subsequent users)

**Request body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `first_name` | string | Yes | |
| `last_name` | string | Yes | |
| `email` | string | Yes | Must be unique |
| `password` | string | Yes | |

**Response `201 Created`:**

```json
{
  "user_id": "uuid",
  "email": "user@example.com",
  "full_name": "Jane Doe",
  "is_admin": false
}
```

**Error codes:**

| Code | Reason |
|------|--------|
| `403 Forbidden` | Non-admin trying to register an additional user |
| `409 Conflict` | Email already registered |

---

### POST /auth/login

Authenticate a user and create a session.

**Auth required:** No

**Request body:**

| Field | Type | Required |
|-------|------|----------|
| `email` | string | Yes |
| `password` | string | Yes |

**Response `200 OK`:**

```json
{
  "user_id": "uuid",
  "email": "user@example.com",
  "full_name": "Jane Doe",
  "is_admin": false
}
```

**Error codes:**

| Code | Reason |
|------|--------|
| `401 Unauthorized` | Invalid credentials |

---

### POST /auth/logout

End the current session.

**Auth required:** Yes

**Response `200 OK`:**

```json
{ "detail": "Logged out successfully." }
```

---

### GET /auth/me

Get the authenticated user's profile.

**Auth required:** Yes

**Response `200 OK`:**

```json
{
  "user_id": "uuid",
  "email": "user@example.com",
  "full_name": "Jane Doe",
  "is_admin": false
}
```

**Error codes:**

| Code | Reason |
|------|--------|
| `401 Unauthorized` | Not authenticated or session expired |

---

### PATCH /auth/me

Update the authenticated user's profile (first name, last name, email).

**Auth required:** Yes

**Request body** (all fields optional):

| Field | Type | Description |
|-------|------|-------------|
| `first_name` | string | null |
| `last_name` | string | null |
| `email` | string | null — must be unique if provided |

**Response `200 OK`:** `UserResponse` (same shape as `GET /auth/me`)

**Error codes:**

| Code | Reason |
|------|--------|
| `401 Unauthorized` | Not authenticated |
| `409 Conflict` | Email already taken by another account |

---

### POST /auth/me/change-password

Change password for the authenticated user.

**Auth required:** Yes

**Request body:**

| Field | Type | Required |
|-------|------|----------|
| `current_password` | string | Yes |
| `new_password` | string | Yes |

**Response `200 OK`:**

```json
{ "detail": "Password changed successfully." }
```

**Error codes:**

| Code | Reason |
|------|--------|
| `401 Unauthorized` | Not authenticated, or `current_password` is wrong |

---

### POST /auth/password-reset/request

Initiate a password reset. In dev mode the reset token is returned directly in the response. In production it would be emailed.

**Auth required:** No

**Request body:**

| Field | Type | Required |
|-------|------|----------|
| `email` | string | Yes |

**Response `200 OK`:**

```json
{
  "detail": "If the email exists, a reset link has been sent.",
  "reset_token": "uuid-or-null"
}
```

Note: Always returns `200` even when the email is not found (prevents enumeration).

---

### POST /auth/password-reset/confirm

Set a new password using a valid reset token.

**Auth required:** No

**Request body:**

| Field | Type | Required |
|-------|------|----------|
| `token` | UUID | Yes |
| `new_password` | string | Yes |

**Response `200 OK`:**

```json
{ "detail": "Password reset successfully." }
```

**Error codes:**

| Code | Reason |
|------|--------|
| `422 Unprocessable Entity` | Token is invalid or expired, or user not found |

---

## Accounts (`/api/finance/accounts`)

### GET /finance/accounts

List all accounts for the authenticated user.

**Auth required:** Yes (returns empty list if unauthenticated)

**Response `200 OK`:** Array of account objects.

```json
[
  {
    "account_id": "uuid",
    "name": "BBVA Checking",
    "type": "bank",
    "supported_currencies": ["MXN", "USD"],
    "default_currencies": ["MXN"],
    "current_balance": { "MXN": "12500.00", "USD": "0.00" }
  }
]
```

---

### POST /finance/accounts

Create a new account (wallet, cash, or bank).

**Auth required:** Yes

**Request body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Unique per user |
| `type` | AccountType | Yes | `"wallet"`, `"cash"`, `"bank"` |
| `supported_currencies` | Currency[] | Yes | e.g. `["MXN", "USD"]` |
| `default_currencies` | Currency[] | Yes | Subset of supported |

**Response `201 Created`:**

```json
{
  "account_id": "uuid",
  "name": "BBVA Checking",
  "type": "bank"
}
```

**Error codes:**

| Code | Reason |
|------|--------|
| `409 Conflict` | Account name already exists for this user |

---

### PATCH /finance/accounts/{account_id}

Update an existing account's name, type, or currency settings.

**Auth required:** Yes

**Path params:** `account_id` (UUID)

**Request body:** Same fields as `POST /finance/accounts` (all required).

**Response `200 OK`:**

```json
{
  "account_id": "uuid",
  "name": "Updated Name",
  "type": "bank",
  "supported_currencies": ["MXN"],
  "default_currencies": ["MXN"]
}
```

**Error codes:**

| Code | Reason |
|------|--------|
| `403 Forbidden` | Account belongs to another user |
| `404 Not Found` | Account not found |

---

### DELETE /finance/accounts/{account_id}

Delete an account. Only allowed when the account has no transactions.

**Auth required:** Yes

**Path params:** `account_id` (UUID)

**Response `200 OK`:**

```json
{ "account_id": "uuid" }
```

**Error codes:**

| Code | Reason |
|------|--------|
| `401 Unauthorized` | Not authenticated |
| `403 Forbidden` | Account belongs to another user |
| `404 Not Found` | Account not found |
| `409 Conflict` | Account still has transactions |

---

### POST /finance/accounts/refresh-balances

Force recalculation and return of all account balances for the authenticated user.

**Auth required:** Yes

**Response `200 OK`:** Same as `GET /finance/accounts`.

---

### GET /finance/accounts/{account_id}/balance-history

Get monthly balance history (income, expenses, net) for a single account.

**Auth required:** Yes

**Path params:** `account_id` (UUID)

**Query params:**

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `months` | int | `6` | Number of past months to include |

**Response `200 OK`:**

```json
{
  "account_id": "uuid",
  "items": [
    {
      "year": 2026,
      "month": 4,
      "income": "5000.00",
      "expenses": "3200.00",
      "net": "1800.00"
    }
  ]
}
```

**Error codes:**

| Code | Reason |
|------|--------|
| `401 Unauthorized` | Not authenticated |
| `403 Forbidden` | Account belongs to another user |
| `404 Not Found` | Account not found |

---

## Transactions (`/api/finance/transactions`)

### GET /finance/transactions

List transactions for the authenticated user with optional filters and pagination.

**Auth required:** Yes (returns empty list if unauthenticated)

**Query params:**

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `year` | int | null | Filter by year |
| `month` | int | null | Filter by month |
| `account_id` | UUID | null | Filter by account |
| `tx_type` | string | null | `"income"`, `"expense"`, `"exchange"` |
| `category_id` | UUID | null | Filter by expense category |
| `min_amount` | string | null | Minimum amount (decimal string) |
| `max_amount` | string | null | Maximum amount (decimal string) |
| `limit` | int | `100` | Page size |
| `offset` | int | `0` | Page offset |

**Response `200 OK`:** Array of transaction objects.

```json
[
  {
    "transaction_id": "uuid",
    "type": "income",
    "amount": "5000.00",
    "currency": "MXN",
    "exchange_rate": "17.50",
    "category": "salary",
    "category_id": null,
    "description": null,
    "is_base_salary": true,
    "date": "2026-05-01",
    "notes": null,
    "related_transaction_id": null
  }
]
```

---

### GET /finance/transactions/recent

Get the latest N transactions for the authenticated user.

**Auth required:** Yes (returns empty list if unauthenticated)

**Query params:**

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `limit` | int | `10` | Number of results |

**Response `200 OK`:** Same shape as `GET /finance/transactions`.

---

### POST /finance/transactions/income

Register an income transaction linked to an account.

**Auth required:** Yes

**Request body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `account_id` | UUID | Yes | |
| `amount` | Decimal | Yes | |
| `currency` | Currency | Yes | |
| `exchange_rate` | Decimal | Yes | Rate to USD |
| `category` | IncomeCategory | Yes | e.g. `"salary"`, `"freelance"` |
| `is_base_salary` | bool | No (false) | Only one per month allowed |
| `date` | date | Yes | ISO 8601 (YYYY-MM-DD) |
| `notes` | string | No | |

**Response `201 Created`:**

```json
{
  "transaction_id": "uuid",
  "type": "income",
  "amount": "5000.00",
  "currency": "MXN",
  "is_base_salary": true,
  "notes": null
}
```

**Error codes:**

| Code | Reason |
|------|--------|
| `401 Unauthorized` | Not authenticated |
| `403 Forbidden` | Account belongs to another user |
| `404 Not Found` | Account not found |
| `409 Conflict` | A base salary entry already exists for this month |

---

### POST /finance/transactions/exchange

Register a currency exchange as a linked pair of transactions (one out, one in).

**Auth required:** Yes

**Request body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `source_account_id` | UUID | Yes | Account being debited |
| `dest_account_id` | UUID | Yes | Account being credited |
| `amount_out` | Decimal | Yes | Amount leaving source |
| `currency_out` | Currency | Yes | |
| `amount_in` | Decimal | Yes | Amount arriving at destination |
| `currency_in` | Currency | Yes | |
| `exchange_rate` | Decimal | Yes | |
| `date` | date | Yes | |
| `notes` | string | No | |

**Response `201 Created`:**

```json
{
  "tx_out_id": "uuid",
  "tx_in_id": "uuid",
  "amount_out": "1000.00",
  "currency_out": "MXN",
  "amount_in": "57.14",
  "currency_in": "USD"
}
```

**Error codes:**

| Code | Reason |
|------|--------|
| `403 Forbidden` | Account belongs to another user |
| `404 Not Found` | Source or destination account not found |
| `422 Unprocessable Entity` | Exchange math validation failed |

---

### PATCH /finance/transactions/{transaction_id}

Edit a transaction's fields. Requires password confirmation.

**Auth required:** Yes

**Path params:** `transaction_id` (UUID)

**Request body** (all optional except `password`):

| Field | Type | Description |
|-------|------|-------------|
| `password` | string | **Required** — current user password |
| `account_id` | UUID | null |
| `amount` | Decimal | null |
| `currency` | Currency | null |
| `date` | date | null |
| `description` | string | null |
| `exchange_rate` | Decimal | null |
| `notes` | string | null |
| `category_id` | UUID | null |

**Response `200 OK`:**

```json
{
  "transaction_id": "uuid",
  "account_id": "uuid",
  "amount": "5000.00",
  "currency": "MXN",
  "date": "2026-05-01",
  "description": null,
  "exchange_rate": "17.50",
  "notes": "updated note"
}
```

**Error codes:**

| Code | Reason |
|------|--------|
| `401 Unauthorized` | Not authenticated, or wrong password |
| `403 Forbidden` | Transaction belongs to another user |
| `404 Not Found` | Transaction not found |

---

### DELETE /finance/transactions/{transaction_id}

Delete a transaction. Exchange transaction pairs are deleted atomically. Requires password.

**Auth required:** Yes

**Path params:** `transaction_id` (UUID)

**Request body:**

| Field | Type | Required |
|-------|------|----------|
| `password` | string | Yes |

**Response `200 OK`:**

```json
{
  "transaction_id": "uuid",
  "related_transaction_id": "uuid-or-null"
}
```

**Error codes:**

| Code | Reason |
|------|--------|
| `401 Unauthorized` | Not authenticated, or wrong password |
| `403 Forbidden` | Transaction belongs to another user |
| `404 Not Found` | Transaction not found |

---

### POST /finance/transactions/{transaction_id}/reverse

Reverse an income or expense by creating a counter-transaction. Requires password.

**Auth required:** Yes

**Path params:** `transaction_id` (UUID)

**Request body:**

| Field | Type | Required |
|-------|------|----------|
| `password` | string | Yes |

**Response `201 Created`:**

```json
{
  "original_transaction_id": "uuid",
  "reversal_transaction_id": "uuid",
  "amount": "5000.00",
  "currency": "MXN",
  "date": "2026-05-15"
}
```

**Error codes:**

| Code | Reason |
|------|--------|
| `401 Unauthorized` | Not authenticated, or wrong password |
| `403 Forbidden` | Transaction belongs to another user |
| `404 Not Found` | Transaction not found |
| `422 Unprocessable Entity` | Transaction type cannot be reversed (e.g. exchange legs) |

---

## Expense Categories (`/api/finance/categories`)

### GET /finance/categories

List all expense categories for the authenticated user.

**Auth required:** Yes (returns empty list if unauthenticated)

**Response `200 OK`:**

```json
[
  {
    "category_id": "uuid",
    "name": "Groceries",
    "is_fixed_expense": false,
    "default_amount_usd": "0.00"
  }
]
```

---

### POST /finance/categories

Create a new expense category.

**Auth required:** Yes

**Request body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Unique per user |
| `is_fixed_expense` | bool | No (false) | Fixed vs variable |
| `default_amount_usd` | Decimal | No (0) | Default budget hint |

**Response `201 Created`:** Same shape as list item.

**Error codes:**

| Code | Reason |
|------|--------|
| `409 Conflict` | Category name already exists |

---

## Expenses (`/api/finance/expenses`)

### POST /finance/expenses

Categorize and record an expense entry (lightweight — no account debit).

**Auth required:** Yes

**Request body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `description` | string | Yes | |
| `amount` | Decimal | Yes | |
| `currency` | string | No (`"MXN"`) | |
| `date` | date | Yes | |
| `category` | string | Yes | Category name |
| `invoice_id` | UUID | No | Link to an invoice |

**Response `201 Created`:**

```json
{
  "expense_id": "uuid",
  "category": "Groceries"
}
```

---

### POST /finance/expenses/register

Register an expense transaction that debits an account balance.

**Auth required:** Yes

**Request body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `account_id` | UUID | Yes | Account to debit |
| `category_name` | string | Yes | Must exist |
| `amount` | Decimal | Yes | |
| `currency` | Currency | Yes | |
| `exchange_rate` | Decimal | Yes | Rate to USD |
| `date` | date | Yes | |
| `description` | string | No | |

**Response `201 Created`:**

```json
{
  "transaction_id": "uuid",
  "amount": "250.00",
  "currency": "MXN",
  "category_id": "uuid",
  "description": null
}
```

**Error codes:**

| Code | Reason |
|------|--------|
| `401 Unauthorized` | Not authenticated |
| `403 Forbidden` | Account belongs to another user |
| `404 Not Found` | Account or category not found |

---

## Invoices (`/api/finance/invoices`)

### POST /finance/invoices

Create a new unpaid invoice.

**Auth required:** Yes

**Request body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `vendor` | string | Yes | |
| `amount` | Decimal | Yes | |
| `currency` | string | No (`"MXN"`) | |
| `due_date` | date | Yes | |

**Response `201 Created`:**

```json
{
  "invoice_id": "uuid",
  "vendor": "CFE",
  "amount": "350.00",
  "currency": "MXN",
  "status": "pending"
}
```

**Error codes:**

| Code | Reason |
|------|--------|
| `401 Unauthorized` | Not authenticated |

---

### POST /finance/invoices/{invoice_id}/process

Mark an invoice as paid. Optionally creates an expense transaction against an account.

**Auth required:** Yes

**Path params:** `invoice_id` (UUID)

**Query params:**

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `account_id` | UUID | null | If provided, creates a linked expense transaction |

**Response `200 OK`:**

```json
{
  "invoice_id": "uuid",
  "status": "paid",
  "transaction_id": "uuid-or-null"
}
```

**Error codes:**

| Code | Reason |
|------|--------|
| `401 Unauthorized` | Not authenticated |
| `403 Forbidden` | Invoice or account belongs to another user |
| `404 Not Found` | Invoice or account not found |
| `409 Conflict` | Invoice already paid |

---

### GET /finance/invoices/upcoming

Get upcoming unpaid invoices ordered by due date.

**Auth required:** Yes

**Response `200 OK`:**

```json
{
  "invoices": [
    {
      "invoice_id": "uuid",
      "vendor": "CFE",
      "amount": "350.00",
      "currency": "MXN",
      "due_date": "2026-05-20",
      "days_until_due": 5,
      "is_overdue": false
    }
  ]
}
```

**Error codes:**

| Code | Reason |
|------|--------|
| `401 Unauthorized` | Not authenticated |

---

## Budget (`/api/finance/budget`)

### POST /finance/budget

Create a monthly budget plan for a given year/month.

**Auth required:** Yes

**Request body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `year` | int | Yes | |
| `month` | int | Yes | 1–12 |
| `budget_usd` | Decimal | No (`500`) | Total spending budget |
| `income_usd` | Decimal | No | Expected income |

**Response `201 Created`:**

```json
{
  "plan_id": "uuid",
  "user_id": "uuid",
  "year": 2026,
  "month": 5,
  "budget_usd": "2000.00",
  "income_usd": "4000.00"
}
```

**Error codes:**

| Code | Reason |
|------|--------|
| `401 Unauthorized` | Not authenticated |
| `409 Conflict` | Budget plan already exists for this year/month |

---

### GET /finance/budget

Get the budget plan with planned vs actual breakdown (per category).

**Auth required:** Yes

**Query params:**

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `year` | int | current year | |
| `month` | int | current month | |

**Response `200 OK`:**

```json
{
  "plan_id": "uuid",
  "user_id": "uuid",
  "year": 2026,
  "month": 5,
  "budget_usd": "2000.00",
  "income_usd": "4000.00",
  "total_planned_usd": "1800.00",
  "total_actual_usd": "1450.00",
  "items": [
    {
      "item_id": "uuid",
      "category_id": "uuid",
      "category_name": "Groceries",
      "planned_usd": "300.00",
      "actual_usd": "280.00",
      "deviation_usd": "-20.00",
      "deviation_pct": "-6.67",
      "over_budget": false
    }
  ],
  "rule_50_30_20": { "needs": "50", "wants": "30", "savings": "20" }
}
```

**Error codes:**

| Code | Reason |
|------|--------|
| `401 Unauthorized` | Not authenticated |
| `404 Not Found` | No budget plan for the given period |

---

### GET /finance/budget/summary

Lightweight budget vs actual summary, useful for dashboard widgets.

**Auth required:** Yes

**Query params:** Same as `GET /finance/budget` (`year`, `month`).

**Response `200 OK`:**

```json
{
  "plan_id": "uuid",
  "year": 2026,
  "month": 5,
  "budget_usd": "2000.00",
  "total_planned_usd": "1800.00",
  "total_actual_usd": "1450.00",
  "pct_executed": "80.56",
  "over_budget_categories": 1
}
```

**Error codes:**

| Code | Reason |
|------|--------|
| `401 Unauthorized` | Not authenticated |
| `404 Not Found` | No budget plan for the given period |

---

### POST /finance/budget/{plan_id}/items

Add or update a planned spending item in a budget plan.

**Auth required:** Yes

**Path params:** `plan_id` (UUID)

**Request body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `category_id` | UUID | No | null = savings bucket |
| `planned_amount_usd` | Decimal | Yes | |

**Response `200 OK`:**

```json
{
  "item_id": "uuid",
  "plan_id": "uuid",
  "category_id": "uuid-or-null",
  "planned_amount_usd": "300.00"
}
```

**Error codes:**

| Code | Reason |
|------|--------|
| `401 Unauthorized` | Not authenticated |
| `403 Forbidden` | Plan belongs to another user |
| `404 Not Found` | Budget plan not found |

---

### DELETE /finance/budget/{plan_id}/items/{category_id}

Remove a planned item by category.

**Auth required:** Yes

**Path params:** `plan_id` (UUID), `category_id` (UUID)

**Response `200 OK`:** `{}` (empty dict on success)

**Error codes:**

| Code | Reason |
|------|--------|
| `401 Unauthorized` | Not authenticated |
| `403 Forbidden` | Plan belongs to another user |
| `404 Not Found` | Plan or item not found |

---

### DELETE /finance/budget/{plan_id}/items/savings-bucket

Remove the savings bucket planned item (the item with `category_id = null`).

**Auth required:** Yes

**Path params:** `plan_id` (UUID)

**Response `200 OK`:** `{}` (empty dict on success)

**Error codes:** Same as `DELETE /finance/budget/{plan_id}/items/{category_id}`.

---

### POST /finance/budget/{plan_id}/copy-from-previous

Copy all planned items from the previous calendar month into this plan.

**Auth required:** Yes

**Path params:** `plan_id` (UUID)

**Response `200 OK`:** Same shape as `POST /finance/budget` response (`BudgetPlanCreatedSchema`).

**Error codes:**

| Code | Reason |
|------|--------|
| `401 Unauthorized` | Not authenticated |
| `403 Forbidden` | Plan belongs to another user |
| `404 Not Found` | Plan or previous plan not found |

---

## Savings (`/api/finance/savings`)

### GET /finance/savings/goals

List all savings goals for the authenticated user.

**Auth required:** Yes (returns empty list if unauthenticated)

**Response `200 OK`:**

```json
[
  {
    "goal_id": "uuid",
    "motive": "Emergency fund",
    "target_amount_usd": "5000.00",
    "deposited_usd": "1200.00",
    "expected_monthly_contribution": "200.00",
    "is_completed": false
  }
]
```

---

### POST /finance/savings/goals

Create a new savings goal.

**Auth required:** Yes

**Request body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `motive` | string | Yes | Goal description |
| `target_amount_usd` | Decimal | Yes | |
| `expected_monthly_contribution` | Decimal | No (`0`) | |

**Response `201 Created`:**

```json
{
  "goal_id": "uuid",
  "user_id": "uuid",
  "motive": "Emergency fund",
  "target_amount_usd": "5000.00",
  "expected_monthly_contribution": "200.00",
  "is_completed": false
}
```

---

### PUT /finance/savings/goals/{goal_id}

Edit a savings goal's motive, target amount, or expected monthly contribution.

**Auth required:** Yes

**Path params:** `goal_id` (UUID)

**Request body** (all optional):

| Field | Type | Description |
|-------|------|-------------|
| `motive` | string | null |
| `target_amount_usd` | Decimal | null |
| `expected_monthly_contribution` | Decimal | null |

**Response `200 OK`:** Same shape as `GET /finance/savings/goals` list item (`SavingsGoalSummaryResponseSchema`).

**Error codes:**

| Code | Reason |
|------|--------|
| `404 Not Found` | Goal not found |

---

### GET /finance/savings/goals/{goal_id}/contributions

Get all deposits/contributions for a specific savings goal.

**Auth required:** Yes (returns empty list if unauthenticated or goal not found)

**Path params:** `goal_id` (UUID)

**Response `200 OK`:**

```json
[
  {
    "deposit_id": "uuid",
    "amount": "200.00",
    "currency": "USD",
    "date": "2026-05-01",
    "notes": null
  }
]
```

---

### POST /finance/savings/deposits

Deposit an amount to a savings goal. Only USD/USDT accounts are accepted.

**Auth required:** Yes

**Request body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `goal_id` | UUID | Yes | |
| `account_id` | UUID | Yes | Must hold USD/USDT |
| `amount` | Decimal | Yes | |
| `currency` | Currency | Yes | |
| `date` | date | Yes | |
| `notes` | string | No | |

**Response `201 Created`:**

```json
{
  "deposit_id": "uuid",
  "goal_id": "uuid",
  "amount": "200.00",
  "currency": "USD"
}
```

**Error codes:**

| Code | Reason |
|------|--------|
| `404 Not Found` | Goal not found |
| `422 Unprocessable Entity` | Account currency is not USD/USDT |

---

### DELETE /finance/savings/deposits/{deposit_id}

Delete a savings deposit by ID.

**Auth required:** Yes

**Path params:** `deposit_id` (UUID)

**Response `200 OK`:**

```json
{
  "deposit_id": "uuid",
  "deleted": true
}
```

**Error codes:**

| Code | Reason |
|------|--------|
| `401 Unauthorized` | Not authenticated |
| `403 Forbidden` | Deposit belongs to another user |
| `404 Not Found` | Deposit not found |

---

### GET /finance/savings/projection

Get completion projections for each active savings goal.

**Auth required:** Yes (returns empty list if unauthenticated)

**Response `200 OK`:**

```json
[
  {
    "goal_id": "uuid",
    "motive": "Emergency fund",
    "target_amount_usd": "5000.00",
    "deposited_usd": "1200.00",
    "remaining_usd": "3800.00",
    "expected_monthly_contribution": "200.00",
    "months_to_completion": 19,
    "projected_completion_date": "2027-12-01",
    "deadline": null,
    "priority": 1
  }
]
```

---

### GET /finance/savings/rate

Get monthly savings rate for the last N months.

**Auth required:** Yes

**Query params:**

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `months` | int | `6` | |

**Response `200 OK`:**

```json
{
  "months": [
    {
      "year": 2026,
      "month": 5,
      "income_usd": "4000.00",
      "savings_usd": "800.00",
      "rate_pct": "20.00"
    }
  ],
  "avg_rate_pct": "18.50"
}
```

**Error codes:**

| Code | Reason |
|------|--------|
| `401 Unauthorized` | Not authenticated |

---

### GET /finance/savings/dashboard

Aggregated savings dashboard: goal progress, monthly saved amount, savings rate.

**Auth required:** Yes

**Response `200 OK`:**

```json
{
  "year": 2026,
  "month": 5,
  "saved_this_month_usd": "800.00",
  "savings_rate_pct": "20.00",
  "active_goals_count": 2,
  "completed_goals_count": 1,
  "goals": [
    {
      "goal_id": "uuid",
      "motive": "Emergency fund",
      "target_amount_usd": "5000.00",
      "deposited_usd": "1200.00",
      "deposited_this_month_usd": "200.00",
      "progress_pct": "24.00",
      "is_completed": false,
      "deadline": null,
      "priority": 1
    }
  ]
}
```

**Error codes:**

| Code | Reason |
|------|--------|
| `401 Unauthorized` | Not authenticated |

---

### POST /finance/savings/distribution

Define a monthly savings distribution plan across multiple goals.

**Auth required:** Yes

**Request body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `year` | int | Yes | |
| `month` | int | Yes | |
| `items` | array | Yes | List of `{goal_id, planned_usd}` objects |

**Response `200 OK`:**

```json
{
  "plan_id": "uuid",
  "year": 2026,
  "month": 5,
  "total_planned_usd": "600.00",
  "items": [
    { "goal_id": "uuid", "planned_usd": "400.00" },
    { "goal_id": "uuid", "planned_usd": "200.00" }
  ]
}
```

**Error codes:**

| Code | Reason |
|------|--------|
| `401 Unauthorized` | Not authenticated |
| `404 Not Found` | One or more goal IDs not found |

---

### GET /finance/savings/distribution/suggest

Get AI-style suggestions for distributing a monthly savings budget across active goals (priority-weighted).

**Auth required:** Yes

**Query params:**

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `monthly_budget_usd` | string | `"500"` | Total budget to distribute (decimal string) |

**Response `200 OK`:**

```json
{
  "monthly_budget_usd": "500.00",
  "suggestions": [
    { "goal_id": "uuid", "motive": "Emergency fund", "suggested_usd": "300.00" },
    { "goal_id": "uuid", "motive": "Vacation", "suggested_usd": "200.00" }
  ]
}
```

**Error codes:**

| Code | Reason |
|------|--------|
| `401 Unauthorized` | Not authenticated |

---

## Dashboard & Reports

### GET /finance/dashboard

Main dashboard snapshot — fetches all key widgets in a single call.

**Auth required:** Yes

**Response `200 OK`:**

```json
{
  "net_worth_usd": "15000.00",
  "monthly_summary": { "year": 2026, "month": 5, "total_income_usd": "4000.00", "total_expenses_usd": "1450.00", "total_savings_usd": "800.00", "budget_usd": "2000.00", "balance_usd": "1750.00" },
  "budget_status": { "plan_id": "uuid", "year": 2026, "month": 5, "budget_usd": "2000.00", "total_planned_usd": "1800.00", "total_actual_usd": "1450.00", "pct_executed": "80.56", "over_budget_categories": 0 },
  "savings_overview": { "...": "SavingsDashboardSchema" },
  "upcoming_invoices": []
}
```

**Error codes:**

| Code | Reason |
|------|--------|
| `401 Unauthorized` | Not authenticated |

---

### GET /finance/summary/current

Get the financial summary (income, expenses, savings, balance) for a specific month.

**Auth required:** Yes

**Query params:**

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `year` | int | current year | |
| `month` | int | current month | |

**Response `200 OK`:**

```json
{
  "year": 2026,
  "month": 5,
  "total_income_usd": "4000.00",
  "total_expenses_usd": "1450.00",
  "total_savings_usd": "800.00",
  "budget_usd": "2000.00",
  "balance_usd": "1750.00"
}
```

**Error codes:**

| Code | Reason |
|------|--------|
| `401 Unauthorized` | Not authenticated |

---

### GET /finance/summary/current/extended

Extended monthly summary that also includes savings rate, budget execution %, and goal counts.

**Auth required:** Yes

**Query params:** Same as `GET /finance/summary/current`.

**Response `200 OK`:**

```json
{
  "year": 2026,
  "month": 5,
  "total_income_usd": "4000.00",
  "total_expenses_usd": "1450.00",
  "total_savings_usd": "800.00",
  "budget_usd": "2000.00",
  "balance_usd": "1750.00",
  "savings_rate_pct": "20.00",
  "budget_execution_pct": "72.50",
  "goals_active_count": 2,
  "goals_completed_this_month": 0
}
```

**Error codes:**

| Code | Reason |
|------|--------|
| `401 Unauthorized` | Not authenticated |

---

### GET /finance/net-worth

Total net worth broken down by account type.

**Auth required:** Yes

**Response `200 OK`:**

```json
{
  "total_usd": "15000.00",
  "cash_usd": "500.00",
  "bank_usd": "12000.00",
  "wallet_usd": "2500.00",
  "accounts": [
    {
      "account_id": "uuid",
      "name": "BBVA Checking",
      "type": "bank",
      "balances": { "MXN": "210000.00" },
      "usd_equivalent": "12000.00"
    }
  ]
}
```

**Error codes:**

| Code | Reason |
|------|--------|
| `401 Unauthorized` | Not authenticated |

---

### GET /finance/trend

Monthly income/expenses/savings trend for the last N months.

**Auth required:** Yes

**Query params:**

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `months` | int | `6` | |

**Response `200 OK`:**

```json
{
  "months": [
    {
      "year": 2026,
      "month": 5,
      "income_usd": "4000.00",
      "expenses_usd": "1450.00",
      "savings_usd": "800.00",
      "balance_usd": "1750.00"
    }
  ]
}
```

**Error codes:**

| Code | Reason |
|------|--------|
| `401 Unauthorized` | Not authenticated |

---

### GET /finance/expenses/breakdown

Expense breakdown by category for a given month.

**Auth required:** Yes

**Query params:**

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `year` | int | current year | |
| `month` | int | current month | |

**Response `200 OK`:**

```json
{
  "year": 2026,
  "month": 5,
  "total_expenses_usd": "1450.00",
  "items": [
    {
      "category_id": "uuid",
      "category_name": "Groceries",
      "total_usd": "280.00",
      "pct_of_total": "19.31"
    }
  ]
}
```

**Error codes:**

| Code | Reason |
|------|--------|
| `401 Unauthorized` | Not authenticated |

---

### GET /finance/reports/monthly

Generate a monthly expenses and invoices report.

**Auth required:** No (no session guard in view)

**Query params:**

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `year` | int | Yes | |
| `month` | int | Yes | |

**Response `200 OK`:**

```json
{
  "year": 2026,
  "month": 5,
  "total_expenses": "1450.00",
  "total_invoices": 5,
  "unpaid_invoices": 2,
  "expenses_by_category": {
    "Groceries": "280.00",
    "Transport": "150.00"
  }
}
```

---

### GET /finance/reports/annual

Annual report with per-month breakdown, totals, and peak months.

**Auth required:** Yes

**Query params:**

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `year` | int | current year | |

**Response `200 OK`:**

```json
{
  "year": 2026,
  "months": [
    { "month": 1, "income_usd": "4000.00", "expenses_usd": "1300.00", "savings_usd": "600.00", "balance_usd": "2100.00" }
  ],
  "total_income_usd": "18000.00",
  "total_expenses_usd": "7200.00",
  "total_savings_usd": "3600.00",
  "peak_expense_month": 12,
  "peak_savings_month": 6,
  "dominant_category_by_quarter": { "Q1": "Groceries", "Q2": "Transport", "Q3": null, "Q4": null }
}
```

**Error codes:**

| Code | Reason |
|------|--------|
| `401 Unauthorized` | Not authenticated |

---

### GET /finance/cashflow/calendar

Daily cashflow breakdown for a given month.

**Auth required:** Yes

**Query params:**

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `year` | int | current year | |
| `month` | int | current month | |

**Response `200 OK`:**

```json
{
  "year": 2026,
  "month": 5,
  "days": [
    {
      "day": 1,
      "date": "2026-05-01",
      "income_usd": "4000.00",
      "expenses_usd": "0.00",
      "balance_usd": "4000.00"
    }
  ]
}
```

**Error codes:**

| Code | Reason |
|------|--------|
| `401 Unauthorized` | Not authenticated |
