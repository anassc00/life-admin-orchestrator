from decimal import Decimal
from http import HTTPStatus
from uuid import UUID

from ninja import Body, Router

from adapters.api.finance.schemas import (
    AccountBalanceHistoryResponseSchema,
    AccountDeletedResponseSchema,
    AccountRegisteredResponseSchema,
    AccountSummarySchema,
    AccountUpdatedResponseSchema,
    CategorizeExpenseRequest,
    CreateExpenseCategoryRequest,
    CreateInvoiceRequest,
    CreateSavingsGoalRequest,
    CurrencyExchangeRegisteredResponseSchema,
    DeleteTransactionRequest,
    DepositToSavingsRequest,
    EditSavingsGoalRequest,
    EditTransactionRequest,
    ExpenseCategorizedResponseSchema,
    ExpenseCategoryResponseSchema,
    ExpenseRegisteredResponseSchema,
    IncomeRegisteredResponseSchema,
    InvoiceCreatedResponseSchema,
    InvoiceProcessedResponseSchema,
    MonthlyFinancialSummarySchema,
    MonthlyReportResponseSchema,
    RegisterAccountRequest,
    RegisterCurrencyExchangeRequest,
    RegisterExpenseRequest,
    RegisterIncomeRequest,
    ReverseTransactionRequest,
    SavingsDepositContributionSchema,
    SavingsDepositResponseSchema,
    SavingsGoalResponseSchema,
    SavingsGoalSummaryResponseSchema,
    TransactionDeletedResponseSchema,
    TransactionEditedResponseSchema,
    TransactionListItemSchema,
    TransactionReversedResponseSchema,
    UpdateAccountRequest,
)
from adapters.api.users.schemas import ErrorResponse
from application.dtos.finance import (
    CategorizeExpenseCommand,
    CreateExpenseCategoryCommand,
    CreateInvoiceCommand,
    CreateSavingsGoalCommand,
    DeleteAccountCommand,
    DeleteTransactionCommand,
    DepositToSavingsCommand,
    EditSavingsGoalCommand,
    EditTransactionCommand,
    GenerateMonthlyReportQuery,
    GetAccountBalanceHistoryQuery,
    GetAccountsByUserQuery,
    GetExpenseCategoriesQuery,
    GetMonthlyFinancialSummaryQuery,
    GetSavingsGoalsQuery,
    GetTransactionsByUserQuery,
    ProcessInvoiceCommand,
    RegisterAccountCommand,
    RegisterCurrencyExchangeCommand,
    RegisterExpenseCommand,
    RegisterIncomeCommand,
    ReverseTransactionCommand,
    UpdateAccountCommand,
)
from domain.exceptions.finance import (
    AccountAccessForbiddenError,
    AccountAlreadyExistsError,
    AccountHasTransactionsError,
    AccountNotFoundError,
    DuplicateBaseSalaryError,
    ExpenseCategoryAlreadyExistsError,
    ExpenseCategoryNotFoundError,
    InvalidEditionCredentialsError,
    InvalidExchangeMathError,
    InvoiceAccessForbiddenError,
    InvoiceAlreadyPaidError,
    InvoiceNotFoundError,
    SavingsDepositCurrencyError,
    SavingsGoalNotFoundError,
    TransactionNotFoundError,
    TransactionReversalNotSupportedError,
    UnauthorizedEditError,
)
from infrastructure.di import (
    get_account_balance_history_use_case,
    get_accounts_by_user_use_case,
    get_categorize_expense_use_case,
    get_create_expense_category_use_case,
    get_create_invoice_use_case,
    get_create_savings_goal_use_case,
    get_delete_account_use_case,
    get_delete_transaction_use_case,
    get_deposit_to_savings_use_case,
    get_edit_savings_goal_use_case,
    get_edit_transaction_use_case,
    get_expense_categories_use_case,
    get_generate_monthly_report_use_case,
    get_monthly_financial_summary_use_case,
    get_process_invoice_use_case,
    get_register_account_use_case,
    get_register_currency_exchange_use_case,
    get_register_expense_use_case,
    get_register_income_use_case,
    get_reverse_transaction_use_case,
    get_savings_goal_contributions_use_case,
    get_savings_goals_use_case,
    get_transactions_by_user_use_case,
    get_update_account_use_case,
)

