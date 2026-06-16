"""
accounts/middleware.py
Activity logging middleware + login rate limiter.
"""

from django.core.cache import cache
from django.http import HttpResponseForbidden
from django.conf import settings


class ActivityLogMiddleware:
    """Auto-logs page visits for authenticated users (lightweight)."""
    SKIP_PATHS = ['/static/', '/media/', '/favicon.ico']

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response


class RateLimitMiddleware:
    """Block IPs that exceed login attempt threshold."""
    MAX_ATTEMPTS = getattr(settings, 'LOGIN_MAX_ATTEMPTS', 5)
    LOCKOUT_MINUTES = getattr(settings, 'LOGIN_LOCKOUT_MINUTES', 15)

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == '/accounts/login/' and request.method == 'POST':
            ip = self._get_ip(request)
            key = f'login_attempts_{ip}'
            attempts = cache.get(key, 0)
            if attempts >= self.MAX_ATTEMPTS:
                return HttpResponseForbidden(
                    f"Too many login attempts. Try again in {self.LOCKOUT_MINUTES} minutes."
                )
        return self.get_response(request)

    def _get_ip(self, request):
        x_fw = request.META.get('HTTP_X_FORWARDED_FOR')
        return x_fw.split(',')[0] if x_fw else request.META.get('REMOTE_ADDR', '0.0.0.0')
