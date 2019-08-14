# from datetime import datetime, timedelta

# from django.core.files.uploadedfile import SimpleUploadedFile
# from django.test import TestCase
# from django.urls import reverse

# from accounts.models import Account
# from common.models import Address, Attachments, Comment, User
# from invoices.models import Invoice
# from teams.models import Teams


# class InvoiceCreateTest(object):

#     def setUp(self):
#         self.user = User.objects.create(
#             first_name="johnInvoice", username='johnDoeInvoice', email='johnDoeInvoice@example.com', role='ADMIN')
#         self.user.set_password('password')
#         self.user.save()

#         self.user1 = User.objects.create(
#             first_name="janeInvoice",
#             username='janeDoeInvoice',
#             email='janeDoeInvoice@example.com',
#             role="USER",
#             has_sales_access=True)
#         self.user1.set_password('password')
#         self.user1.save()

#         self.user2 = User.objects.create(
#             first_name="joeInvoice",
#             username='joeInvoice',
#             email='joeInvoice@example.com',
#             role="USER",
#             has_sales_access=True)
#         self.user2.set_password('password')
#         self.user2.save()

#         self.team_dev = Teams.objects.create(name='invoices teams')
#         self.team_dev.users.add(self.user2.id)

#         self.account = Account.objects.create(
#             name="john invoice", email="johnDoeInvoice@example.com", phone="123456789",
#             billing_address_line="", billing_street="street name",
#             billing_city="city name",
#             billing_state="state", billing_postcode="1234",
#             billing_country="US",
#             website="www.example.como", created_by=self.user, status="open",
#             industry="SOFTWARE", description="Testing")

#         self.invoice = Invoice.objects.create(
#             invoice_title='invoice title',
#             invoice_number='invoice number',
#             currency='USD',
#             email='invoiceTitle@email.com',
#             due_date=(datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d'),
#             total_amount='1000',
#             # created
#         )

#         self.comment = Comment.objects.create(
#             comment='test comment', invoice=self.invoice,
#             commented_by=self.user
#         )
#         self.attachment = Attachments.objects.create(
#             attachment='image.png', invoice=self.invoice,
#             created_by=self.user
#         )


# class TaskListTestCase(TaskCreateTest, TestCase):

#     def test_tasks_list(self):
#         self.client.login(email='johnTask@example.com', password='password')
#         response = self.client.get(reverse('tasks:tasks_list'))
#         self.assertEqual(response.status_code, 200)

#         data = {
#             'task_title': 'title',
#             'status': 'New',
#             'priority': 'Medium'
#         }
#         response = self.client.post(reverse('tasks:tasks_list'), data)
#         self.assertEqual(response.status_code, 200)

#         self.client.login(email='janeDoeTask@example.com', password='password')
#         response = self.client.get(reverse('tasks:tasks_list'))
#         self.assertEqual(response.status_code, 200)

#         response = self.client.post(reverse('tasks:tasks_list'), data)
#         self.assertEqual(response.status_code, 200)
