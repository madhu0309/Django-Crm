from celery.task import task
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from accounts.models import Account, Email
from common.models import User
from contacts.models import Contact
from tasks.models import Task


@task
def send_email(task_id):
    task = Task.objects.filter(id=task_id).first()
    if task:
        subject = 'CRM Task : {0}'.format(task.title)
        context = {}
        context['task_title'] = task.title
        context['task_id'] = task.id
        context['task_created_by'] = task.created_by
        html_content = render_to_string(
            'tasks_email_template.html', context=context)
        recipients = task.assigned_to.all()
        if recipients.count() > 0:
            for recipient in recipients:
                msg = EmailMessage(
                    subject=subject, body=html_content, to=[recipient.email, ])
                msg.content_subtype = "html"
                msg.send()


# TODO what should be in the email template
