from celery import shared_task
from django.core.mail import send_mail
from .models import Task
from django.utils import timezone
from datetime import timedelta


@shared_task
def send_daily_email_task():
    now = timezone.now()
    next_24_hours = now + timedelta(hours=24)

    tasks_within_24_hours = Task.objects.exclude(status='completed').filter(due_date__lte=next_24_hours).values('id', 'title')

    msg = ''
    for task in tasks_within_24_hours:
        msg += f"task:{task['id']}-{task['title'][:10]} | "

    subject = 'Reminder Tasks Email'
    message = "the tasks in " + msg + " due within the next 24 hours"
    from_email = "my_site@gmail.com"
    recipient_list = ['test@example.com']  # Replace with actual recipient email address

    send_mail(subject, message, from_email, recipient_list)
