from rest_framework import serializers
from .models import Academy


class AcademySerializer(serializers.ModelSerializer):
    class Meta:
        model = Academy
        fields = "__all__"
        read_only_fields = ("id", "organization", "created_at", "updated_at")
