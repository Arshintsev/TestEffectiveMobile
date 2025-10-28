# users/serializers.py
from rest_framework import serializers

from users.models import Element


class ElementSerializer(serializers.ModelSerializer):
    owner_email = serializers.CharField(source='owner.email', read_only=True)

    class Meta:
        model = Element
        fields = ['id', 'name', 'description', 'owner', 'owner_email']
        read_only_fields = ['owner_email']
