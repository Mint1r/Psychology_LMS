from functools import wraps
from django.http import Http404

def login_or_404(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise Http404()

        return view_func(request, *args, **kwargs)

    return wrapper