router = Router(tags=["Finance"])


@router.post(
    "/invoices",
    response={
        HTTPStatus.CREATED: InvoiceCreatedResponseSchema,
        HTTPStatus.UNAUTHORIZED: ErrorResponse,
    },
    summary="Create a new invoice",
)
def create_invoice(request, payload: CreateInvoiceRequest):
    user_id_str = request.session.get("user_id")
    if not user_id_str:
        return HTTPStatus.UNAUTHORIZED, ErrorResponse(detail="Not authenticated.")
    from uuid import UUID

    user_id = UUID(user_id_str)
    uc = get_create_invoice_use_case()
    result = uc.execute(
        CreateInvoiceCommand(
            user_id=user_id,
            vendor=payload.vendor,
            amount=payload.amount,
            currency=payload.currency,
            due_date=payload.due_date,
        )
    )
    return HTTPStatus.CREATED, result.model_dump()


@router.post(
    "/invoices/{invoice_id}/process",
    response={
        HTTPStatus.OK: InvoiceProcessedResponseSchema,
        HTTPStatus.UNAUTHORIZED: ErrorResponse,
        HTTPStatus.FORBIDDEN: ErrorResponse,
        HTTPStatus.NOT_FOUND: ErrorResponse,
        HTTPStatus.CONFLICT: ErrorResponse,
    },
    summary="Mark an invoice as paid (creates an expense transaction if account_id is provided)",
)
def process_invoice(request, invoice_id: UUID, account_id: UUID = None):
    user_id_str = request.session.get("user_id")
    if not user_id_str:
        return HTTPStatus.UNAUTHORIZED, ErrorResponse(detail="Not authenticated.")
    from uuid import UUID as _UUID

    user_id = _UUID(user_id_str)
    uc = get_process_invoice_use_case()
    try:
        result = uc.execute(
            ProcessInvoiceCommand(
                user_id=user_id,
                invoice_id=invoice_id,
                account_id=account_id,
            )
        )
        return HTTPStatus.OK, result.model_dump()
    except InvoiceNotFoundError as exc:
        return HTTPStatus.NOT_FOUND, ErrorResponse(detail=str(exc))
    except InvoiceAccessForbiddenError as exc:
        return HTTPStatus.FORBIDDEN, ErrorResponse(detail=str(exc))
    except InvoiceAlreadyPaidError as exc:
        return HTTPStatus.CONFLICT, ErrorResponse(detail=str(exc))
    except AccountNotFoundError as exc:
        return HTTPStatus.NOT_FOUND, ErrorResponse(detail=str(exc))
    except AccountAccessForbiddenError as exc:
        return HTTPStatus.FORBIDDEN, ErrorResponse(detail=str(exc))


@router.post(
    "/expenses",
    response={
        HTTPStatus.CREATED: ExpenseCategorizedResponseSchema,
        HTTPStatus.UNAUTHORIZED: ErrorResponse,
    },
    summary="Categorize and record an expense entry",
)
def categorize_expense(request, payload: CategorizeExpenseRequest):
    user_id_str = request.session.get("user_id")
    if not user_id_str:
        return HTTPStatus.UNAUTHORIZED, ErrorResponse(detail="Not authenticated.")
    from uuid import UUID

    user_id = UUID(user_id_str)
    uc = get_categorize_expense_use_case()
    result = uc.execute(
        CategorizeExpenseCommand(
            user_id=user_id,
            description=payload.description,
            amount=payload.amount,
            currency=payload.currency,
            date=payload.date,
            category=payload.category,
            invoice_id=payload.invoice_id,
        )
    )
    return HTTPStatus.CREATED, result.model_dump()


@router.get("/reports/monthly", response=MonthlyReportResponseSchema)
def monthly_report(request, year: int, month: int):
    uc = get_generate_monthly_report_use_case()
    return uc.execute(GenerateMonthlyReportQuery(year=year, month=month)).model_dump()


