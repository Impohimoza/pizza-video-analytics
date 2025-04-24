from django.contrib.auth.views import LoginView
from django.shortcuts import redirect


class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('/pizzas')
        return super().dispatch(request, *args, **kwargs)