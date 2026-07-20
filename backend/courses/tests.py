from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from academies.models import Academy
from organizations.models import Organization, OrganizationMembership
from programs.models import Program

from .models import Course


User = get_user_model()


class CourseModelSecurityTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner",
            email="owner@example.com",
            password="StrongPass123!",
        )

        self.organization = Organization.objects.create(
            name="Secure Academy Organization",
            slug="secure-academy-organization",
        )

        self.academy = Academy.objects.create(
            organization=self.organization,
            name="Secure Academy",
            slug="secure-academy",
            created_by=self.owner,
            updated_by=self.owner,
        )

        self.program = Program.objects.create(
            organization=self.organization,
            academy=self.academy,
            name="Cybersecurity Program",
            slug="cybersecurity-program",
            created_by=self.owner,
            updated_by=self.owner,
        )

    def test_course_rejects_academy_from_another_organization(self):
        other_organization = Organization.objects.create(
            name="Other Organization",
            slug="other-organization",
        )

        other_academy = Academy.objects.create(
            organization=other_organization,
            name="Other Academy",
            slug="other-academy",
            created_by=self.owner,
            updated_by=self.owner,
        )

        course = Course(
            organization=self.organization,
            academy=other_academy,
            title="Invalid Course",
            slug="invalid-course",
            created_by=self.owner,
            updated_by=self.owner,
        )

        with self.assertRaises(ValidationError):
            course.full_clean()

    def test_course_rejects_program_from_another_academy(self):
        other_academy = Academy.objects.create(
            organization=self.organization,
            name="Second Academy",
            slug="second-academy",
            created_by=self.owner,
            updated_by=self.owner,
        )

        other_program = Program.objects.create(
            organization=self.organization,
            academy=other_academy,
            name="Other Program",
            slug="other-program",
            created_by=self.owner,
            updated_by=self.owner,
        )

        course = Course(
            organization=self.organization,
            academy=self.academy,
            program=other_program,
            title="Invalid Program Course",
            slug="invalid-program-course",
            created_by=self.owner,
            updated_by=self.owner,
        )

        with self.assertRaises(ValidationError):
            course.full_clean()

    def test_duplicate_slug_is_rejected_within_same_academy(self):
        Course.objects.create(
            organization=self.organization,
            academy=self.academy,
            title="Course One",
            slug="shared-slug",
            created_by=self.owner,
            updated_by=self.owner,
        )

        duplicate = Course(
            organization=self.organization,
            academy=self.academy,
            title="Course Two",
            slug="shared-slug",
            created_by=self.owner,
            updated_by=self.owner,
        )

        with self.assertRaises(ValidationError):
            duplicate.full_clean()

    def test_duplicate_slug_is_allowed_across_different_academies(self):
        other_academy = Academy.objects.create(
            organization=self.organization,
            name="Second Academy",
            slug="second-academy",
            created_by=self.owner,
            updated_by=self.owner,
        )

        Course.objects.create(
            organization=self.organization,
            academy=self.academy,
            title="Course One",
            slug="shared-slug",
            created_by=self.owner,
            updated_by=self.owner,
        )

        second_course = Course.objects.create(
            organization=self.organization,
            academy=other_academy,
            title="Course Two",
            slug="shared-slug",
            created_by=self.owner,
            updated_by=self.owner,
        )

        self.assertEqual(second_course.slug, "shared-slug")


class CourseAPISecurityTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.manager = User.objects.create_user(
            username="manager",
            email="manager@example.com",
            password="StrongPass123!",
        )
        self.member = User.objects.create_user(
            username="member",
            email="member@example.com",
            password="StrongPass123!",
        )
        self.outsider = User.objects.create_user(
            username="outsider",
            email="outsider@example.com",
            password="StrongPass123!",
        )
        self.superuser = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="StrongPass123!",
        )

        self.organization = Organization.objects.create(
            name="Primary Organization",
            slug="primary-organization",
        )
        self.other_organization = Organization.objects.create(
            name="Other Organization",
            slug="other-organization",
        )

        OrganizationMembership.objects.create(
            organization=self.organization,
            user=self.manager,
            role=OrganizationMembership.Role.OWNER,
            is_active=True,
        )
        OrganizationMembership.objects.create(
            organization=self.organization,
            user=self.member,
            role=OrganizationMembership.Role.STUDENT,
            is_active=True,
        )

        self.academy = Academy.objects.create(
            organization=self.organization,
            name="Primary Academy",
            slug="primary-academy",
            created_by=self.manager,
            updated_by=self.manager,
        )
        self.other_academy = Academy.objects.create(
            organization=self.other_organization,
            name="Other Academy",
            slug="other-academy",
            created_by=self.manager,
            updated_by=self.manager,
        )

        self.program = Program.objects.create(
            organization=self.organization,
            academy=self.academy,
            name="Primary Program",
            slug="primary-program",
            created_by=self.manager,
            updated_by=self.manager,
        )
        self.other_program = Program.objects.create(
            organization=self.other_organization,
            academy=self.other_academy,
            name="Other Program",
            slug="other-program",
            created_by=self.manager,
            updated_by=self.manager,
        )

        self.course = Course.objects.create(
            organization=self.organization,
            academy=self.academy,
            program=self.program,
            title="Secure Course",
            slug="secure-course",
            created_by=self.manager,
            updated_by=self.manager,
        )
        self.other_course = Course.objects.create(
            organization=self.other_organization,
            academy=self.other_academy,
            program=self.other_program,
            title="Other Course",
            slug="other-course",
            created_by=self.manager,
            updated_by=self.manager,
        )

        self.list_url = reverse("course-list")

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def course_payload(self, **overrides):
        payload = {
            "organization_id": str(self.organization.id),
            "academy_id": str(self.academy.id),
            "program_id": str(self.program.id),
            "title": "New Secure Course",
            "slug": "new-secure-course",
            "description": "Secure learning content.",
            "short_description": "Security-first course.",
            "status": "draft",
            "estimated_duration_minutes": 60,
            "is_featured": False,
        }
        payload.update(overrides)
        return payload

    def test_manager_can_create_course(self):
        self.authenticate(self.manager)

        response = self.client.post(
            self.list_url,
            self.course_payload(),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        course = Course.objects.get(slug="new-secure-course")
        self.assertEqual(course.created_by, self.manager)
        self.assertEqual(course.updated_by, self.manager)
        self.assertEqual(course.organization, self.organization)
        self.assertEqual(course.academy, self.academy)
        self.assertEqual(course.program, self.program)

    def test_regular_member_cannot_create_course(self):
        self.authenticate(self.member)

        response = self.client.post(
            self.list_url,
            self.course_payload(),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_outsider_cannot_create_course(self):
        self.authenticate(self.outsider)

        response = self.client.post(
            self.list_url,
            self.course_payload(),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_member_only_sees_courses_in_own_organization(self):
        self.authenticate(self.member)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        items = response.data.get("results", response.data)
        returned_ids = {item["id"] for item in items}
        self.assertIn(str(self.course.id), returned_ids)
        self.assertNotIn(str(self.other_course.id), returned_ids)

    def test_superuser_sees_courses_across_organizations(self):
        self.authenticate(self.superuser)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        items = response.data.get("results", response.data)
        returned_ids = {item["id"] for item in items}
        self.assertIn(str(self.course.id), returned_ids)
        self.assertIn(str(self.other_course.id), returned_ids)

    def test_manager_can_update_course_and_sets_updated_by(self):
        self.authenticate(self.manager)
        detail_url = reverse("course-detail", args=[self.course.id])

        response = self.client.patch(
            detail_url,
            {"title": "Updated Secure Course"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.course.refresh_from_db()
        self.assertEqual(self.course.title, "Updated Secure Course")
        self.assertEqual(self.course.updated_by, self.manager)

    def test_regular_member_cannot_update_course(self):
        self.authenticate(self.member)
        detail_url = reverse("course-detail", args=[self.course.id])

        response = self.client.patch(
            detail_url,
            {"title": "Unauthorized Update"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_manager_cannot_change_organization(self):
        self.authenticate(self.manager)
        detail_url = reverse("course-detail", args=[self.course.id])

        response = self.client.patch(
            detail_url,
            {"organization_id": str(self.other_organization.id)},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_manager_cannot_change_academy(self):
        self.authenticate(self.manager)
        detail_url = reverse("course-detail", args=[self.course.id])

        response = self.client.patch(
            detail_url,
            {"academy_id": str(self.other_academy.id)},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_manager_cannot_change_program(self):
        self.authenticate(self.manager)
        detail_url = reverse("course-detail", args=[self.course.id])

        response = self.client.patch(
            detail_url,
            {"program_id": str(self.other_program.id)},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_rejects_academy_from_another_organization(self):
        self.authenticate(self.manager)

        response = self.client.post(
            self.list_url,
            self.course_payload(
                academy_id=str(self.other_academy.id),
            ),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_rejects_program_from_another_organization(self):
        self.authenticate(self.manager)

        response = self.client.post(
            self.list_url,
            self.course_payload(
                program_id=str(self.other_program.id),
            ),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_manager_can_delete_course(self):
        self.authenticate(self.manager)
        detail_url = reverse("course-detail", args=[self.course.id])

        response = self.client.delete(detail_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Course.objects.filter(id=self.course.id).exists())

    def test_regular_member_cannot_delete_course(self):
        self.authenticate(self.member)
        detail_url = reverse("course-detail", args=[self.course.id])

        response = self.client.delete(detail_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Course.objects.filter(id=self.course.id).exists())