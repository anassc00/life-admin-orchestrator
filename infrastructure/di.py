"""Dependency Injection container.

Wires concrete infrastructure implementations to abstract interfaces
before injecting them into use cases. All factory functions are
intentionally stateless — they create fresh instances on each call.
For performance-critical paths, introduce a request-scoped cache here.
"""
from application.use_cases.users.authenticate_user import AuthenticateUserUseCase
from application.use_cases.users.register_user import RegisterUserUseCase
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
from application.use_cases.finance.create_invoice import CreateInvoiceUseCase
from application.use_cases.finance.generate_monthly_report import GenerateMonthlyReportUseCase
from application.use_cases.finance.process_invoice import ProcessInvoiceUseCase
from infrastructure.repositories.calendar import DjangoAppointmentRepository
from infrastructure.repositories.contact import DjangoContactRepository, DjangoInteractionRepository
from infrastructure.repositories.document import DjangoDocumentRepository
from infrastructure.repositories.finance import DjangoExpenseRepository, DjangoInvoiceRepository
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


# --- Finance ---

def get_create_invoice_use_case() -> CreateInvoiceUseCase:
    return CreateInvoiceUseCase(invoice_repo=DjangoInvoiceRepository())


def get_process_invoice_use_case() -> ProcessInvoiceUseCase:
    return ProcessInvoiceUseCase(invoice_repo=DjangoInvoiceRepository())


def get_categorize_expense_use_case() -> CategorizeExpenseUseCase:
    return CategorizeExpenseUseCase(expense_repo=DjangoExpenseRepository())


def get_generate_monthly_report_use_case() -> GenerateMonthlyReportUseCase:
    return GenerateMonthlyReportUseCase(
        expense_repo=DjangoExpenseRepository(),
        invoice_repo=DjangoInvoiceRepository(),
    )


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
