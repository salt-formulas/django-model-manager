from rest_framework.routers import DefaultRouter

from .views import OrganisationView, UserViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'organisations', OrganisationView)

urlpatterns = router.urls