@router.get(
    "/summary/current",
    response={
        HTTPStatus.OK: MonthlyFinancialSummarySchema,
        HTTPStatus.UNAUTHORIZED: ErrorResponse,
    },
    summary="Get the financial summary (income, expenses, savings) for a specific month (defaults to current month)",
)
def monthly_financial_summary(request, year: int = None, month: int = None):
    from datetime import date

    user_id_str = request.session.get("user_id")
    if not user_id_str:
        return HTTPStatus.UNAUTHORIZED, ErrorResponse(detail="Not authenticated.")
    from uuid import UUID

    today = date.today()
    query_year = year if year is not None else today.year
    query_month = month if month is not None else today.month

    uc = get_monthly_financial_summary_use_case()
    result = uc.execute(
        GetMonthlyFinancialSummaryQuery(
            user_id=UUID(user_id_str),
            year=query_year,
            month=query_month,
        )
    )
    return HTTPStatus.OK, result.model_dump()


@router.get(
    "/transactions",
    response=list[TransactionListItemSchema],
    summary="List transactions for the current user with optional filters and pagination",
)
def list_transactions(
    request,
    year: int = None,
    month: int = None,
    account_id: UUID = None,
    tx_type: str = None,
    category_id: UUID = None,
    min_amount: str = None,
    max_amount: str = None,
    limit: int = 100,
    offset: int = 0,
):
    user_id_str = request.session.get("user_id")
    if not user_id_str:
        return []
    from decimal import Decimal
    from uuid import UUID as _UUID

    from domain.entities.finance import TransactionType as TxType

    parsed_tx_type = TxType(tx_type) if tx_type else None
    parsed_min = Decimal(min_amount) if min_amount else None
    parsed_max = Decimal(max_amount) if max_amount else None

    uc = get_transactions_by_user_use_case()
    results = uc.execute(
        GetTransactionsByUserQuery(
            user_id=_UUID(user_id_str),
            year=year,
            month=month,
            account_id=account_id,
            tx_type=parsed_tx_type,
            category_id=category_id,
            min_amount=parsed_min,
            max_amount=parsed_max,
            limit=limit,
            offset=offset,
        )
    )
    return [r.model_dump() for r in results]


# --- Accounts ---


@router.get(
    "/accounts",
    response=list[AccountSummarySchema],
    summary="List all accounts for the current user",
)
def list_accounts(request):
    user_id_str = request.session.get("user_id")
    if not user_id_str:
        return []
    from uuid import UUID

    user_id = UUID(user_id_str)
    uc = get_accounts_by_user_use_case()
    results = uc.execute(GetAccountsByUserQuery(user_id=user_id))
    return [r.model_dump() for r in results]


@router.post(
    "/accounts/refresh-balances",
    response={
        HTTPStatus.OK: list[AccountSummarySchema],
    },
    summary="Recalculate and return all account balances",
)
def refresh_account_balances(request):
    """Force recalculation of all account balances for the current user."""
    user_id_str = request.session.get("user_id")
    if not user_id_str:
        return HTTPStatus.UNAUTHORIZED, ErrorResponse(detail="Not authenticated.")
    from uuid import UUID

    uc = get_accounts_by_user_use_case()
    results = uc.execute(GetAccountsByUserQuery(user_id=UUID(user_id_str)))
    return [r.model_dump() for r in results]


@router.patch(
    "/accounts/{account_id}",
    response={
        HTTPStatus.OK: AccountUpdatedResponseSchema,
        HTTPStatus.NOT_FOUND: ErrorResponse,
        HTTPStatus.FORBIDDEN: ErrorResponse,
    },
    summary="Update an existing account",
)
def update_account(request, account_id: UUID, payload: UpdateAccountRequest):
    user_id_str = request.session.get("user_id")
    if not user_id_str:
        return HTTPStatus.UNAUTHORIZED, ErrorResponse(detail="Not authenticated.")
    from uuid import UUID as _UUID

    user_id = _UUID(user_id_str)
    uc = get_update_account_use_case()
    try:
        result = uc.execute(
            UpdateAccountCommand(
                user_id=user_id,
                account_id=account_id,
                name=payload.name,
                type=payload.type,
                supported_currencies=payload.supported_currencies,
                default_currencies=payload.default_currencies,
            )
        )
        return HTTPStatus.OK, result.model_dump()
    except AccountNotFoundError as exc:
        return HTTPStatus.NOT_FOUND, ErrorResponse(detail=str(exc))
    except AccountAccessForbiddenError as exc:
        return HTTPStatus.FORBIDDEN, ErrorResponse(detail=str(exc))


