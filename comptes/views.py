from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import AudioUploadForm
from .models import DepotAudio


@login_required
def accueil(request):
    return render(request, "comptes/accueil.html", {"form": AudioUploadForm()})


@login_required
def resultat(request):
    if request.method == "POST":
        form = AudioUploadForm(request.POST, request.FILES)
        if form.is_valid():
            depot = DepotAudio.objects.create(
                utilisateur=request.user,
                nom_fichier=form.cleaned_data["audio"].name,
            )
            return redirect("resultat-detail", depot_id=depot.pk)
        return render(
            request,
            "comptes/accueil.html",
            {"form": form},
            status=400,
        )

    return render(request, "comptes/resultat.html")


@login_required
def historique(request):
    depots = DepotAudio.objects.filter(utilisateur=request.user)
    return render(request, "comptes/historique.html", {"depots": depots})


@login_required
def resultat_detail(request, depot_id):
    depot = get_object_or_404(DepotAudio, pk=depot_id, utilisateur=request.user)
    return render(request, "comptes/resultat.html", {"depot": depot})


@login_required
def telecharger_partition_demo(request, depot_id):
    get_object_or_404(DepotAudio, pk=depot_id, utilisateur=request.user)
    pdf_content = _partition_demo_pdf()
    response = HttpResponse(pdf_content, content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="partition-demo-{depot_id}.pdf"'
    )
    return response


def _partition_demo_pdf():
    stream = (
        b"BT\n/F1 20 Tf\n72 740 Td\n"
        b"(Partition de demonstration) Tj\n"
        b"/F1 12 Tf\n0 -32 Td\n"
        b"(Le traitement audio n'est pas encore active.) Tj\n"
        b"0 -22 Td\n"
        b"(Ce PDF est un exemple, pas la transcription du fichier.) Tj\n"
        b"ET\n"
    )
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        (
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>"
        ),
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n"
        + stream
        + b"endstream",
    ]

    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for index, obj in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{index} 0 obj\n".encode("ascii"))
        pdf.extend(obj)
        pdf.extend(b"\nendobj\n")

    xref_offset = len(pdf)
    pdf.extend(f"xref\n0 {len(offsets)}\n".encode("ascii"))
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    pdf.extend(
        (
            f"trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\n"
            f"startxref\n{xref_offset}\n%%EOF\n"
        ).encode("ascii")
    )
    return bytes(pdf)


def deconnexion(request):
    if request.method != "POST":
        return redirect("connexion")
    logout(request)
    return redirect("connexion")
