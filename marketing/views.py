import json
from django.conf import Settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http.response import JsonResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy, reverse
from common import status
from marketing.models import Tag, ContactList, Contact
from marketing.forms import ContactListForm, ContactForm
from marketing.tasks import upload_csv_file


def get_exact_match(query, m2m_field, ids):
    # query = tasks_list.annotate(count=Count(m2m_field))\
    #             .filter(count=len(ids))
    query = query
    for _id in ids:
        query = query.filter(**{m2m_field: _id})
    return query


@login_required(login_url='/login')
def dashboard(request):
    return render(request, 'marketing/dashboard.html')


@login_required(login_url='/login')
def contact_lists(request):
    tags = Tag.objects.all()
    if (request.user.is_superuser):
        queryset = ContactList.objects.all()
    else:
        queryset = ContactList.objects.filter(created_by=request.user)
    if request.method == 'POST':
        post_tags = request.POST.get('tags')
        if request.POST.get('search'):
            queryset = queryset.filter(
                Q(name__icontains=request.POST['search']) |
                Q(created_by__email__icontains=request.POST['search'])).distinct()

        if post_tags:

            filtered_list = json.loads(request.POST['tags'])

            if len(filtered_list) > 1:
                queryset = get_exact_match(queryset, 'tags', filtered_list)
            else:
                queryset = queryset.filter(tags__id__in=filtered_list)

    per_page = request.GET.get("per_page", 10)
    paginator = Paginator(queryset, per_page)
    page = request.GET.get('page', 1)
    try:
        contact_lists = paginator.page(page)
    except PageNotAnInteger:
        contact_lists = paginator.page(1)
    except EmptyPage:
        contact_lists = paginator.page(paginator.num_pages)
    data = {'contact_lists': contact_lists, 'tags': tags}
    return render(request, 'marketing/lists/index.html', data)


@login_required(login_url='/login')
def contacts_list(request):
    contacts = Contact.objects.all()
    data = {"contacts": contacts}
    return render(request, 'marketing/lists/all.html', data)


@login_required(login_url='/login')
def contact_list_new(request):
    data = {}
    if request.POST:
        form = ContactListForm(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.created_by = request.user
            instance.save()
            for each in json.loads(request.POST['tags']):
                tag, _ = Tag.objects.get_or_create(
                    name=each, created_by=request.user)
                instance.tags.add(tag)
            if request.FILES.get('contacts_file'):
                upload_csv_file.delay(form.validated_rows, request.user.id, [instance.id])

            return JsonResponse({'error': False, 'data': form.data}, status=status.HTTP_201_CREATED)
        return JsonResponse({'error': True, 'errors': form.errors}, status=status.HTTP_400_BAD_REQUEST)

    return render(request, 'marketing/lists/new.html', data)


@login_required(login_url='/login')
def edit_contact_list(request, pk):
    user = request.user
    try:
        contact_list = ContactList.objects.get(pk=pk)
    except ContactList.DoesNotExist:
        contact_list = ContactList.objects.none()
        return JsonResponse({}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        # contact_lists = ContactList.objects.filter(company=request.company)
        if (user.is_superuser):
            contact_lists = ContactList.objects.all()
        else:
            contact_lists = ContactList.objects.filter(created_by=request.user)

        data = {'contact_list': contact_list, 'contact_lists': contact_lists}
        return render(request, 'marketing/lists/new.html', data)
    else:
        form = ContactListForm(request.POST, request.FILES, instance=contact_list)
        if form.is_valid():
            instance = form.save()
            instance.tags.clear()
            for each in json.loads(request.POST['tags']):
                tag, _ = Tag.objects.get_or_create(name=each, created_by=request.user)
                instance.tags.add(tag)
            if request.FILES.get('contacts_file'):
                upload_csv_file.delay(form.validated_rows, request.user.id, [instance.id])

            return JsonResponse(form.data, status=status.HTTP_201_CREATED)
        return JsonResponse({'error': True, 'errors': form.errors}, status=status.HTTP_400_BAD_REQUEST)


@login_required(login_url='/login')
def view_contact_list(request, pk):
    contact_list = get_object_or_404(ContactList, pk=pk)
    contacts = Contact.objects.filter(contact_list__in=[contact_list])
    if request.POST and request.POST.get("search"):
        contacts = contacts.filter(
            Q(name__icontains=request.POST['search']) | Q(email__icontains=request.POST['search']))

    per_page = request.GET.get("per_page", 10)
    paginator = Paginator(contacts.order_by('id'), per_page)
    page = request.GET.get('page', 1)
    try:
        contacts = paginator.page(page)
    except PageNotAnInteger:
        contacts = paginator.page(1)
    except EmptyPage:
        contacts = paginator.page(paginator.num_pages)

    data = {'contact_list': contact_list, "contacts": contacts}
    template_name = "marketing/lists/all.html"
    return render(request, template_name, data)


@login_required(login_url='/login')
def delete_contact_list(request, pk):
    try:
        ContactList.objects.get(pk=pk).delete()
        redirect_to = HttpResponseRedirect(reverse('marketing:contact_lists'))
    except ContactList.DoesNotExist:
        redirect_to = HttpResponseRedirect(reverse('marketing:contact_lists'))
    return HttpResponseRedirect(redirect_to)


@login_required(login_url='/login')
def contacts_list_new(request):
    if request.POST:
        form = ContactForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.created_by = request.user
            instance.save()
            for each in json.loads(request.POST['contact_list']):
                instance.contact_list.add(ContactList.objects.get(id=each))
            # return JsonResponse(form.data, status=status.HTTP_201_CREATED)
            return reverse('marketing:contact_list')
        else:
            data = {'error': True, 'errors': form.errors}
    else:
        if (request.user.is_superuser):
            queryset = ContactList.objects.all()
        else:
            queryset = ContactList.objects.filter(created_by=request.user)
        data = {"contact_list": queryset}
    return render(request, 'marketing/lists/cnew.html', data)


@login_required(login_url='/login')
def edit_contact(request):
    return render(request, 'marketing/lists/edit_contact.html')


@login_required(login_url='/login')
def contact_list_detail(request):
    return render(request, 'marketing/lists/detail.html')


@login_required(login_url='/login')
def email_template_list(request):
    return render(request, 'marketing/email_template/index.html')


@login_required(login_url='/login')
def email_template_new(request):
    return render(request, 'marketing/email_template/new.html')


@login_required(login_url='/login')
def email_template_edit(request):
    return render(request, 'marketing/email_template/edit.html')


@login_required(login_url='/login')
def email_template_detail(request):
    return render(request, 'marketing/email_template/details.html')


@login_required(login_url='/login')
def campaign_list(request):
    return render(request, 'marketing/campaign/index.html')


@login_required(login_url='/login')
def campaign_new(request):
    return render(request, 'marketing/campaign/new.html')


@login_required(login_url='/login')
def campaign_edit(request):
    return render(request, 'marketing/campaign/edit.html')


@login_required(login_url='/login')
def campaign_details(request):
    return render(request, 'marketing/campaign/details.html')
