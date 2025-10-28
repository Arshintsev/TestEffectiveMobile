from django.contrib.contenttypes.models import ContentType
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from my_auth.permissions import IsAdmin

from .models import AccessRule
from .serializers import AccessRuleSerializer


class AccessRuleViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления правилами доступа (AccessRule).
    Доступ только для авторизованных администраторов.
    """
    queryset = AccessRule.objects.select_related('role').all()
    serializer_class = AccessRuleSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    @action(detail=False, methods=['get'], url_path='by-model/(?P<model_name>[^/.]+)')
    def by_model(self, request, model_name=None):
        """
        Получение списка правил доступа для конкретной модели.
        """
        try:
            content_type = ContentType.objects.get(model=model_name.lower())
        except ContentType.DoesNotExist:
            return Response({"detail": "Модель не найдена"}, status=404)

        rules = self.queryset.filter(content_type=content_type)
        serializer = self.get_serializer(rules, many=True)
        return Response(serializer.data)
