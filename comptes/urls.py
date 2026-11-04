from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path("", views.accueil, name="accueil"),
    path("resultat/", views.resultat, name="resultat"),
    path("historique/", views.historique, name="historique"),
    path(
        "historique/<int:depot_id>/",
        views.resultat_detail,
        name="resultat-detail",
    ),
    path(
        "historique/<int:depot_id>/telecharger/",
        views.telecharger_partition_demo,
        name="telecharger-partition",
    ),
    path(
        "connexion/",
        auth_views.LoginView.as_view(
            template_name="comptes/connexion.html",
            redirect_authenticated_user=True,
        ),
        name="connexion",
    ),
    path("deconnexion/", views.deconnexion, name="deconnexion"),
]
