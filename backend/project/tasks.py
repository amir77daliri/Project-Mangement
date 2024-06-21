from celery import shared_task
from django.core.mail import send_mail
from .models import Project
from django.db.models import Count, Case, When, IntegerField
import json


@shared_task
def send_daily_project_summary_report():
    # Get projects with the count of each task by status
    projects = Project.objects.annotate(
        pending_tasks_count=Count(Case(When(tasks__status='pending', then=1), output_field=IntegerField())),
        completed_tasks_count=Count(Case(When(tasks__status='completed', then=1), output_field=IntegerField())),
        in_progress_tasks_count=Count(Case(When(tasks__status='in_progress', then=1), output_field=IntegerField())),
        # Add more statuses as needed
    )
    data = {}
    for project in projects:
        data[f'{project.id}- {project.name}'] = {
            'pending_tasks': f'{project.pending_tasks_count}',
            'completed_tasks': f'{project.completed_tasks_count}',
            'in_progress_tasks': f'{project.in_progress_tasks_count}'
        }

    subject = 'Reminder Projects Email'
    message = json.dumps(data)
    from_email = "my_site@gmail.com"
    recipient_list = ['test@example.com']

    send_mail(subject, message, from_email, recipient_list)
