from datetime import datetime, timedelta

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.test.utils import override_settings
from django.urls import reverse

from accounts.models import Account
from common.models import Address, Attachments, Comment, User
from invoices.models import Invoice, InvoiceHistory
from invoices.tasks import send_email
from invoices.tests import InvoiceCreateTest
from teams.models import Teams


# class AddTestCase(InvoiceCreateTest, TestCase):

#     @override_settings(CELERY_EAGER_PROPAGATES_EXCEPTIONS=True,
#                        CELERY_ALWAYS_EAGER=True,
#                        BROKER_BACKEND='memory')
#     def test_mytask(self):
#         task = send_email.apply((self.invoice.id,))
#         self.assertEqual('SUCCESS', task.state)
