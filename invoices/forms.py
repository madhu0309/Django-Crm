from django import forms
from invoices.models import Invoice
from common.models import User


class InvoiceForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        request_user = kwargs.pop('request_user', None)
        assigned_users = kwargs.pop('assigned_to', [])
        super(InvoiceForm, self).__init__(*args, **kwargs)

        if request_user.role == 'ADMIN' or request_user.is_superuser:
            self.fields['assigned_to'].queryset = User.objects.all()
        elif request_user.google.all():
            self.fields['assigned_to'].queryset = User.objects.none()
        elif request_user.role == 'USER':
            self.fields['assigned_to'].queryset = User.objects.filter(role='ADMIN')
        else:
            pass

        self.fields['phone'].widget.attrs.update({
            'placeholder': '+91-123-456-7890'})

    class Meta:
        model = Invoice
        fields = ('invoice_title', 'invoice_number',
                  'from_address', 'to_address', 'name',
                  'email', 'phone', 'status', 'assigned_to',
                  'quantity', 'rate', 'total_amount',
                  'currency',
                  )
