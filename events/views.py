from django.shortcuts import render, reverse
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from events.models import Event
from events.forms import EventForm
from datetime import datetime, date, timedelta


def events_list(request):
    return HttpResponse('<h1>events list</h1>')


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
                        end_time=data['end_time'],date_of_meeting=each
                    )
                    print(request.POST.get('contacts'))
                    import pdb; pdb.set_trace()
                    print(request.POST.get('assigned_to'))
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
