from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse


def test_comptes(request):
    return HttpResponse("Bonjour depuis l'app comptes !")
