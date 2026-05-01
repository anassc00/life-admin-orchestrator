import uuid

from django.db import models


class ContactModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, db_index=True)
    email = models.CharField(max_length=320, blank=True, default="")
    phone = models.CharField(max_length=50, blank=True, default="")
    company = models.CharField(max_length=255, blank=True, default="")
    tags = models.JSONField(default=list, blank=True)
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "contacts"

    def __str__(self) -> str:
        return f"Contact({self.name})"


class InteractionModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contact = models.ForeignKey(
        ContactModel,
        on_delete=models.CASCADE,
        related_name="interactions",
    )
    channel = models.CharField(max_length=50)
    summary = models.TextField()
    timestamp = models.DateTimeField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "interactions"

    def __str__(self) -> str:
        return f"Interaction({self.contact_id}, {self.channel})"
