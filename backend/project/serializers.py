from rest_framework import serializers
from .models import Project


class ProjectSerializers(serializers.ModelSerializer):
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Project
        fields = ('id', 'name', 'description', 'created_at', 'updated_at')
