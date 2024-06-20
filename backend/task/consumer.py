from channels.generic.websocket import AsyncWebsocketConsumer
import json


class TaskNotificationConsumer(AsyncWebsocketConsumer):
    _group_name = "task_notification"

    async def connect(self):
        await self.channel_layer.group_add(self._group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self._group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        message = "i am django framework"
        await self.send(json.dumps({'msg': message}))

    async def notify_task_changes(self, event):
        await self.send(text_data=event['data'])
