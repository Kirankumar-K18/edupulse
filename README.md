# Smart Lecturer Review System

A college feedback and attendance management system built with **Django 4.2, MySQL, HTML, CSS, JavaScript, and Bootstrap 5**.

The system provides role-based access for **Admin, HOD, Lecturer, and Student**, with attendance tracking, lecturer review management, bad-word filtering, and analytics dashboards.

---

## Features

### Admin

* Manage Departments
* Manage HODs
* Manage Lecturers
* Manage Students
* Manage Subjects
* View system analytics
* View activity logs
* Manage bad-word filters
* View blocked reviews
* Unblock reviews

### HOD

* Department-specific access
* Manage lecturers within department
* Manage students within department
* View department attendance statistics
* View lecturer performance
* View approved and blocked reviews

### Lecturer

* Mark attendance
* Edit attendance records
* View attendance reports
* View ratings and reviews
* Monitor student attendance

### Student

* Secure login
* View attendance summary
* View subject-wise attendance
* Submit lecturer reviews
* View review history
* Attendance eligibility validation

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
smart_lecturer_2/
│
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── setup.py
│   │
│   ├── apps/
│   │   ├── accounts/
│   │   ├── attendance/
│   │   ├── dashboard/
│   │   └── reviews/
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
│   │   └── js/
│   │
│   └── templates/
│       ├── accounts/
│       ├── attendance/
│       ├── dashboard/
│       ├── reviews/
│       └── base.html
│
├── .gitignore
└── README.md
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

## Attendance System

### Features

* Subject-wise Attendance
* Daily Attendance Records
* Percentage Calculation
* Attendance Analytics
* Attendance Eligibility Check for Reviews

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
* Subject Management UI
* Lecturer Performance Trends
* Mobile Responsive Improvements

---

## Author

**Kiran Kumar**

GitHub:
https://github.com/Kirankumar-K18

Repository:
https://github.com/Kirankumar-K18/smart-lecturer-review-system
