from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.utils.text import slugify
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from organizations.models import Organization, OrganizationMembership

User = get_user_model()


def _unique_username(email: str) -> str:
    base = (email.split("@", 1)[0] or "member")[:120]
    candidate = base
    number = 1
    while User.objects.filter(username=candidate).exists():
        number += 1
        candidate = f"{base}-{number}"
    return candidate


def _unique_slug(name: str) -> str:
    base = slugify(name)[:180] or "workspace"
    candidate = base
    number = 1
    while Organization.objects.filter(slug=candidate).exists():
        number += 1
        candidate = f"{base}-{number}"
    return candidate


class CsrfView(APIView):
    permission_classes = [AllowAny]

    @ensure_csrf_cookie
    def get(self, request):
        return Response({"detail": "CSRF cookie set."})


class SignupView(APIView):
    permission_classes = [AllowAny]

    @transaction.atomic
    def post(self, request):
        email = str(request.data.get("email", "")).strip().lower()
        password = str(request.data.get("password", ""))
        display_name = str(request.data.get("display_name", "")).strip()
        workspace_name = str(request.data.get("workspace_name", "")).strip()
        organization_name = str(request.data.get("organization_name", "")).strip()

        errors = {}
        if not email:
            errors["email"] = ["Email address is required."]
        elif User.objects.filter(email__iexact=email).exists():
            errors["email"] = ["An account already exists for this email address."]
        if not workspace_name:
            errors["workspace_name"] = ["Workspace name is required."]

        try:
            validate_password(password)
        except DjangoValidationError as exc:
            errors["password"] = list(exc.messages)

        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(
            username=_unique_username(email),
            email=email,
            password=password,
            display_name=display_name,
        )
        organization = Organization.objects.create(
            name=organization_name or workspace_name,
            slug=_unique_slug(organization_name or workspace_name),
        )
        OrganizationMembership.objects.create(
            organization=organization,
            user=user,
            role=OrganizationMembership.Role.OWNER,
            is_active=True,
        )
        login(request, user)
        return Response(
            {
                "user": {"id": user.pk, "email": user.email, "display_name": user.display_name},
                "organization": {"id": organization.pk, "name": organization.name, "slug": organization.slug},
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = str(request.data.get("email", "")).strip().lower()
        password = str(request.data.get("password", ""))
        user = authenticate(request, email=email, password=password)
        if user is None:
            return Response({"detail": "Invalid email or password."}, status=status.HTTP_400_BAD_REQUEST)
        login(request, user)
        return Response({"user": {"id": user.pk, "email": user.email, "display_name": user.display_name}})


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class SessionView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        if not request.user.is_authenticated:
            return Response({"authenticated": False})
        return Response({
            "authenticated": True,
            "user": {"id": request.user.pk, "email": request.user.email, "display_name": request.user.display_name},
        })
