from typing import Any

from rest_framework import serializers

from .models import EducationBusiness


class EducationBusinessSerializer(serializers.ModelSerializer):
    """
    Serialize tenant-owned education businesses.

    The organization is assigned by the secured viewset and cannot be changed
    through serializer input.
    """

    class Meta:
        model = EducationBusiness
        fields = (
            "id",
            "organization",
            "name",
            "slug",
            "business_type",
            "mission",
            "target_audience",
            "transformation_promise",
            "delivery_model",
            "revenue_model",
            "blueprint",
            "is_active",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "organization",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        )

    def validate_name(self, value: str) -> str:
        """
        Normalize and validate the business name.
        """
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Business name cannot be empty."
            )

        return value

    def validate_slug(self, value: str) -> str:
        """
        Normalize slugs so casing cannot create unexpected duplicates.
        """
        value = value.strip().lower()

        if not value:
            raise serializers.ValidationError(
                "Business slug cannot be empty."
            )

        return value

    def validate_delivery_model(
        self,
        value: dict[str, Any],
    ) -> dict[str, Any]:
        return self._validate_json_object(
            value,
            field_name="delivery_model",
        )

    def validate_revenue_model(
        self,
        value: dict[str, Any],
    ) -> dict[str, Any]:
        return self._validate_json_object(
            value,
            field_name="revenue_model",
        )

    def validate_blueprint(
        self,
        value: dict[str, Any],
    ) -> dict[str, Any]:
        return self._validate_json_object(
            value,
            field_name="blueprint",
        )

    def validate(
        self,
        attrs: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Explicitly reject attempts to move a business between organizations.

        Because organization is read-only, DRF would normally ignore a
        submitted organization value. Checking initial_data makes the API
        reject the attempt instead of silently accepting it.
        """
        if self.instance is None:
            return attrs

        submitted_organization = self.initial_data.get("organization")

        if submitted_organization is not None:
            submitted_organization_id = str(submitted_organization)
            current_organization_id = str(
                self.instance.organization_id
            )

            if submitted_organization_id != current_organization_id:
                raise serializers.ValidationError(
                    {
                        "organization": (
                            "An education business cannot be moved to "
                            "another organization."
                        )
                    }
                )

        return attrs

    @staticmethod
    def _validate_json_object(
        value: Any,
        field_name: str,
    ) -> dict[str, Any]:
        """
        Require structured JSON fields to contain objects, not lists,
        strings, numbers, or other JSON values.
        """
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                f"{field_name} must be a JSON object."
            )

        return value