from asgiref.sync import sync_to_async
from django.test import TestCase
from channels.testing import WebsocketCommunicator
from task.consumer import TaskNotificationConsumer
from task.models import Task, Comment
from project.models import Project
from rest_framework.test import APIClient
from django.utils.timezone import make_aware
from datetime import datetime, timedelta
from django.core.cache import cache


class TestTaskNotificationConsumer(TestCase):

    def setUp(self):
        self.client = APIClient()
        cache.clear()
        self.project = Project.objects.create(name='project 1')
        self.task = Task.objects.create(
            title='task_1',
            description='test task_1',
            project=self.project,
            due_date=make_aware(datetime.now() + timedelta(days=1))
        )
        self.task_2 = Task.objects.create(
            title='task_2',
            description='test task_2',
            project=self.project,
            due_date=make_aware(datetime.now() + timedelta(days=1))
        )

    async def test_task_notifications(self):
        communicator = WebsocketCommunicator(TaskNotificationConsumer.as_asgi(), "/ws/notification/")
        connected, _ = await communicator.connect()

        # Check connection is established
        self.assertTrue(connected)

        # Send a test data to the consumer
        data = {'data': 'Test notification'}
        await communicator.send_json_to(data)
        response = await communicator.receive_json_from()
        self.assertEqual(response, {'msg': 'i am django framework'})

        # Create notification:
        data = {
            'title': 'New Test Task',
            'project': self.project.id,
            'due_date': "2024-08-22T10:00:00"
        }
        await sync_to_async(self.client.post)('/api/v1/tasks/', data, format='json')
        create_notification_message = await communicator.receive_from()
        # print(create_notification_message)
        self.assertEqual(create_notification_message, 'A new task created !')

        # Update Notification :
        update_data = {
            'title': 'Update Test Task title',
            'project': self.project.id,
            'due_date': "2024-08-22T10:00:00"
        }
        await sync_to_async(self.client.put)(f'/api/v1/tasks/{self.task.id}', update_data, format='json')
        updated_task = await sync_to_async(Task.objects.get)(id=self.task.id)
        self.assertEqual(updated_task.title, update_data['title'])
        update_notification_message = await communicator.receive_from()
        # print(update_notification_message)
        self.assertEqual(update_notification_message, f"the task {update_data['title']} updated!")

        # Delete notification:
        response = await sync_to_async(self.client.delete)(f'/api/v1/tasks/{self.task.id}')
        self.assertEqual(response.status_code, 204)
        delete_notification_message = await communicator.receive_from()
        # print(delete_notification_message)
        self.assertEqual(delete_notification_message, f"the task by id= {self.task.id} deleted!")

        # Add Comment notification:
        comment_data = {
            'author': 'reza',
            'content': 'new comment for task 1'
        }

        response = await sync_to_async(self.client.post)(f'/api/v1/tasks/{self.task_2.id}/comments/', comment_data, format='json')
        self.assertEqual(response.status_code, 201)
        add_comment_notification = await communicator.receive_from()
        # print(add_comment_notification)
        self.assertEqual(add_comment_notification, f"comment Added for task {self.task_2}!")

        # Disconnect ct from the consumer
        await communicator.disconnect()
