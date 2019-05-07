from django.urls import path
from tasks.views import (tasks_list, task_create)

app_name = 'tasks'


urlpatterns = [
    path('list/', tasks_list, name='tasks_list'),
    path('create/', task_create, name='task_create'),

]
