from decimal import Decimal
from http import HTTPStatus
from uuid import UUID

from ninja import Router

from adapters.api.finance.schemas import (
    AccountRegisteredResponseSchema,
    AccountSummarySchema,
    AccountUpdatedResponseSchema,
    CategorizeExpenseRequest,
    CreateInvoiceRequest,
    CurrencyExchangeRegisteredResponseSchema,
    EditTransactionRequest,
    ExpenseCategorizedResponseSchema,
    IncomeRegisteredResponseSchema,
    InvoiceCreatedResponseSchema,
    InvoiceProcessedResponseSchema,
    MonthlyFinancialSummarySchema,
    MonthlyReportResponseSchema,
    RegisterAccountRequest,
    RegisterCurrencyExchangeRequest,
    RegisterIncomeRequest,
    TransactionEditedResponseSchema,
    UpdateAccountRequest,
)
from adapters.api.users.schemas import ErrorResponse
from application.dtos.finance import (
    EditTransactionCommand,
    GenerateMonthlyReportQuery,
    GetAccountsByUserQuery,
    GetMonthlyFinancialSummaryQuery,
    ProcessInvoiceCommand,
    RegisterAccountCommand,
    RegisterCurrencyExchangeCommand,
    RegisterIncomeCommand,
    UpdateAccountCommand,
)
from domain.exceptions.finance import (
    AccountAccessForbiddenError,
    AccountAlreadyExistsError,
    AccountNotFoundError,
    TransactionNotFoundError,
    UnauthorizedEditError,
)
from domain.exceptions.user import InvalidCredentialsError
from infrastructure.di import (
    get_accounts_by_user_use_case,
    get_categorize_expense_use_case,
    get_create_invoice_use_case,
    get_edit_transaction_use_case,
    get_generate_monthly_report_use_case,
    get_monthly_financial_summary_use_case,
    get_process_invoice_use_case,
    get_register_account_use_case,
    get_register_currency_exchange_use_case,
    get_register_income_use_case,
    get_update_account_use_case,
)

router = Router(tags=["Finance"])


@router.post("/invoices", response=InvoiceCreatedResponseSchema)
def create_invoice(request, payload: CreateInvoiceRequest):
    uc = get_create_invoice_use_case()
    return uc.execute(payload.to_command()).model_dump()


@router.post("/invoices/{invoice_id}/process", response=InvoiceProcessedResponseSchema)
def process_invoice(request, invoice_id: UUID):
    uc = get_process_invoice_use_case()
    return uc.execute(ProcessInvoiceCommand(invoice_id=invoice_id)).model_dump()


@router.post("/expenses", response=ExpenseCategorizedResponseSchema)
def categorize_expense(request, payload: CategorizeExpenseRequest):
    uc = get_categorize_expense_use_case()
    return uc.execute(payload.to_command()).model_dump()


@router.get("/reports/monthly", response=MonthlyReportResponseSchema)
def monthly_report(request, year: int, month: int):
    uc = get_generate_monthly_report_use_case()
    return uc.execute(GenerateMonthlyReportQuery(year=year, month=month)).model_dump()


@router.get(
    "/summary/current",
    response=MonthlyFinancialSummarySchema,
    summary="Get the financial summary (income, expenses, savings) for the current month",
)
def monthly_financial_summary(request):
    from datetime import date

    user_id_str = request.session.get("user_id")
    if not user_id_str:
        return MonthlyFinancialSummarySchema(
            year=0,
            month=0,
            total_income=Decimal("0"),
            total_expenses=Decimal("0"),
            savings=Decimal("0"),
        )
    from uuid import UUID

    today = date.today()
    uc = get_monthly_financial_summary_use_case()
    result = uc.execute(
        GetMonthlyFinancialSummaryQuery(
            user_id=UUID(user_id_str),
            year=today.year,
            month=today.month,
        )
    )
    return result.model_dump()


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
                date=payload.date,
                notes=payload.notes,
            )
        )
        return HTTPStatus.CREATED, result.model_dump()
    except AccountNotFoundError as exc:
        return HTTPStatus.NOT_FOUND, ErrorResponse(detail=str(exc))
    except AccountAccessForbiddenError as exc:
        return HTTPStatus.FORBIDDEN, ErrorResponse(detail=str(exc))


# --- Currency Exchange ---


@router.post(
    "/transactions/exchange",
    response={
        HTTPStatus.CREATED: CurrencyExchangeRegisteredResponseSchema,
        HTTPStatus.NOT_FOUND: ErrorResponse,
        HTTPStatus.FORBIDDEN: ErrorResponse,
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
        result = uc.execute(
            EditTransactionCommand(
                user_id=user_id,
                transaction_id=transaction_id,
                password=payload.password,
                notes=payload.notes,
            )
        )
        return HTTPStatus.OK, result.model_dump()
    except TransactionNotFoundError as exc:
        return HTTPStatus.NOT_FOUND, ErrorResponse(detail=str(exc))
    except UnauthorizedEditError as exc:
        return HTTPStatus.FORBIDDEN, ErrorResponse(detail=str(exc))
    except InvalidCredentialsError as exc:
        return HTTPStatus.UNAUTHORIZED, ErrorResponse(detail=str(exc))
