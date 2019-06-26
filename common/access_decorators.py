from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied
from functools import wraps


def sales_access(function):
    """ this function is a decorator used to authorize if a user has sales access """
    def wrap(request, *args, **kwargs):
        if request.user.user_role == 'ADMIN' or request.user.is_superuser or request.user.has_sales_access:
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied
    return wrap


def marketing_access(function):
    """ this function is a decorator used to authorize if a user has marketing access """
    def wrap(request, *args, **kwargs):
        if request.user.user_role == 'ADMIN' or request.user.is_superuser or request.user.has_marketing_access:
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied
    return wrap
