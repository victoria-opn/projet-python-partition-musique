import uuid
from django.contrib.auth.models import User
from django.db import models


class Job(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING"
        PROCESSING = "PROCESSING"
        COMPLETED = "COMPLETED"
        FAILED = "FAILED"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="jobs")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    progress = models.PositiveSmallIntegerField(default=0)
    audio = models.FileField(upload_to="uploads/")
    tonalite = models.CharField(max_length=10)
    resultat = models.FileField(upload_to="results/", blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_fin = models.DateTimeField(blank=True, null=True)
    message_erreur = models.TextField(blank=True)

    def __str__(self):
        return f"Job {self.id} ({self.status})"