from django.urls import path
from invoices.views import *

app_name = 'invoices'


urlpatterns = [
    path('list/', invoices_list, name='invoices_list'),

]
