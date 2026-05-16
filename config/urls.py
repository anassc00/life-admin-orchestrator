from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI

from adapters.api.finance.views import router as finance_router
from adapters.api.users.views import router as users_router
from infrastructure.django_app import views as v

api = NinjaAPI(
    title="Life Admin Orchestrator API",
    version="1.0.0",
    description="Personal ERP powered by AI agents.",
)

api.add_router("/auth", users_router)
api.add_router("/finance", finance_router)

urlpatterns = [
    path("", v.landing, name="landing"),
    path("register/", v.register_page, name="register"),
    path("login/", v.login_page, name="login"),
    path("dashboard/", v.dashboard, name="dashboard"),
    path("finance/accounts/", v.finance_accounts_page, name="finance_accounts"),
    path("finance/income/", v.finance_income_page, name="finance_income"),
    path("finance/exchange/", v.finance_exchange_page, name="finance_exchange"),
    path("finance/expenses/", v.finance_expenses_page, name="finance_expenses"),
    path("finance/transactions/", v.finance_transactions_page, name="finance_transactions"),
    path("finance/savings/", v.finance_savings_page, name="finance_savings"),
    path("finance/planning/", v.finance_planning_page, name="finance_planning"),
    path("profile/", v.profile_page, name="profile"),
    path("finance/reports/", v.finance_reports_page, name="finance_reports"),
    path("finance/cashflow/", v.finance_cashflow_page, name="finance_cashflow"),
    path("finance/invoices/", v.finance_invoices_page, name="finance_invoices"),
    path("admin/", admin.site.urls),
    path("api/", api.urls),
]
