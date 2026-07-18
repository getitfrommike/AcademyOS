from rest_framework import serializers
from .models import EducationBusiness


class EducationBusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = EducationBusiness
        fields = "__all__"
        read_only_fields = ("id", "organization", "created_by", "updated_by", "created_at", "updated_at")