@router.delete(
    "/accounts/{account_id}",
    response={
        HTTPStatus.OK: AccountDeletedResponseSchema,
        HTTPStatus.NOT_FOUND: ErrorResponse,
        HTTPStatus.FORBIDDEN: ErrorResponse,
        HTTPStatus.CONFLICT: ErrorResponse,
        HTTPStatus.UNAUTHORIZED: ErrorResponse,
    },
    summary="Delete an account (only allowed when it has no transactions)",
)
def delete_account(request, account_id: UUID):
    user_id_str = request.session.get("user_id")
    if not user_id_str:
        return HTTPStatus.UNAUTHORIZED, ErrorResponse(detail="Not authenticated.")
    from uuid import UUID as _UUID

    user_id = _UUID(user_id_str)
    uc = get_delete_account_use_case()
    try:
        result = uc.execute(DeleteAccountCommand(user_id=user_id, account_id=account_id))
        return HTTPStatus.OK, result.model_dump()
    except AccountNotFoundError as exc:
        return HTTPStatus.NOT_FOUND, ErrorResponse(detail=str(exc))
    except AccountAccessForbiddenError as exc:
        return HTTPStatus.FORBIDDEN, ErrorResponse(detail=str(exc))
    except AccountHasTransactionsError as exc:
        return HTTPStatus.CONFLICT, ErrorResponse(detail=str(exc))


@router.get(
    "/accounts/{account_id}/balance-history",
    response={
        HTTPStatus.OK: AccountBalanceHistoryResponseSchema,
        HTTPStatus.NOT_FOUND: ErrorResponse,
        HTTPStatus.FORBIDDEN: ErrorResponse,
        HTTPStatus.UNAUTHORIZED: ErrorResponse,
    },
    summary="Get monthly balance history for an account (default: last 6 months)",
)
def get_account_balance_history(request, account_id: UUID, months: int = 6):
    user_id_str = request.session.get("user_id")
    if not user_id_str:
        return HTTPStatus.UNAUTHORIZED, ErrorResponse(detail="Not authenticated.")
    from uuid import UUID as _UUID

    user_id = _UUID(user_id_str)
    uc = get_account_balance_history_use_case()
    try:
        result = uc.execute(
            GetAccountBalanceHistoryQuery(
                user_id=user_id, account_id=account_id, months=months
            )
        )
        return HTTPStatus.OK, result.model_dump()
    except AccountNotFoundError as exc:
        return HTTPStatus.NOT_FOUND, ErrorResponse(detail=str(exc))
    except AccountAccessForbiddenError as exc:
        return HTTPStatus.FORBIDDEN, ErrorResponse(detail=str(exc))


@router.post(
    "/accounts",
    response={
        HTTPStatus.CREATED: AccountRegisteredResponseSchema,
        HTTPStatus.CONFLICT: ErrorResponse,
    },
    summary="Create a new account (wallet/cash/bank)",
)
def register_account(request, payload: RegisterAccountRequest):
    user_id_str = request.session.get("user_id")
    if not user_id_str:
        return HTTPStatus.UNAUTHORIZED, ErrorResponse(detail="Not authenticated.")
    from uuid import UUID

    user_id = UUID(user_id_str)
    uc = get_register_account_use_case()
    try:
        result = uc.execute(
            RegisterAccountCommand(
                user_id=user_id,
                name=payload.name,
                type=payload.type,
                supported_currencies=payload.supported_currencies,
                default_currencies=payload.default_currencies,
            )
        )
        return HTTPStatus.CREATED, result.model_dump()
    except AccountAlreadyExistsError as exc:
        return HTTPStatus.CONFLICT, ErrorResponse(detail=str(exc))


