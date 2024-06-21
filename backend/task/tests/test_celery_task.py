from django.test import TestCase
from unittest.mock import patch
from datetime import timedelta
from django.utils import timezone
from config.celery import celery_app
from celery.schedules import crontab
from task.tasks import send_daily_email_task
from task.models import Task


class CeleryTaskTestCase(TestCase):

    def test_send_daily_email_schedule(self):
        # Check if the task is scheduled correctly
        scheduled_tasks = celery_app.conf.beat_schedule
        self.assertIn('send_daily_email', scheduled_tasks)
        self.assertEqual(scheduled_tasks['send_daily_email']['task'], 'task.tasks.send_daily_email_task')
        self.assertEqual(scheduled_tasks['send_daily_email']['schedule'], crontab(minute='0', hour='*/12'))

    @patch('task.tasks.send_mail')
    @patch('task.tasks.Task.objects')
    def test_send_daily_email_task(self, mock_task_objects, mock_send_mail):
        # Set up mock Task queryset
        now = timezone.now()
        next_24_hours = now + timedelta(hours=24)
        mock_task_objects.exclude.return_value.filter.return_value.values.return_value = [
            {'id': 1, 'title': 'Task 1'},
            {'id': 2, 'title': 'Task 2'},
        ]

        # Call the task
        send_daily_email_task()

        # Ensure send_mail was called once with the correct parameters
        expected_message = "the tasks in task:1-Task 1 | task:2-Task 2 |  due within the next 24 hours"
        mock_send_mail.assert_called_once_with(
            'Reminder Tasks Email',
            expected_message,
            'my_site@gmail.com',
            ['test@example.com']
        )
