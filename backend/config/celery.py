from celery import Celery
from celery.schedules import crontab
from datetime import timedelta
import os


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
celery_app = Celery('config')

celery_app.conf.broker_url = 'amqp://rabbitmq'
celery_app.conf.result_backend = 'rpc://rabbitmq'
celery_app.conf.task_serializer = 'json'
celery_app.conf.result_serializer = 'json'
celery_app.conf.timezone = 'UTC'
celery_app.conf.accept_content = ['json']
celery_app.conf.result_expires = timedelta(days=1)

celery_app.autodiscover_tasks()

celery_app.conf.beat_schedule = {
    'send_daily_email': {
        'task': 'task.tasks.send_daily_email_task',
        'schedule': crontab(minute='0', hour='*/12'),  # Execute every 12 hours
    },
    'send_daily_report': {
        'task': 'project.tasks.send_daily_project_summary_report',
        'schedule': crontab(minute='0', hour='1'),  # Execute at midnight
    },
}
