from datetime import datetime

import pytz
from celery.task import task
from django.conf import settings
from django.core.mail import EmailMessage
from django.shortcuts import reverse
from django.template import Context, Template
from django.template.loader import render_to_string

from accounts.models import Account, Email
from common.models import User
from common.utils import convert_to_custom_timezone
from contacts.models import Contact

# @task
# def send_email(subject, html_content, from_email=None,
#                recipients=[]):
#     account = Account.objects.filter(id=from_email).first()
#     if account:
#         contacts = recipients
#         for contact in contacts:
#             contact_obj = Contact.objects.filter(email=contact).first()
#             if contact_obj:
#                 Email.objects.create(sender=account,
#                     recipient=contact_obj,message_subject=subject,
#                     message_body=html_content)
#                 msg = EmailMessage(
#                     subject,
#                     html_content,
#                     from_email=account.email,
#                     to=[contact_obj.email, ]
#                 )
#                 msg.content_subtype = "html"
#                 msg.send()


@task
def send_email(email_obj_id):
    email_obj = Email.objects.filter(id=email_obj_id).first()
    if email_obj:
        account = email_obj.account.email
        contact = email_obj.recipient.email
        contact_obj = Contact.objects.filter(email=contact).first()
        if contact_obj:
            html = email_obj.message_body
            context_data = {
                'email': contact_obj.email if contact_obj.email else '',
                'name': contact_obj.first_name if contact_obj.first_name else '' + ' ' + contact_obj.last_name if contact_obj.last_name else '',
            }
            try:
                html_content = Template(html).render(Context(context_data))
                subject = email_obj.message_subject
                msg = EmailMessage(
                    subject,
                    html_content,
                    from_email=account.email,
                    to=[contact_obj.email, ]
                )
                msg.content_subtype = "html"
                res = msg.send()
                if res:
                    email_obj.is_sent = True
                    email_obj.sent_at = datetime.now()
                    email_obj.save()
            except Exception as e:
                print(e)
                pass



@task
def send_email_to_assigned_user(recipients, from_email, domain='demo.django-crm.io', protocol='http'):
    """ Send Mail To Users When they are assigned to a contact """
    account = Account.objects.filter(id=from_email).first()
    created_by = account.created_by
    for user in recipients:
        recipients_list = []
        user = User.objects.filter(id=user, is_active=True).first()
        if user:
            recipients_list.append(user.email)
            context = {}
            context["url"] = protocol + '://' + domain + \
                reverse('accounts:view_account', args=(account.id,))
            context["user"] = user
            context["account"] = account
            context["created_by"] = created_by
            subject = 'Assigned a account for you.'
            html_content = render_to_string(
                'assigned_to/account_assigned.html', context=context)

            msg = EmailMessage(
                subject,
                html_content,
                to=recipients_list
            )
            msg.content_subtype = "html"
            msg.send()


@task
def send_scheduled_emails():
    email_objs = Email.objects.filter(scheduled_later=True, is_sent=False)

    for each in email_objs:
        scheduled_date_time = each.scheduled_date_time

        sent_time = datetime.now().strftime('%Y-%m-%d %H:%M')
        sent_time = datetime.strptime(sent_time, '%Y-%m-%d %H:%M')
        local_tz = pytz.timezone(settings.TIME_ZONE)
        sent_time = local_tz.localize(sent_time)
        sent_time = convert_to_custom_timezone(
            sent_time, each.timezone, to_utc=True)

        if (
            str(each.scheduled_date_time.date()) == str(sent_time.date()) and
            str(scheduled_date_time.hour) == str(sent_time.hour)
        ):
            send_email.delay(each.id)
