from django.test import TestCase
from rest_framework.exceptions import ValidationError
from task.serializers import TaskSerializer, CommentSerializer
from project.models import Project
from datetime import datetime, timedelta


class TestProjectSerializer(TestCase):
    def setUp(self):
        self.project = Project.objects.create(name='prj_1', description='project 1 desc')

    def test_valid_serializer(self):
        valid_data_1 = {
            'title': 'task 1',
            'description': 'This is task 1',
            'status': 'pending',
            'due_date': datetime.now() + timedelta(days=2),
            'project': self.project.id
        }
        valid_data_2 = {
            'title': 'Test Project 2',
            'status': 'in_progress',
            'due_date': datetime.now() + timedelta(hours=20),
            'project': self.project.id
        }

        valid_ser_1 = TaskSerializer(data=valid_data_1)
        valid_ser_2 = TaskSerializer(data=valid_data_2)

        self.assertTrue(valid_ser_1.is_valid())
        self.assertTrue(valid_ser_2.is_valid())

    def test_invalid_serializer(self):
        invalid_data_1 = {
            'description': 'This is a test project.',
        }
        invalid_data_2 = {
            'title': 'Test Project 2',
            'status': 'finish',
            'due_date': datetime.now() + timedelta(hours=20),
            'project': self.project.id
        }

        serializer_1 = TaskSerializer(data=invalid_data_1)
        serializer_2 = TaskSerializer(data=invalid_data_2)

        with self.assertRaises(ValidationError):
            serializer_1.is_valid(raise_exception=True)

        with self.assertRaises(ValidationError):
            serializer_2.is_valid(raise_exception=True)

        self.assertIn('title', serializer_1.errors)
        self.assertIn('status', serializer_2.errors)
