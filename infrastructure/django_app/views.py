from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render


def _protected(request: HttpRequest, template: str) -> HttpResponse:
    if "user_id" not in request.session:
        return redirect("login")
    return render(request, template)


def landing(request: HttpRequest) -> HttpResponse:
    if "user_id" in request.session:
        return redirect("dashboard")
    return render(request, "landing.html")


def register_page(request: HttpRequest) -> HttpResponse:
    if "user_id" in request.session:
        return redirect("dashboard")
    return render(request, "register.html")


def login_page(request: HttpRequest) -> HttpResponse:
    if "user_id" in request.session:
        return redirect("dashboard")
    return render(request, "login.html")


def dashboard(request: HttpRequest) -> HttpResponse:
    return _protected(request, "dashboard.html")


def finance_accounts_page(request: HttpRequest) -> HttpResponse:
    return _protected(request, "finance_accounts.html")


def finance_income_page(request: HttpRequest) -> HttpResponse:
    return _protected(request, "finance_income.html")


def finance_exchange_page(request: HttpRequest) -> HttpResponse:
    return _protected(request, "finance_exchange.html")


def finance_transactions_page(request: HttpRequest) -> HttpResponse:
    return _protected(request, "finance_transactions.html")


def finance_expenses_page(request: HttpRequest) -> HttpResponse:
    return _protected(request, "finance_expenses.html")


def finance_savings_page(request: HttpRequest) -> HttpResponse:
    return _protected(request, "finance_savings.html")


def finance_planning_page(request: HttpRequest) -> HttpResponse:
    return _protected(request, "finance_planning.html")


def profile_page(request: HttpRequest) -> HttpResponse:
    return _protected(request, "profile.html")


def finance_reports_page(request: HttpRequest) -> HttpResponse:
    return _protected(request, "finance_reports.html")


def finance_cashflow_page(request: HttpRequest) -> HttpResponse:
    return _protected(request, "finance_cashflow.html")


def finance_invoices_page(request: HttpRequest) -> HttpResponse:
    return _protected(request, "finance_invoices.html")
