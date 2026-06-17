# EduPulse : Academic Feedback and Attendance Management System

A college feedback and attendance management system built with **Django 4.2, MySQL, HTML, CSS, JavaScript, and Bootstrap 5**.

The system provides role-based access for **Admin, HOD, Lecturer, and Student**, with attendance tracking, lecturer review management, subject management, bad-word filtering, attendance analytics, and performance dashboards.

---

## Features

### Admin

* Manage Departments
* Manage HODs
* Manage Lecturers
* Manage Students
* Manage Subjects
* View System Analytics
* View Activity Logs
* Manage Bad Word Filters
* View Blocked Reviews
* Unblock Reviews

### HOD

* Department-specific Access
* Manage Lecturers within Department
* Manage Students within Department
* Manage Subjects within Department
* View Department Attendance Statistics
* View Lecturer Performance
* View Approved and Blocked Reviews

### Lecturer

* Mark Attendance using Subject + Date Selection
* Edit Attendance Records using Subject + Date Filters
* View Attendance Reports
* View Ratings and Reviews
* Monitor Student Attendance

### Student

* Secure Login
* View Overall Attendance Percentage
* View Subject-wise Attendance
* View Detailed Attendance History
* Submit Lecturer Reviews
* View Review History
* Attendance Eligibility Validation

---

## Technology Stack

| Layer          | Technology               |
| -------------- | ------------------------ |
| Backend        | Python 3.11, Django 4.2  |
| Database       | MySQL 8+                 |
| Frontend       | HTML5, CSS3, JavaScript  |
| UI Framework   | Bootstrap 5              |
| Authentication | Django Custom User Model |
| ORM            | Django ORM               |

---

## Project Structure

```text
EduPulse/
│
├── README.md
├── .gitignore
│
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── setup.py
│   ├── smart_lecturer_backup.sql
│   │
│   ├── apps/
│   │   ├── accounts/
│   │   │   ├── models.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   ├── forms.py
│   │   │   ├── decorators.py
│   │   │   ├── admin.py
│   │   │   └── management/
│   │   │       └── commands/
│   │   │           └── create_admin.py
│   │   │
│   │   ├── attendance/
│   │   │   ├── models.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   ├── forms.py
│   │   │   ├── admin.py
│   │   │   └── migrations/
│   │   │
│   │   ├── reviews/
│   │   │   ├── models.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   ├── forms.py
│   │   │   └── admin.py
│   │   │
│   │   └── dashboard/
│   │       ├── views.py
│   │       └── urls.py
│   │
│   └── smart_lecturer/
│       ├── settings.py
│       ├── urls.py
│       ├── wsgi.py
│       └── asgi.py
│
├── frontend/
│   ├── static/
│   │   ├── css/
│   │   │   └── main.css
│   │   ├── js/
│   │   │   └── main.js
│   │   └── images/
│   │
│   └── templates/
│       ├── base.html
│       │
│       ├── accounts/
│       │   ├── login.html
│       │   ├── profile.html
│       │   ├── departments.html
│       │   ├── lecturers.html
│       │   ├── students.html
│       │   └── hods.html
│       │
│       ├── attendance/
│       │   ├── student_attendance.html
│       │   ├── subject_history.html
│       │   ├── mark_attendance.html
│       │   ├── edit_attendance.html
│       │   ├── subjects.html
│       │   ├── subject_form.html
│       │   └── report.html
│       │
│       ├── reviews/
│       │   ├── submit_review.html
│       │   ├── my_reviews.html
│       │   ├── lecturer_reviews.html
│       │   └── admin_reviews.html
│       │
│       └── dashboard/
│           ├── admin_dashboard.html
│           ├── hod_dashboard.html
│           ├── lecturer_dashboard.html
│           └── student_dashboard.html
│
└── docs/
    └── screenshots/
```

---

## Installation

### 1. Clone Repository

```bash
git clone https://github.com/Kirankumar-K18/smart-lecturer-review-system.git

cd smart-lecturer-review-system
```

### 2. Create Virtual Environment

Windows:

```bash
python -m venv .venv

.venv\Scripts\activate
```

Linux / macOS:

```bash
python3 -m venv .venv

source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r backend/requirements.txt
```

