from django.core.exceptions import (
    ValidationError as DjangoValidationError,
)
from rest_framework import serializers

from academies.models import Academy
from programs.models import Program

from .models import (
    Activity,
    Course,
    Lesson,
    Module,
)


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


class ModuleSerializer(serializers.ModelSerializer):
    course = serializers.UUIDField(
        source="course_id",
        read_only=True,
    )

    class Meta:
        model = Module
        fields = (
            "id",
            "course",
            "title",
            "slug",
            "description",
            "estimated_duration_minutes",
            "status",
            "order",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "course",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        )

    def validate_title(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Module title cannot be blank."
            )

        return value

    def validate_slug(self, value):
        return value.strip().lower()

    def validate_order(self, value):
        if value < 1:
            raise serializers.ValidationError(
                "Module order must be 1 or greater."
            )

        return value

    def validate(self, attrs):
        if self.instance is not None:
            immutable_fields = {
                "course": (
                    "A module's course cannot be changed."
                ),
                "course_id": (
                    "A module's course cannot be changed."
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
    def validate_course_for_module(course_id):
        if not course_id:
            raise serializers.ValidationError(
                {
                    "course_id": (
                        "A course is required."
                    )
                }
            )

        try:
            course = Course.objects.select_related(
                "organization",
                "academy",
                "program",
            ).get(id=course_id)
        except (
            Course.DoesNotExist,
            ValueError,
            TypeError,
            DjangoValidationError,
        ) as exc:
            raise serializers.ValidationError(
                {
                    "course_id": (
                        "A valid course is required."
                    )
                }
            ) from exc

        if not course.organization.is_active:
            raise serializers.ValidationError(
                {
                    "course_id": (
                        "The selected course belongs to an "
                        "inactive organization."
                    )
                }
            )

        if not course.academy.is_active:
            raise serializers.ValidationError(
                {
                    "course_id": (
                        "The selected course belongs to an "
                        "inactive academy."
                    )
                }
            )

        return course
    
class LessonSerializer(serializers.ModelSerializer):
    module = serializers.UUIDField(
        source="module_id",
        read_only=True,
    )

    class Meta:
        model = Lesson

        fields = (
            "id",
            "module",
            "title",
            "slug",
            "summary",
            "description",
            "estimated_duration_minutes",
            "status",
            "order",
            "is_preview",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "module",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        )

    def validate_title(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Lesson title cannot be blank."
            )

        return value

    def validate_slug(self, value):
        return value.strip().lower()

    def validate_summary(self, value):
        return value.strip()

    def validate_order(self, value):
        if value < 1:
            raise serializers.ValidationError(
                "Lesson order must be 1 or greater."
            )

        return value

    def validate(self, attrs):
        if self.instance is not None:
            immutable_fields = {
                "module": (
                    "A lesson's module cannot be changed."
                ),
                "module_id": (
                    "A lesson's module cannot be changed."
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
    def validate_module_for_lesson(module_id):
        if not module_id:
            raise serializers.ValidationError(
                {
                    "module_id": (
                        "A module is required."
                    )
                }
            )

        try:
            module = Module.objects.select_related(
                "course",
                "course__organization",
                "course__academy",
                "course__program",
            ).get(id=module_id)

        except (
            Module.DoesNotExist,
            ValueError,
            TypeError,
            DjangoValidationError,
        ) as exc:
            raise serializers.ValidationError(
                {
                    "module_id": (
                        "A valid module is required."
                    )
                }
            ) from exc

        if not module.course.organization.is_active:
            raise serializers.ValidationError(
                {
                    "module_id": (
                        "The selected module belongs to an "
                        "inactive organization."
                    )
                }
            )

        if not module.course.academy.is_active:
            raise serializers.ValidationError(
                {
                    "module_id": (
                        "The selected module belongs to an "
                        "inactive academy."
                    )
                }
            )

        return module
    
class ActivitySerializer(serializers.ModelSerializer):
    lesson = serializers.UUIDField(
        source="lesson_id",
        read_only=True,
    )

    class Meta:
        model = Activity

        fields = (
            "id",
            "lesson",
            "lesson_id",
            "title",
            "slug",
            "description",
            "estimated_duration_minutes",
            "status",
            "activity_type",
            "order",
            "is_required",
            "points_possible",
            "configuration",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "lesson",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        )

    def validate_title(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Activity title cannot be blank."
            )

        return value

    def validate_order(self, value):
        if value < 1:
            raise serializers.ValidationError(
                "Activity order must be 1 or greater."
            )

        return value

    def validate_points_possible(self, value):
        if value < 0:
            raise serializers.ValidationError(
                "Points possible cannot be negative."
            )

        return value

    def validate(self, attrs):
        if self.instance is not None:
            immutable_fields = {
                "lesson": (
                    "An activity's lesson cannot be changed."
                ),
                "lesson_id": (
                    "An activity's lesson cannot be changed."
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
    def validate_lesson_for_activity(lesson_id):
        if not lesson_id:
            raise serializers.ValidationError(
                {
                    "lesson_id": (
                        "A lesson is required."
                    )
                }
            )

        try:
            lesson = Lesson.objects.select_related(
                "module",
                "module__course",
                "module__course__organization",
                "module__course__academy",
            ).get(id=lesson_id)

        except (
            Lesson.DoesNotExist,
            ValueError,
            TypeError,
            DjangoValidationError,
        ) as exc:
            raise serializers.ValidationError(
                {
                    "lesson_id": (
                        "A valid lesson is required."
                    )
                }
            ) from exc

        if not lesson.module.course.organization.is_active:
            raise serializers.ValidationError(
                {
                    "lesson_id": (
                        "The selected lesson belongs to an "
                        "inactive organization."
                    )
                }
            )

        if not lesson.module.course.academy.is_active:
            raise serializers.ValidationError(
                {
                    "lesson_id": (
                        "The selected lesson belongs to an "
                        "inactive academy."
                    )
                }
            )

        return lesson