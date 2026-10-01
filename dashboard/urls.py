from django.urls import path
from . import views
app_name = "dashboard"
urlpatterns = [
    path("", views.home, name="home"),
    path("stats/", views.api_stats, name="stats"),
    path("jobs/", views.jobs, name="jobs"),
    path("jobs/<uuid:job_id>/relancer/", views.retry_job, name="retry_job"),
    path("jobs/<uuid:job_id>/supprimer/", views.delete_job, name="delete_job"),
    path("utilisateurs/", views.users, name="users"),
    path("utilisateurs/<int:user_id>/activer/", views.toggle_user, name="toggle_user"),
]
