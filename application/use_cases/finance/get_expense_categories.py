from application.dtos.finance import ExpenseCategoryResponse, GetExpenseCategoriesQuery
from domain.repositories.finance import ExpenseCategoryRepository


class GetExpenseCategoriesUseCase:
    def __init__(self, category_repo: ExpenseCategoryRepository) -> None:
        self._category_repo = category_repo

    def execute(self, query: GetExpenseCategoriesQuery) -> list[ExpenseCategoryResponse]:
        categories = self._category_repo.list_by_user(query.user_id)
        return [
            ExpenseCategoryResponse(
                category_id=c.id,
                name=c.name,
                is_fixed_expense=c.is_fixed_expense,
                default_amount_usd=c.default_amount_usd,
            )
            for c in categories
        ]
