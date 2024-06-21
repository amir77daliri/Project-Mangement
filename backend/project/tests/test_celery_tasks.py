from django.test import TestCase
from project.models import Project
from task.models import Task
from unittest.mock import patch
from project.tasks import send_daily_project_summary_report
import json
from datetime import timedelta, datetime
from django.utils.timezone import make_aware
from django.db.models import Count, Case, When, IntegerField


class SendDailyProjectSummaryReportTestCase(TestCase):
    def setUp(self):
        # Create projects and tasks for testing
        self.project1 = Project.objects.create(name='Project 1', description='Description 1')
        self.project2 = Project.objects.create(name='Project 2', description='Description 2')

        Task.objects.create(title='Task 1', status='pending', project=self.project1, due_date=make_aware(datetime.now() + timedelta(days=1)))
        Task.objects.create(title='Task 2', status='completed', project=self.project1, due_date=make_aware(datetime.now() + timedelta(days=1)))
        Task.objects.create(title='Task 3', status='in_progress', project=self.project1, due_date=make_aware(datetime.now() + timedelta(days=1)))
        Task.objects.create(title='Task 4', status='pending', project=self.project2, due_date=make_aware(datetime.now() + timedelta(days=1)))
        Task.objects.create(title='Task 5', status='completed', project=self.project2, due_date=make_aware(datetime.now() + timedelta(days=1)))

    @patch('project.tasks.send_mail')
    def test_send_daily_project_summary_report(self, mock_send_mail):
        # Call the task
        send_daily_project_summary_report()

        # Check that send_mail was called once
        self.assertEqual(mock_send_mail.call_count, 1)

        projects = Project.objects.annotate(
            pending_tasks_count=Count(Case(When(tasks__status='pending', then=1), output_field=IntegerField())),
            completed_tasks_count=Count(Case(When(tasks__status='completed', then=1), output_field=IntegerField())),
            in_progress_tasks_count=Count(Case(When(tasks__status='in_progress', then=1), output_field=IntegerField())),
        )
        data = {}
        for project in projects:
            data[f'{project.id}- {project.name}'] = {
                'pending_tasks': f'{project.pending_tasks_count}',
                'completed_tasks': f'{project.completed_tasks_count}',
                'in_progress_tasks': f'{project.in_progress_tasks_count}'
            }
        expected_message = json.dumps(data)

        mock_send_mail.assert_called_once_with(
            'Reminder Projects Email',
            expected_message,
            'my_site@gmail.com',
            ['test@example.com']
        )
