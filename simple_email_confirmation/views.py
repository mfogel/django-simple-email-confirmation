from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.utils.translation import gettext_lazy as _


class LoginView(auth_views.LoginView):
    redirect_authenticated_user = True

    def post(self, request, *args, **kwargs):
        response = super(LoginView).post(request, *args, **kwargs)
        if request.user.is_authenticated():
            if request.user.is_confirmed == False:
                messages.error(request, _('Email not verified'))
                auth_views.LogoutView.as_view()(request)
                response = self.get(request, *args, **kwargs)

        return response
