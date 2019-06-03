from django.urls import path
from events.views import *

app_name = 'events'


urlpatterns = [
    path('list/', events_list, name='events_list'),
    path('create/', event_create, name='event_create'),
]
