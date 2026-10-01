import logging
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .services import stats
logger = logging.getLogger(__name__)

def diffuser_evenement_admin(job):
    """Contrat P3 : appelé par P2 à la création, progression et fin d’un job."""
    data = {"type": "admin.job", "job_id": str(job.pk), "user": job.user.get_username(),
            "status": job.status, "progress": job.progress,
            "etape": getattr(job, "etape", ""), "error": job.message_erreur}
    layer = get_channel_layer()
    try:
        async_to_sync(layer.group_send)("admin", {"type": "admin.event", "payload": data})
        async_to_sync(layer.group_send)("admin", {"type": "admin.event", "payload": stats()})
    except Exception:
        logger.exception("Diffusion admin indisponible")

def diffuser_presence_admin():
    try:
        async_to_sync(get_channel_layer().group_send)("admin", {"type": "admin.event", "payload": stats()})
    except Exception:
        logger.exception("Diffusion présence admin indisponible")