# --- Income ---


@router.post(
    "/transactions/income",
    response={
        HTTPStatus.CREATED: IncomeRegisteredResponseSchema,
        HTTPStatus.NOT_FOUND: ErrorResponse,
        HTTPStatus.FORBIDDEN: ErrorResponse,
        HTTPStatus.CONFLICT: ErrorResponse,
        HTTPStatus.UNAUTHORIZED: ErrorResponse,
    },
    summary="Register an income transaction",
)
def register_income(request, payload: RegisterIncomeRequest):
    user_id_str = request.session.get("user_id")
    if not user_id_str:
        return HTTPStatus.UNAUTHORIZED, ErrorResponse(detail="Not authenticated.")
    from uuid import UUID

    user_id = UUID(user_id_str)
    uc = get_register_income_use_case()
    try:
        result = uc.execute(
            RegisterIncomeCommand(
                user_id=user_id,
                account_id=payload.account_id,
                amount=payload.amount,
                currency=payload.currency,
                exchange_rate=payload.exchange_rate,
                category=payload.category,
                is_base_salary=payload.is_base_salary,
                date=payload.date,
                notes=payload.notes,
            )
        )
        return HTTPStatus.CREATED, result.model_dump()
    except AccountNotFoundError as exc:
        return HTTPStatus.NOT_FOUND, ErrorResponse(detail=str(exc))
    except AccountAccessForbiddenError as exc:
        return HTTPStatus.FORBIDDEN, ErrorResponse(detail=str(exc))
    except DuplicateBaseSalaryError as exc:
        return HTTPStatus.CONFLICT, ErrorResponse(detail=str(exc))


# --- Currency Exchange ---


@router.post(
    "/transactions/exchange",
    response={
        HTTPStatus.CREATED: CurrencyExchangeRegisteredResponseSchema,
        HTTPStatus.NOT_FOUND: ErrorResponse,
        HTTPStatus.FORBIDDEN: ErrorResponse,
        HTTPStatus.UNPROCESSABLE_ENTITY: ErrorResponse,
    },
    summary="Register a currency exchange (creates a linked pair of transactions)",
)
def register_currency_exchange(request, payload: RegisterCurrencyExchangeRequest):
    user_id_str = request.session.get("user_id")
    if not user_id_str:
        return HTTPStatus.UNAUTHORIZED, ErrorResponse(detail="Not authenticated.")
    from uuid import UUID

    user_id = UUID(user_id_str)
    uc = get_register_currency_exchange_use_case()
    try:
        result = uc.execute(
            RegisterCurrencyExchangeCommand(
                user_id=user_id,
                source_account_id=payload.source_account_id,
                dest_account_id=payload.dest_account_id,
                amount_out=payload.amount_out,
                currency_out=payload.currency_out,
                amount_in=payload.amount_in,
                currency_in=payload.currency_in,
                exchange_rate=payload.exchange_rate,
                date=payload.date,
                notes=payload.notes,
            )
        )
        return HTTPStatus.CREATED, result.model_dump()
    except AccountNotFoundError as exc:
        return HTTPStatus.NOT_FOUND, ErrorResponse(detail=str(exc))
    except AccountAccessForbiddenError as exc:
        return HTTPStatus.FORBIDDEN, ErrorResponse(detail=str(exc))
    except InvalidExchangeMathError as exc:
        return HTTPStatus.UNPROCESSABLE_ENTITY, ErrorResponse(detail=str(exc))


# --- Edit Transaction ---


