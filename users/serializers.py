from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from .models import AccessRule, Role


class AccessRuleSerializer(serializers.ModelSerializer):
    content_type = serializers.SlugRelatedField(
        slug_field='model',
        queryset=ContentType.objects.all()
    )

    role = serializers.SlugRelatedField(
        slug_field='name', queryset=Role.objects.all()
    )

    class Meta:
        model = AccessRule
        fields = (
            'id',
            'role',
            'content_type',
            'read_permission',
            'create_permission',
            'update_permission',
            'delete_permission',
            'read_all_permission',
            'update_all_permission',
            'delete_all_permission',
        )

    def validate(self, attrs):
        role = attrs.get('role')
        content_type = attrs.get('content_type')
        instance = getattr(self, 'instance', None)

        exists_qs = AccessRule.objects.filter(role=role, content_type=content_type)
        if instance is not None:
            exists_qs = exists_qs.exclude(pk=instance.pk)
        if exists_qs.exists():
            raise serializers.ValidationError('Правило для этой роли и типа'
                                              ' уже существует')
        return attrs

