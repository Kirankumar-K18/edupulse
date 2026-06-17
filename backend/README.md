# EduPulse : Academic Feedback and Attendance Management System

A production-ready college management system built with **Django 4.2 + MySQL + HTML/CSS/JavaScript**.

---

## Tech Stack

| Layer    | Technology                          |
|----------|-------------------------------------|
| Backend  | Python 3.9+, Django 4.2             |
| Database | MySQL 8.0+                          |
| Frontend | HTML5, CSS3, JavaScript (Bootstrap 5)|
| Auth     | Django session auth + custom User   |

---

## Project Structure

```
smart_lecturer/
├── manage.py
├── setup.py                    ← one-time setup wizard
├── requirements.txt
├── .env.example                ← copy to .env and fill in values
├── smart_lecturer/             ← Django project config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── accounts/               ← Users, Departments, HOD, Lecturer, Student, Bad Words, Activity Log
│   ├── attendance/             ← Subjects, Attendance Records
│   ├── reviews/                ← Reviews, Blocked Reviews
│   ├── arq/                    ← Stop-and-Wait ARQ Simulation
│   └── dashboard/              ← Role-specific dashboards
├── templates/                  ← All HTML templates
│   ├── base.html
│   ├── accounts/
│   ├── attendance/
│   ├── reviews/
│   ├── arq/
│   └── dashboard/
└── static/
    ├── css/main.css
    └── js/main.js
```

---

## Quick Start

### 1. Prerequisites

- Python 3.9+
- MySQL 8.0+ running locally
- `pip`

### 2. Clone / download the project

```bash
git clone <your-repo-url>
cd smart_lecturer
```

### 3. Create a virtual environment

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 4. Run the setup wizard

```bash
python setup.py
```

This will:
- Install all Python dependencies
- Create your `.env` file interactively
- Create the MySQL database
- Run all Django migrations
- Collect static files

### 5. Create the admin account

```bash
python manage.py create_admin
```

Only one admin account is allowed system-wide.

### 6. Start the server

```bash
python manage.py runserver
```

Open **http://127.0.0.1:8000/**

---

## Manual Setup (if setup.py fails)

```bash
# Install dependencies
pip install -r requirements.txt

# Copy and edit .env
cp .env.example .env
# Edit .env with your MySQL credentials

# Create MySQL database manually
mysql -u root -p -e "CREATE DATABASE smart_lecturer_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Create admin
python manage.py create_admin

# Run server
python manage.py runserver
```

---

## System Roles & Default URLs

| Role     | Login URL                        | Dashboard              |
|----------|----------------------------------|------------------------|
| Admin    | `/accounts/login/` (Staff tab)   | `/dashboard/admin/`    |
| HOD      | `/accounts/login/` (Staff tab)   | `/dashboard/hod/`      |
| Lecturer | `/accounts/login/` (Staff tab)   | `/dashboard/lecturer/` |
| Student  | `/accounts/login/` (Student tab) | `/dashboard/student/`  |

### Student Login requires
- College email (`@college.edu`)
- USN
- Department
- Section
- Password

---

## Features

### Admin
- Create/Edit/Delete Departments
- Create/Edit/Delete HODs (one per department enforced)
- Manage all Lecturers and Students
- View all Activity Logs (login, logout, attendance, reviews, etc.)
- Manage bad-word filter list
- View all reviews including blocked ones
- Unblock flagged reviews
- System analytics dashboard
- ARQ Simulation access

### HOD
- Department-scoped access only
- Add/Edit/Deactivate Lecturers in their department
- Add/Edit/Deactivate Students in their department
- View lecturer ratings and performance
- View approved and blocked reviews
- Department attendance summary
- ARQ Simulation access

### Lecturer
- Mark attendance per subject per date
- Edit attendance records
- View their own ratings and student reviews
- Attendance statistics per subject
- ARQ Simulation access

### Student
- Login with USN + Department + Section + Email
- View subject-wise attendance with progress bars
- Submit lecturer reviews (blocked if attendance < 75%)
- View submitted review history
- ARQ Simulation access

### Stop-and-Wait ARQ Simulation
- Configure: packets, loss probability, timeout, max retries
- Animated event timeline (SEND → ACK / DROP → TIMEOUT → RETRANSMIT)
- Efficiency calculation
- All events logged to ActivityLog
- History of past sessions

### Review System
- 1–5 star rating
- Text comments (max 1000 chars)
- Auto bad-word detection (regex whole-word matching)
- Offensive reviews auto-blocked and stored separately
- HOD sees blocked reviews for their department
- Admin can unblock reviews
- One review per student per lecturer per semester per academic year
- Attendance eligibility check before submission

---

## Adding Subjects

Subjects are managed via **Django Admin** (`/admin/`) or can be added programmatically.

```python
# Example: add via Django shell
python manage.py shell

from apps.accounts.models import Department, Lecturer
from apps.attendance.models import Subject

dept = Department.objects.get(code='CS')
lec  = Lecturer.objects.get(employee_id='EMP001')

Subject.objects.create(
    name='Data Structures',
    code='CS301',
    department=dept,
    lecturer=lec,
    semester=3,
    credits=4,
)
```

---

## Environment Variables (`.env`)

| Variable              | Default           | Description                        |
|-----------------------|-------------------|------------------------------------|
| `DJANGO_SECRET_KEY`   | —                 | Django secret key (required)       |
| `DEBUG`               | `True`            | Set to `False` in production       |
| `ALLOWED_HOSTS`       | `localhost,...`   | Comma-separated hostnames          |
| `DB_NAME`             | `smart_lecturer_db` | MySQL database name              |
| `DB_USER`             | `root`            | MySQL username                     |
| `DB_PASSWORD`         | —                 | MySQL password                     |
| `DB_HOST`             | `localhost`       | MySQL host                         |
| `DB_PORT`             | `3306`            | MySQL port                         |
| `COLLEGE_EMAIL_DOMAIN`| `college.edu`     | Required email suffix for all users|

---

## Production Checklist

```bash
# 1. Set in .env:
DEBUG=False
DJANGO_SECRET_KEY=<long-random-key>
ALLOWED_HOSTS=yourdomain.com

# 2. Install gunicorn
pip install gunicorn

# 3. Run with gunicorn
gunicorn smart_lecturer.wsgi:application --bind 0.0.0.0:8000 --workers 3

# 4. Serve static files via nginx (point to staticfiles/ directory)
# 5. Use HTTPS (CSRF_COOKIE_SECURE and SESSION_COOKIE_SECURE auto-enable when DEBUG=False)
```

---

## Security Features

- CSRF protection on all POST forms
- Password hashing (Django PBKDF2)
- Strong password validation (8+ chars, uppercase, lowercase, digit, special)
- Rate limiting: 5 failed login attempts → 15-minute lockout per IP
- College email domain enforcement
- Role-based access control (decorators on every view)
- HOD department isolation (can only manage own department)
- Single admin enforcement
- SQL injection protection (Django ORM)
- Session security (HttpOnly cookies, configurable expiry)
- Activity logging for all sensitive actions
- Bad-word auto-block on review submission
