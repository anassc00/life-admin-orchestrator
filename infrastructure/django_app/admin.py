from django.contrib import admin

from infrastructure.django_app.models import ExpenseModel, InvoiceModel


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
