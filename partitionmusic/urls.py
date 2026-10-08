"""
URL configuration for partitionmusic project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path("comptes/", include("comptes.urls")),

urlpatterns = [
    path("", views.home, name="home"),
    path("jobs/<uuid:job_id>/", views.job_detail, name="job_detail"),
    path("api/jobs/", views.api_job_create, name="api_job_create"),
    path("api/jobs/<uuid:job_id>/", views.api_job_status, name="api_job_status"),
    path("api/jobs/<uuid:job_id>/result/", views.api_job_result, name="api_job_result"),
]