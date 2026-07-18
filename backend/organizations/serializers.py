from rest_framework import serializers
from .models import Organization, OrganizationMembership


class OrganizationSerializer(serializers.ModelSerializer):
    current_user_role = serializers.SerializerMethodField()

    class Meta:
        model = Organization
        fields = ("id", "name", "slug", "is_active", "current_user_role", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at", "current_user_role")

    def get_current_user_role(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return None
        membership = obj.memberships.filter(user=request.user, is_active=True).first()
        return membership.role if membership else None


class MembershipSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = OrganizationMembership
        fields = ("id", "organization", "user", "user_email", "role", "is_active", "joined_at", "updated_at")
        read_only_fields = ("id", "organization", "joined_at", "updated_at")