### 4. Configure Environment

Create a `.env` file inside the backend folder.

Example:

```env
DJANGO_SECRET_KEY=your-secret-key

DEBUG=True

ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=smart_lecturer_db
DB_USER=root
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306

COLLEGE_EMAIL_DOMAIN=college.edu
```

### 5. Create Database

```sql
CREATE DATABASE smart_lecturer_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;
```

### 6. Apply Migrations

```bash
cd backend

python manage.py migrate
```

### 7. Create Superuser

```bash
python manage.py createsuperuser
```

### 8. Run Development Server

```bash
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

---

## Login Roles

| Role     | Dashboard              |
| -------- | ---------------------- |
| Admin    | `/dashboard/admin/`    |
| HOD      | `/dashboard/hod/`      |
| Lecturer | `/dashboard/lecturer/` |
| Student  | `/dashboard/student/`  |

---

## Subject Management

### Admin

* Add Subjects
* Edit Subjects
* Assign Lecturers
* Configure Semester and Credits
* Activate / Deactivate Subjects

### HOD

* View Department Subjects
* Manage Subjects within Department

---

## Attendance System

### Features
### Attendance System

- Subject Management UI
- Manual Date Selection for Attendance
- Mark Attendance by Subject and Date
- Edit Attendance by Subject and Date
- Duplicate Attendance Detection
- Student Attendance History
- Subject-wise Attendance Percentage
- Overall Attendance Percentage
- Attendance Reports for HOD and Admin
- Attendance Eligibility Check for Reviews

### Lecturer Workflow

1. Select Subject
2. Select Attendance Date
3. Load Students
4. Mark Present / Absent / Late
5. Save Attendance Records

### Attendance Editing

1. Select Subject
2. Select Date
3. Search Records
4. Edit Attendance
5. Save Changes

### Student Attendance Tracking

Students can:

* View Overall Attendance Percentage
* View Subject-wise Attendance Statistics
* View Attendance History for Individual Subjects
* View Present / Absent / Late Records

---

## Review System

### Features

* 1–5 Star Rating
* Text Feedback
* Attendance Eligibility Check
* Bad Word Detection
* Auto Block Offensive Reviews
* Review Moderation
* One Review Per Lecturer Per Semester

### Review Validation

Students can submit reviews only when:

* Attendance meets minimum threshold
* Lecturer exists
* Review has not already been submitted for that semester

---

## Navigation Features

* Universal Back Button
* Dashboard-aware Navigation
* Responsive Sidebar
* Mobile-Friendly Interface

---

## Security Features

* Django CSRF Protection
* Password Hashing (PBKDF2)
* Strong Password Validation
* Role-Based Access Control
* Department Isolation for HOD
* Session Authentication
* SQL Injection Protection via ORM
* Activity Logging
* Review Moderation

---

## Environment Variables

| Variable             | Description            |
| -------------------- | ---------------------- |
| DJANGO_SECRET_KEY    | Django Secret Key      |
| DEBUG                | Development Mode       |
| ALLOWED_HOSTS        | Allowed Hosts          |
| DB_NAME              | Database Name          |
| DB_USER              | Database Username      |
| DB_PASSWORD          | Database Password      |
| DB_HOST              | Database Host          |
| DB_PORT              | Database Port          |
| COLLEGE_EMAIL_DOMAIN | Allowed College Domain |

---

## Production Deployment

Before deployment:

```env
DEBUG=False
```

Generate a strong secret key and update:

```env
DJANGO_SECRET_KEY=your-production-secret-key
```

Configure:

```env
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

Then run:

```bash
python manage.py collectstatic
```

Recommended production stack:

* Nginx
* Gunicorn
* MySQL
* Ubuntu Server

---

## Future Enhancements

* Email Notifications
* PDF Attendance Reports
* Export Reviews to Excel
* Advanced Analytics Dashboard
* Lecturer Performance Trends
* Mobile Application
* AI-based Feedback Analysis

---

## Author

**Kirankumar K**

GitHub:
https://github.com/Kirankumar-K18

Project:
**EduPulse : Academic Feedback and Attendance Management System**

Repository:
https://github.com/Kirankumar-K18/edupulse
