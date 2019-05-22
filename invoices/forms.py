from django import forms
from invoices.models import Invoice
from common.models import User


class InvoiceForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        request_user = kwargs.pop('request_user', None)
        assigned_users = kwargs.pop('assigned_to', [])
        super(InvoiceForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs = {"class": "form-control"}
        # self.fields['first_name'].required = False
        # self.fields['last_name'].required = False
        # self.fields['title'].required = True

        if request_user.role == 'ADMIN' or request_user.is_superuser:
            self.fields['assigned_to'].queryset = User.objects.all()
        elif request_user.google.all():
            self.fields['assigned_to'].queryset = User.objects.none()
        elif request_user.role == 'USER':
            self.fields['assigned_to'].queryset = User.objects.filter(role='ADMIN')
        else:
            pass

        self.fields['assigned_to'].required = False

        for key, value in self.fields.items():
            if key == 'phone':
                value.widget.attrs['placeholder'] =\
                    'Enter phone number with country code'
            else:
                value.widget.attrs['placeholder'] = value.label

        # self.fields['first_name'].widget.attrs.update({
        #     'placeholder': 'First Name'})
        # self.fields['last_name'].widget.attrs.update({
        #     'placeholder': 'Last Name'})
        # self.fields['account_name'].widget.attrs.update({
        #     'placeholder': 'Account Name'})
        self.fields['phone'].widget.attrs.update({
            'placeholder': '+91-123-456-7890'})
        # self.fields['description'].widget.attrs.update({
        #     'rows': '6'})

    class Meta:
        model = Invoice
        fields = ('invoice_title', 'invoice_number',
                  'from_address', 'to_address', 'name',
                  'email', 'phone', 'status', 'assigned_to',
                  'quantity', 'rate', 'total_amount',
                  'currency',
                  )