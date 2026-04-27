from django.contrib import admin

from infrastructure.django_app.models import (
    AppointmentModel,
    ContactModel,
    DocumentModel,
    ExpenseModel,
    InteractionModel,
    InvoiceModel,
)


@admin.register(InvoiceModel)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("id", "vendor", "amount", "currency", "due_date", "is_paid")
    list_filter = ("is_paid", "currency")
    search_fields = ("vendor",)
    ordering = ("-due_date",)


@admin.register(ExpenseModel)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("id", "description", "amount", "currency", "category", "date")
    list_filter = ("category", "currency")
    search_fields = ("description",)
    ordering = ("-date",)


@admin.register(AppointmentModel)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "start_time", "end_time", "is_confirmed")
    list_filter = ("is_confirmed",)
    search_fields = ("title",)
    ordering = ("-start_time",)


@admin.register(DocumentModel)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("id", "filename", "content_type", "category", "status")
    list_filter = ("status", "category")
    search_fields = ("filename",)


@admin.register(ContactModel)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "email", "phone", "company")
    search_fields = ("name", "email", "company")


@admin.register(InteractionModel)
class InteractionAdmin(admin.ModelAdmin):
    list_display = ("id", "contact", "channel", "timestamp")
    list_filter = ("channel",)
    ordering = ("-timestamp",)
