from datetime import date
from uuid import UUID

from application.dtos.finance import FinanceDashboardResponse, GetBudgetPlanQuery, GetSavingsGoalsQuery
from domain.exceptions.finance import BudgetPlanNotFoundError
from domain.repositories.finance import (
    AccountRepository,
    BudgetPlanRepository,
    ExpenseCategoryRepository,
    InvoiceRepository,
    SavingsDepositRepository,
    SavingsGoalRepository,
    TransactionRepository,
)

from application.use_cases.finance.get_net_worth import GetNetWorthUseCase
from application.use_cases.finance.get_finance_trend import GetFinanceTrendUseCase
from application.use_cases.finance.get_budget_vs_actual_summary import GetBudgetVsActualSummaryUseCase
from application.use_cases.finance.get_savings_dashboard import GetSavingsDashboardUseCase
from application.use_cases.finance.get_upcoming_invoices import GetUpcomingInvoicesUseCase
from application.use_cases.finance.get_monthly_financial_summary import GetMonthlyFinancialSummaryUseCase
from application.dtos.finance import GetMonthlyFinancialSummaryQuery


class GetFinanceDashboardUseCase:
    """Single endpoint aggregating all dashboard data in one call (DH1)."""

    def __init__(
        self,
        account_repo: AccountRepository,
        transaction_repo: TransactionRepository,
        savings_goal_repo: SavingsGoalRepository,
        savings_deposit_repo: SavingsDepositRepository,
        invoice_repo: InvoiceRepository,
        budget_plan_repo: BudgetPlanRepository,
        category_repo: ExpenseCategoryRepository,
    ) -> None:
        self._net_worth_uc = GetNetWorthUseCase(account_repo)
        self._trend_uc = GetFinanceTrendUseCase(transaction_repo)
        self._summary_uc = GetMonthlyFinancialSummaryUseCase(transaction_repo, savings_deposit_repo)
        self._savings_dashboard_uc = GetSavingsDashboardUseCase(
            savings_goal_repo, savings_deposit_repo, transaction_repo
        )
        self._invoices_uc = GetUpcomingInvoicesUseCase(invoice_repo)
        self._budget_uc = GetBudgetVsActualSummaryUseCase(budget_plan_repo, transaction_repo)

    def execute(self, user_id: UUID) -> FinanceDashboardResponse:
        today = date.today()
        year, month = today.year, today.month

        net_worth = self._net_worth_uc.execute(user_id)
        monthly_summary = self._summary_uc.execute(
            GetMonthlyFinancialSummaryQuery(user_id=user_id, year=year, month=month)
        )
        savings_overview = self._savings_dashboard_uc.execute(
            GetSavingsGoalsQuery(user_id=user_id)
        )
        upcoming_invoices = self._invoices_uc.execute(user_id)

        # Budget status is optional — may not have a plan for this month
        budget_status = None
        try:
            budget_status = self._budget_uc.execute(
                GetBudgetPlanQuery(user_id=user_id, year=year, month=month)
            )
        except BudgetPlanNotFoundError:
            pass

        return FinanceDashboardResponse(
            net_worth_usd=net_worth.total_usd,
            monthly_summary=monthly_summary,
            budget_status=budget_status,
            savings_overview=savings_overview,
            upcoming_invoices=upcoming_invoices.invoices[:5],  # top 5 upcoming
        )
