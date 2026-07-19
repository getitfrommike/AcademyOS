from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from businesses.models import EducationBusiness
from organizations.models import (
    Organization,
    OrganizationMembership,
)

from .models import Academy


class AcademySecurityTests(TestCase):
    def setUp(self):
        User = get_user_model()

        self.owner = User.objects.create_user(
            username="academy-owner",
            email="academy-owner@example.com",
            password="safe-password-123",
        )
        self.student = User.objects.create_user(
            username="academy-student",
            email="academy-student@example.com",
            password="safe-password-123",
        )
        self.outsider = User.objects.create_user(
            username="academy-outsider",
            email="academy-outsider@example.com",
            password="safe-password-123",
        )
        self.other_owner = User.objects.create_user(
            username="other-academy-owner",
            email="other-academy-owner@example.com",
            password="safe-password-123",
        )

        self.organization = Organization.objects.create(
            name="Academy Organization",
            slug="academy-organization",
        )
        self.other_organization = Organization.objects.create(
            name="Other Academy Organization",
            slug="other-academy-organization",
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

        self.business = EducationBusiness.objects.create(
            organization=self.organization,
            name="Academy Business",
            slug="academy-business",
            business_type="online_academy",
            created_by=self.owner,
            updated_by=self.owner,
        )
        self.other_business = EducationBusiness.objects.create(
            organization=self.other_organization,
            name="Other Academy Business",
            slug="other-academy-business",
            business_type="custom",
            created_by=self.other_owner,
            updated_by=self.other_owner,
        )

        self.academy = Academy.objects.create(
            organization=self.organization,
            business=self.business,
            name="Cyber Academy",
            slug="cyber-academy",
            created_by=self.owner,
            updated_by=self.owner,
        )
        self.other_academy = Academy.objects.create(
            organization=self.other_organization,
            business=self.other_business,
            name="Other Cyber Academy",
            slug="other-cyber-academy",
            created_by=self.other_owner,
            updated_by=self.other_owner,
        )

        self.client = APIClient()

    def academy_payload(self, **overrides):
        payload = {
            "organization_id": str(self.organization.id),
            "business_id": str(self.business.id),
            "name": "Second Academy",
            "slug": "second-academy",
            "description": "A secure learning environment.",
            "logo_url": "https://example.com/logo.png",
            "primary_color": "#111111",
            "secondary_color": "#FFD700",
            "custom_domain": "academy.example.com",
            "is_public": False,
            "is_active": True,
        }
        payload.update(overrides)
        return payload

    def test_outsider_cannot_retrieve_academy(self):
        self.client.force_authenticate(self.outsider)

        response = self.client.get(
            f"/api/academies/{self.academy.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_outsider_cannot_see_academy_in_list(self):
        self.client.force_authenticate(self.outsider)

        response = self.client.get("/api/academies/")

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        data = response.json()

        if isinstance(data, dict):
            items = data.get("results", [])
        else:
            items = data

        returned_ids = {
            item["id"]
            for item in items
        }

        self.assertNotIn(
            str(self.academy.id),
            returned_ids,
        )

    def test_owner_cannot_retrieve_other_tenant_academy(self):
        self.client.force_authenticate(self.owner)

        response = self.client.get(
            f"/api/academies/{self.other_academy.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_owner_can_create_academy(self):
        self.client.force_authenticate(self.owner)

        response = self.client.post(
            "/api/academies/",
            self.academy_payload(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertEqual(
            response.json()["organization"],
            str(self.organization.id),
        )
        self.assertEqual(
            response.json()["business"],
            str(self.business.id),
        )

        academy = Academy.objects.get(
            slug="second-academy"
        )

        self.assertEqual(
            academy.organization,
            self.organization,
        )
        self.assertEqual(
            academy.business,
            self.business,
        )
        self.assertEqual(
            academy.created_by,
            self.owner,
        )
        self.assertEqual(
            academy.updated_by,
            self.owner,
        )

    def test_owner_can_create_academy_without_business(self):
        self.client.force_authenticate(self.owner)

        response = self.client.post(
            "/api/academies/",
            self.academy_payload(
                business_id=None,
                name="Independent Academy",
                slug="independent-academy",
            ),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        academy = Academy.objects.get(
            slug="independent-academy"
        )

        self.assertIsNone(academy.business)

    def test_student_cannot_create_academy(self):
        self.client.force_authenticate(self.student)

        response = self.client.post(
            "/api/academies/",
            self.academy_payload(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertFalse(
            Academy.objects.filter(
                slug="second-academy"
            ).exists()
        )

    def test_invalid_organization_id_returns_400(self):
        self.client.force_authenticate(self.owner)

        response = self.client.post(
            "/api/academies/",
            self.academy_payload(
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

    def test_missing_organization_id_returns_400(self):
        self.client.force_authenticate(self.owner)

        payload = self.academy_payload()
        payload.pop("organization_id")

        response = self.client.post(
            "/api/academies/",
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

    def test_inactive_organization_rejected(self):
        inactive_organization = Organization.objects.create(
            name="Inactive Academy Organization",
            slug="inactive-academy-organization",
            is_active=False,
        )

        OrganizationMembership.objects.create(
            organization=inactive_organization,
            user=self.owner,
            role="owner",
        )

        self.client.force_authenticate(self.owner)

        response = self.client.post(
            "/api/academies/",
            self.academy_payload(
                organization_id=str(inactive_organization.id),
                business_id=None,
                name="Inactive Academy",
                slug="inactive-academy",
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

    def test_invalid_business_id_returns_400(self):
        self.client.force_authenticate(self.owner)

        response = self.client.post(
            "/api/academies/",
            self.academy_payload(
                business_id="not-a-valid-uuid",
            ),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            "business_id",
            response.json(),
        )

    def test_business_from_other_organization_rejected(self):
        self.client.force_authenticate(self.owner)

        response = self.client.post(
            "/api/academies/",
            self.academy_payload(
                business_id=str(self.other_business.id),
            ),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            "business_id",
            response.json(),
        )

    def test_inactive_business_rejected(self):
        self.business.is_active = False
        self.business.save()

        self.client.force_authenticate(self.owner)

        response = self.client.post(
            "/api/academies/",
            self.academy_payload(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            "business_id",
            response.json(),
        )

    def test_owner_can_update_academy(self):
        self.client.force_authenticate(self.owner)

        response = self.client.patch(
            f"/api/academies/{self.academy.id}/",
            {
                "name": "Updated Cyber Academy",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.academy.refresh_from_db()

        self.assertEqual(
            self.academy.name,
            "Updated Cyber Academy",
        )
        self.assertEqual(
            self.academy.updated_by,
            self.owner,
        )

    def test_student_cannot_update_academy(self):
        self.client.force_authenticate(self.student)

        response = self.client.patch(
            f"/api/academies/{self.academy.id}/",
            {
                "name": "Unauthorized Academy Update",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.academy.refresh_from_db()

        self.assertEqual(
            self.academy.name,
            "Cyber Academy",
        )

    def test_owner_can_delete_academy(self):
        self.client.force_authenticate(self.owner)

        response = self.client.delete(
            f"/api/academies/{self.academy.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )
        self.assertFalse(
            Academy.objects.filter(
                id=self.academy.id
            ).exists()
        )

    def test_student_cannot_delete_academy(self):
        self.client.force_authenticate(self.student)

        response = self.client.delete(
            f"/api/academies/{self.academy.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertTrue(
            Academy.objects.filter(
                id=self.academy.id
            ).exists()
        )

    def test_organization_cannot_be_changed(self):
        self.client.force_authenticate(self.owner)

        response = self.client.patch(
            f"/api/academies/{self.academy.id}/",
            {
                "organization_id": str(
                    self.other_organization.id
                ),
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

        self.academy.refresh_from_db()

        self.assertEqual(
            self.academy.organization,
            self.organization,
        )

    def test_business_cannot_be_changed(self):
        self.client.force_authenticate(self.owner)

        response = self.client.patch(
            f"/api/academies/{self.academy.id}/",
            {
                "business_id": str(
                    self.other_business.id
                ),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            "business_id",
            response.json(),
        )

        self.academy.refresh_from_db()

        self.assertEqual(
            self.academy.business,
            self.business,
        )

    def test_slug_is_normalized_to_lowercase(self):
        self.client.force_authenticate(self.owner)

        response = self.client.post(
            "/api/academies/",
            self.academy_payload(
                name="Normalized Academy",
                slug="  Normalized-Academy  ",
            ),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        academy = Academy.objects.get(
            name="Normalized Academy"
        )

        self.assertEqual(
            academy.slug,
            "normalized-academy",
        )

    def test_academy_name_is_trimmed(self):
        self.client.force_authenticate(self.owner)

        response = self.client.post(
            "/api/academies/",
            self.academy_payload(
                name="  Trimmed Academy  ",
                slug="trimmed-academy",
            ),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        academy = Academy.objects.get(
            slug="trimmed-academy"
        )

        self.assertEqual(
            academy.name,
            "Trimmed Academy",
        )
