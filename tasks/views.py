from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, reverse

from accounts.models import Account
from common.models import User
from contacts.models import Contact
from tasks.forms import TaskForm
from tasks.models import Task

# Create your views here.


@login_required
def tasks_list(request):
    return render(request, 'tasks_list.html', {})


@login_required
def task_create(request):
    if request.method == 'GET':
        form = TaskForm(request_user=request.user)
        users = User.objects.filter(is_active=True).order_by('email')
        return render(request, 'task_create.html', {'users': users, 'form': form})

    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task_id = form.save()
            return JsonResponse({'error': False, 'success_url': reverse('tasks:tasks_list')})
        else:
            return JsonResponse({'error': True, 'errors': form.errors})
