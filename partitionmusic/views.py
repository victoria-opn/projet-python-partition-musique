from django.db import connection
from django.http import HttpRequest, HttpResponse
from django.views.decorators.http import require_GET


@require_GET
def health(request: HttpRequest) -> HttpResponse:
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
    return HttpResponse("ok")