@router.patch(
    "/transactions/{transaction_id}",
    response={
        HTTPStatus.OK: TransactionEditedResponseSchema,
        HTTPStatus.NOT_FOUND: ErrorResponse,
        HTTPStatus.FORBIDDEN: ErrorResponse,
        HTTPStatus.UNAUTHORIZED: ErrorResponse,
    },
    summary="Edit transaction notes (requires password confirmation)",
)
def edit_transaction(request, transaction_id: UUID, payload: EditTransactionRequest):
    user_id_str = request.session.get("user_id")
    if not user_id_str:
        return HTTPStatus.UNAUTHORIZED, ErrorResponse(detail="Not authenticated.")
    from uuid import UUID as _UUID

    user_id = _UUID(user_id_str)
    uc = get_edit_transaction_use_case()
    try:
        payload_dict = payload.model_dump(exclude_none=True)
        # Convert date to ISO string if present
        if "date" in payload_dict and payload_dict["date"] is not None:
            if hasattr(payload_dict["date"], "isoformat"):
                payload_dict["date"] = payload_dict["date"].isoformat()

        result = uc.execute(
            EditTransactionCommand(user_id=user_id, transaction_id=transaction_id, **payload_dict)
        )
        return HTTPStatus.OK, result.model_dump()
    except TransactionNotFoundError as exc:
        return HTTPStatus.NOT_FOUND, ErrorResponse(detail=str(exc))
    except UnauthorizedEditError as exc:
        return HTTPStatus.FORBIDDEN, ErrorResponse(detail=str(exc))
    except InvalidEditionCredentialsError as exc:
        return HTTPStatus.UNAUTHORIZED, ErrorResponse(detail=str(exc))


# --- Delete Transaction ---


@router.delete(
    "/transactions/{transaction_id}",
    response={
        HTTPStatus.OK: TransactionDeletedResponseSchema,
        HTTPStatus.NOT_FOUND: ErrorResponse,
        HTTPStatus.FORBIDDEN: ErrorResponse,
        HTTPStatus.UNAUTHORIZED: ErrorResponse,
    },
    summary="Delete a transaction (requires password confirmation). Exchange pairs are deleted atomically.",
)
def delete_transaction(request, transaction_id: UUID, payload: DeleteTransactionRequest):
    user_id_str = request.session.get("user_id")
    if not user_id_str:
        return HTTPStatus.UNAUTHORIZED, ErrorResponse(detail="Not authenticated.")
    from uuid import UUID as _UUID

    user_id = _UUID(user_id_str)
    uc = get_delete_transaction_use_case()
    try:
        result = uc.execute(
            DeleteTransactionCommand(
                user_id=user_id,
                transaction_id=transaction_id,
                password=payload.password,
            )
        )
        return HTTPStatus.OK, result.model_dump()
    except TransactionNotFoundError as exc:
        return HTTPStatus.NOT_FOUND, ErrorResponse(detail=str(exc))
    except UnauthorizedEditError as exc:
        return HTTPStatus.FORBIDDEN, ErrorResponse(detail=str(exc))
    except InvalidEditionCredentialsError as exc:
        return HTTPStatus.UNAUTHORIZED, ErrorResponse(detail=str(exc))


@router.post(
    "/transactions/{transaction_id}/reverse",
    response={
        HTTPStatus.CREATED: TransactionReversedResponseSchema,
        HTTPStatus.NOT_FOUND: ErrorResponse,
        HTTPStatus.FORBIDDEN: ErrorResponse,
        HTTPStatus.UNAUTHORIZED: ErrorResponse,
        HTTPStatus.UNPROCESSABLE_ENTITY: ErrorResponse,
    },
    summary="Reverse an income or expense transaction (creates a counter-transaction). Requires password.",
)
def reverse_transaction(request, transaction_id: UUID, payload: ReverseTransactionRequest):
    user_id_str = request.session.get("user_id")
    if not user_id_str:
        return HTTPStatus.UNAUTHORIZED, ErrorResponse(detail="Not authenticated.")
    from uuid import UUID as _UUID

    user_id = _UUID(user_id_str)
    uc = get_reverse_transaction_use_case()
    try:
        result = uc.execute(
            ReverseTransactionCommand(
                user_id=user_id,
                transaction_id=transaction_id,
                password=payload.password,
            )
        )
        return HTTPStatus.CREATED, result.model_dump()
    except TransactionNotFoundError as exc:
        return HTTPStatus.NOT_FOUND, ErrorResponse(detail=str(exc))
    except UnauthorizedEditError as exc:
        return HTTPStatus.FORBIDDEN, ErrorResponse(detail=str(exc))
    except InvalidEditionCredentialsError as exc:
        return HTTPStatus.UNAUTHORIZED, ErrorResponse(detail=str(exc))
    except TransactionReversalNotSupportedError as exc:
        return HTTPStatus.UNPROCESSABLE_ENTITY, ErrorResponse(detail=str(exc))


