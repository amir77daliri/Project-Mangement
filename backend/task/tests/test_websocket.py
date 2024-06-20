from django.test import TestCase
from channels.testing import WebsocketCommunicator
from task.consumer import TaskNotificationConsumer
import json


class TestTaskNotificationConsumer(TestCase):
    async def test_task_notifications(self):
        communicator = WebsocketCommunicator(TaskNotificationConsumer.as_asgi(), "/ws/notification/")
        connected, _ = await communicator.connect()

        # Check connection is established
        self.assertTrue(connected)

        # Send a test data to the consumer
        data = {'data': 'Test notification'}
        await communicator.send_json_to(data)

        # Check if the consumer receives and responds correctly
        response = await communicator.receive_json_from()
        print(response)
        self.assertEqual(response, {'msg': 'i am django framework'})

        # Disconnect from the consumer
        await communicator.disconnect()
