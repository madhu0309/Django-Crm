from datetime import date, datetime, timedelta

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.views.generic import (CreateView, DeleteView, DetailView, FormView,
                                  TemplateView, UpdateView, View)

from common.models import User, Attachments, Comment
from events.forms import EventForm, EventCommentForm, EventAttachmentForm
from events.models import Event


def events_list(request):

    if request.user.role == 'ADMIN' or request.user.is_superuser:
        users = User.objects.all()
    elif request.user.google.all():
        users = User.objects.none()
    elif request.user.role == 'USER':
        users = User.objects.filter(role='ADMIN')

    if request.method == 'GET':
        context = {}
        if request.user.role == 'ADMIN' or request.user.is_superuser:
            events = Event.objects.all().distinct()
        else:
            events = Event.objects.filter(
                Q(created_by=request.user) | Q(assigned_to=request.user)).distinct()
        context['events'] = events.order_by('id')
        # context['status'] = status
        context['users'] = users
        return render(request, 'events_list.html', context)

    if request.method == 'POST':
        context = {}
        # context['status'] = status
        context['users'] = users
        events = Event.objects.filter()
        if request.user.role == 'ADMIN' or request.user.is_superuser:
            events = events
        else:
            events = events.filter(
                Q(created_by=request.user) | Q(assigned_to=request.user)).distinct()

        if request.POST.get('invoice_title_number', None):
            events = events.filter(
                Q(invoice_title__icontains=request.POST.get('invoice_title_number')) |
                Q(invoice_number__icontains=request.POST.get('invoice_title_number')))

        if request.POST.get('created_by', None):
            events = events.filter(
                created_by__id=request.POST.get('created_by'))

        if request.POST.getlist('assigned_to', None):
            events = events.filter(
                assigned_to__in=request.POST.getlist('assigned_to'))
            context['assigned_to'] = request.POST.getlist('assigned_to')

        if request.POST.get('status', None):
            events = events.filter(status=request.POST.get('status'))

        if request.POST.get('total_amount', None):
            events = events.filter(
                total_amount=request.POST.get('total_amount'))

        context['events'] = events.distinct().order_by('id')
        return render(request, 'events_list.html', context)


@login_required
def event_create(request):
    if request.method == 'GET':
        context = {}
        context["form"] = EventForm(request_user=request.user)
        return render(request, 'event_create.html', context)

    if request.method == 'POST':
        form = EventForm(request.POST, request_user=request.user)
        if form.is_valid():
            print(request.POST)
            start_date = form.cleaned_data.get('start_date')
            end_date = form.cleaned_data.get('end_date')
            # recurring_days
            recurring_days = request.POST.getlist('days')
            if form.cleaned_data.get('event_type') == 'Non-Recurring':
                event = form.save(commit=False)
                event.date_of_meeting = start_date
                event.created_by = request.user
                event.save()
                form.save_m2m()

            if form.cleaned_data.get('event_type') == 'Recurring':
                delta = end_date - start_date
                all_dates = []
                required_dates = []

                for day in range(delta.days + 1):
                    each_date = (start_date + timedelta(days=day))
                    if each_date.strftime("%A") in recurring_days:
                        required_dates.append(each_date)

                for each in required_dates:
                    each = datetime.strptime(str(each), '%Y-%m-%d').date()
                    data = form.cleaned_data

                    event = Event.objects.create(
                        created_by=request.user, start_date=start_date, end_date=end_date,
                        name=data['name'], event_type=data['event_type'],
                        description=data['description'], start_time=data['start_time'],
                        end_time=data['end_time'], date_of_meeting=each
                    )
                    event.contacts.add(*request.POST.getlist('contacts'))
                    event.assigned_to.add(*request.POST.getlist('assigned_to'))

        #     recipients = []
        #     if selected_users:
        #         for user in selected_users:
        #             recipients.append(user.user.email)

        #     if recipients:
        #         message = "Meeting Successfully Created!"
        #         subject = 'A new Meeting Session Created'
        #         from_email = settings.DEFAULT_FROM_EMAIL
        #         text_content = 'Meeting Session Created'
        #         from_email = settings.DEFAULT_FROM_EMAIL
        #         context = {
        #             'user': profile.user,
        #             'request': request,
        #             'title': new_title if new_title else '',
        #             'from_date': start_date if start_date else '',
        #             'to_date': end_date if end_date else '',
        #             'description': description if description else '',
        #             'start_time': start_time,
        #             'meeting_option': meeting_option,
        #             'action': 'Created',
        #         }

        #         if meeting_option == 'day':
        #             text_content = 'Meeting Session Created - %s' % (meeting_instance.title)
        #             url = request.scheme + '://' + request.company.subdomain + settings.FRONTEND_URL
        #             redirect_url = url + '/hcm/meetings/' + str(meeting_instance.id)
        #             accept_invitation_url = redirect_url + '/accept'
        #             reject_invitation_url = redirect_url + '/reject'
        #             meeting_url = redirect_url
        #             # context['meeting_url'] = meeting_url
        #             context['accept_invitation_url'] =  accept_invitation_url
        #             context['reject_invitation_url'] = reject_invitation_url
        #             # context['url'] = url
        #         else:
        #             context['days'] = days

        #         template_name = 'pm_meeting.html'

        #         html_content = get_rendered_html(template_name, context)
        #         mail_kwargs = {
        #             "subject": subject, "text_content": text_content,
        #             "html_content": html_content, "from_email": from_email,
        #             "recipients": recipients
        #         }
        #         send_email.delay(**mail_kwargs)
        #     data = {"error": False, "message": message}
        #     return JsonResponse(data, status=status.HTTP_201_CREATED)
        # else:
        #     data = {"error": True, "errors": form.errors}
        #     return JsonResponse(data, status=status.HTTP_400_BAD_REQUEST)
            return JsonResponse({'error': False, 'success_url': reverse('events:events_list')})
        else:
            return JsonResponse({'error': True, 'errors': form.errors, })


