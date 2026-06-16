"""
accounts/models.py
Complete user model hierarchy with custom User, Department, role profiles,
bad-word list, and activity logging.
"""

import re
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
from django.core.validators import RegexValidator
from django.conf import settings


# ─── DEPARTMENT ───────────────────────────────────────────────────────────────

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"

    @property
    def total_students(self):
        return self.students.filter(is_active=True).count()

    @property
    def total_lecturers(self):
        return self.lecturers.filter(is_active=True).count()


# ─── CUSTOM USER MANAGER ──────────────────────────────────────────────────────

class UserManager(BaseUserManager):

    def _validate_email(self, email, role=None):
        email = self.normalize_email(email)

        if role != "admin":
            if not email.endswith("@college.edu"):
                raise ValueError("Email must end with @college.edu")

        return email

    def create_user(self, email, password=None, **extra_fields):
        email = self._validate_email(
            email,
            extra_fields.get("role")
        )   
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('role', User.Role.ADMIN)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        # Enforce single admin
        if self.filter(role=User.Role.ADMIN).exists():
            raise ValueError("An admin account already exists. Only one admin is allowed.")
        return self.create_user(email, password, **extra_fields)


# ─── USER ─────────────────────────────────────────────────────────────────────

class User(AbstractBaseUser, PermissionsMixin):

    class Role(models.TextChoices):
        ADMIN    = 'admin',    'Admin'
        HOD      = 'hod',      'HOD'
        LECTURER = 'lecturer', 'Lecturer'
        STUDENT  = 'student',  'Student'

    email      = models.EmailField(unique=True)
    full_name  = models.CharField(max_length=150)
    role       = models.CharField(max_length=20, choices=Role.choices)
    phone      = models.CharField(max_length=15, blank=True)
    is_active  = models.BooleanField(default=True)
    is_staff   = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    last_login  = models.DateTimeField(null=True, blank=True)
    profile_pic = models.ImageField(upload_to='profiles/', null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['full_name', 'role']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.full_name} ({self.role})"

    @property
    def first_name(self):
        parts = self.full_name.split()
        return parts[0] if parts else ''

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN

    @property
    def is_hod(self):
        return self.role == self.Role.HOD

    @property
    def is_lecturer(self):
        return self.role == self.Role.LECTURER

    @property
    def is_student(self):
        return self.role == self.Role.STUDENT

    def get_dashboard_url(self):
        from django.urls import reverse
        routes = {
            self.Role.ADMIN:    'dashboard:admin',
            self.Role.HOD:      'dashboard:hod',
            self.Role.LECTURER: 'dashboard:lecturer',
            self.Role.STUDENT:  'dashboard:student',
        }
        return reverse(routes.get(self.role, 'dashboard:student'))


# ─── STUDENT PROFILE ──────────────────────────────────────────────────────────

class Student(models.Model):
    user       = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    usn        = models.CharField(max_length=20, unique=True, verbose_name='USN')
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name='students')
    section    = models.CharField(max_length=5)
    semester   = models.PositiveSmallIntegerField(default=1)
    batch_year = models.PositiveIntegerField()
    is_active  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['usn']

    def __str__(self):
        return f"{self.usn} - {self.user.full_name}"

    @property
    def attendance_percentage(self):
        from apps.attendance.models import AttendanceRecord
        total  = AttendanceRecord.objects.filter(student=self).count()
        present = AttendanceRecord.objects.filter(student=self, status='present').count()
        return round((present / total * 100), 1) if total > 0 else 0.0

    @property
    def can_submit_review(self):
        threshold = getattr(settings, 'MIN_ATTENDANCE_FOR_REVIEW', 75)
        return self.attendance_percentage >= threshold


# ─── LECTURER PROFILE ─────────────────────────────────────────────────────────

