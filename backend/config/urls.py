from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from academies.api import AcademyViewSet
from businesses.api import EducationBusinessViewSet
from courses.api import (
    ActivityViewSet,
    CourseViewSet,
    LessonViewSet,
    ModuleViewSet,
)
from organizations.api import MembershipViewSet, OrganizationViewSet
from programs.api import ProgramViewSet
from accounts.views import CsrfView, LoginView, LogoutView, SessionView, SignupView

router = DefaultRouter()

router.register(
    "organizations",
    OrganizationViewSet,
    basename="organization",
)

router.register(
    "businesses",
    EducationBusinessViewSet,
    basename="business",
)

router.register(
    "academies",
    AcademyViewSet,
    basename="academy",
)

router.register(
    "programs",
    ProgramViewSet,
    basename="program",
)

router.register(
    "courses",
    CourseViewSet,
    basename="course",
)

router.register(
    "modules",
    ModuleViewSet,
    basename="module",
)

router.register(
    "lessons",
    LessonViewSet,
    basename="lesson",
)

router.register(
    "activities",
    ActivityViewSet,
    basename="activity",
)


def health(request):
    return JsonResponse(
        {
            "status": "ok",
            "service": "AcademyOS",
        }
    )


urlpatterns = [
    path("api/auth/csrf/", CsrfView.as_view(), name="auth-csrf"),
    path("api/auth/signup/", SignupView.as_view(), name="auth-signup"),
    path("api/auth/login/", LoginView.as_view(), name="auth-login"),
    path("api/auth/logout/", LogoutView.as_view(), name="auth-logout"),
    path("api/auth/session/", SessionView.as_view(), name="auth-session"),
    path(
        "health/",
        health,
        name="health",
    ),
    path(
        "admin/",
        admin.site.urls,
    ),
    path(
        "api/auth/",
        include("rest_framework.urls"),
    ),
    path(
        "api/",
        include(router.urls),
    ),
    path(
        "api/organizations/<uuid:organization_pk>/memberships/",
        MembershipViewSet.as_view(
            {
                "get": "list",
                "post": "create",
            }
        ),
        name="organization-memberships",
    ),
    path(
        "api/organizations/<uuid:organization_pk>/memberships/<uuid:pk>/",
        MembershipViewSet.as_view(
            {
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="organization-membership-detail",
    ),
]