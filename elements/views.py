from rest_framework import status, viewsets
from rest_framework.response import Response

from users.models import Element

from .permissions import RoleAccessPermission
from .serializers import ElementSerializer


class ElementViewSet(viewsets.ModelViewSet):
    queryset = Element.objects.all()
    serializer_class = ElementSerializer
    permission_classes = [RoleAccessPermission]

    def get_queryset(self):
        return RoleAccessPermission.filter_queryset(self.request.user,
                                                    Element.objects.all())

    def perform_create(self, serializer):
        """
        Автоматически устанавливаем owner текущим пользователем.
        """
        serializer.save(owner=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"detail": f"Элемент '{instance.name}' успешно удалён."},
            status=status.HTTP_200_OK
        )
