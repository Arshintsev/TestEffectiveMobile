from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from .views import (
                    AdminDetailView,
                    ChangePasswordView,
                    CustomTokenObtainPairView,
                    LogoutView,
                    UserDeleteView,
                    UserListView,
                    UserRegistrationView,
                    UserUpdateView,
)

app_name = 'my_auth'

urlpatterns = [
    path('api/register', UserRegistrationView.as_view(), name='user-register'),
    path('api/users', UserListView.as_view(), name='user-list'),
    path('api/login/', CustomTokenObtainPairView.as_view(), name='user-login'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('api/logout', LogoutView.as_view(), name='user-logout'),
    path('api/update', UserUpdateView.as_view(), name='user-update'),
    path('api/profile/change-password',
         ChangePasswordView.as_view(),
         name='change-password'
    ),
    path('api/profile/delete', UserDeleteView.as_view(), name='user-delete'),
    path('api/users/<int:pk>', AdminDetailView.as_view(), name='user-detail')
]