# --- Expense Categories ---


@router.post(
    "/categories",
    response={
        HTTPStatus.CREATED: ExpenseCategoryResponseSchema,
        HTTPStatus.CONFLICT: ErrorResponse,
    },
    summary="Create a new expense category",
)
def create_expense_category(request, payload: CreateExpenseCategoryRequest):
    user_id_str = request.session.get("user_id")
    if not user_id_str:
        return HTTPStatus.UNAUTHORIZED, ErrorResponse(detail="Not authenticated.")
    from uuid import UUID

    user_id = UUID(user_id_str)
    uc = get_create_expense_category_use_case()
    try:
        result = uc.execute(
            CreateExpenseCategoryCommand(
                user_id=user_id,
                name=payload.name,
                is_fixed_expense=payload.is_fixed_expense,
                default_amount_usd=payload.default_amount_usd,
            )
        )
        return HTTPStatus.CREATED, result.model_dump()
    except ExpenseCategoryAlreadyExistsError as exc:
        return HTTPStatus.CONFLICT, ErrorResponse(detail=str(exc))


@router.get(
    "/categories",
    response=list[ExpenseCategoryResponseSchema],
    summary="List all expense categories for the current user",
)
def list_expense_categories(request):
    user_id_str = request.session.get("user_id")
    if not user_id_str:
        return []
    from uuid import UUID

    user_id = UUID(user_id_str)
    uc = get_expense_categories_use_case()
    results = uc.execute(GetExpenseCategoriesQuery(user_id=user_id))
    return [r.model_dump() for r in results]


# --- Expenses ---


@router.post(
    "/expenses/register",
    response={
        HTTPStatus.CREATED: ExpenseRegisteredResponseSchema,
        HTTPStatus.NOT_FOUND: ErrorResponse,
        HTTPStatus.FORBIDDEN: ErrorResponse,
        HTTPStatus.UNAUTHORIZED: ErrorResponse,
    },
    summary="Register an expense transaction",
)
def register_expense(request, expense_data: RegisterExpenseRequest = Body(...)):
    user_id_str = request.session.get("user_id")
    if not user_id_str:
        return HTTPStatus.UNAUTHORIZED, ErrorResponse(detail="Not authenticated.")
    from uuid import UUID

    user_id = UUID(user_id_str)
    uc = get_register_expense_use_case()
    try:
        result = uc.execute(
            RegisterExpenseCommand(
                user_id=user_id,
                account_id=expense_data.account_id,
                category_name=expense_data.category_name,
                amount=expense_data.amount,
                currency=expense_data.currency,
                exchange_rate=expense_data.exchange_rate,
                date=expense_data.date,
                description=expense_data.description,
            )
        )
        return HTTPStatus.CREATED, result.model_dump()
    except AccountNotFoundError as exc:
        return HTTPStatus.NOT_FOUND, ErrorResponse(detail=str(exc))
    except AccountAccessForbiddenError as exc:
        return HTTPStatus.FORBIDDEN, ErrorResponse(detail=str(exc))
    except ExpenseCategoryNotFoundError as exc:
        return HTTPStatus.NOT_FOUND, ErrorResponse(detail=str(exc))


# --- Savings Goals ---


