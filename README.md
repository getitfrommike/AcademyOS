# AcademyOS

AcademyOS is a secure, multi-tenant education-business operating system. The current backend foundation supports organizations, memberships, education businesses, academies, programs, courses, modules, lessons, activities, and immutable-style audit events.

## Local setup

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Paste the generated value into `backend/.env` as `DJANGO_SECRET_KEY`, then run:

```powershell
python manage.py migrate
python manage.py createsuperuser
python manage.py test
python manage.py runserver
```

Health endpoint: `http://127.0.0.1:8000/health/`

## Security rules

- Never commit `.env`, `db.sqlite3`, `.venv`, uploaded media, or production secrets.
- Every tenant-owned query must be filtered through active organization membership.
- Cross-organization object references must fail validation.
- Organization owner/admin roles are required for writes.
- Every security-sensitive or publishing action should create an `AuditEvent`.
- Run `python manage.py check --deploy` before production deployment.

## Current next milestone

Build the guided Founder Discovery workflow that produces an Education Business Blueprint, then connects that blueprint to academy creation.
