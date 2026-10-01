from django.apps import AppConfig

class DashboardConfig(AppConfig):
    name = "dashboard"
    def ready(self):
        from django.apps import apps
        from django.contrib import admin
        try:
            job = apps.get_model("partitions", "Job")
        except LookupError:
            return
        if not admin.site.is_registered(job):
            admin.site.register(job)
