from rest_framework.response import Response
from django.utils.translation import gettext_lazy as _
from rest_framework import status

def allowed_users(allowed_roles=[]):
    """
    Decorator for views that limits access for django and non django roles.
    """
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if request.user:
                is_admin = request.user.is_superuser
                is_staff = request.user.is_staff
                is_administrator = request.user.role == 'Administrator'
                is_supervisor = request.user.role == 'Supervisor'
            if 'admin' in allowed_roles and is_admin:
                return view_func(request, *args, **kwargs)
            elif 'staff' in allowed_roles and is_staff:
                return view_func(request, *args, **kwargs)
            elif 'administrator' in allowed_roles and is_administrator:
                return view_func(request, *args, **kwargs)
            elif 'supervisor' in allowed_roles and (is_supervisor or is_administrator):
                return view_func(request, *args, **kwargs)
            else:
                return Response({'error': _('You are not authorized to access this resource.')}, status=status.HTTP_401_UNAUTHORIZED)
        return _wrapped_view
    return decorator
