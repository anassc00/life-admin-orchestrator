from application.dtos.finance import BudgetPlanCreatedResponse, CreateBudgetPlanCommand
from domain.entities.finance import BudgetPlan
from domain.exceptions.finance import BudgetPlanAlreadyExistsError
from domain.repositories.finance import BudgetPlanRepository


class CreateBudgetPlanUseCase:
    def __init__(self, budget_plan_repo: BudgetPlanRepository) -> None:
        self._repo = budget_plan_repo

    def execute(self, cmd: CreateBudgetPlanCommand) -> BudgetPlanCreatedResponse:
        existing = self._repo.get_by_user_and_period(cmd.user_id, cmd.year, cmd.month)
        if existing:
            raise BudgetPlanAlreadyExistsError(cmd.year, cmd.month)

        plan = BudgetPlan(
            user_id=cmd.user_id,
            year=cmd.year,
            month=cmd.month,
            budget_usd=cmd.budget_usd,
            income_usd=cmd.income_usd,
        )
        self._repo.save(plan)
        return BudgetPlanCreatedResponse(
            plan_id=plan.id,
            user_id=plan.user_id,
            year=plan.year,
            month=plan.month,
            budget_usd=plan.budget_usd,
            income_usd=plan.income_usd,
        )
