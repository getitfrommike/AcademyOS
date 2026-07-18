from django.contrib import admin

from .models import Organization, OrganizationMembership


class OrganizationMembershipInline(admin.TabularInline):
    model = OrganizationMembership
    extra = 0
    autocomplete_fields = ("user",)


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
        "is_active",
        "created_at",
    )
    list_filter = (
        "is_active",
        "created_at",
    )
    search_fields = (
        "name",
        "slug",
    )
    prepopulated_fields = {
        "slug": ("name",),
    }
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    inlines = (
        OrganizationMembershipInline,
    )


@admin.register(OrganizationMembership)
class OrganizationMembershipAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "organization",
        "role",
        "is_active",
        "joined_at",
    )
    list_filter = (
        "role",
        "is_active",
        "organization",
    )
    search_fields = (
        "user__email",
        "user__username",
        "organization__name",
    )
    autocomplete_fields = (
        "user",
        "organization",
    )
    readonly_fields = (
        "joined_at",
        "updated_at",
    )