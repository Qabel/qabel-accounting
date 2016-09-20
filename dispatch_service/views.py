from django.shortcuts import get_object_or_404, redirect

from .models import Redirect


def dispatch(request, redirect_from):
    redirect_obj = get_object_or_404(Redirect, redirect_from=redirect_from)
    return redirect(redirect_obj.get_destination(request))
