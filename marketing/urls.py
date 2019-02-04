from django.urls import path
from .views import (
    index, contact_lists
)

app_name = 'marketing'

urlpatterns = [
    path('', index, name='index'),
    path('list/', contact_lists, name='contact_lists'),
]
