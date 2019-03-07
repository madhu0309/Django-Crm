from django.test import TestCase
from django.test import Client
from common.models import User
from emails.models import Email
from emails.forms import EmailForm


class UserCreation(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(
            first_name="nicole", username='nicole', email="n@mp.com", role="ADMIN")
        self.user.set_password('navi123')
        self.user.save()
        self.email = Email.objects.create(
            from_email="admin@micropyramid.com", to_email="nike@micropyramid.com", subject="wish", message="haii",
            important=False)
        self.client.login(username='n@mp.com', password='navi123')


class EmailSentEdit(UserCreation, TestCase):
    def test_edit_form_valid(self):
        form = EmailForm(data={'from_email': "abc@mp.com",
                               'to_email': "xyz@mp.com",
                               'subject': "hello hi",
                               'message': 'simple mail'})
        # print('yes')
        self.assertTrue(form.is_valid())

    def test_edit_form_invalid(self):
        form = EmailForm(data={'from_email': "abc@mp.com",
                               'to_email': "",
                               'subject': "hello hi",
                               'message': 'simple mail'})
        # print('yes2')
        self.assertFalse(form.is_valid())


class EmailListTestCase(UserCreation, TestCase):
    def test_email_list(self):
        url = "/emails/list/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class EmailTestCase(UserCreation, TestCase):
    def test_email_compose(self):
        url = "/emails/compose/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_email_trash_get(self):
        url = "/emails/email_trash_delete/" + str(self.email.pk) + "/"
        # print(url)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_email_send_fail(self):
        url = "/emails/compose/"
        data = {
            'from_email': "abc@micropyramid.com", 'to_email': "",
            'subject': 'act', 'message': "Hello"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
# email_trash_delete/

    def test_email_send(self):
        url = "/emails/compose/"
        data = {
            'from_email': "abc@micropyramid.com", 'to_email': "meg@gmail.com",
            'subject': 'act', 'message': "Hello"
        }
        response = self.client.post(url, data)
        get_email = Email.objects.get(subject="wish")
        # boo = Email.objects.get(important=True)
        # print('yes')
        self.assertFalse(get_email.important)
        self.assertEqual(get_email.subject, get_email.__str__())

        self.assertEqual(response.status_code, 302)

    def test_email_sent(self):
        url = "/emails/email_sent/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_email_trash(self):
        url = "/emails/email_trash/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_email_draft(self):
        url = "/emails/email_draft/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_email_draft_delete(self):
        url = "/emails/email_draft_delete/" + str(self.email.pk) + "/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_email_delete(self):
        url = "/emails/email_delete/" + str(self.email.pk) + "/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_email_view(self):
        url = "/emails/email_view/" + str(self.email.pk) + "/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_email_sent_edit_get(self):
        url = "/emails/email_sent_edit/" + str(self.email.pk) + "/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_email_sent_edit_post(self):
        url = "/emails/email_sent_edit/" + str(self.email.pk) + "/"
        data = {
            'from_email': "abc@micropyramid.com", 'to_email': "meg@gmail.com",
            'subject': 'act', 'message': "Hello"
        }
        data1 = {
            'from_email': "abc@micropyramid.com", 'to_email': "",
            'subject': 'act', 'message': "Hello"
        }
        response = self.client.post(url, data)
        response1 = self.client.post(url, data1)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response1.status_code, 200)

    def test_email_imp_list(self):
        url = "/emails/email_imp_list/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


    # def test_email_move_to_trash(self):
    #     url = "/emails/email_move_to_trash/" + str(self.email.pk) + "/"
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, 302)
    #     response = self.client.post(reverse('302'), {}, HTTP_REFERER=url)

    # def test_email_trash_del(self):
    #     url = "/emails/trash_delete/"+str(self.email.pk)+"/$"
    #     print(url)
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code,200)
