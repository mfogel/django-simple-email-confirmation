from django.urls import path, include

from simple_email_confirmation.contrib.rest_framework.urls import router


urlpatterns = [
    path('api/', include(router.urls)),
]
