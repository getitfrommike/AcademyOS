from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from .models import Organization, OrganizationMembership


class OrganizationSecurityTests(TestCase):
    password = "safe-password-123"

    def setUp(self):
        User = get_user_model()

        self.alice = User.objects.create_user(
            username="alice",
            email="alice@example.com",
            password=self.password,
        )
        self.bob = User.objects.create_user(
            username="bob",
            email="bob@example.com",
            password=self.password,
        )
        self.admin_user = User.objects.create_user(
            username="admin-user",
            email="admin@example.com",
            password=self.password,
        )
        self.student = User.objects.create_user(
            username="student",
            email="student@example.com",
            password=self.password,
        )
        self.replacement_user = User.objects.create_user(
            username="replacement",
            email="replacement@example.com",
            password=self.password,
        )
        self.inactive_user = User.objects.create_user(
            username="inactive-user",
            email="inactive@example.com",
            password=self.password,
            is_active=False,
        )
        self.superuser = User.objects.create_superuser(
            username="superuser",
            email="superuser@example.com",
            password=self.password,
        )

        self.org_a = Organization.objects.create(
            name="Alpha",
            slug="alpha",
        )
        self.org_b = Organization.objects.create(
            name="Beta",
            slug="beta",
        )

        self.alice_membership = OrganizationMembership.objects.create(
            organization=self.org_a,
            user=self.alice,
            role=OrganizationMembership.Role.OWNER,
            is_active=True,
        )
        self.bob_membership = OrganizationMembership.objects.create(
            organization=self.org_b,
            user=self.bob,
            role=OrganizationMembership.Role.OWNER,
            is_active=True,
        )
        self.admin_membership = OrganizationMembership.objects.create(
            organization=self.org_a,
            user=self.admin_user,
            role=OrganizationMembership.Role.ADMINISTRATOR,
            is_active=True,
        )
        self.student_membership = OrganizationMembership.objects.create(
            organization=self.org_a,
            user=self.student,
            role=OrganizationMembership.Role.STUDENT,
            is_active=True,
        )

        self.client = APIClient()

    @staticmethod
    def response_items(response):
        """
        Return results from either paginated or non-paginated API responses.
        """
        response_data = response.json()

        if isinstance(response_data, dict) and "results" in response_data:
            return response_data["results"]

        return response_data

    def membership_list_url(self, organization):
        return reverse(
            "organization-memberships",
            kwargs={"organization_pk": organization.pk},
        )

    def membership_detail_url(self, organization, membership):
        return reverse(
            "organization-membership-detail",
            kwargs={
                "organization_pk": organization.pk,
                "pk": membership.pk,
            },
        )

    def test_user_only_lists_their_organizations(self):
        self.client.force_authenticate(self.alice)

        response = self.client.get(
            reverse("organization-list"),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        organization_ids = {
            str(item["id"])
            for item in self.response_items(response)
        }

        self.assertEqual(
            organization_ids,
            {str(self.org_a.id)},
        )

    def test_user_cannot_retrieve_another_organization(self):
        self.client.force_authenticate(self.alice)

        response = self.client.get(
            reverse(
                "organization-detail",
                kwargs={"pk": self.org_b.pk},
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_new_organization_makes_creator_owner(self):
        self.client.force_authenticate(self.alice)

        response = self.client.post(
            reverse("organization-list"),
            {
                "name": "New Org",
                "slug": "new-org",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertTrue(
            OrganizationMembership.objects.filter(
                user=self.alice,
                organization_id=response.json()["id"],
                role=OrganizationMembership.Role.OWNER,
                is_active=True,
            ).exists()
        )

    def test_manager_cannot_view_another_organizations_memberships(self):
        """
        An owner or administrator in Organization A must not receive
        membership records belonging to Organization B.
        """
        self.client.force_authenticate(self.alice)

        response = self.client.get(
            self.membership_list_url(self.org_b),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            self.response_items(response),
            [],
        )

    def test_administrator_cannot_promote_themselves_to_owner(self):
        self.client.force_authenticate(self.admin_user)

        response = self.client.patch(
            self.membership_detail_url(
                self.org_a,
                self.admin_membership,
            ),
            {
                "role": OrganizationMembership.Role.OWNER,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.admin_membership.refresh_from_db()

        self.assertEqual(
            self.admin_membership.role,
            OrganizationMembership.Role.ADMINISTRATOR,
        )

    def test_last_active_owner_cannot_be_deleted(self):
        self.client.force_authenticate(self.alice)

        response = self.client.delete(
            self.membership_detail_url(
                self.org_a,
                self.alice_membership,
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertTrue(
            OrganizationMembership.objects.filter(
                pk=self.alice_membership.pk,
            ).exists()
        )

    def test_last_active_owner_cannot_be_demoted(self):
        self.client.force_authenticate(self.alice)

        response = self.client.patch(
            self.membership_detail_url(
                self.org_a,
                self.alice_membership,
            ),
            {
                "role": OrganizationMembership.Role.ADMINISTRATOR,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.alice_membership.refresh_from_db()

        self.assertEqual(
            self.alice_membership.role,
            OrganizationMembership.Role.OWNER,
        )
        self.assertTrue(self.alice_membership.is_active)

    def test_membership_cannot_be_moved_to_another_organization(self):
        self.client.force_authenticate(self.alice)

        response = self.client.patch(
            self.membership_detail_url(
                self.org_a,
                self.student_membership,
            ),
            {
                "organization": str(self.org_b.pk),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.student_membership.refresh_from_db()

        self.assertEqual(
            self.student_membership.organization_id,
            self.org_a.id,
        )

    def test_existing_membership_user_cannot_be_changed(self):
        self.client.force_authenticate(self.alice)

        response = self.client.patch(
            self.membership_detail_url(
                self.org_a,
                self.student_membership,
            ),
            {
                "user": str(self.replacement_user.pk),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.student_membership.refresh_from_db()

        self.assertEqual(
            self.student_membership.user_id,
            self.student.id,
        )

    def test_inactive_user_cannot_be_added_to_organization(self):
        self.client.force_authenticate(self.alice)

        response = self.client.post(
            self.membership_list_url(self.org_a),
            {
                "user": str(self.inactive_user.pk),
                "role": OrganizationMembership.Role.STUDENT,
                "is_active": True,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertFalse(
            OrganizationMembership.objects.filter(
                organization=self.org_a,
                user=self.inactive_user,
            ).exists()
        )

    def test_superuser_can_view_organization_memberships(self):
        self.client.force_authenticate(self.superuser)

        response = self.client.get(
            self.membership_list_url(self.org_b),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        membership_ids = {
            str(item["id"])
            for item in self.response_items(response)
        }

        self.assertIn(
            str(self.bob_membership.id),
            membership_ids,
        )

    def test_student_cannot_access_membership_management(self):
        self.client.force_authenticate(self.student)

        response = self.client.get(
            self.membership_list_url(self.org_a),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            self.response_items(response),
            [],
        )