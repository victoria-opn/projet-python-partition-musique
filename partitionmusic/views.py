from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_GET, require_POST

from .forms import JobForm, TONALITES
from .models import Job
from .tasks import process_job


def job_to_dict(job):
    data = {
        "job_id": str(job.id),
        "status": job.status,
        "progress": job.progress,
        "tonalite": job.tonalite,
        "error": job.message_erreur,
    }
    if job.status == Job.Status.COMPLETED:
        data["result"] = f"/api/jobs/{job.id}/result/"
    return data


@login_required
def home(request):
    profil = getattr(request.user, "profil", None)  # créé par P1 plus tard
    defaut = getattr(profil, "tonalite_defaut", "") or "C"
    return render(request, "partitions/home.html",
                  {"tonalites": TONALITES, "tonalite_defaut": defaut})


@login_required
def job_detail(request, job_id):
    job = get_object_or_404(Job, id=job_id, user=request.user)
    return render(request, "partitions/job_detail.html", {"job": job})


@login_required
@require_POST
def api_job_create(request):
    form = JobForm(request.POST, request.FILES)
    if not form.is_valid():
        return JsonResponse({"errors": form.errors.get_json_data()}, status=400)
    job = Job.objects.create(
        user=request.user,
        audio=form.cleaned_data["audio"],
        tonalite=form.cleaned_data["tonalite"],
    )
    process_job.delay(str(job.id))
    return JsonResponse(job_to_dict(job), status=201)


@login_required
@require_GET
def api_job_status(request, job_id):
    job = get_object_or_404(Job, id=job_id, user=request.user)
    return JsonResponse(job_to_dict(job))


@login_required
@require_GET
def api_job_result(request, job_id):
    job = get_object_or_404(Job, id=job_id, user=request.user)
    if job.status != Job.Status.COMPLETED or not job.resultat:
        raise Http404("Résultat indisponible")
    return FileResponse(job.resultat.open("rb"), content_type="application/pdf")