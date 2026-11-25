from django.db import models
from django.contrib.auth.models import User
import uuid
# Create your models here.
class Statut(models.TextChoices):
    ATTENTE = "attente", "En attente"
    EN_COURS = "en_cours", "En cours"
    TERMINE = "termine","Terminé"
    ERREUR = "erreur", "Erreur"

class Tonalite(models.TextChoices):
    DO="c","Do"
    DO_DIESE="cis", "Do#"
    RE="d", "Ré"
    MI_BEMOL="ees", "Mib"
    MI="e","Mi"
    FA="f","Fa"
    FA_DIESE="fis","Fa#"
    SOL="g","Sol"
    LA_BEMOL="aes","Lab"
    LA="a","La"
    SI_BEMOL="bes","Sib"
    SI="b","Si"
class Job(models.Model):
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )
    utilisateur = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="jobs",
    )

    audio = models.FileField(
        upload_to= "audios/",
    )
    tonalite=models.CharField(
        max_length=4,
        choices=Tonalite,
        default=Tonalite.SOL
    )
    statut = models.CharField(
        max_length=22,
        choices=Statut,
        default=Statut.ATTENTE
    )
    pdf = models.FileField(
        upload_to="partitions/",
        blank=True,
    )
    message_erreur = models.TextField(
        blank=True,
    )
    progression = models.PositiveSmallIntegerField(
        default=0,
    )
    date_fin = models.DateTimeField(
        null=True,
        blank=True,
    )
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date_creation"]

    def __str__(self):
        return self.utilisateur.username