@login_required
def event_detail_view(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    if not (request.user.role == 'ADMIN' or request.user.is_superuser or event.created_by == request.user or request.user in event.assigned_to.all()):
        raise PermissionDenied

    if request.method == 'GET':
        context = {}
        context['event'] = event
        # context['attachments'] = invoice.invoice_attachment.all()
        # context['comments'] = invoice.invoice_comments.all()
        if request.user.is_superuser or request.user.role == 'ADMIN':
            context['users_mention'] = list(
                User.objects.all().values('username'))
        elif request.user != event.created_by:
            context['users_mention'] = [
                {'username': event.created_by.username}]
        else:
            context['users_mention'] = list(
                event.assigned_to.all().values('username'))
        return render(request, 'event_detail.html', context)


@login_required
def event_update(request, event_id):
    event_obj = get_object_or_404(Event, pk=event_id)
    if not (request.user.role == 'ADMIN' or request.user.is_superuser or event.created_by == request.user or request.user in event.assigned_to.all()):
        raise PermissionDenied

    if request.method == 'GET':
        context = {}
        context["event_obj"] = event_obj
        context["form"] = EventForm(
            instance=event_obj, request_user=request.user)
        selected_recurring_days = Event.objects.filter(
            name=event_obj.name).values_list('date_of_meeting', flat=True)
        # import pdb; pdb.set_trace()
        selected_recurring_days = [day.strftime(
            '%A') for day in selected_recurring_days]
        context['selected_recurring_days'] = selected_recurring_days
        return render(request, 'event_create.html', context)

    if request.method == 'POST':
        form = EventForm(request.POST, instance=event_obj,
                         request_user=request.user)
        if form.is_valid():
            print(request.POST)
            start_date = form.cleaned_data.get('start_date')
            end_date = form.cleaned_data.get('end_date')
            # recurring_days
            # recurring_days = request.POST.getlist('days')

            if form.cleaned_data.get('event_type') == 'Non-Recurring':
                event = form.save(commit=False)
                event.date_of_meeting = start_date
                # event.created_by = request.user
                event.save()
                form.save_m2m()

            if form.cleaned_data.get('event_type') == 'Recurring':
                print(request.POST.get('assigned_to'))
                event = form.save(commit=False)
                event.save()
                form.save_m2m()
                # event.contacts.add(*request.POST.getlist('contacts'))
                # event.assigned_to.add(*request.POST.getlist('assigned_to'))

            # send mail to assigned users and maybe even to contacts
            return JsonResponse({'error': False, 'success_url': reverse('events:events_list')})
        else:
            return JsonResponse({'error': True, 'errors': form.errors, })


@login_required
def event_delete(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    if not (request.user.role == 'ADMIN' or request.user.is_superuser or event.created_by == request.user):
        raise PermissionDenied

    if request.method == 'GET':
        event.delete()
        return redirect('events:events_list')


class AddCommentView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = EventCommentForm
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        self.object = None
        self.event = get_object_or_404(
            Event, id=request.POST.get('event_id'))
        if (
            request.user == self.event.created_by or request.user.is_superuser or
            request.user.role == 'ADMIN'
        ):
            form = self.get_form()
            if form.is_valid():
                return self.form_valid(form)
            return self.form_invalid(form)

        data = {
            'error': "You don't have permission to comment for this account."}
        return JsonResponse(data)

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.commented_by = self.request.user
        comment.event = self.event
        comment.save()
        comment_id = comment.id
        current_site = get_current_site(self.request)
        # send_email_user_mentions.delay(comment_id, 'invoices', domain=current_site.domain,
                                    #    protocol=self.request.scheme)
        return JsonResponse({
            "comment_id": comment.id, "comment": comment.comment,
            "commented_on": comment.commented_on,
            "commented_by": comment.commented_by.email
        })

    def form_invalid(self, form):
        return JsonResponse({"error": form['comment'].errors})


class UpdateCommentView(LoginRequiredMixin, View):
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        self.comment_obj = get_object_or_404(
            Comment, id=request.POST.get("commentid"))
        if request.user == self.comment_obj.commented_by:
            form = EventCommentForm(request.POST, instance=self.comment_obj)
            if form.is_valid():
                return self.form_valid(form)

            return self.form_invalid(form)

        data = {'error': "You don't have permission to edit this comment."}
        return JsonResponse(data)

    def form_valid(self, form):
        self.comment_obj.comment = form.cleaned_data.get("comment")
        self.comment_obj.save(update_fields=["comment"])
        comment_id = self.comment_obj.id
        current_site = get_current_site(self.request)
        # send_email_user_mentions.delay(comment_id, 'invoices', domain=current_site.domain,
                                    #    protocol=self.request.scheme)
        return JsonResponse({
            "comment_id": self.comment_obj.id,
            "comment": self.comment_obj.comment,
        })

    def form_invalid(self, form):
        return JsonResponse({"error": form['comment'].errors})


class DeleteCommentView(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        self.object = get_object_or_404(
            Comment, id=request.POST.get("comment_id"))
        if request.user == self.object.commented_by:
            self.object.delete()
            data = {"cid": request.POST.get("comment_id")}
            return JsonResponse(data)

        data = {'error': "You don't have permission to delete this comment."}
        return JsonResponse(data)


class AddAttachmentView(LoginRequiredMixin, CreateView):
    model = Attachments
    form_class = EventAttachmentForm
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        self.object = None
        self.event = get_object_or_404(
            Event, id=request.POST.get('event_id'))
        if (
            request.user == self.event.created_by or
            request.user.is_superuser or
            request.user.role == 'ADMIN'
        ):
            form = self.get_form()
            if form.is_valid():
                return self.form_valid(form)

            return self.form_invalid(form)

        data = {
            'error': "You don't have permission to add attachment \
            for this account."}
        return JsonResponse(data)

    def form_valid(self, form):
        attachment = form.save(commit=False)
        attachment.created_by = self.request.user
        attachment.file_name = attachment.attachment.name
        attachment.event = self.event
        attachment.save()
        return JsonResponse({
            "attachment_id": attachment.id,
            "attachment": attachment.file_name,
            "attachment_url": attachment.attachment.url,
            "download_url": reverse('common:download_attachment',
                                    kwargs={'pk': attachment.id}),
            "attachment_display": attachment.get_file_type_display(),
            "created_on": attachment.created_on,
            "created_by": attachment.created_by.email,
            "file_type": attachment.file_type()
        })

    def form_invalid(self, form):
        return JsonResponse({"error": form['attachment'].errors})


class DeleteAttachmentsView(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        self.object = get_object_or_404(
            Attachments, id=request.POST.get("attachment_id"))
        if (
            request.user == self.object.created_by or
            request.user.is_superuser or
            request.user.role == 'ADMIN'
        ):
            self.object.delete()
            data = {"acd": request.POST.get("attachment_id")}
            return JsonResponse(data)

        data = {
            'error': "You don't have permission to delete this attachment."}
        return JsonResponse(data)
