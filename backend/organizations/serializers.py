from typing import Any

from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Organization, OrganizationMembership

User = get_user_model()


class OrganizationSerializer(serializers.ModelSerializer):
    """
    Serialize organizations while exposing the requesting user's active role.
    """

    current_user_role = serializers.SerializerMethodField()

    class Meta:
        model = Organization
        fields = (
            "id",
            "name",
            "slug",
            "is_active",
            "current_user_role",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "current_user_role",
            "created_at",
            "updated_at",
        )

    def get_current_user_role(
        self,
        obj: Organization,
    ) -> str | None:
        request = self.context.get("request")

        if (
            request is None
            or not getattr(request.user, "is_authenticated", False)
            or not getattr(request.user, "is_active", False)
        ):
            return None

        if request.user.is_superuser:
            return "superuser"

        membership = (
            obj.memberships.filter(
                user=request.user,
                is_active=True,
            )
            .only("role")
            .first()
        )

        return membership.role if membership else None

    def validate_name(self, value: str) -> str:
        """
        Remove surrounding whitespace and reject empty organization names.
        """
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Organization name cannot be empty."
            )

        return value

    def validate_slug(self, value: str) -> str:
        """
        Normalize organization slugs to lowercase.
        """
        value = value.strip().lower()

        if not value:
            raise serializers.ValidationError(
                "Organization slug cannot be empty."
            )

        return value


class MembershipSerializer(serializers.ModelSerializer):
    """
    Serialize organization memberships.

    The organization is assigned from the secured organization_pk URL
    parameter by the viewset.

    After a membership has been created, neither its organization nor its user
    may be changed.
    """

    user_email = serializers.EmailField(
        source="user.email",
        read_only=True,
    )

    class Meta:
        model = OrganizationMembership
        fields = (
            "id",
            "organization",
            "user",
            "user_email",
            "role",
            "is_active",
            "joined_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "organization",
            "user_email",
            "joined_at",
            "updated_at",
        )

    def validate_user(self, value: Any) -> Any:
        """
        Require an active user.

        Also prevent replacing the user assigned to an existing membership.
        """
        if not getattr(value, "is_active", False):
            raise serializers.ValidationError(
                "An inactive user cannot be added to an organization."
            )

        if (
            self.instance is not None
            and value.pk != self.instance.user_id
        ):
            raise serializers.ValidationError(
                "The user assigned to a membership cannot be changed."
            )

        return value

    def validate(
        self,
        attrs: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Explicitly reject attempts to change immutable relationships.

        Django REST Framework normally ignores submitted read-only fields.
        Checking initial_data ensures that attempts to change organization are
        rejected with a 400 response instead of being silently ignored.
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
                            "A membership cannot be moved to another "
                            "organization."
                        )
                    }
                )

        submitted_user = self.initial_data.get("user")

        if submitted_user is not None:
            submitted_user_id = str(submitted_user)
            current_user_id = str(self.instance.user_id)

            if submitted_user_id != current_user_id:
                raise serializers.ValidationError(
                    {
                        "user": (
                            "The user assigned to a membership cannot "
                            "be changed."
                        )
                    }
                )

        return attrs