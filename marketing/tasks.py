from celery.task import task
from marketing.models import Contact, ContactList


@task
def campaign_sechedule(request):
    pass


@task
def campaign_open(request):
    pass


@task
def campaign_click(request):
    pass


@task
def upload_csv_file(data, user, contact_lists):
    for each in data:
        contact = Contact.objects.filter(email=each['email']).first()
        if not contact:
            contact = Contact.objects.create(
                email=each['email'], created_by_id=user,
                name=each['first name'])
            if each.get('company name', None):
                contact.company_name = each['company name']
            if each.get('last name', None):
                contact.last_name = each['last name']
            if each.get('city', None):
                contact.city = each['city']
            if each.get("state", None):
                contact.state = each['state']
            contact.save()
        for contact_list in contact_lists:
            contact.contact_list.add(ContactList.objects.get(id=int(contact_list)))
