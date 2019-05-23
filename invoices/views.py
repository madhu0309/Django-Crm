from django.shortcuts import render
from django.http.response import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
def invoices_list(request):
    return HttpResponse('invoices')