from domain.entities.finance import Expense
from domain.repositories.finance import ExpenseRepository
from application.dtos.finance import CategorizeExpenseCommand, ExpenseCategorizedResponse


class CategorizeExpenseUseCase:

    def __init__(self, expense_repo: ExpenseRepository) -> None:
        self._repo = expense_repo

    def execute(self, command: CategorizeExpenseCommand) -> ExpenseCategorizedResponse:
        expense = Expense(
            description=command.description,
            amount=command.amount,
            currency=command.currency,
            category=command.category,
            date=command.date,
            invoice_id=command.invoice_id,
        )
        self._repo.save(expense)
        return ExpenseCategorizedResponse(expense_id=expense.id, category=expense.category)
