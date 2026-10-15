from django.core.exceptions import PermissionDenied
from functools import wraps

def role_required(*allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                from django.shortcuts import redirect
                return redirect('login')
            if request.user.is_superuser or request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            raise PermissionDenied("You do not have permission to access this clinic module.")
        return _wrapped_view
    return decorator

# Specific helper decorators
def admin_required(view_func):
    return role_required('ADMIN')(view_func)

def vet_required(view_func):
    return role_required('VET', 'ADMIN')(view_func)

def receptionist_required(view_func):
    return role_required('RECEPTIONIST', 'ADMIN')(view_func)
