"""Dependency Injection container.

Wires concrete infrastructure implementations to abstract interfaces
before injecting them into use cases. All factory functions are
intentionally stateless — they create fresh instances on each call.
For performance-critical paths, introduce a request-scoped cache here.
"""

from application.use_cases.calendar.detect_conflict import DetectConflictUseCase
from application.use_cases.calendar.schedule_appointment import ScheduleAppointmentUseCase
from application.use_cases.calendar.send_reminder import SendReminderUseCase
from application.use_cases.contact.log_interaction import LogInteractionUseCase
from application.use_cases.contact.update_contact_record import UpdateContactRecordUseCase
from application.use_cases.document.archive_document import ArchiveDocumentUseCase
from application.use_cases.document.classify_document import ClassifyDocumentUseCase
from application.use_cases.document.extract_metadata import ExtractMetadataUseCase
from application.use_cases.document.register_document import RegisterDocumentUseCase
from application.use_cases.finance.categorize_expense import CategorizeExpenseUseCase
from application.use_cases.finance.delete_transaction import DeleteTransactionUseCase
from application.use_cases.finance.create_expense_category import CreateExpenseCategoryUseCase
from application.use_cases.finance.create_invoice import CreateInvoiceUseCase
from application.use_cases.finance.create_savings_goal import CreateSavingsGoalUseCase
from application.use_cases.finance.deposit_to_savings import DepositToSavingsUseCase
from application.use_cases.finance.edit_savings_goal import EditSavingsGoalUseCase
from application.use_cases.finance.edit_transaction import EditTransactionUseCase
from application.use_cases.finance.generate_monthly_report import GenerateMonthlyReportUseCase
from application.use_cases.finance.get_accounts_by_user import GetAccountsByUserUseCase
from application.use_cases.finance.get_expense_categories import GetExpenseCategoriesUseCase
from application.use_cases.finance.get_monthly_financial_summary import (
    GetMonthlyFinancialSummaryUseCase,
)
from application.use_cases.finance.get_savings_goal_contributions import (
    GetSavingsGoalContributionsUseCase,
)
from application.use_cases.finance.get_savings_goals import GetSavingsGoalsUseCase
from application.use_cases.finance.get_transactions_by_user import GetTransactionsByUserUseCase
from application.use_cases.finance.process_invoice import ProcessInvoiceUseCase
from application.use_cases.finance.register_account import RegisterAccountUseCase
from application.use_cases.finance.register_currency_exchange import RegisterCurrencyExchangeUseCase
from application.use_cases.finance.register_expense import RegisterExpenseUseCase
from application.use_cases.finance.register_income import RegisterIncomeUseCase
from application.use_cases.finance.update_account import UpdateAccountUseCase
from application.use_cases.users.authenticate_user import AuthenticateUserUseCase
from application.use_cases.users.get_user_profile import GetUserProfileUseCase
from application.use_cases.users.register_user import RegisterUserUseCase
from infrastructure.repositories.calendar import DjangoAppointmentRepository
from infrastructure.repositories.contact import DjangoContactRepository, DjangoInteractionRepository
from infrastructure.repositories.document import DjangoDocumentRepository
from infrastructure.repositories.finance import (
    DjangoAccountRepository,
    DjangoExpenseCategoryRepository,
    DjangoExpenseRepository,
    DjangoInvoiceRepository,
    DjangoSavingsDepositRepository,
    DjangoSavingsGoalRepository,
    DjangoTransactionRepository,
)
from infrastructure.repositories.user import DjangoPasswordHasher, DjangoUserRepository

# --- Auth / Users ---


def get_register_user_use_case() -> RegisterUserUseCase:
    return RegisterUserUseCase(
        user_repo=DjangoUserRepository(),
        password_hasher=DjangoPasswordHasher(),
    )


def get_authenticate_user_use_case() -> AuthenticateUserUseCase:
    return AuthenticateUserUseCase(
        user_repo=DjangoUserRepository(),
        password_hasher=DjangoPasswordHasher(),
    )


def get_user_profile_use_case() -> GetUserProfileUseCase:
    return GetUserProfileUseCase(user_repo=DjangoUserRepository())


# --- Finance ---


def get_register_account_use_case() -> RegisterAccountUseCase:
    return RegisterAccountUseCase(account_repo=DjangoAccountRepository())


def get_accounts_by_user_use_case() -> GetAccountsByUserUseCase:
    return GetAccountsByUserUseCase(account_repo=DjangoAccountRepository())


def get_update_account_use_case() -> UpdateAccountUseCase:
    return UpdateAccountUseCase(account_repo=DjangoAccountRepository())


def get_register_income_use_case() -> RegisterIncomeUseCase:
    return RegisterIncomeUseCase(
        account_repo=DjangoAccountRepository(),
        transaction_repo=DjangoTransactionRepository(),
    )


def get_register_currency_exchange_use_case() -> RegisterCurrencyExchangeUseCase:
    return RegisterCurrencyExchangeUseCase(
        account_repo=DjangoAccountRepository(),
        transaction_repo=DjangoTransactionRepository(),
    )


def get_edit_transaction_use_case() -> EditTransactionUseCase:
    return EditTransactionUseCase(
        transaction_repo=DjangoTransactionRepository(),
        user_repo=DjangoUserRepository(),
        password_hasher=DjangoPasswordHasher(),
        account_repo=DjangoAccountRepository(),
    )


