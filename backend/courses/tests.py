from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from academies.models import Academy
from organizations.models import Organization, OrganizationMembership
from programs.models import Program

from .models import Activity, Course, Lesson, Module


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

class ModuleModelSecurityTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="module_owner",
            email="module_owner@example.com",
            password="StrongPass123!",
        )

        self.organization = Organization.objects.create(
            name="Module Organization",
            slug="module-organization",
        )

        self.academy = Academy.objects.create(
            organization=self.organization,
            name="Module Academy",
            slug="module-academy",
            created_by=self.owner,
            updated_by=self.owner,
        )

        self.program = Program.objects.create(
            organization=self.organization,
            academy=self.academy,
            name="Module Program",
            slug="module-program",
            created_by=self.owner,
            updated_by=self.owner,
        )

        self.course = Course.objects.create(
            organization=self.organization,
            academy=self.academy,
            program=self.program,
            title="Python Security",
            slug="python-security",
            created_by=self.owner,
            updated_by=self.owner,
        )

    def test_duplicate_slug_is_rejected_within_same_course(self):
        Module.objects.create(
            course=self.course,
            title="Lesson One",
            slug="intro",
            order=1,
            created_by=self.owner,
            updated_by=self.owner,
        )

        duplicate = Module(
            course=self.course,
            title="Lesson Two",
            slug="intro",
            order=2,
            created_by=self.owner,
            updated_by=self.owner,
        )

        with self.assertRaises(ValidationError):
            duplicate.full_clean()

    def test_duplicate_slug_allowed_in_different_courses(self):
        second_course = Course.objects.create(
            organization=self.organization,
            academy=self.academy,
            program=self.program,
            title="Networking",
            slug="networking",
            created_by=self.owner,
            updated_by=self.owner,
        )

        Module.objects.create(
            course=self.course,
            title="Module One",
            slug="shared-module",
            order=1,
            created_by=self.owner,
            updated_by=self.owner,
        )

        module = Module.objects.create(
            course=second_course,
            title="Module Two",
            slug="shared-module",
            order=1,
            created_by=self.owner,
            updated_by=self.owner,
        )

        self.assertEqual(
            module.slug,
            "shared-module",
        )

    def test_order_must_be_positive(self):
        module = Module(
            course=self.course,
            title="Bad Module",
            slug="bad-module",
            order=0,
            created_by=self.owner,
            updated_by=self.owner,
        )

        with self.assertRaises(ValidationError):
            module.full_clean()   

class LessonModelSecurityTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="lesson_owner",
            email="lesson_owner@example.com",
            password="StrongPass123!",
        )

        self.organization = Organization.objects.create(
            name="Lesson Organization",
            slug="lesson-organization",
        )

        self.academy = Academy.objects.create(
            organization=self.organization,
            name="Lesson Academy",
            slug="lesson-academy",
            created_by=self.owner,
            updated_by=self.owner,
        )

        self.program = Program.objects.create(
            organization=self.organization,
            academy=self.academy,
            name="Lesson Program",
            slug="lesson-program",
            created_by=self.owner,
            updated_by=self.owner,
        )

        self.course = Course.objects.create(
            organization=self.organization,
            academy=self.academy,
            program=self.program,
            title="Lesson Security Course",
            slug="lesson-security-course",
            created_by=self.owner,
            updated_by=self.owner,
        )

        self.module = Module.objects.create(
            course=self.course,
            title="Lesson Security Module",
            slug="lesson-security-module",
            order=1,
            created_by=self.owner,
            updated_by=self.owner,
        )

    def test_duplicate_slug_is_rejected_within_same_module(self):
        Lesson.objects.create(
            module=self.module,
            title="Lesson One",
            slug="shared-lesson",
            order=1,
            created_by=self.owner,
            updated_by=self.owner,
        )

        duplicate = Lesson(
            module=self.module,
            title="Lesson Two",
            slug="shared-lesson",
            order=2,
            created_by=self.owner,
            updated_by=self.owner,
        )

        with self.assertRaises(ValidationError):
            duplicate.full_clean()

    def test_duplicate_slug_allowed_in_different_modules(self):
        second_module = Module.objects.create(
            course=self.course,
            title="Second Module",
            slug="second-module",
            order=2,
            created_by=self.owner,
            updated_by=self.owner,
        )

        Lesson.objects.create(
            module=self.module,
            title="Lesson One",
            slug="shared-lesson",
            order=1,
            created_by=self.owner,
            updated_by=self.owner,
        )

        lesson = Lesson.objects.create(
            module=second_module,
            title="Lesson Two",
            slug="shared-lesson",
            order=1,
            created_by=self.owner,
            updated_by=self.owner,
        )

        self.assertEqual(
            lesson.slug,
            "shared-lesson",
        )

    def test_duplicate_order_is_rejected_within_same_module(self):
        Lesson.objects.create(
            module=self.module,
            title="Lesson One",
            slug="lesson-one",
            order=1,
            created_by=self.owner,
            updated_by=self.owner,
        )

        duplicate = Lesson(
            module=self.module,
            title="Lesson Two",
            slug="lesson-two",
            order=1,
            created_by=self.owner,
            updated_by=self.owner,
        )

        with self.assertRaises(ValidationError):
            duplicate.full_clean()

    def test_order_must_be_positive(self):
        lesson = Lesson(
            module=self.module,
            title="Invalid Lesson",
            slug="invalid-lesson",
            order=0,
            created_by=self.owner,
            updated_by=self.owner,
        )

        with self.assertRaises(ValidationError):
            lesson.full_clean()     


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

