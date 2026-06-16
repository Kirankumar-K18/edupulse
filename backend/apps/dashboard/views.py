"""
dashboard/views.py
Role-specific dashboard views with full stats for Admin, HOD, Lecturer, Student.
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, Q

from apps.accounts.models import User, Student, Lecturer, HOD, Department, ActivityLog
from apps.attendance.models import Subject, AttendanceRecord
from apps.reviews.models import Review, BlockedReview
from apps.accounts.decorators import admin_required, hod_required, lecturer_required, student_required


@login_required
def dashboard_redirect(request):
    return redirect(request.user.get_dashboard_url())


# ─── ADMIN DASHBOARD ─────────────────────────────────────────────────────────

@admin_required
def admin_dashboard(request):
    stats = {
        'total_departments':  Department.objects.filter(is_active=True).count(),
        'total_hods':         HOD.objects.filter(is_active=True).count(),
        'total_lecturers':    Lecturer.objects.filter(is_active=True).count(),
        'total_students':     Student.objects.filter(is_active=True).count(),
        'total_reviews':      Review.objects.count(),
        'total_blocked':      BlockedReview.objects.count(),
        'total_subjects':     Subject.objects.filter(is_active=True).count(),
    }
    recent_logs   = ActivityLog.objects.select_related('user').all()[:10]
    departments   = Department.objects.filter(is_active=True).annotate(
        lecturer_count=Count('lecturers', filter=Q(lecturers__is_active=True)),
        student_count=Count('students',   filter=Q(students__is_active=True)),
    )
    recent_reviews = Review.objects.select_related(
        'student__user', 'lecturer__user').order_by('-submitted_at')[:5]

    return render(request, 'dashboard/admin.html', {
        'stats':           stats,
        'recent_logs':     recent_logs,
        'departments':     departments,
        'recent_reviews':  recent_reviews,
    })


# ─── HOD DASHBOARD ───────────────────────────────────────────────────────────

@hod_required
def hod_dashboard(request):
    dept      = request.user.hod_profile.department
    lecturers = Lecturer.objects.filter(department=dept, is_active=True)
    students  = Student.objects.filter(department=dept, is_active=True)
    subjects  = Subject.objects.filter(department=dept, is_active=True)

    # Per-lecturer stats
    lecturer_stats = []
    for lec in lecturers:
        reviews = Review.objects.filter(lecturer=lec, is_blocked=False)
        avg = reviews.aggregate(a=Avg('rating'))['a'] or 0.0
        lecturer_stats.append({
            'lecturer':      lec,
            'avg_rating':    round(avg, 1),
            'total_reviews': reviews.count(),
            'blocked':       BlockedReview.objects.filter(review__lecturer=lec).count(),
        })

    # Attendance overview
    records = AttendanceRecord.objects.filter(student__department=dept)
    total_r   = records.count()
    present_r = records.filter(status__in=['present', 'late']).count()
    dept_attendance = round((present_r / total_r * 100), 1) if total_r else 0.0

    blocked_reviews = BlockedReview.objects.filter(
        review__lecturer__department=dept
    ).select_related('review__student__user', 'review__lecturer__user').order_by('-blocked_at')[:5]

    stats = {
        'total_lecturers':   lecturers.count(),
        'total_students':    students.count(),
        'total_subjects':    subjects.count(),
        'dept_attendance':   dept_attendance,
        'total_reviews':     Review.objects.filter(lecturer__department=dept, is_blocked=False).count(),
        'blocked_reviews':   BlockedReview.objects.filter(review__lecturer__department=dept).count(),
    }

    return render(request, 'dashboard/hod.html', {
        'dept':             dept,
        'stats':            stats,
        'lecturer_stats':   lecturer_stats,
        'blocked_reviews':  blocked_reviews,
    })


# ─── LECTURER DASHBOARD ──────────────────────────────────────────────────────

@lecturer_required
def lecturer_dashboard(request):
    lecturer = request.user.lecturer_profile
    subjects = Subject.objects.filter(lecturer=lecturer, is_active=True)

    # Attendance summary per subject
    subject_stats = []
    for subj in subjects:
        total_students = Student.objects.filter(
            department=lecturer.department, semester=subj.semester, is_active=True).count()
        total_records  = AttendanceRecord.objects.filter(subject=subj).count()
        present_records = AttendanceRecord.objects.filter(
            subject=subj, status__in=['present', 'late']).count()
        avg_attendance = round((present_records / total_records * 100), 1) if total_records else 0.0
        subject_stats.append({
            'subject':         subj,
            'total_students':  total_students,
            'avg_attendance':  avg_attendance,
        })

    reviews      = Review.objects.filter(lecturer=lecturer, is_blocked=False)
    distribution = {i: reviews.filter(rating=i).count() for i in range(1, 6)}
    recent_reviews = reviews.select_related('student__user').order_by('-submitted_at')[:5]

    stats = {
        'avg_rating':    lecturer.average_rating,
        'total_reviews': lecturer.total_reviews,
        'total_subjects': subjects.count(),
        'total_students': Student.objects.filter(
            department=lecturer.department, is_active=True).count(),
    }

    return render(request, 'dashboard/lecturer.html', {
        'lecturer':       lecturer,
        'stats':          stats,
        'subject_stats':  subject_stats,
        'distribution':   distribution,
        'recent_reviews': recent_reviews,
    })


# ─── STUDENT DASHBOARD ───────────────────────────────────────────────────────

@student_required
def student_dashboard(request):
    student = request.user.student_profile
    summary = AttendanceRecord.get_subject_summary(student)
    reviews = Review.objects.filter(
        student=student).select_related('lecturer__user').order_by('-submitted_at')[:5]

    from django.conf import settings
    threshold = getattr(settings, 'MIN_ATTENDANCE_FOR_REVIEW', 75)

    stats = {
        'overall_attendance': student.attendance_percentage,
        'can_review':         student.can_submit_review,
        'threshold':          threshold,
        'total_reviews':      Review.objects.filter(student=student).count(),
        'total_subjects':     len(summary),
    }

    return render(request, 'dashboard/student.html', {
        'student':  student,
        'stats':    stats,
        'summary':  summary,
        'reviews':  reviews,
    })
