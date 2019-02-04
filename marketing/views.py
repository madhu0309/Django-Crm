from django.shortcuts import render


def index(request):
    return render(request, {}, 'marketing/index.html')


def contact_lists(request):
    pass


def new_contact_list(request):
    pass


def contact_list_detail(request):
    pass


def email_template_list(request):
    pass


def email_template_new(request):
    pass


def campaign_open(request):
    pass


def campaign_click(request):
    pass
