import uuid

from django.contrib.postgres.fields import ArrayField
from django.db import models


class AppointmentModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    start_time = models.DateTimeField(db_index=True)
    end_time = models.DateTimeField()
    location = models.CharField(max_length=500, blank=True, default="")
    attendees = ArrayField(models.CharField(max_length=255), default=list, blank=True)
    is_confirmed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "appointments"

    def __str__(self) -> str:
        return f"Appointment({self.title}, {self.start_time})"
