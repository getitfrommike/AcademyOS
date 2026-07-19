from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from academies.models import Academy
from organizations.models import (
    Organization,
    OrganizationMembership,
)

from .models import Program


class ProgramSecurityTests(TestCase):
    def setUp(self):
        User = get_user_model()

        self.owner = User.objects.create_user(
            username="program-owner",
            email="program-owner@example.com",
            password="safe-password-123",
        )
        self.student = User.objects.create_user(
            username="program-student",
            email="program-student@example.com",
            password="safe-password-123",
        )
        self.outsider = User.objects.create_user(
            username="program-outsider",
            email="program-outsider@example.com",
            password="safe-password-123",
        )
        self.other_owner = User.objects.create_user(
            username="other-program-owner",
            email="other-program-owner@example.com",
            password="safe-password-123",
        )

        self.organization = Organization.objects.create(
            name="Program Organization",
            slug="program-organization",
        )
        self.other_organization = Organization.objects.create(
            name="Other Program Organization",
            slug="other-program-organization",
        )

        OrganizationMembership.objects.create(
            organization=self.organization,
            user=self.owner,
            role="owner",
        )
        OrganizationMembership.objects.create(
            organization=self.organization,
            user=self.student,
            role="student",
        )
        OrganizationMembership.objects.create(
            organization=self.other_organization,
            user=self.other_owner,
            role="owner",
        )

        self.academy = Academy.objects.create(
            organization=self.organization,
            name="Technology Academy",
            slug="technology-academy",
            created_by=self.owner,
            updated_by=self.owner,
        )
        self.other_academy = Academy.objects.create(
            organization=self.other_organization,
            name="Other Technology Academy",
            slug="other-technology-academy",
            created_by=self.other_owner,
            updated_by=self.other_owner,
        )

        self.program = Program.objects.create(
            organization=self.organization,
            academy=self.academy,
            name="Cybersecurity Program",
            slug="cybersecurity-program",
            short_description="Learn secure systems.",
            status=Program.Status.DRAFT,
            created_by=self.owner,
            updated_by=self.owner,
        )
        self.other_program = Program.objects.create(
            organization=self.other_organization,
            academy=self.other_academy,
            name="Other Cybersecurity Program",
            slug="other-cybersecurity-program",
            status=Program.Status.DRAFT,
            created_by=self.other_owner,
            updated_by=self.other_owner,
        )

        self.client = APIClient()

    def program_payload(self, **overrides):
        payload = {
            "organization_id": str(self.organization.id),
            "academy_id": str(self.academy.id),
            "name": "Python Developer Program",
            "slug": "python-developer-program",
            "short_description": "Become a Python developer.",
            "description": "A complete Python development program.",
            "status": Program.Status.DRAFT,
            "is_featured": False,
        }
        payload.update(overrides)
        return payload

    def response_items(self, response):
        data = response.json()

        if isinstance(data, dict):
            return data.get("results", [])

        return data

    def test_owner_can_list_own_programs(self):
        self.client.force_authenticate(self.owner)

        response = self.client.get("/api/programs/")

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        returned_ids = {
            item["id"]
            for item in self.response_items(response)
        }

        self.assertIn(str(self.program.id), returned_ids)
        self.assertNotIn(
            str(self.other_program.id),
            returned_ids,
        )

    def test_outsider_cannot_retrieve_program(self):
        self.client.force_authenticate(self.outsider)

        response = self.client.get(
            f"/api/programs/{self.program.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_owner_cannot_retrieve_other_tenant_program(self):
        self.client.force_authenticate(self.owner)

        response = self.client.get(
            f"/api/programs/{self.other_program.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_owner_can_create_program(self):
        self.client.force_authenticate(self.owner)

        response = self.client.post(
            "/api/programs/",
            self.program_payload(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        data = response.json()

        self.assertEqual(
            data["organization"],
            str(self.organization.id),
        )
        self.assertEqual(
            data["academy"],
            str(self.academy.id),
        )

        program = Program.objects.get(
            slug="python-developer-program"
        )

        self.assertEqual(
            program.organization,
            self.organization,
        )
        self.assertEqual(
            program.academy,
            self.academy,
        )
        self.assertEqual(program.created_by, self.owner)
        self.assertEqual(program.updated_by, self.owner)

    def test_student_cannot_create_program(self):
        self.client.force_authenticate(self.student)

        response = self.client.post(
            "/api/programs/",
            self.program_payload(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertFalse(
            Program.objects.filter(
                slug="python-developer-program"
            ).exists()
        )

    def test_missing_organization_id_returns_400(self):
        self.client.force_authenticate(self.owner)

        payload = self.program_payload()
        payload.pop("organization_id")

        response = self.client.post(
            "/api/programs/",
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            "organization_id",
            response.json(),
        )

    def test_invalid_organization_id_returns_400(self):
        self.client.force_authenticate(self.owner)

        response = self.client.post(
            "/api/programs/",
            self.program_payload(
                organization_id="not-a-valid-uuid",
            ),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            "organization_id",
            response.json(),
        )

    def test_inactive_organization_is_rejected(self):
        inactive_organization = Organization.objects.create(
            name="Inactive Program Organization",
            slug="inactive-program-organization",
            is_active=False,
        )

        inactive_academy = Academy.objects.create(
            organization=inactive_organization,
            name="Inactive Academy",
            slug="inactive-academy",
            created_by=self.owner,
            updated_by=self.owner,
        )

        OrganizationMembership.objects.create(
            organization=inactive_organization,
            user=self.owner,
            role="owner",
        )

        self.client.force_authenticate(self.owner)

        response = self.client.post(
            "/api/programs/",
            self.program_payload(
                organization_id=str(
                    inactive_organization.id
                ),
                academy_id=str(inactive_academy.id),
                name="Inactive Organization Program",
                slug="inactive-organization-program",
            ),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            "organization_id",
            response.json(),
        )

    def test_missing_academy_id_returns_400(self):
        self.client.force_authenticate(self.owner)

        payload = self.program_payload()
        payload.pop("academy_id")

        response = self.client.post(
            "/api/programs/",
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            "academy_id",
            response.json(),
        )

    def test_invalid_academy_id_returns_400(self):
        self.client.force_authenticate(self.owner)

        response = self.client.post(
            "/api/programs/",
            self.program_payload(
                academy_id="not-a-valid-uuid",
            ),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            "academy_id",
            response.json(),
        )

    def test_other_organization_academy_is_rejected(self):
        self.client.force_authenticate(self.owner)

        response = self.client.post(
            "/api/programs/",
            self.program_payload(
                academy_id=str(self.other_academy.id),
            ),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            "academy_id",
            response.json(),
        )

    def test_inactive_academy_is_rejected(self):
        self.academy.is_active = False
        self.academy.save()

        self.client.force_authenticate(self.owner)

        response = self.client.post(
            "/api/programs/",
            self.program_payload(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            "academy_id",
            response.json(),
        )

    def test_owner_can_update_program(self):
        self.client.force_authenticate(self.owner)

        response = self.client.patch(
            f"/api/programs/{self.program.id}/",
            {
                "name": "Updated Cybersecurity Program",
                "status": Program.Status.PUBLISHED,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.program.refresh_from_db()

        self.assertEqual(
            self.program.name,
            "Updated Cybersecurity Program",
        )
        self.assertEqual(
            self.program.status,
            Program.Status.PUBLISHED,
        )
        self.assertEqual(
            self.program.updated_by,
            self.owner,
        )

    def test_student_cannot_update_program(self):
        self.client.force_authenticate(self.student)

        response = self.client.patch(
            f"/api/programs/{self.program.id}/",
            {
                "name": "Unauthorized Program Update",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.program.refresh_from_db()

        self.assertEqual(
            self.program.name,
            "Cybersecurity Program",
        )

    def test_organization_cannot_be_changed(self):
        self.client.force_authenticate(self.owner)

        response = self.client.patch(
            f"/api/programs/{self.program.id}/",
            {
                "organization_id": str(
                    self.other_organization.id
                )
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            "organization_id",
            response.json(),
        )

        self.program.refresh_from_db()

        self.assertEqual(
            self.program.organization,
            self.organization,
        )

    def test_academy_cannot_be_changed(self):
        self.client.force_authenticate(self.owner)

        response = self.client.patch(
            f"/api/programs/{self.program.id}/",
            {
                "academy_id": str(self.other_academy.id),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            "academy_id",
            response.json(),
        )

        self.program.refresh_from_db()

        self.assertEqual(
            self.program.academy,
            self.academy,
        )

    def test_owner_can_delete_program(self):
        self.client.force_authenticate(self.owner)

        response = self.client.delete(
            f"/api/programs/{self.program.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )
        self.assertFalse(
            Program.objects.filter(
                id=self.program.id
            ).exists()
        )

    def test_student_cannot_delete_program(self):
        self.client.force_authenticate(self.student)

        response = self.client.delete(
            f"/api/programs/{self.program.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertTrue(
            Program.objects.filter(
                id=self.program.id
            ).exists()
        )

    def test_program_name_is_trimmed(self):
        self.client.force_authenticate(self.owner)

        response = self.client.post(
            "/api/programs/",
            self.program_payload(
                name="  AI Business Program  ",
                slug="ai-business-program",
            ),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        program = Program.objects.get(
            slug="ai-business-program"
        )

        self.assertEqual(
            program.name,
            "AI Business Program",
        )

    def test_program_slug_is_normalized(self):
        self.client.force_authenticate(self.owner)

        response = self.client.post(
            "/api/programs/",
            self.program_payload(
                name="Normalized Program",
                slug="  Normalized-Program  ",
            ),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        program = Program.objects.get(
            name="Normalized Program"
        )

        self.assertEqual(
            program.slug,
            "normalized-program",
        )

    def test_short_description_is_trimmed(self):
        self.client.force_authenticate(self.owner)

        response = self.client.post(
            "/api/programs/",
            self.program_payload(
                name="Description Program",
                slug="description-program",
                short_description=(
                    "  A useful program description.  "
                ),
            ),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        program = Program.objects.get(
            slug="description-program"
        )

        self.assertEqual(
            program.short_description,
            "A useful program description.",
        )