def get_create_invoice_use_case() -> CreateInvoiceUseCase:
    return CreateInvoiceUseCase(invoice_repo=DjangoInvoiceRepository())


def get_process_invoice_use_case() -> ProcessInvoiceUseCase:
    return ProcessInvoiceUseCase(
        invoice_repo=DjangoInvoiceRepository(),
        transaction_repo=DjangoTransactionRepository(),
    )


def get_categorize_expense_use_case() -> CategorizeExpenseUseCase:
    return CategorizeExpenseUseCase(expense_repo=DjangoExpenseRepository())


def get_create_expense_category_use_case() -> CreateExpenseCategoryUseCase:
    return CreateExpenseCategoryUseCase(category_repo=DjangoExpenseCategoryRepository())


def get_expense_categories_use_case() -> GetExpenseCategoriesUseCase:
    return GetExpenseCategoriesUseCase(category_repo=DjangoExpenseCategoryRepository())


def get_register_expense_use_case() -> RegisterExpenseUseCase:
    return RegisterExpenseUseCase(
        account_repo=DjangoAccountRepository(),
        category_repo=DjangoExpenseCategoryRepository(),
        transaction_repo=DjangoTransactionRepository(),
    )


def get_generate_monthly_report_use_case() -> GenerateMonthlyReportUseCase:
    return GenerateMonthlyReportUseCase(
        expense_repo=DjangoExpenseRepository(),
        invoice_repo=DjangoInvoiceRepository(),
    )


def get_monthly_financial_summary_use_case() -> GetMonthlyFinancialSummaryUseCase:
    return GetMonthlyFinancialSummaryUseCase(
        transaction_repo=DjangoTransactionRepository(),
        savings_deposit_repo=DjangoSavingsDepositRepository(),
    )


def get_create_savings_goal_use_case() -> CreateSavingsGoalUseCase:
    return CreateSavingsGoalUseCase(savings_goal_repo=DjangoSavingsGoalRepository())


def get_deposit_to_savings_use_case() -> DepositToSavingsUseCase:
    from django.db import transaction

    return DepositToSavingsUseCase(
        savings_goal_repo=DjangoSavingsGoalRepository(),
        savings_deposit_repo=DjangoSavingsDepositRepository(),
        transaction_repo=DjangoTransactionRepository(),
        account_repo=DjangoAccountRepository(),
        atomic_context=transaction.atomic,
    )


def get_savings_goals_use_case() -> GetSavingsGoalsUseCase:
    return GetSavingsGoalsUseCase(
        savings_goal_repo=DjangoSavingsGoalRepository(),
        savings_deposit_repo=DjangoSavingsDepositRepository(),
    )


def get_edit_savings_goal_use_case() -> EditSavingsGoalUseCase:
    return EditSavingsGoalUseCase(
        savings_goal_repo=DjangoSavingsGoalRepository(),
        savings_deposit_repo=DjangoSavingsDepositRepository(),
    )


def get_savings_goal_contributions_use_case() -> GetSavingsGoalContributionsUseCase:
    return GetSavingsGoalContributionsUseCase(
        savings_goal_repo=DjangoSavingsGoalRepository(),
        savings_deposit_repo=DjangoSavingsDepositRepository(),
    )


def get_delete_transaction_use_case() -> DeleteTransactionUseCase:
    return DeleteTransactionUseCase(
        transaction_repo=DjangoTransactionRepository(),
        user_repo=DjangoUserRepository(),
        password_hasher=DjangoPasswordHasher(),
    )


def get_transactions_by_user_use_case() -> GetTransactionsByUserUseCase:
    return GetTransactionsByUserUseCase(transaction_repo=DjangoTransactionRepository())


# --- Calendar ---


def get_schedule_appointment_use_case() -> ScheduleAppointmentUseCase:
    return ScheduleAppointmentUseCase(appointment_repo=DjangoAppointmentRepository())


def get_detect_conflict_use_case() -> DetectConflictUseCase:
    return DetectConflictUseCase(appointment_repo=DjangoAppointmentRepository())


def get_send_reminder_use_case() -> SendReminderUseCase:
    return SendReminderUseCase(appointment_repo=DjangoAppointmentRepository())


# --- Documents ---


def get_register_document_use_case() -> RegisterDocumentUseCase:
    return RegisterDocumentUseCase(document_repo=DjangoDocumentRepository())


def get_classify_document_use_case() -> ClassifyDocumentUseCase:
    return ClassifyDocumentUseCase(document_repo=DjangoDocumentRepository())


def get_extract_metadata_use_case() -> ExtractMetadataUseCase:
    return ExtractMetadataUseCase(document_repo=DjangoDocumentRepository())


def get_archive_document_use_case() -> ArchiveDocumentUseCase:
    return ArchiveDocumentUseCase(document_repo=DjangoDocumentRepository())


# --- Contacts ---


def get_update_contact_record_use_case() -> UpdateContactRecordUseCase:
    return UpdateContactRecordUseCase(contact_repo=DjangoContactRepository())


def get_log_interaction_use_case() -> LogInteractionUseCase:
    return LogInteractionUseCase(
        contact_repo=DjangoContactRepository(),
        interaction_repo=DjangoInteractionRepository(),
    )
