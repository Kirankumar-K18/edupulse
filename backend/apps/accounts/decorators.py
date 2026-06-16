"""
accounts/decorators.py
Role-based access decorators for views.
"""

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            if request.user.role not in roles:
                messages.error(request, "You do not have permission to access this page.")
                return redirect(request.user.get_dashboard_url())
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def admin_required(view_func):
    return role_required('admin')(view_func)


def hod_required(view_func):
    return role_required('hod')(view_func)


def lecturer_required(view_func):
    return role_required('lecturer')(view_func)


def student_required(view_func):
    return role_required('student')(view_func)


def admin_or_hod_required(view_func):
    return role_required('admin', 'hod')(view_func)


def not_student_required(view_func):
    return role_required('admin', 'hod', 'lecturer')(view_func)
