import logging
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_GET, require_POST
from django.utils.dateparse import parse_date
from .services import job_model, stats, snapshot
from .events import diffuser_evenement_admin
logger = logging.getLogger(__name__)

def unavailable():
    return HttpResponse("Le modèle Job de P2 n’est pas encore intégré.", status=503)

@staff_member_required
@require_GET
def home(request):
    model = job_model()
    return render(request, "dashboard/home.html", {"stats": stats(), "jobs": model.objects.select_related("user").order_by("-date_creation")[:30] if model else []})

@staff_member_required
@require_GET
def api_stats(request):
    return JsonResponse(snapshot())

@staff_member_required
@require_GET
def jobs(request):
    model = job_model()
    queryset = model.objects.select_related("user").order_by("-date_creation") if model else []
    if model:
        status = request.GET.get("status", "")
        if status in {"PENDING", "PROCESSING", "COMPLETED", "FAILED"}:
            queryset = queryset.filter(status=status)
        user = request.GET.get("user", "")
        if user:
            queryset = queryset.filter(user__username__icontains=user)
        try:
            day = parse_date(request.GET.get("date", ""))
        except ValueError:
            day = None
        if day:
            queryset = queryset.filter(date_creation__date=day)
    return render(request, "dashboard/jobs.html", {"page": Paginator(queryset, 30).get_page(request.GET.get("page")), "p2_disponible": model is not None})

@staff_member_required
@require_POST
def retry_job(request, job_id):
    model = job_model()
    if model is None:
        return unavailable()
    job = get_object_or_404(model, pk=job_id)
    # Le lancement reste sous la responsabilité de la tâche Celery P2.
    from partitions.tasks import process_job
    if model.objects.filter(pk=job.pk, status="FAILED").update(status="PENDING", progress=0, message_erreur="", date_fin=None):
        job.refresh_from_db()
        try:
            process_job.delay(str(job.pk))
        except Exception:
            logger.exception("Impossible de relancer le job %s", job.pk)
            model.objects.filter(pk=job.pk, status="PENDING").update(status="FAILED", message_erreur="Le service de traitement est indisponible.")
            messages.error(request, "Le service de traitement est indisponible.")
        job.refresh_from_db()
        diffuser_evenement_admin(job)
    else:
        messages.error(request, "Seul un job en échec peut être relancé.")
    return redirect("dashboard:jobs")

@staff_member_required
@require_POST
def delete_job(request, job_id):
    model = job_model()
    if model is None:
        return unavailable()
    job = get_object_or_404(model, pk=job_id)
    if job.status in {"PENDING", "PROCESSING"}:
        messages.error(request, "Attendez la fin du traitement avant de supprimer ce job.")
        return redirect("dashboard:jobs")
    for file in [job.audio, job.resultat]:
        if file:
            file.delete(save=False)
    job.delete()
    from .events import diffuser_presence_admin
    diffuser_presence_admin()
    messages.success(request, "Job et fichiers supprimés.")
    return redirect("dashboard:jobs")

@staff_member_required
@require_GET
def users(request):
    queryset = get_user_model().objects.order_by("username")
    return render(request, "dashboard/users.html", {"page": Paginator(queryset, 30).get_page(request.GET.get("page"))})

@staff_member_required
@require_POST
def toggle_user(request, user_id):
    user = get_object_or_404(get_user_model(), pk=user_id)
    if user.pk == request.user.pk or user.is_superuser:
        messages.error(request, "Ce compte ne peut pas être désactivé depuis le tableau de bord.")
    else:
        user.is_active = not user.is_active
        user.save(update_fields=["is_active"])
        messages.success(request, "Compte mis à jour.")
    return redirect("dashboard:users")
