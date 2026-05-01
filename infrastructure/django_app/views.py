from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render


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
    if "user_id" not in request.session:
        return redirect("login")
    return render(request, "dashboard.html")