class Lecturer(models.Model):
    user           = models.OneToOneField(User, on_delete=models.CASCADE, related_name='lecturer_profile')
    employee_id    = models.CharField(max_length=20, unique=True)
    department     = models.ForeignKey(Department, on_delete=models.PROTECT, related_name='lecturers')
    designation    = models.CharField(max_length=100, default='Assistant Professor')
    qualification  = models.CharField(max_length=200, blank=True)
    experience_years = models.PositiveSmallIntegerField(default=0)
    is_active      = models.BooleanField(default=True)
    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['user__full_name']

    def __str__(self):
        return f"{self.employee_id} - {self.user.full_name}"

    @property
    def average_rating(self):
        from apps.reviews.models import Review
        reviews = Review.objects.filter(lecturer=self, is_blocked=False)
        if not reviews.exists():
            return 0.0
        return round(sum(r.rating for r in reviews) / reviews.count(), 1)

    @property
    def total_reviews(self):
        from apps.reviews.models import Review
        return Review.objects.filter(lecturer=self, is_blocked=False).count()


# ─── HOD PROFILE ──────────────────────────────────────────────────────────────

class HOD(models.Model):
    user       = models.OneToOneField(User, on_delete=models.CASCADE, related_name='hod_profile')
    department = models.OneToOneField(Department, on_delete=models.PROTECT, related_name='hod')
    joined_date = models.DateField(null=True, blank=True)
    is_active  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'HOD'

    def __str__(self):
        return f"HOD - {self.department.name}: {self.user.full_name}"


# ─── BAD WORD ─────────────────────────────────────────────────────────────────

class BadWord(models.Model):
    word       = models.CharField(max_length=100, unique=True)
    added_by   = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='bad_words_added')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active  = models.BooleanField(default=True)

    class Meta:
        ordering = ['word']

    def __str__(self):
        return self.word

    @classmethod
    def contains_bad_word(cls, text):
        """Return (is_clean, matched_words) tuple."""
        active_words = list(cls.objects.filter(is_active=True).values_list('word', flat=True))
        text_lower = text.lower()
        matched = []
        for w in active_words:
            pattern = r'\b' + re.escape(w.lower()) + r'\b'
            if re.search(pattern, text_lower):
                matched.append(w)
        return (len(matched) == 0), matched


# ─── ACTIVITY LOG ─────────────────────────────────────────────────────────────

class ActivityLog(models.Model):

    class Action(models.TextChoices):
        LOGIN         = 'login',          'Login'
        LOGOUT        = 'logout',         'Logout'
        LOGIN_FAILED  = 'login_failed',   'Login Failed'
        ATTENDANCE    = 'attendance',     'Attendance Marked'
        REVIEW        = 'review',         'Review Submitted'
        REVIEW_BLOCKED = 'review_blocked','Review Blocked'
        USER_CREATED  = 'user_created',   'User Created'
        USER_DELETED  = 'user_deleted',   'User Deleted'
        USER_UPDATED  = 'user_updated',   'User Updated'
        DEPT_CREATED  = 'dept_created',   'Department Created'
        DEPT_UPDATED  = 'dept_updated',   'Department Updated'
        ARQ_EVENT     = 'arq_event',      'ARQ Protocol Event'
        BADWORD_ADDED = 'badword_added',  'Bad Word Added'
        PASSWORD_CHANGE = 'password_change', 'Password Changed'

    user       = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='activity_logs')
    action     = models.CharField(max_length=30, choices=Action.choices)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    extra_data = models.JSONField(default=dict, blank=True)
    timestamp  = models.DateTimeField(auto_now_add=True)
    is_success = models.BooleanField(default=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['action', '-timestamp']),
            models.Index(fields=['user', '-timestamp']),
        ]

    def __str__(self):
        return f"[{self.timestamp:%Y-%m-%d %H:%M}] {self.user} - {self.action}"

    @classmethod
    def log(cls, user, action, description, request=None, extra_data=None, is_success=True):
        ip = None
        if request:
            x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
            ip = x_forwarded.split(',')[0] if x_forwarded else request.META.get('REMOTE_ADDR')
        cls.objects.create(
            user=user,
            action=action,
            description=description,
            ip_address=ip,
            extra_data=extra_data or {},
            is_success=is_success,
        )
