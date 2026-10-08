import os
from asgiref.sync import async_to_sync
from celery import shared_task
from channels.layers import get_channel_layer
from django.conf import settings
from django.utils import timezone

from .models import Job

# Moteur de P3, avec une fausse version tant qu'il n'est pas branché
try:
    from engine.engine import generer_partition
except ImportError:
    import time

    def generer_partition(fichier_audio, tonalite_cible, output, on_progress=None):
        for pct, etape in [(20, "Lecture"), (45, "Détection des notes"),
                           (75, "Transposition"), (95, "PDF")]:
            time.sleep(1)
            if on_progress:
                on_progress(pct, etape)
        with open(output, "wb") as f:
            f.write(b"%PDF-1.4\n%fake\n")
        return output

# Fonctions des autres personnes, avec repli si pas encore là
try:
    from comptes.notifications import notifier_utilisateur
except ImportError:
    def notifier_utilisateur(user, titre, message, lien=""):
        pass

try:
    from dashboard.events import diffuser_evenement_admin
except ImportError:
    def diffuser_evenement_admin(job):
        pass


def _send_job(job_id, payload):
    layer = get_channel_layer()
    async_to_sync(layer.group_send)(f"job_{job_id}", {"type": payload["type"], "data": payload})


def _admin(job):
    try:
        diffuser_evenement_admin(job)
    except Exception:
        pass  # le dashboard ne doit jamais casser un job


@shared_task
def process_job(job_id):
    job = Job.objects.get(id=job_id)
    job.status = Job.Status.PROCESSING
    job.progress = 0
    job.save(update_fields=["status", "progress"])
    _admin(job)

    def on_progress(pourcentage, etape=""):
        job.progress = int(pourcentage)
        job.save(update_fields=["progress"])
        _send_job(job_id, {"type": "job.progress", "job_id": job_id, "status": "PROCESSING",
                           "progress": job.progress, "etape": etape})
        _admin(job)

    output_dir = os.path.join(settings.MEDIA_ROOT, "results")
    os.makedirs(output_dir, exist_ok=True)
    output = os.path.join(output_dir, f"{job_id}.pdf")

    try:
        generer_partition(job.audio.path, job.tonalite, output, on_progress=on_progress)
        job.resultat.name = f"results/{job_id}.pdf"
        job.status = Job.Status.COMPLETED
        job.progress = 100
        job.date_fin = timezone.now()
        job.save()
        _send_job(job_id, {"type": "job.completed", "job_id": job_id,
                           "result": f"/api/jobs/{job_id}/result/"})
        notifier_utilisateur(job.user, "Partition terminée",
                             "Votre partition est prête.", f"/jobs/{job_id}/")
    except Exception as e:
        job.status = Job.Status.FAILED
        job.message_erreur = str(e)
        job.date_fin = timezone.now()
        job.save()
        _send_job(job_id, {"type": "job.failed", "job_id": job_id,
                           "error": "Impossible de générer la partition"})
        notifier_utilisateur(job.user, "Échec de la génération",
                             "Votre partition n'a pas pu être générée.", f"/jobs/{job_id}/")
    finally:
        _admin(job)