"""Lecture du contrat P2 sans créer ni modifier son modèle Job."""
from django.apps import apps
from django.contrib.auth import get_user_model
from django.db.models import Count, Avg, F, ExpressionWrapper, DurationField

def job_model():
    try:
        return apps.get_model("partitions", "Job")
    except LookupError:
        return None

def stats():
    model = job_model()
    users = get_user_model().objects.count()
    from .presence import count_connected
    result = {"type": "admin.stats", "utilisateurs": users,
              "utilisateurs_connectes": count_connected(), "jobs_en_cours": 0,
              "partitions": 0, "taux_echec": 0, "temps_moyen": None, "tonalites": [],
              "p2_disponible": model is not None}
    if model is None:
        return result
    jobs = model.objects.all()
    total = jobs.count()
    result.update({
        "jobs_en_cours": jobs.filter(status__in=["PENDING", "PROCESSING"]).count(),
        "partitions": jobs.filter(status="COMPLETED").count(),
        "taux_echec": round(100 * jobs.filter(status="FAILED").count() / total, 1) if total else 0,
        "tonalites": list(jobs.values("tonalite").annotate(nombre=Count("id")).order_by("-nombre")[:10]),
    })
    duration = jobs.filter(date_fin__isnull=False).aggregate(value=Avg(
        ExpressionWrapper(F("date_fin") - F("date_creation"), output_field=DurationField())))['value']
    result["temps_moyen"] = round(duration.total_seconds(), 1) if duration else None
    return result


def snapshot():
    result = stats()
    model = job_model()
    result["jobs"] = [{"type": "admin.job", "job_id": str(job.pk),
                       "user": job.user.get_username(), "status": job.status,
                       "progress": job.progress, "etape": getattr(job, "etape", ""),
                       "error": job.message_erreur}
                      for job in model.objects.select_related("user").order_by("-date_creation")[:30]] if model else []
    return result
