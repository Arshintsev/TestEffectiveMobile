from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AccessRuleViewSet

router = DefaultRouter()
router.register(r'access-rules', AccessRuleViewSet, basename='access-rule')


urlpatterns = [
    path('api/', include(router.urls)),
]

