from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from academies.api import AcademyViewSet
from businesses.api import EducationBusinessViewSet
from organizations.api import MembershipViewSet, OrganizationViewSet

router = DefaultRouter()
router.register("organizations", OrganizationViewSet, basename="organization")
router.register("businesses", EducationBusinessViewSet, basename="business")
router.register("academies", AcademyViewSet, basename="academy")


def health(request):
    return JsonResponse({"status": "ok", "service": "AcademyOS"})


urlpatterns = [
    path("health/", health, name="health"),
    path("admin/", admin.site.urls),
    path("api/auth/", include("rest_framework.urls")),
    path("api/", include(router.urls)),
    path(
        "api/organizations/<uuid:organization_pk>/memberships/",
        MembershipViewSet.as_view({"get": "list", "post": "create"}),
        name="organization-memberships",
    ),
    path(
        "api/organizations/<uuid:organization_pk>/memberships/<uuid:pk>/",
        MembershipViewSet.as_view({"patch": "partial_update", "delete": "destroy"}),
        name="organization-membership-detail",
    ),
]
