from django import forms
from contacts.models import Contact
from common.models import User, Attachments, Comment
from django.db.models import Q
from events.models import Event


class EventForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        # assigned_users = kwargs.pop('assigned_to', [])
        request_user = kwargs.pop('request_user', None)
        self.obj_instance = kwargs.get('instance', None)
        super(EventForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs = {"class": "form-control"}

        if request_user.role == 'ADMIN' or request_user.is_superuser:
            self.fields['assigned_to'].queryset = User.objects.all()
            self.fields["contacts"].queryset = Contact.objects.filter()
        elif request_user.google.all():
            self.fields['assigned_to'].queryset = User.objects.none()
            self.fields["contacts"].queryset = Contact.objects.filter(
                Q(assigned_to__in=[request_user]) | Q(created_by=request_user))
        elif request_user.role == 'USER':
            self.fields['assigned_to'].queryset = User.objects.filter(
                role='ADMIN')
            self.fields["contacts"].queryset = Contact.objects.filter(
                Q(assigned_to__in=[request_user]) | Q(created_by=request_user))
        else:
            pass

        self.fields['assigned_to'].required = False
        self.fields['name'].required = True
        self.fields['event_type'].required = True
        self.fields['contacts'].required = True
        self.fields['start_date'].required = True
        self.fields['start_time'].required = False
        self.fields['end_date'].required = True
        self.fields['end_time'].required = False
        self.fields['description'].required = False

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if Event.objects.filter(name=name).exclude(id=self.instance.id).exists():
            raise forms.ValidationError(
                'Event with this name already exists.')

        return name

    def clean_end_date(self):
        end_date = self.cleaned_data.get('end_date')
        if self.cleaned_data.get('start_date') > end_date:
            raise forms.ValidationError(
                'End Date cannot be less than start date')
        return end_date

    class Meta:
        model = Event
        fields = (
            'name', 'event_type', 'contacts', 'assigned_to', 'start_date', 'start_time',
            'end_date', 'end_time', 'description',
        )


# class TaskCommentForm(forms.ModelForm):
#     comment = forms.CharField(max_length=64, required=True)

#     class Meta:
#         model = Comment
#         fields = ('comment', 'task', 'commented_by')


# class TaskAttachmentForm(forms.ModelForm):
#     attachment = forms.FileField(max_length=1001, required=True)

#     class Meta:
#         model = Attachments
#         fields = ('attachment', 'task')
