from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI

from adapters.api.finance.views import router as finance_router
from adapters.api.calendar.views import router as calendar_router
from adapters.api.document.views import router as document_router
from adapters.api.contact.views import router as contact_router
from adapters.api.users.views import router as users_router
from infrastructure.django_app import views as template_views

api = NinjaAPI(
    title="Life Admin Orchestrator API",
    version="1.0.0",
    description="Personal ERP powered by AI agents.",
)

api.add_router("/auth", users_router)
api.add_router("/finance", finance_router)
api.add_router("/calendar", calendar_router)
api.add_router("/documents", document_router)
api.add_router("/contacts", contact_router)

urlpatterns = [
    path("", template_views.home, name="home"),
    path("admin/", admin.site.urls),
    path("api/", api.urls),
]
