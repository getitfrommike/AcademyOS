from django.contrib import admin

from core.admin import TenantRestrictedAdminMixin

from .models import Activity, Course, Lesson, Module


class ActivityInline(admin.TabularInline):
    model = Activity
    extra = 0
    fields = (
        "order",
        "title",
        "activity_type",
        "status",
        "is_required",
        "points_possible",
    )
    ordering = ("order",)
    show_change_link = True


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 0
    fields = (
        "order",
        "title",
        "status",
        "estimated_duration_minutes",
        "is_preview",
    )
    ordering = ("order",)
    show_change_link = True


class ModuleInline(admin.TabularInline):
    model = Module
    extra = 0
    fields = (
        "order",
        "title",
        "status",
        "estimated_duration_minutes",
    )
    ordering = ("order",)
    show_change_link = True


@admin.register(Course)
class CourseAdmin(TenantRestrictedAdminMixin, admin.ModelAdmin):
    list_display = (
        "title",
        "academy",
        "program",
        "status",
        "is_featured",
        "estimated_duration_minutes",
        "updated_at",
    )

    list_filter = (
        "status",
        "is_featured",
        "organization",
        "academy",
        "program",
    )

    search_fields = (
        "title",
        "slug",
        "short_description",
        "description",
        "academy__name",
        "program__name",
    )

    prepopulated_fields = {
        "slug": ("title",),
    }

    autocomplete_fields = (
        "organization",
        "academy",
        "program",
        "created_by",
        "updated_by",
    )

    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Course",
            {
                "fields": (
                    "organization",
                    "academy",
                    "program",
                    "title",
                    "slug",
                    "short_description",
                    "description",
                )
            },
        ),
        (
            "Publishing",
            {
                "fields": (
                    "status",
                    "is_featured",
                )
            },
        ),
        (
            "Duration",
            {
                "fields": (
                    "estimated_duration_minutes",
                )
            },
        ),
        (
            "Record information",
            {
                "classes": ("collapse",),
                "fields": (
                    "id",
                    "created_by",
                    "updated_by",
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )

    inlines = [ModuleInline]

    def save_model(self, request, obj, form, change):
        if not obj.created_by_id:
            obj.created_by = request.user

        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Module)
class ModuleAdmin(TenantRestrictedAdminMixin, admin.ModelAdmin):
    organization_lookup = "course__organization_id"

    def get_object_organization(self, obj):
        return obj.course.organization

    list_display = (
        "title",
        "course",
        "order",
        "status",
        "estimated_duration_minutes",
        "updated_at",
    )

    list_filter = (
        "status",
        "course__academy",
        "course",
    )

    search_fields = (
        "title",
        "slug",
        "description",
        "course__title",
    )

    prepopulated_fields = {
        "slug": ("title",),
    }

    autocomplete_fields = (
        "course",
        "created_by",
        "updated_by",
    )

    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Module",
            {
                "fields": (
                    "course",
                    "title",
                    "slug",
                    "description",
                    "order",
                )
            },
        ),
        (
            "Publishing and duration",
            {
                "fields": (
                    "status",
                    "estimated_duration_minutes",
                )
            },
        ),
        (
            "Record information",
            {
                "classes": ("collapse",),
                "fields": (
                    "id",
                    "created_by",
                    "updated_by",
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )

    inlines = [LessonInline]

    def save_model(self, request, obj, form, change):
        if not obj.created_by_id:
            obj.created_by = request.user

        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Lesson)
class LessonAdmin(TenantRestrictedAdminMixin, admin.ModelAdmin):
    organization_lookup = "module__course__organization_id"

    def get_object_organization(self, obj):
        return obj.module.course.organization

    list_display = (
        "title",
        "module",
        "order",
        "status",
        "is_preview",
        "estimated_duration_minutes",
        "updated_at",
    )

    list_filter = (
        "status",
        "is_preview",
        "module__course",
        "module",
    )

    search_fields = (
        "title",
        "slug",
        "summary",
        "description",
        "module__title",
        "module__course__title",
    )

    prepopulated_fields = {
        "slug": ("title",),
    }

    autocomplete_fields = (
        "module",
        "created_by",
        "updated_by",
    )

    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Lesson",
            {
                "fields": (
                    "module",
                    "title",
                    "slug",
                    "summary",
                    "description",
                    "order",
                )
            },
        ),
        (
            "Publishing and access",
            {
                "fields": (
                    "status",
                    "is_preview",
                    "estimated_duration_minutes",
                )
            },
        ),
        (
            "Record information",
            {
                "classes": ("collapse",),
                "fields": (
                    "id",
                    "created_by",
                    "updated_by",
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )

    inlines = [ActivityInline]

    def save_model(self, request, obj, form, change):
        if not obj.created_by_id:
            obj.created_by = request.user

        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Activity)
class ActivityAdmin(TenantRestrictedAdminMixin, admin.ModelAdmin):
    organization_lookup = "lesson__module__course__organization_id"

    def get_object_organization(self, obj):
        return obj.lesson.module.course.organization

    list_display = (
        "title",
        "lesson",
        "activity_type",
        "order",
        "status",
        "is_required",
        "points_possible",
        "estimated_duration_minutes",
        "updated_at",
    )

    list_filter = (
        "activity_type",
        "status",
        "is_required",
        "lesson__module__course",
    )

    search_fields = (
        "title",
        "slug",
        "description",
        "lesson__title",
        "lesson__module__title",
        "lesson__module__course__title",
    )

    prepopulated_fields = {
        "slug": ("title",),
    }

    autocomplete_fields = (
        "lesson",
        "created_by",
        "updated_by",
    )

    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Activity",
            {
                "fields": (
                    "lesson",
                    "title",
                    "slug",
                    "description",
                    "activity_type",
                    "order",
                )
            },
        ),
        (
            "Completion and scoring",
            {
                "fields": (
                    "status",
                    "estimated_duration_minutes",
                    "is_required",
                    "points_possible",
                )
            },
        ),
        (
            "Configuration",
            {
                "fields": (
                    "configuration",
                )
            },
        ),
        (
            "Record information",
            {
                "classes": ("collapse",),
                "fields": (
                    "id",
                    "created_by",
                    "updated_by",
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )

    def save_model(self, request, obj, form, change):
        if not obj.created_by_id:
            obj.created_by = request.user

        obj.updated_by = request.user
        super().save_model(request, obj, form, change)