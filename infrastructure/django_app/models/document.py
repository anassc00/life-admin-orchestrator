import uuid

from django.db import models


class DocumentModel(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("classified", "Classified"),
        ("archived", "Archived"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    filename = models.CharField(max_length=500)
    content_type = models.CharField(max_length=100)
    category = models.CharField(max_length=100, blank=True, default="")
    metadata = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    storage_path = models.CharField(max_length=1000, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "documents"

    def __str__(self) -> str:
        return f"Document({self.filename}, {self.status})"
