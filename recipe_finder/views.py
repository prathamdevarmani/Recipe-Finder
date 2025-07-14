from django.shortcuts import redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from recipes.views import register

@login_required
def custom_logout(request):
    logout(request)  # This will clear the session
    request.session.flush()  # Additional cleanup of session data
    return redirect('recipe_list')
