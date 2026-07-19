from django.core.exceptions import (
    ValidationError as DjangoValidationError,
)
from rest_framework import serializers

from academies.models import Academy

from .models import Program


class ProgramSerializer(serializers.ModelSerializer):
    organization = serializers.UUIDField(
        source="organization_id",
        read_only=True,
    )

    academy = serializers.UUIDField(
        source="academy_id",
        read_only=True,
    )

    class Meta:
        model = Program
        fields = (
            "id",
            "organization",
            "academy",
            "name",
            "slug",
            "short_description",
            "description",
            "status",
            "is_featured",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "organization",
            "academy",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        )

    def validate_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Program name cannot be blank."
            )

        return value

    def validate_slug(self, value):
        return value.strip().lower()

    def validate_short_description(self, value):
        return value.strip()

    def validate(self, attrs):
        if self.instance is not None:
            if "organization" in self.initial_data:
                raise serializers.ValidationError(
                    {
                        "organization": (
                            "A program's organization cannot be changed."
                        )
                    }
                )

            if "organization_id" in self.initial_data:
                raise serializers.ValidationError(
                    {
                        "organization_id": (
                            "A program's organization cannot be changed."
                        )
                    }
                )

            if "academy" in self.initial_data:
                raise serializers.ValidationError(
                    {
                        "academy": (
                            "A program's academy cannot be changed."
                        )
                    }
                )

            if "academy_id" in self.initial_data:
                raise serializers.ValidationError(
                    {
                        "academy_id": (
                            "A program's academy cannot be changed."
                        )
                    }
                )

        return attrs

    @staticmethod
    def validate_academy_for_organization(
        academy_id,
        organization,
    ):
        if not academy_id:
            raise serializers.ValidationError(
                {
                    "academy_id": (
                        "An academy is required."
                    )
                }
            )

        try:
            academy = Academy.objects.get(
                id=academy_id,
            )
        except (
            Academy.DoesNotExist,
            ValueError,
            TypeError,
            DjangoValidationError,
        ) as exc:
            raise serializers.ValidationError(
                {
                    "academy_id": (
                        "A valid academy is required."
                    )
                }
            ) from exc

        if academy.organization_id != organization.id:
            raise serializers.ValidationError(
                {
                    "academy_id": (
                        "The selected academy must belong to the "
                        "selected organization."
                    )
                }
            )

        if not academy.is_active:
            raise serializers.ValidationError(
                {
                    "academy_id": (
                        "The selected academy is inactive."
                    )
                }
            )

        return academy