@router.post(
    "/savings/goals",
    response={
        HTTPStatus.CREATED: SavingsGoalResponseSchema,
    },
    summary="Create a new savings goal",
)
def create_savings_goal(request, payload: CreateSavingsGoalRequest):
    user_id_str = request.session.get("user_id")
    if not user_id_str:
        return HTTPStatus.UNAUTHORIZED, ErrorResponse(detail="Not authenticated.")
    from uuid import UUID

    user_id = UUID(user_id_str)
    uc = get_create_savings_goal_use_case()
    result = uc.execute(
        CreateSavingsGoalCommand(
            user_id=user_id,
            motive=payload.motive,
            target_amount_usd=payload.target_amount_usd,
        )
    )
    return HTTPStatus.CREATED, result.model_dump()


@router.get(
    "/savings/goals",
    response=list[SavingsGoalSummaryResponseSchema],
    summary="List all savings goals for the current user",
)
def list_savings_goals(request):
    user_id_str = request.session.get("user_id")
    if not user_id_str:
        return []
    from uuid import UUID

    user_id = UUID(user_id_str)
    uc = get_savings_goals_use_case()
    results = uc.execute(GetSavingsGoalsQuery(user_id=user_id))
    return [r.model_dump() for r in results]


@router.post(
    "/savings/deposits",
    response={
        HTTPStatus.CREATED: SavingsDepositResponseSchema,
        HTTPStatus.NOT_FOUND: ErrorResponse,
        HTTPStatus.UNPROCESSABLE_ENTITY: ErrorResponse,
    },
    summary="Deposit to a savings goal (USD/USDT accounts only)",
)
def deposit_to_savings(request, payload: DepositToSavingsRequest):
    user_id_str = request.session.get("user_id")
    if not user_id_str:
        return HTTPStatus.UNAUTHORIZED, ErrorResponse(detail="Not authenticated.")
    from uuid import UUID

    user_id = UUID(user_id_str)
    uc = get_deposit_to_savings_use_case()
    try:
        result = uc.execute(
            DepositToSavingsCommand(
                user_id=user_id,
                goal_id=payload.goal_id,
                account_id=payload.account_id,
                amount=payload.amount,
                currency=payload.currency,
                date=payload.date,
            )
        )
        return HTTPStatus.CREATED, result.model_dump()
    except SavingsGoalNotFoundError as exc:
        return HTTPStatus.NOT_FOUND, ErrorResponse(detail=str(exc))
    except SavingsDepositCurrencyError as exc:
        return HTTPStatus.UNPROCESSABLE_ENTITY, ErrorResponse(detail=str(exc))


@router.put(
    "/savings/goals/{goal_id}",
    response={
        HTTPStatus.OK: SavingsGoalSummaryResponseSchema,
        HTTPStatus.NOT_FOUND: ErrorResponse,
    },
    summary="Edit a savings goal (motive, target amount, expected monthly contribution)",
)
def edit_savings_goal(request, goal_id: UUID, payload: EditSavingsGoalRequest):
    user_id_str = request.session.get("user_id")
    if not user_id_str:
        return HTTPStatus.UNAUTHORIZED, ErrorResponse(detail="Not authenticated.")
    from uuid import UUID as _UUID

    user_id = _UUID(user_id_str)
    uc = get_edit_savings_goal_use_case()
    try:
        result = uc.execute(
            EditSavingsGoalCommand(
                user_id=user_id,
                goal_id=goal_id,
                motive=payload.motive,
                target_amount_usd=payload.target_amount_usd,
                expected_monthly_contribution=payload.expected_monthly_contribution,
            )
        )
        return HTTPStatus.OK, result.model_dump()
    except SavingsGoalNotFoundError as exc:
        return HTTPStatus.NOT_FOUND, ErrorResponse(detail=str(exc))


@router.get(
    "/savings/goals/{goal_id}/contributions",
    response=list[SavingsDepositContributionSchema],
    summary="Get all contributions/deposits for a specific savings goal",
)
def get_savings_goal_contributions(request, goal_id: UUID):
    user_id_str = request.session.get("user_id")
    if not user_id_str:
        return []
    from uuid import UUID as _UUID

    user_id = _UUID(user_id_str)
    uc = get_savings_goal_contributions_use_case()
    try:
        results = uc.execute(goal_id, user_id)
        return [r.model_dump() for r in results]
    except SavingsGoalNotFoundError:
        return []
