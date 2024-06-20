from django.core.cache import cache
from django.test import TestCase
from django.utils.timezone import make_aware
from rest_framework.test import APIClient
from project.models import Project
from task.models import Comment, Task
from task.views import Task_LIST_CACHE_KEY
from unittest.mock import patch
from datetime import datetime, timedelta


class TestProjectView(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.project = Project.objects.create(name='test_prj')
        cache.clear()
        self.task_1 = Task.objects.create(
            title='task_1',
            description='test task_1',
            project=self.project,
            due_date=make_aware(datetime.now() + timedelta(days=1))
        )
        self.task_2 = Task.objects.create(
            title='task_2',
            description='test task_2',
            project=self.project,
            status='completed',
            due_date=make_aware(datetime.now() + timedelta(days=2))
        )

    def tearDown(self):
        cache.clear()

    def test_get_task_list_and_cache_logic(self):
        """
            Test Get method of TaskListCreateApiView
        """
        self.assertIsNone(cache.get(Task_LIST_CACHE_KEY))
        response = self.client.get('/api/v1/tasks/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['title'], 'task_1')
        self.assertEqual(response.data[1]['status'], 'completed')
        # check data cache successfully
        cached_data = cache.get(Task_LIST_CACHE_KEY)
        self.assertIsNotNone(cached_data)
        self.assertEqual(len(cached_data), 2)
        # check correct data is cache :
        self.assertEqual(cached_data[0]['title'], self.task_1.title)
        self.assertEqual(cached_data[1]['status'], self.task_2.status)

    @patch('task.views.send_notification')
    def test_create_project_and_cache_invalidation(self, mock_send_notification):
        """
            Test Post method of TaskListCreateApiView
        """
        initial_count = Task.objects.count()
        # get tasks for cache set :
        response = self.client.get('/api/v1/tasks/')
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(cache.get(Task_LIST_CACHE_KEY))

        # create new task :
        data = {
            'title': 'New Test Task',
            'project': self.project.id,
            'due_date': "2024-08-22T10:00:00"
        }
        response = self.client.post('/api/v1/tasks/', data, format='json')
        # check for creating new task is success :
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Task.objects.count(), initial_count + 1)
        # check for cache invalidation :
        self.assertIsNone(cache.get(Task_LIST_CACHE_KEY))

    @patch('task.views.send_notification')
    def test_update_task(self, mock_send_notification):
        """
            Test Put method of TaskRetrieveUpdateDestroyApiView
        """
        # get tasks for cache set :
        response = self.client.get('/api/v1/tasks/')
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(cache.get(Task_LIST_CACHE_KEY))

        task_1 = self.task_1
        updated_data = {
            'title': 'update task 1 title',
            'status': 'completed',
            'project': self.project.id,
            'due_date': task_1.due_date
        }
        self.client.put(f"/api/v1/tasks/{task_1.id}", updated_data, format='json')
        # re fetch task from db after update
        updated_task = Task.objects.get(id=task_1.id)
        # check for update task is success :
        self.assertEqual(updated_task.title, updated_data['title'])
        self.assertEqual(updated_task.status, updated_data['status'])
        self.assertEqual(updated_task.due_date, task_1.due_date)
        # check for cache invalidation :
        self.assertIsNone(cache.get(Task_LIST_CACHE_KEY))

    @patch('task.views.send_notification')
    def test_delete_task(self, mock_send_notification):
        """
            Test Delete method of TaskRetrieveUpdateDestroyApiView
        """
        # get tasks for cache set :
        response = self.client.get('/api/v1/tasks/')
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(cache.get(Task_LIST_CACHE_KEY))

        task_1 = self.task_1
        response = self.client.delete(f"/api/v1/tasks/{task_1.id}")

        # check for deleting task was success
        self.assertEqual(response.status_code, 204)
        with self.assertRaises(Task.DoesNotExist):
            Task.objects.get(id=task_1.id)
        # check for invalidating cache :
        self.assertIsNone(cache.get(Task_LIST_CACHE_KEY))
