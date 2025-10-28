from rest_framework.permissions import BasePermission

from users.models import Role


class IsAdmin(BasePermission):
    """
    Разрешает доступ только администратору
    """

    def has_permission(self, request, view):
        return bool(
            request.user.is_authenticated and request.user.is_active and
            request.user.role.name == Role.ADMIN
        )

    def has_object_permission(self, request, view, obj):
        # На уровне объекта тоже разрешаем только админам
        return bool(
            request.user.is_authenticated and request.user.is_active and
            request.user.role.name == Role.ADMIN
        )
