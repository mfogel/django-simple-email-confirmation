from rest_framework.routers import SimpleRouter

from . import views


router = SimpleRouter()

router.register(
    r'auth/emails',
    views.EmailViewSet,
    basename='user-emails',
)
