from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from organizations.models import (
    Organization,
    OrganizationMembership,
)

from .models import EducationBusiness


class EducationBusinessSecurityTests(TestCase):
    def setUp(self):
        User = get_user_model()

        self.owner = User.objects.create_user(
            username="owner",
            email="owner@example.com",
            password="safe-password-123",
        )
        self.student = User.objects.create_user(
            username="student",
            email="student@example.com",
            password="safe-password-123",
        )
        self.outsider = User.objects.create_user(
            username="outsider",
            email="outsider@example.com",
            password="safe-password-123",
        )
        self.other_owner = User.objects.create_user(
            username="other-owner",
            email="other-owner@example.com",
            password="safe-password-123",
        )

        self.organization = Organization.objects.create(
            name="Secure Academy Co",
            slug="secure-academy-co",
        )
        self.other_organization = Organization.objects.create(
            name="Other Academy Co",
            slug="other-academy-co",
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
            name="Cyber Academy",
            slug="cyber-academy",
            business_type="online_academy",
            created_by=self.owner,
            updated_by=self.owner,
        )
        self.other_business = EducationBusiness.objects.create(
            organization=self.other_organization,
            name="Other Business",
            slug="other-business",
            business_type="custom",
            created_by=self.other_owner,
            updated_by=self.other_owner,
        )

        self.client = APIClient()

    def business_payload(self, **overrides):
        payload = {
            "organization_id": str(self.organization.id),
            "name": "Second Academy",
            "slug": "second-academy",
            "business_type": "custom",
            "delivery_model": {},
            "revenue_model": {},
            "blueprint": {},
        }
        payload.update(overrides)
        return payload

    def test_outsider_cannot_retrieve_business(self):
        self.client.force_authenticate(self.outsider)

        response = self.client.get(
            f"/api/businesses/{self.business.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_outsider_cannot_see_business_in_list(self):
        self.client.force_authenticate(self.outsider)

        response = self.client.get("/api/businesses/")

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
            str(self.business.id),
            returned_ids,
        )

    def test_owner_cannot_retrieve_other_tenant_business(self):
        self.client.force_authenticate(self.owner)

        response = self.client.get(
            f"/api/businesses/{self.other_business.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_owner_can_create_business_for_organization(self):
        self.client.force_authenticate(self.owner)

        response = self.client.post(
            "/api/businesses/",
            self.business_payload(),
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

        business = EducationBusiness.objects.get(
            slug="second-academy"
        )

        self.assertEqual(
            business.organization,
            self.organization,
        )
        self.assertEqual(
            business.created_by,
            self.owner,
        )
        self.assertEqual(
            business.updated_by,
            self.owner,
        )

    def test_student_cannot_create_business(self):
        self.client.force_authenticate(self.student)

        response = self.client.post(
            "/api/businesses/",
            self.business_payload(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertFalse(
            EducationBusiness.objects.filter(
                slug="second-academy"
            ).exists()
        )

    def test_invalid_organization_id_returns_400(self):
        self.client.force_authenticate(self.owner)

        response = self.client.post(
            "/api/businesses/",
            self.business_payload(
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

        payload = self.business_payload()
        payload.pop("organization_id")

        response = self.client.post(
            "/api/businesses/",
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

    def test_business_cannot_be_created_in_inactive_organization(self):
        inactive_organization = Organization.objects.create(
            name="Inactive Academy",
            slug="inactive-academy",
            is_active=False,
        )
        OrganizationMembership.objects.create(
            organization=inactive_organization,
            user=self.owner,
            role="owner",
        )

        self.client.force_authenticate(self.owner)

        response = self.client.post(
            "/api/businesses/",
            self.business_payload(
                organization_id=str(inactive_organization.id),
                slug="inactive-business",
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

    def test_owner_can_update_business(self):
        self.client.force_authenticate(self.owner)

        response = self.client.patch(
            f"/api/businesses/{self.business.id}/",
            {
                "name": "Updated Cyber Academy",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.business.refresh_from_db()

        self.assertEqual(
            self.business.name,
            "Updated Cyber Academy",
        )
        self.assertEqual(
            self.business.updated_by,
            self.owner,
        )

    def test_student_cannot_update_business(self):
        self.client.force_authenticate(self.student)

        response = self.client.patch(
            f"/api/businesses/{self.business.id}/",
            {
                "name": "Unauthorized Update",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.business.refresh_from_db()

        self.assertEqual(
            self.business.name,
            "Cyber Academy",
        )

    def test_owner_can_delete_business(self):
        self.client.force_authenticate(self.owner)

        response = self.client.delete(
            f"/api/businesses/{self.business.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )
        self.assertFalse(
            EducationBusiness.objects.filter(
                id=self.business.id
            ).exists()
        )

    def test_student_cannot_delete_business(self):
        self.client.force_authenticate(self.student)

        response = self.client.delete(
            f"/api/businesses/{self.business.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertTrue(
            EducationBusiness.objects.filter(
                id=self.business.id
            ).exists()
        )

    def test_business_organization_cannot_be_changed(self):
        self.client.force_authenticate(self.owner)

        response = self.client.patch(
            f"/api/businesses/{self.business.id}/",
            {
                "organization": str(
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
            "organization",
            response.json(),
        )

        self.business.refresh_from_db()

        self.assertEqual(
            self.business.organization,
            self.organization,
        )

    def test_slug_is_normalized_to_lowercase(self):
        self.client.force_authenticate(self.owner)

        response = self.client.post(
            "/api/businesses/",
            self.business_payload(
                name="Normalized Academy",
                slug="  Normalized-Academy  ",
            ),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        business = EducationBusiness.objects.get(
            name="Normalized Academy"
        )

        self.assertEqual(
            business.slug,
            "normalized-academy",
        )

    def test_business_name_is_trimmed(self):
        self.client.force_authenticate(self.owner)

        response = self.client.post(
            "/api/businesses/",
            self.business_payload(
                name="  Trimmed Academy  ",
                slug="trimmed-academy",
            ),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        business = EducationBusiness.objects.get(
            slug="trimmed-academy"
        )

        self.assertEqual(
            business.name,
            "Trimmed Academy",
        )

    def test_structured_json_fields_reject_non_objects(self):
        self.client.force_authenticate(self.owner)

        invalid_fields = (
            "delivery_model",
            "revenue_model",
            "blueprint",
        )

        for index, field_name in enumerate(invalid_fields):
            with self.subTest(field=field_name):
                response = self.client.post(
                    "/api/businesses/",
                    self.business_payload(
                        name=f"Invalid JSON Academy {index}",
                        slug=f"invalid-json-academy-{index}",
                        **{
                            field_name: [
                                "not",
                                "an",
                                "object",
                            ]
                        },
                    ),
                    format="json",
                )

                self.assertEqual(
                    response.status_code,
                    status.HTTP_400_BAD_REQUEST,
                )
                self.assertIn(
                    field_name,
                    response.json(),
                )

    def test_valid_json_objects_are_accepted(self):
        self.client.force_authenticate(self.owner)

        response = self.client.post(
            "/api/businesses/",
            self.business_payload(
                name="Structured Academy",
                slug="structured-academy",
                delivery_model={
                    "format": "online",
                    "live_sessions": True,
                },
                revenue_model={
                    "type": "subscription",
                    "monthly_price": 49,
                },
                blueprint={
                    "phase": "launch",
                },
            ),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        business = EducationBusiness.objects.get(
            slug="structured-academy"
        )

        self.assertEqual(
            business.delivery_model["format"],
            "online",
        )
        self.assertEqual(
            business.revenue_model["monthly_price"],
            49,
        )
        self.assertEqual(
            business.blueprint["phase"],
            "launch",
        )