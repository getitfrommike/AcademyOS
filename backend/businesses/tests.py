from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from organizations.models import Organization, OrganizationMembership
from .models import EducationBusiness


class EducationBusinessSecurityTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.owner = User.objects.create_user(username="owner", email="owner@example.com", password="safe-password-123")
        self.outsider = User.objects.create_user(username="outsider", email="outsider@example.com", password="safe-password-123")
        self.organization = Organization.objects.create(name="Secure Academy Co", slug="secure-academy-co")
        OrganizationMembership.objects.create(organization=self.organization, user=self.owner, role="owner")
        self.business = EducationBusiness.objects.create(organization=self.organization, name="Cyber Academy", slug="cyber-academy", business_type="online_academy")
        self.client = APIClient()

    def test_outsider_cannot_see_business(self):
        self.client.force_authenticate(self.outsider)
        response = self.client.get(f"/api/businesses/{self.business.id}/")
        self.assertEqual(response.status_code, 404)

    def test_owner_can_create_business_for_organization(self):
        self.client.force_authenticate(self.owner)
        response = self.client.post("/api/businesses/", {"organization_id": str(self.organization.id), "name": "Second Academy", "slug": "second-academy", "business_type": "custom"}, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["organization"], str(self.organization.id))
