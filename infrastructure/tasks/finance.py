from celery import shared_task

from infrastructure.di import (
    get_categorize_expense_use_case,
    get_create_invoice_use_case,
)


@shared_task(name="tasks.finance.process_document", bind=True, max_retries=3)
def process_finance_document_task(self, raw_document: str) -> dict:
    """Dispatch a raw financial document to the FinanceAgent for extraction and persistence."""
    from application.agents.finance_agent import FinanceAgentOrchestrator

    agent = FinanceAgentOrchestrator(
        create_invoice_uc=get_create_invoice_use_case(),
        categorize_expense_uc=get_categorize_expense_use_case(),
    )
    result = agent.run(raw_document)
    return {"error": result.get("error")}
