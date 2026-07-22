from rest_framework import serializers

from .models import KnowledgeSource


class KnowledgeUploadSerializer(serializers.Serializer):
    """
    Accepts a single uploaded knowledge file.

    Validation and secure storage are handled through
    dedicated validators and services.
    """

    file = serializers.FileField(required=True)


class KnowledgeSourceSerializer(serializers.ModelSerializer):
    """
    Safe representation of a knowledge source.

    Internal storage details are intentionally excluded.
    """

    class Meta:
        model = KnowledgeSource

        fields = (
            "id",
            "original_filename",
            "file_size_bytes",
            "status",
            "created_at",
            "updated_at",
        )

        read_only_fields = fields