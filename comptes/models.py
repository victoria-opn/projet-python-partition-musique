from django.db import models
from django.contrib.auth.models import User


class DepotAudio(models.Model):
    utilisateur = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="depots_audio",
    )
    nom_fichier = models.CharField(max_length=255)
    date_depot = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date_depot"]

    def __str__(self):
        return self.nom_fichier
