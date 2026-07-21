from django.core.exceptions import (
    ValidationError as DjangoValidationError,
)
from rest_framework import serializers, viewsets
from rest_framework.exceptions import PermissionDenied

from core.permissions import IsOrganizationMember
from core.tenant import (
    MANAGER_ROLES,
    has_organization_role,
    organization_ids_for,
)
from organizations.models import Organization

from .models import (
    Activity,
    Course,
    Lesson,
    Module,
)

from .serializers import (
    ActivitySerializer,
    CourseSerializer,
    LessonSerializer,
    ModuleSerializer,
)


class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    permission_classes = [IsOrganizationMember]

    def get_queryset(self):
        organization_ids = organization_ids_for(
            self.request.user
        )

        queryset = Course.objects.select_related(
            "organization",
            "academy",
            "program",
            "created_by",
            "updated_by",
        )

        if organization_ids is None:
            return queryset

        return queryset.filter(
            organization_id__in=organization_ids
        )

    def _get_requested_organization(self):
        organization_id = self.request.data.get(
            "organization_id"
        )

        if not organization_id:
            raise serializers.ValidationError(
                {
                    "organization_id": (
                        "An organization is required."
                    )
                }
            )

        try:
            organization = Organization.objects.get(
                id=organization_id
            )
        except (
            Organization.DoesNotExist,
            ValueError,
            TypeError,
            DjangoValidationError,
        ) as exc:
            raise serializers.ValidationError(
                {
                    "organization_id": (
                        "A valid organization is required."
                    )
                }
            ) from exc

        if not organization.is_active:
            raise serializers.ValidationError(
                {
                    "organization_id": (
                        "The selected organization is inactive."
                    )
                }
            )

        return organization

    def _require_manager_access(self, organization):
        if self.request.user.is_superuser:
            return

        has_manager_access = (
            organization.memberships.filter(
                user=self.request.user,
                is_active=True,
                role__in=MANAGER_ROLES,
            ).exists()
        )

        if not has_manager_access:
            raise PermissionDenied(
                "Manager access is required."
            )

    def perform_create(self, serializer):
        organization = self._get_requested_organization()
        self._require_manager_access(organization)

        academy = (
            serializer.validate_academy_for_organization(
                self.request.data.get("academy_id"),
                organization,
            )
        )

        program = serializer.validate_program_for_course(
            self.request.data.get("program_id"),
            organization,
            academy,
        )

        serializer.save(
            organization=organization,
            academy=academy,
            program=program,
            created_by=self.request.user,
            updated_by=self.request.user,
        )

    def perform_update(self, serializer):
        course = self.get_object()

        self._require_manager_access(
            course.organization
        )

        serializer.save(
            updated_by=self.request.user
        )

    def perform_destroy(self, instance):
        self._require_manager_access(
            instance.organization
        )

        instance.delete()


class ModuleViewSet(viewsets.ModelViewSet):
    serializer_class = ModuleSerializer
    permission_classes = [IsOrganizationMember]

    def get_queryset(self):
        organization_ids = organization_ids_for(
            self.request.user
        )

        queryset = Module.objects.select_related(
            "course",
            "course__organization",
            "course__academy",
            "course__program",
            "created_by",
            "updated_by",
        )

        if organization_ids is None:
            return queryset

        return queryset.filter(
            course__organization_id__in=organization_ids
        )

    def _require_manager_access(self, organization):
        if self.request.user.is_superuser:
            return

        has_manager_access = (
            organization.memberships.filter(
                user=self.request.user,
                is_active=True,
                role__in=MANAGER_ROLES,
            ).exists()
        )

        if not has_manager_access:
            raise PermissionDenied(
                "Manager access is required."
            )

    def perform_create(self, serializer):
        course = serializer.validate_course_for_module(
            self.request.data.get("course_id")
        )

        self._require_manager_access(
            course.organization
        )

        serializer.save(
            course=course,
            created_by=self.request.user,
            updated_by=self.request.user,
        )

    def perform_update(self, serializer):
        module = self.get_object()

        self._require_manager_access(
            module.course.organization
        )

        serializer.save(
            updated_by=self.request.user
        )

    def perform_destroy(self, instance):
        self._require_manager_access(
            instance.course.organization
        )

        instance.delete()

class LessonViewSet(viewsets.ModelViewSet):
    serializer_class = LessonSerializer
    permission_classes = [IsOrganizationMember]

    def get_queryset(self):
        organization_ids = organization_ids_for(
            self.request.user
        )

        queryset = Lesson.objects.select_related(
            "module",
            "module__course",
            "module__course__organization",
            "module__course__academy",
            "created_by",
            "updated_by",
        )

        if organization_ids is None:
            return queryset

        return queryset.filter(
            module__course__organization_id__in=organization_ids
        )

    def _require_manager_access(self, organization):
        if self.request.user.is_superuser:
            return

        has_manager_access = (
            organization.memberships.filter(
                user=self.request.user,
                is_active=True,
                role__in=MANAGER_ROLES,
            ).exists()
        )

        if not has_manager_access:
            raise PermissionDenied(
                "Manager access is required."
            )

    def perform_create(self, serializer):
        module = serializer.validate_module_for_lesson(
            self.request.data.get("module_id")
        )

        self._require_manager_access(
            module.course.organization
        )

        serializer.save(
            module=module,
            created_by=self.request.user,
            updated_by=self.request.user,
        )

    def perform_update(self, serializer):
        lesson = self.get_object()

        self._require_manager_access(
            lesson.module.course.organization
        )

        serializer.save(
            updated_by=self.request.user,
        )

    def perform_destroy(self, instance):
        self._require_manager_access(
            instance.module.course.organization
        )

        instance.delete()

class ActivityViewSet(viewsets.ModelViewSet):
    serializer_class = ActivitySerializer
    permission_classes = [IsOrganizationMember]

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser:
            return Activity.objects.select_related(
                "lesson",
                "lesson__module",
                "lesson__module__course",
                "created_by",
                "updated_by",
            )

        organization_ids = (
            user.organization_memberships.values_list(
                "organization_id",
                flat=True,
            )
        )

        return Activity.objects.filter(
            lesson__module__course__organization_id__in=organization_ids,
        ).select_related(
            "lesson",
            "lesson__module",
            "lesson__module__course",
            "created_by",
            "updated_by",
        )

    def perform_create(self, serializer):
        lesson = (
            ActivitySerializer.validate_lesson_for_activity(
                self.request.data.get("lesson_id")
            )
        )

        if not has_organization_role(
            user=self.request.user,
            organization=lesson.module.course.organization,
            roles=MANAGER_ROLES,
        ):
            raise PermissionDenied()

        serializer.save(
            lesson=lesson,
            created_by=self.request.user,
            updated_by=self.request.user,
        )

    def perform_update(self, serializer):
        activity = self.get_object()

        if not has_organization_role(
            user=self.request.user,
            organization=activity.lesson.module.course.organization,
            roles=MANAGER_ROLES,
        ):
            raise PermissionDenied()

        serializer.save(
            updated_by=self.request.user,
        )

    def perform_destroy(self, instance):
        if not has_organization_role(
            user=self.request.user,
            organization=instance.lesson.module.course.organization,
            roles=MANAGER_ROLES,
        ):
            raise PermissionDenied()

        instance.delete()