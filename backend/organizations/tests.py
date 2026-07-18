from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from .models import Organization, OrganizationMembership


class TenantIsolationTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.alice = User.objects.create_user(username="alice", email="alice@example.com", password="safe-password-123")
        self.bob = User.objects.create_user(username="bob", email="bob@example.com", password="safe-password-123")
        self.org_a = Organization.objects.create(name="Alpha", slug="alpha")
        self.org_b = Organization.objects.create(name="Beta", slug="beta")
        OrganizationMembership.objects.create(organization=self.org_a, user=self.alice, role="owner")
        OrganizationMembership.objects.create(organization=self.org_b, user=self.bob, role="owner")
        self.client = APIClient()

    def test_user_only_lists_their_organizations(self):
        self.client.force_authenticate(self.alice)
        response = self.client.get("/api/organizations/")
        self.assertEqual(response.status_code, 200)
        ids = {item["id"] for item in response.json()["results"]}
        self.assertEqual(ids, {str(self.org_a.id)})

    def test_user_cannot_retrieve_another_organization(self):
        self.client.force_authenticate(self.alice)
        response = self.client.get(f"/api/organizations/{self.org_b.id}/")
        self.assertEqual(response.status_code, 404)

    def test_new_organization_makes_creator_owner(self):
        self.client.force_authenticate(self.alice)
        response = self.client.post("/api/organizations/", {"name": "New Org", "slug": "new-org"}, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertTrue(OrganizationMembership.objects.filter(user=self.alice, organization_id=response.json()["id"], role="owner").exists())
