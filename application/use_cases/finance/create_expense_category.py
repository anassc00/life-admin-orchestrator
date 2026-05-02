from application.dtos.finance import CreateExpenseCategoryCommand, ExpenseCategoryCreatedResponse
from domain.entities.finance import ExpenseCategory
from domain.exceptions.finance import ExpenseCategoryAlreadyExistsError
from domain.repositories.finance import ExpenseCategoryRepository


class CreateExpenseCategoryUseCase:
    def __init__(self, category_repo: ExpenseCategoryRepository) -> None:
        self._category_repo = category_repo

    def execute(self, command: CreateExpenseCategoryCommand) -> ExpenseCategoryCreatedResponse:
        if self._category_repo.exists_by_name_and_user(command.name, command.user_id):
            raise ExpenseCategoryAlreadyExistsError(command.name)

        category = ExpenseCategory(
            user_id=command.user_id,
            name=command.name,
            is_fixed_expense=command.is_fixed_expense,
            default_amount_usd=command.default_amount_usd,
        )
        self._category_repo.save(category)

        return ExpenseCategoryCreatedResponse(
            category_id=category.id,
            name=category.name,
            is_fixed_expense=category.is_fixed_expense,
            default_amount_usd=category.default_amount_usd,
        )