class ModuleAPISecurityTests(TestCase):
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

        self.module = Module.objects.create(
            course=self.course,
            title="Introduction",
            slug="introduction",
            order=1,
            created_by=self.manager,
            updated_by=self.manager,
        )
        self.other_module = Module.objects.create(
            course=self.other_course,
            title="Other Module",
            slug="other-module",
            order=1,
            created_by=self.manager,
            updated_by=self.manager,
        )

        self.list_url = reverse("module-list")

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def module_payload(self, **overrides):
        payload = {
            "course_id": str(self.course.id),
            "title": "New Secure Module",
            "slug": "new-secure-module",
            "description": "Secure module content.",
            "order": 2,
        }
        payload.update(overrides)
        return payload
    
    def test_manager_can_create_module(self):
        self.authenticate(self.manager)

        response = self.client.post(
            self.list_url,
            self.module_payload(),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        module = Module.objects.get(slug="new-secure-module")

        self.assertEqual(module.created_by, self.manager)
        self.assertEqual(module.updated_by, self.manager)
        self.assertEqual(module.course, self.course)
        self.assertEqual(module.order, 2)

    def test_regular_member_cannot_create_module(self):
        self.authenticate(self.member)

        response = self.client.post(
            self.list_url,
            self.module_payload(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.assertFalse(
            Module.objects.filter(
                slug="new-secure-module",
            ).exists()
        )

    def test_outsider_cannot_create_module(self):
        self.authenticate(self.outsider)

        response = self.client.post(
            self.list_url,
            self.module_payload(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.assertFalse(
            Module.objects.filter(
                slug="new-secure-module",
            ).exists()
        )

    def test_member_only_sees_modules_in_own_organization(self):
        self.authenticate(self.member)

        response = self.client.get(self.list_url)

        self.assertEqual(
        response.status_code,
        status.HTTP_200_OK,
        )

        items = response.data.get("results", response.data)
        returned_ids = {item["id"] for item in items}

        self.assertIn(str(self.module.id), returned_ids)
        self.assertNotIn(str(self.other_module.id), returned_ids)

class LessonAPISecurityTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.manager = User.objects.create_user(
            username="lesson_manager",
            email="lesson_manager@example.com",
            password="StrongPass123!",
        )

        self.member = User.objects.create_user(
            username="lesson_member",
            email="lesson_member@example.com",
            password="StrongPass123!",
        )

        self.outsider = User.objects.create_user(
            username="lesson_outsider",
            email="lesson_outsider@example.com",
            password="StrongPass123!",
        )

        self.superuser = User.objects.create_superuser(
            username="lesson_admin",
            email="lesson_admin@example.com",
            password="StrongPass123!",
        )

        self.organization = Organization.objects.create(
            name="Lesson Organization",
            slug="lesson-organization-api",
        )

        self.other_organization = Organization.objects.create(
            name="Other Lesson Organization",
            slug="other-lesson-organization",
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
            name="Lesson Academy",
            slug="lesson-academy-api",
            created_by=self.manager,
            updated_by=self.manager,
        )

        self.other_academy = Academy.objects.create(
            organization=self.other_organization,
            name="Other Lesson Academy",
            slug="other-lesson-academy",
            created_by=self.manager,
            updated_by=self.manager,
        )

        self.program = Program.objects.create(
            organization=self.organization,
            academy=self.academy,
            name="Lesson Program",
            slug="lesson-program-api",
            created_by=self.manager,
            updated_by=self.manager,
        )

        self.other_program = Program.objects.create(
            organization=self.other_organization,
            academy=self.other_academy,
            name="Other Lesson Program",
            slug="other-lesson-program",
            created_by=self.manager,
            updated_by=self.manager,
        )

        self.course = Course.objects.create(
            organization=self.organization,
            academy=self.academy,
            program=self.program,
            title="Lesson Course",
            slug="lesson-course",
            created_by=self.manager,
            updated_by=self.manager,
        )

        self.other_course = Course.objects.create(
            organization=self.other_organization,
            academy=self.other_academy,
            program=self.other_program,
            title="Other Lesson Course",
            slug="other-lesson-course",
            created_by=self.manager,
            updated_by=self.manager,
        )

        self.module = Module.objects.create(
            course=self.course,
            title="Lesson Module",
            slug="lesson-module",
            order=1,
            created_by=self.manager,
            updated_by=self.manager,
        )

        self.other_module = Module.objects.create(
            course=self.other_course,
            title="Other Lesson Module",
            slug="other-lesson-module",
            order=1,
            created_by=self.manager,
            updated_by=self.manager,
        )

        self.lesson = Lesson.objects.create(
            module=self.module,
            title="Existing Lesson",
            slug="existing-lesson",
            order=1,
            created_by=self.manager,
            updated_by=self.manager,
        )

        self.other_lesson = Lesson.objects.create(
            module=self.other_module,
            title="Other Lesson",
            slug="other-existing-lesson",
            order=1,
            created_by=self.manager,
            updated_by=self.manager,
        )

        self.list_url = reverse("lesson-list")

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def lesson_payload(self, **overrides):
        payload = {
            "module_id": str(self.module.id),
            "title": "New Secure Lesson",
            "slug": "new-secure-lesson",
            "summary": "Lesson summary",
            "description": "Lesson description",
            "order": 2,
            "status": "draft",
            "estimated_duration_minutes": 30,
            "is_preview": False,
        }

        payload.update(overrides)
        return payload

    def test_manager_can_create_lesson(self):
        self.authenticate(self.manager)

        response = self.client.post(
            self.list_url,
            self.lesson_payload(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        lesson = Lesson.objects.get(
            slug="new-secure-lesson"
        )

        self.assertEqual(
            lesson.created_by,
            self.manager,
        )

        self.assertEqual(
            lesson.updated_by,
            self.manager,
        )

        self.assertEqual(
            lesson.module,
            self.module,
        )

        self.assertEqual(
            lesson.order,
            2,
        )

    def test_regular_member_cannot_create_lesson        (self):
        self.authenticate(self.member)

        response = self.client.post(
        self.list_url,
        self.lesson_payload(),
        format="json",
        )

        self.assertEqual(
        response.status_code,
        status.HTTP_403_FORBIDDEN,
        )

        self.assertFalse(
        Lesson.objects.filter(
            slug="new-secure-lesson",
        ).exists()
        )

    def test_outsider_cannot_create_lesson(self):
        self.authenticate(self.outsider)

        response = self.client.post(
        self.list_url,
        self.lesson_payload(),
        format="json",
        )

        self.assertEqual(
        response.status_code,
        status.HTTP_403_FORBIDDEN,
        )

        self.assertFalse(
        Lesson.objects.filter(
            slug="new-secure-lesson",
        ).exists()
        )

    def test_member_only_sees_lessons_in_own_organization(self):
        self.authenticate(self.member)

        response = self.client.get(self.list_url)

        self.assertEqual(
        response.status_code,
        status.HTTP_200_OK,
        )

        items = response.data.get(
        "results",
        response.data,
        )

        returned_ids = {
        item["id"]
        for item in items
        }

        self.assertIn(
        str(self.lesson.id),
        returned_ids,
        )

        self.assertNotIn(
        str(self.other_lesson.id),
        returned_ids,
        )

    def test_superuser_sees_lessons_across_organizations(self):
        self.authenticate(self.superuser)

        response = self.client.get(self.list_url)

        self.assertEqual(
        response.status_code,
        status.HTTP_200_OK,
        )

        items = response.data.get(
        "results",
        response.data,
        )

        returned_ids = {
        item["id"]
        for item in items
        }

        self.assertIn(
        str(self.lesson.id),
        returned_ids,
        )

        self.assertIn(
        str(self.other_lesson.id),
        returned_ids,
        )

    def test_manager_can_update_lesson_and_sets_updated_by(self):
        self.authenticate(self.manager)

        detail_url = reverse(
        "lesson-detail",
        args=[self.lesson.id],
        )

        response = self.client.patch(
        detail_url,
        {
            "title": "Updated Lesson",
        },
        format="json",
        )

        self.assertEqual(
        response.status_code,
        status.HTTP_200_OK,
        )

        self.lesson.refresh_from_db()

        self.assertEqual(
        self.lesson.title,
        "Updated Lesson",
        )

        self.assertEqual(
        self.lesson.updated_by,
        self.manager,
        )

    def test_regular_member_cannot_update_lesson(self):
        self.authenticate(self.member)

        detail_url = reverse(
            "lesson-detail",
            args=[self.lesson.id],
        )

        response = self.client.patch(
            detail_url,
            {
                "title": "Unauthorized Lesson Update",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.lesson.refresh_from_db()

        self.assertEqual(
            self.lesson.title,
            "Existing Lesson",
        )

        self.assertEqual(
            self.lesson.updated_by,
            self.manager,
        )

    def test_manager_cannot_change_module(self):
        self.authenticate(self.manager)

        detail_url = reverse(
            "lesson-detail",
            args=[self.lesson.id],
        )

        response = self.client.patch(
            detail_url,
            {
                "module_id": str(self.other_module.id),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.lesson.refresh_from_db()

        self.assertEqual(
            self.lesson.module,
            self.module,
        )

    def test_manager_can_delete_lesson(self):
        self.authenticate(self.manager)

        detail_url = reverse(
        "lesson-detail",
        args=[self.lesson.id],
        )

        response = self.client.delete(detail_url)

        self.assertEqual(
        response.status_code,
        status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(
        Lesson.objects.filter(
            id=self.lesson.id,
        ).exists()
        )

    def test_regular_member_cannot_delete_lesson(self):
        self.authenticate(self.member)

        detail_url = reverse(
        "lesson-detail",
        args=[self.lesson.id],
        )

        response = self.client.delete(detail_url)

        self.assertEqual(
        response.status_code,
        status.HTTP_403_FORBIDDEN,
        )

        self.assertTrue(
        Lesson.objects.filter(
            id=self.lesson.id,
        ).exists()
        )

class ActivityAPISecurityTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.manager = User.objects.create_user(
            username="activity_manager",
            email="activity_manager@example.com",
            password="StrongPass123!",
        )

        self.member = User.objects.create_user(
            username="activity_member",
            email="activity_member@example.com",
            password="StrongPass123!",
        )

        self.outsider = User.objects.create_user(
            username="activity_outsider",
            email="activity_outsider@example.com",
            password="StrongPass123!",
        )

        self.superuser = User.objects.create_superuser(
            username="activity_admin",
            email="activity_admin@example.com",
            password="StrongPass123!",
        )

        self.organization = Organization.objects.create(
            name="Activity Organization",
            slug="activity-organization-api",
        )

        self.other_organization = Organization.objects.create(
            name="Other Activity Organization",
            slug="other-activity-organization",
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
            name="Activity Academy",
            slug="activity-academy-api",
            created_by=self.manager,
            updated_by=self.manager,
        )

        self.other_academy = Academy.objects.create(
            organization=self.other_organization,
            name="Other Activity Academy",
            slug="other-activity-academy",
            created_by=self.manager,
            updated_by=self.manager,
        )

        self.program = Program.objects.create(
            organization=self.organization,
            academy=self.academy,
            name="Activity Program",
            slug="activity-program-api",
            created_by=self.manager,
            updated_by=self.manager,
        )

        self.other_program = Program.objects.create(
            organization=self.other_organization,
            academy=self.other_academy,
            name="Other Activity Program",
            slug="other-activity-program",
            created_by=self.manager,
            updated_by=self.manager,
        )

        self.course = Course.objects.create(
            organization=self.organization,
            academy=self.academy,
            program=self.program,
            title="Activity Course",
            slug="activity-course",
            created_by=self.manager,
            updated_by=self.manager,
        )

        self.other_course = Course.objects.create(
            organization=self.other_organization,
            academy=self.other_academy,
            program=self.other_program,
            title="Other Activity Course",
            slug="other-activity-course",
            created_by=self.manager,
            updated_by=self.manager,
        )

        self.module = Module.objects.create(
            course=self.course,
            title="Activity Module",
            slug="activity-module",
            order=1,
            created_by=self.manager,
            updated_by=self.manager,
        )

        self.other_module = Module.objects.create(
            course=self.other_course,
            title="Other Activity Module",
            slug="other-activity-module",
            order=1,
            created_by=self.manager,
            updated_by=self.manager,
        )

        self.lesson = Lesson.objects.create(
            module=self.module,
            title="Activity Lesson",
            slug="activity-lesson",
            order=1,
            created_by=self.manager,
            updated_by=self.manager,
        )

        self.other_lesson = Lesson.objects.create(
            module=self.other_module,
            title="Other Activity Lesson",
            slug="other-activity-lesson",
            order=1,
            created_by=self.manager,
            updated_by=self.manager,
        )

        self.list_url = reverse("activity-list")

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def activity_payload(self, **overrides):
        payload = {
        "lesson_id": str(self.lesson.id),
        "title": "New Secure Activity",
        "slug": "new-secure-activity",
        "description": "Secure activity content.",
        "activity_type": "article",
        "order": 1,
        "is_required": True,
        "points_possible": 10,
        "configuration": {},
        "status": "draft",
        }

        payload.update(overrides)
        return payload

    def test_manager_can_create_activity(self):
        self.authenticate(self.manager)

        response = self.client.post(
            self.list_url,
            self.activity_payload(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        activity = Activity.objects.get(
            title="New Secure Activity",
        )

        self.assertEqual(
            activity.lesson,
            self.lesson,
        )

        self.assertEqual(
            activity.created_by,
            self.manager,
        )

        self.assertEqual(
            activity.updated_by,
            self.manager,
        )

    def test_regular_member_cannot_create_activity(self):
        self.authenticate(self.member)

        response = self.client.post(
        reverse("activity-list"),
        self.activity_payload(),
        format="json",
        )

        self.assertEqual(
        response.status_code,
        status.HTTP_403_FORBIDDEN,
        )

        self.assertEqual(Activity.objects.count(), 0)

    def test_outsider_cannot_create_activity(self):
        self.authenticate(self.outsider)

        response = self.client.post(
        reverse("activity-list"),
        self.activity_payload(),
        format="json",
        )

        self.assertEqual(
        response.status_code,
        status.HTTP_403_FORBIDDEN,
        )

        self.assertEqual(Activity.objects.count(), 0)

    def test_manager_can_update_activity(self):
        activity = Activity.objects.create(
            lesson=self.lesson,
            title="Original Activity",
            slug="original-activity",
            activity_type=Activity.ActivityType.ARTICLE,
            order=1,
            created_by=self.manager,
            updated_by=self.manager,
        )

        self.authenticate(self.manager)

        response = self.client.patch(
            reverse("activity-detail", args=[activity.pk]),
            {
                "title": "Updated Activity",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        activity.refresh_from_db()

        self.assertEqual(
            activity.title,
            "Updated Activity",
        )

        self.assertEqual(
            activity.updated_by,
            self.manager,
        )    

    def test_member_cannot_update_activity(self):
        activity = Activity.objects.create(
        lesson=self.lesson,
        title="Original Activity",
        slug="original-activity",
        activity_type=Activity.ActivityType.ARTICLE,
        order=1,
        created_by=self.manager,
        updated_by=self.manager,
        )

        self.authenticate(self.member)

        response = self.client.patch(
        reverse("activity-detail", args=[activity.pk]),
        {
            "title": "Hacked Title",
        },
        format="json",
        )

        self.assertEqual(
        response.status_code,
        status.HTTP_403_FORBIDDEN,
        )

        activity.refresh_from_db()

        self.assertEqual(
        activity.title,
        "Original Activity",
        )

        self.assertEqual(
        activity.updated_by,
        self.manager,
        )

    def test_outsider_cannot_update_activity(self):
        activity = Activity.objects.create(
            lesson=self.lesson,
            title="Original Activity",
            slug="original-activity",
            activity_type=Activity.ActivityType.ARTICLE,
            order=1,
            created_by=self.manager,
            updated_by=self.manager,
        )

        self.authenticate(self.outsider)

        response = self.client.patch(
            reverse("activity-detail", args=[activity.pk]),
            {
                "title": "Hacked Title",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        activity.refresh_from_db()

        self.assertEqual(
            activity.title,
            "Original Activity",
        )

        self.assertEqual(
            activity.updated_by,
            self.manager,
        )    

    def test_manager_can_delete_activity(self):
        activity = Activity.objects.create(
            lesson=self.lesson,
            title="Delete Me",
            slug="delete-me",
            activity_type=Activity.ActivityType.ARTICLE,
            order=1,
            created_by=self.manager,
            updated_by=self.manager,
        )

        self.authenticate(self.manager)

        response = self.client.delete(
            reverse("activity-detail", args=[activity.pk])
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(
            Activity.objects.filter(
                id=activity.id,
            ).exists()
        )   

    def test_member_cannot_delete_activity(self):
        activity = Activity.objects.create(
            lesson=self.lesson,
            title="Delete Me",
            slug="delete-me",
            activity_type=Activity.ActivityType.ARTICLE,
            order=1,
            created_by=self.manager,
            updated_by=self.manager,
        )

        self.authenticate(self.member)

        response = self.client.delete(
            reverse("activity-detail", args=[activity.pk])
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.assertTrue(
            Activity.objects.filter(
                id=activity.id,
            ).exists()
        )

    def test_outsider_cannot_delete_activity(self):
        activity = Activity.objects.create(
            lesson=self.lesson,
            title="Delete Me",
            slug="delete-me",
            activity_type=Activity.ActivityType.ARTICLE,
            order=1,
            created_by=self.manager,
            updated_by=self.manager,
        )

        self.authenticate(self.outsider)

        response = self.client.delete(
            reverse("activity-detail", args=[activity.pk])
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        self.assertTrue(
            Activity.objects.filter(
                id=activity.id,
            ).exists()
        )