from django.contrib.contenttypes.models import ContentType
from rest_framework import permissions

from users.models import AccessRule


class RoleAccessPermission(permissions.BasePermission):
    """
    Проверяет права пользователя на объект или тип объекта через AccessRule.
    """

    def has_permission(self, request, view):
        """
        Проверка прав на уровне View для SAFE_METHODS (GET, HEAD, OPTIONS).
        Для создания/редактирования/удаления проверка делается на уровне объекта.
        """
        user = request.user
        if not user.is_authenticated or not user.is_active:
            return False

        if request.method not in permissions.SAFE_METHODS:
            # Все POST/PUT/PATCH/DELETE проверяем на уровне объекта
            return True

        # Для GET проверяем read_permission
        model_class = (getattr(view, 'queryset', None)
                       or getattr(view, 'serializer_class', None))
        if hasattr(model_class, 'model'):
            model_class = model_class.model

        ct = ContentType.objects.get_for_model(model_class)
        try:
            rule = AccessRule.objects.get(role=user.role, content_type=ct)
        except AccessRule.DoesNotExist:
            return False

        return rule.read_permission or rule.read_all_permission

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user.is_authenticated or not user.is_active:
            return False

        ct = ContentType.objects.get_for_model(obj.__class__)
        try:
            rule = AccessRule.objects.get(role=user.role, content_type=ct)
        except AccessRule.DoesNotExist:
            return False

        is_owner = hasattr(obj, 'owner') and obj.owner == user

        if request.method in permissions.SAFE_METHODS:
            return (rule.read_all_permission or
                    (rule.read_permission if is_owner else False))
        elif request.method == 'POST':
            return rule.create_permission
        elif request.method in ['PUT', 'PATCH']:
            return (rule.update_all_permission or
                    (rule.update_permission if is_owner else False))
        elif request.method == 'DELETE':
            return (rule.delete_all_permission or
                    (rule.delete_permission if is_owner else False))

        return False

    @staticmethod
    def filter_queryset(user, queryset):
        """  Фильтрует queryset по правам чтения пользователя.
    - Если user неактивен или неаутентифицирован → пустой queryset.
    - Если AccessRule.read_all_permission=True → возвращает весь queryset.
    - Иначе → возвращает только объекты, где owner=user."""

        if not user.is_authenticated or not user.is_active:
            return queryset.none()

        ct = ContentType.objects.get_for_model(queryset.model)
        try:
            rule = AccessRule.objects.get(role=user.role, content_type=ct)
        except AccessRule.DoesNotExist:
            return queryset.none()

        if rule.read_all_permission:
            return queryset
        else:
            return queryset.filter(owner=user)
