from rest_framework import serializers

from businesses.models import EducationBusiness

from .models import Academy
from django.core.exceptions import (
    ValidationError as DjangoValidationError,
)

class AcademySerializer(serializers.ModelSerializer):
    organization = serializers.UUIDField(
        source="organization_id",
        read_only=True,
    )

    business = serializers.UUIDField(
        source="business_id",
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = Academy
        fields = (
            "id",
            "organization",
            "business",
            "name",
            "slug",
            "description",
            "logo_url",
            "primary_color",
            "secondary_color",
            "custom_domain",
            "is_public",
            "is_active",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "organization",
            "business",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        )

    def validate_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Academy name cannot be blank."
            )

        return value

    def validate_slug(self, value):
        return value.strip().lower()

    def validate(self, attrs):
        if self.instance is not None:
            if "organization" in self.initial_data:
                raise serializers.ValidationError(
                    {
                        "organization": (
                            "An academy's organization cannot be changed."
                        )
                    }
                )

            if "organization_id" in self.initial_data:
                raise serializers.ValidationError(
                    {
                        "organization_id": (
                            "An academy's organization cannot be changed."
                        )
                    }
                )

            if "business" in self.initial_data:
                raise serializers.ValidationError(
                    {
                        "business": (
                            "An academy's business cannot be changed."
                        )
                    }
                )

            if "business_id" in self.initial_data:
                raise serializers.ValidationError(
                    {
                        "business_id": (
                            "An academy's business cannot be changed."
                        )
                    }
                )

        return attrs

    @staticmethod
    def validate_business_for_organization(
        business_id,
        organization,
    ):
        if business_id in (None, ""):
            return None

        try:
            business = EducationBusiness.objects.get(
                id=business_id,
            )
        except (
            EducationBusiness.DoesNotExist,
            ValueError,
            TypeError,
            DjangoValidationError,
        ) as exc:
            raise serializers.ValidationError(
                {
                    "business_id": (
                        "A valid education business is required."
                    )
                }
            ) from exc

        if business.organization_id != organization.id:
            raise serializers.ValidationError(
                {
                    "business_id": (
                        "The selected business must belong to the "
                        "selected organization."
                    )
                }
            )

        if not business.is_active:
            raise serializers.ValidationError(
                {
                    "business_id": (
                        "The selected education business is inactive."
                    )
                }
            )

        return business