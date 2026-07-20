from django.core.exceptions import (
    ValidationError as DjangoValidationError,
)
from rest_framework import serializers

from academies.models import Academy
from programs.models import Program

from .models import Course


class CourseSerializer(serializers.ModelSerializer):
    organization = serializers.UUIDField(
        source="organization_id",
        read_only=True,
    )

    academy = serializers.UUIDField(
        source="academy_id",
        read_only=True,
    )

    program = serializers.UUIDField(
        source="program_id",
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = Course
        fields = (
            "id",
            "organization",
            "academy",
            "program",
            "title",
            "slug",
            "short_description",
            "description",
            "estimated_duration_minutes",
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
            "program",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        )

    def validate_title(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Course title cannot be blank."
            )

        return value

    def validate_slug(self, value):
        return value.strip().lower()

    def validate_short_description(self, value):
        return value.strip()

    def validate(self, attrs):
        if self.instance is not None:
            immutable_fields = {
                "organization": (
                    "A course's organization cannot be changed."
                ),
                "organization_id": (
                    "A course's organization cannot be changed."
                ),
                "academy": (
                    "A course's academy cannot be changed."
                ),
                "academy_id": (
                    "A course's academy cannot be changed."
                ),
                "program": (
                    "A course's program cannot be changed."
                ),
                "program_id": (
                    "A course's program cannot be changed."
                ),
            }

            errors = {}

            for field, message in immutable_fields.items():
                if field in self.initial_data:
                    errors[field] = message

            if errors:
                raise serializers.ValidationError(errors)

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
            academy = Academy.objects.get(id=academy_id)
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
                        "The selected academy must belong to "
                        "the selected organization."
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

    @staticmethod
    def validate_program_for_course(
        program_id,
        organization,
        academy,
    ):
        if not program_id:
            return None

        try:
            program = Program.objects.get(id=program_id)
        except (
            Program.DoesNotExist,
            ValueError,
            TypeError,
            DjangoValidationError,
        ) as exc:
            raise serializers.ValidationError(
                {
                    "program_id": (
                        "A valid program is required."
                    )
                }
            ) from exc

        if program.organization_id != organization.id:
            raise serializers.ValidationError(
                {
                    "program_id": (
                        "The selected program must belong to "
                        "the selected organization."
                    )
                }
            )

        if program.academy_id != academy.id:
            raise serializers.ValidationError(
                {
                    "program_id": (
                        "The selected program must belong to "
                        "the selected academy."
                    )
                }
            )

        return program