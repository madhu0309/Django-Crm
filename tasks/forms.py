from django import forms
from tasks.models import Task
from accounts.models import Account
from contacts.models import Contact
from common.models import User
from django.db.models import Q


class TaskForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        request_user = kwargs.pop('request_user', None)
        super(TaskForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs = {"class": "form-control"}

        if request_user:
            self.fields["account"].queryset = Account.objects.filter(
                created_by=request_user, is_active=True)

            self.fields["contacts"].queryset = Contact.objects.filter(
                Q(assigned_to__in=[request_user]) | Q(created_by=request_user))

        self.fields['title'].required = True
        self.fields['status'].required = True
        self.fields['priority'].required = True
        self.fields['assigned_to'].required = False
        self.fields['account'].required = False
        self.fields['contacts'].required = False
        self.fields['due_date'].required = False

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if Task.objects.filter(title=title).exists():
            raise forms.ValidationError('Task with that title already exists')
        return title

    class Meta:
        model = Task
        fields = (
            'title', 'status', 'priority', 'assigned_to', 'account', 'contacts',
            'due_date'
        )
