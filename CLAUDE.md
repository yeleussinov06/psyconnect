# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
pip install django openpyxl

# Apply migrations and start dev server
python manage.py migrate
python manage.py runserver

# Load sample fixtures (admin, student1, parent1, psycholog1 — all password: psyconnect123)
python manage.py loaddata initial_data

# Import users from Excel
python manage.py import_users <file.xlsx>
python manage.py import_users <file.xlsx> --dry-run

# Run tests (no tests exist yet)
python manage.py test
```

## Architecture

**Single Django app** (`core`) inside a `psyconnect` project. All models, views, and URLs live in `core/`.

### User Role System

The project has 5 roles stored in `UserProfile.role`: `student`, `parent`, `teacher`, `psychologist`, superuser (Django admin). Role determines which dashboard the user is redirected to after login. Key helper functions in `views.py`: `get_role(request)` and `role_redirect(request)`.

Each role has its own dashboard and sidebar template under `core/templates/core/<role>/`. URL namespacing is by role prefix (e.g., `/student/`, `/parent/`, `/psychologist/`, `/teacher/`).

### Models Overview (`core/models.py`)

- `UserProfile` — one-to-one with Django `User`; stores role, school_class, phone, bio, avatar_color
- `SchoolClass` — school class/group; has a teacher FK
- `ParentStudent` — many-to-many bridge between parent and student users
- `EmotionEntry` — daily emotion diary (6 emotion types + event_type)
- `PsychologistSchedule` / `Appointment` — scheduling system; psychologist creates time slots, students/parents book them
- `PsychTest` / `PsychTestQuestion` / `PsychTestResult` — advanced test system created by psychologists; questions have 4 types (radio, checkbox, scale, text); results include risk level (low/medium/high) and AI-generated analysis
- `TestQuestion` / `TestResult` — simpler built-in tests (4 categories: anxiety, stress, motivation, social)
- `ChatMessage` — keyword-based AI chat history
- `AnonymousRequest` — public support requests (no login required)
- `Article` — bilingual content (title/content in `_ru` and `_kz` fields) for different audiences
- `Notification` — in-app notification system

### Bilingual Support (Russian/Kazakh)

Language is stored in the session, toggled via `/lang/<lang>/`. Models with user-facing text have parallel `_ru` and `_kz` fields. The helper `get_lang(request)` reads from session (default: `'ru'`). Templates must select the correct field based on language.

### Views (`core/views.py`)

~1,837 lines, all function-based views. Protected with `@login_required`. No DRF — API endpoints (chat, notification count) return `JsonResponse`. The AI chat (`/api/chat/`) uses keyword matching, not an external LLM.

### URLs (`core/urls.py`)

63 URL patterns, all included directly under `/` (no namespacing). Admin tools for bulk user import are at `/admin-tools/`.

### Static Files

`core/static/css/main.css` and `psy-dashboard.css` — no build step, plain CSS. Icons are PNGs in `core/static/img/icons/`.

### Settings Notes

- `DEBUG = True`, SQLite (`db.sqlite3`), `ALLOWED_HOSTS = ['*']`
- `TIME_ZONE = 'Asia/Almaty'`, `LANGUAGE_CODE = 'ru-ru'`
- Sessions last 30 days (`SESSION_COOKIE_AGE = 86400 * 30`)
- No `.env` file in use — secrets are hardcoded (dev only)
