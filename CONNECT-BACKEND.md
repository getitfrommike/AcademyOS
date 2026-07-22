# Local development

## Backend

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python manage.py migrate
python manage.py runserver 8000
```

## Frontend

Create `frontend/.env.local`:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

Then run:

```powershell
cd frontend
npm install
npm run dev
```

## Onboarding sequence

1. Landing page
2. Create temporary workspace
3. Guided Discovery™
4. Secure Your Workspace (Django account + organization owner membership)
5. Knowledge Upload™ unlocks only after authenticated signup
6. Knowledge Engine™

The signup request uses Django session authentication and CSRF protection.
