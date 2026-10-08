from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from .models import Job
from .views import job_to_dict


class JobConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.job_id = self.scope["url_route"]["kwargs"]["job_id"]
        user = self.scope["user"]
        if not user.is_authenticated:
            await self.close(code=4401)
            return
        job = await self.get_job(user)
        if job is None:
            await self.close(code=4404)
            return
        self.group = f"job_{self.job_id}"
        await self.channel_layer.group_add(self.group, self.channel_name)
        await self.accept()
        # statut courant tout de suite (le job a pu finir avant la connexion)
        await self.send_json(self.etat(job))

    async def disconnect(self, code):
        if hasattr(self, "group"):
            await self.channel_layer.group_discard(self.group, self.channel_name)

    @database_sync_to_async
    def get_job(self, user):
        return Job.objects.filter(id=self.job_id, user=user).first()

    @staticmethod
    def etat(job):
        d = job_to_dict(job)
        if job.status == "COMPLETED":
            return {"type": "job.completed", "job_id": d["job_id"], "result": d["result"]}
        if job.status == "FAILED":
            return {"type": "job.failed", "job_id": d["job_id"],
                    "error": "Impossible de générer la partition"}
        return {"type": "job.progress", "job_id": d["job_id"], "status": d["status"],
                "progress": d["progress"], "etape": ""}

    async def job_progress(self, event):
        await self.send_json(event["data"])

    async def job_completed(self, event):
        await self.send_json(event["data"])

    async def job_failed(self, event):
        await self.send_json(event["data"])