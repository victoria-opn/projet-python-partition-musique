from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from .services import snapshot

class AdminConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.subscribed = False
        user = self.scope["user"]
        if not user.is_authenticated or not user.is_active or not user.is_staff:
            await self.close(code=4403)
            return
        await self.channel_layer.group_add("admin", self.channel_name)
        self.subscribed = True
        await self.accept()
        await self.send_json(await database_sync_to_async(snapshot)())
    async def disconnect(self, code):
        if self.subscribed:
            await self.channel_layer.group_discard("admin", self.channel_name)
    async def admin_event(self, event):
        await self.send_json(event["payload"])
