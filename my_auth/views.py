from rest_framework import status
from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    RetrieveUpdateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenViewBase

from users.models import CustomUser

from .permissions import IsAdmin
from .serializers import (
    ChangePasswordSerializer,
    CustomTokenObtainPairSerializer,
    LogoutSerializer,
    UpdateProfileSerializer,
    UserProfileSerializer,
    UserRegistrationSerializer,
    UserUpdateSerializer,
)


class UserApiListPagination(PageNumberPagination):
    """
    Настройки пагинации для списка пользователей
    """
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 10


class UserRegistrationView(CreateAPIView):
    """
    API для регистрации новых пользователей
    Доступно без авторизации
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        #Создаем токены
        refresh = RefreshToken.for_user(user)

        return Response({
            'success': True,
            'message': 'Пользователь успешно зарегистрирован',
            'user': UserProfileSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),  # Refresh token
                'access': str(refresh.access_token),  # Access token
            }
        }, status=status.HTTP_201_CREATED)

class UserListView(ListAPIView):
    """
    API для получения списка пользователей
    Только для авторизованных пользователей
    """
    queryset = CustomUser.objects.filter(is_active=True)
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = UserApiListPagination


class CustomTokenObtainPairView(TokenViewBase):
    """
    API для входа по email и получения JWT токенов
    """
    serializer_class = CustomTokenObtainPairSerializer

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            "detail": "Вы успешно вышли из системы"},
            status=status.HTTP_200_OK
        )


class UserUpdateView(RetrieveUpdateAPIView):
    """
    API для обновления данных текущего пользователя.
    """
    serializer_class = UserUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

class UserDeleteView(APIView):
    """
    API для мягкого удаления (soft delete) текущего пользователя.
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user = request.user
        user.soft_delete()  # метод модели
        return Response(
            {'detail': 'Пользователь удалён (soft delete)'},
            status=status.HTTP_200_OK
        )

class ChangePasswordView(APIView):
    """
    API для смены пароля текущего пользователя.
    """
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user

        if not user.check_password(serializer.validated_data['old_password']):
            return Response(
                {'old_password': 'Неверный текущий пароль'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response(
            {'detail': 'Пароль успешно изменён'},
            status=status.HTTP_200_OK
        )


class AdminDetailView(RetrieveUpdateDestroyAPIView):
    """
    Админ может просматривать, обновлять и удалять любого пользователя.
    При удалении пользователя вызывается soft_delete(),
    который уже блокирует все токены.
    """
    queryset = CustomUser.objects.filter(is_active=True)
    serializer_class = UpdateProfileSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_object(self):
        return super().get_object()

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        user.soft_delete()
        return Response(
            {'detail': 'Пользователь удалён'},
            status=status.HTTP_200_OK
        )
