"""P1 appelle ces fonctions depuis son consumer de notifications.
Chaque canal représente une connexion ; un TTL élimine les connexions mortes.
"""
import time
from django.conf import settings
from redis import Redis
import logging
logger = logging.getLogger(__name__)
KEY = "partitionmusic:presence"
TTL = 120

def connection_utilisateur(user_id, channel_name):
    client = Redis.from_url(settings.REDIS_URL)
    client.zadd(KEY, {f"{int(user_id)}:{channel_name}": time.time()})
    from .events import diffuser_presence_admin
    diffuser_presence_admin()

def deconnexion_utilisateur(user_id, channel_name):
    Redis.from_url(settings.REDIS_URL).zrem(KEY, f"{int(user_id)}:{channel_name}")
    from .events import diffuser_presence_admin
    diffuser_presence_admin()

def count_connected():
    try:
        client = Redis.from_url(settings.REDIS_URL, socket_connect_timeout=1, socket_timeout=1)
        client.zremrangebyscore(KEY, "-inf", time.time() - TTL)
        return len({entry.split(b":", 1)[0] for entry in client.zrange(KEY, 0, -1)})
    except Exception:
        logger.warning("Compteur de présence Redis indisponible")
        return None
