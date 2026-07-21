from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from academies.models import Academy
from core.models import LearningContent
from organizations.models import Organization
from programs.models import Program


class Course(LearningContent):
    """
    A reusable course offered through an academy and optionally attached
    to a larger program.
    """

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="courses",
    )

    academy = models.ForeignKey(
        Academy,
        on_delete=models.CASCADE,
        related_name="courses",
    )

    program = models.ForeignKey(
        Program,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="courses",
    )

    short_description = models.CharField(
        max_length=300,
        blank=True,
    )

    is_featured = models.BooleanField(default=False)

    class Meta:
        ordering = ["title"]
        verbose_name = "Course"
        verbose_name_plural = "Courses"

        constraints = [
            models.UniqueConstraint(
                fields=["academy", "slug"],
                name="unique_course_slug_per_academy",
            ),
        ]

        indexes = [
            models.Index(
                fields=["organization", "status"],
                name="course_org_status_idx",
            ),
            models.Index(
                fields=["academy", "status"],
                name="course_acad_status_idx",
            ),
            models.Index(
                fields=["program", "status"],
                name="course_prog_status_idx",
            ),
            models.Index(
                fields=["organization", "is_featured"],
                name="course_org_featured_idx",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.title} — {self.academy.name}"

    def clean(self) -> None:
        errors = {}

        if (
            self.academy_id
            and self.organization_id
            and self.academy.organization_id != self.organization_id
        ):
            errors["organization"] = (
                "The selected organization must own the selected academy."
            )

        if self.program_id:
            if self.program.academy_id != self.academy_id:
                errors["program"] = (
                    "The selected program must belong to the selected academy."
                )

            if self.program.organization_id != self.organization_id:
                errors["program"] = (
                    "The selected program must belong to the selected organization."
                )

        if errors:
            raise ValidationError(errors)


class Module(LearningContent):
    """
    A structured section inside a course.
    """

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="modules",
    )

    order = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="The module's position inside the course.",
    )

    class Meta:
        ordering = ["course", "order"]
        verbose_name = "Module"
        verbose_name_plural = "Modules"

        constraints = [
            models.UniqueConstraint(
                fields=["course", "slug"],
                name="unique_module_slug_per_course",
            ),
            models.UniqueConstraint(
                fields=["course", "order"],
                name="unique_module_order_per_course",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.course.title} — Module {self.order}: {self.title}"


class Lesson(LearningContent):
    """
    A lesson inside a module.
    """

    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name="lessons",
    )

    summary = models.CharField(
        max_length=300,
        blank=True,
    )

    order = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="The lesson's position inside the module.",
    )

    is_preview = models.BooleanField(
        default=False,
        help_text="Allow this lesson to be viewed without enrollment.",
    )

    class Meta:
        ordering = ["module", "order"]
        verbose_name = "Lesson"
        verbose_name_plural = "Lessons"

        constraints = [
            models.UniqueConstraint(
                fields=["module", "slug"],
                name="unique_lesson_slug_per_module",
            ),
            models.UniqueConstraint(
                fields=["module", "order"],
                name="unique_lesson_order_per_module",
            ),
        ]

    def __str__(self) -> str:
        return (
            f"{self.module.course.title} — "
            f"Module {self.module.order}, "
            f"Lesson {self.order}: {self.title}"
        )


class Activity(LearningContent):
    """
    A learning experience completed inside a lesson.

    Activities may represent videos, readings, quizzes, coding exercises,
    cybersecurity labs, AI tutor sessions, assignments, downloads,
    or live events.
    """

    class ActivityType(models.TextChoices):
        VIDEO = "video", "Video"
        ARTICLE = "article", "Article"
        BRAIN_LAB = "brain_lab", "Brain Lab"
        QUIZ = "quiz", "Quiz"
        CODING_EXERCISE = "coding_exercise", "Coding Exercise"
        CYBERSECURITY_LAB = "cybersecurity_lab", "Cybersecurity Lab"
        AI_TUTOR_SESSION = "ai_tutor_session", "AI Tutor Session"
        ASSIGNMENT = "assignment", "Assignment"
        DOWNLOAD = "download", "Download"
        LIVE_EVENT = "live_event", "Live Event"

    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="activities",
    )

    activity_type = models.CharField(
        max_length=40,
        choices=ActivityType.choices,
    )

    order = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="The activity's position inside the lesson.",
    )

    is_required = models.BooleanField(
        default=True,
        help_text="Whether learners must complete this activity.",
    )

    points_possible = models.PositiveIntegerField(
        default=0,
        help_text="Maximum points available for this activity.",
    )

    configuration = models.JSONField(
        default=dict,
        blank=True,
        help_text=(
            "Type-specific activity settings, such as video URLs, "
            "quiz rules, lab configuration, or event details."
        ),
    )

    class Meta:
        ordering = ["lesson", "order"]
        verbose_name = "Activity"
        verbose_name_plural = "Activities"

        constraints = [
            models.UniqueConstraint(
                fields=["lesson", "slug"],
                name="unique_activity_slug_per_lesson",
            ),
            models.UniqueConstraint(
                fields=["lesson", "order"],
                name="unique_activity_order_per_lesson",
            ),
        ]

    def __str__(self) -> str:
        return (
            f"{self.lesson.module.course.title} — "
            f"Module {self.lesson.module.order}, "
            f"Lesson {self.lesson.order}, "
            f"Activity {self.order}: {self.title}"
        )