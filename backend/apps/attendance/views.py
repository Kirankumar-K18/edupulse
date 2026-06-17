"""
attendance/views.py
Mark attendance (lecturer), view attendance (student), reports (HOD/Admin).
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db import transaction
from django.utils import timezone
from .forms import SubjectForm
from .models import Subject, AttendanceRecord
from apps.accounts.models import Student, Lecturer, ActivityLog
from apps.accounts.decorators import lecturer_required, student_required, admin_or_hod_required, admin_required


# ─── STUDENT: VIEW ATTENDANCE ─────────────────────────────────────────────────

@student_required
def student_attendance(request):
    student = request.user.student_profile
    summary = AttendanceRecord.get_subject_summary(student)
    overall = student.attendance_percentage
    return render(request, 'attendance/student_attendance.html', {
        'summary': summary,
        'overall': overall,
        'student': student,
        'can_review': student.can_submit_review,
    })


# ─── LECTURER: MARK ATTENDANCE ────────────────────────────────────────────────

@lecturer_required
def mark_attendance(request):
    lecturer  = request.user.lecturer_profile
    subjects  = Subject.objects.filter(lecturer=lecturer, is_active=True)
    today     = timezone.now().date()

    selected_subject = None
    students_data    = []

    if request.GET.get('subject'):
        selected_subject = get_object_or_404(Subject, pk=request.GET['subject'], lecturer=lecturer)
        students = Student.objects.filter(
            department=lecturer.department,
            semester=selected_subject.semester,
            is_active=True,
        ).select_related('user')

        # Annotate with today's existing record
        existing = {
            r.student_id: r
            for r in AttendanceRecord.objects.filter(
                subject=selected_subject,
                date=today,
            )
        }
        for s in students:
            students_data.append({
                'student': s,
                'record':  existing.get(s.pk),
            })

    return render(request, 'attendance/mark_attendance.html', {
        'subjects':          subjects,
        'selected_subject':  selected_subject,
        'students_data':     students_data,
        'today':             today,
    })


@lecturer_required
@require_POST
def submit_attendance(request):
    lecturer = request.user.lecturer_profile
    subject_id = request.POST.get('subject_id')
    date_str   = request.POST.get('date')

    subject = get_object_or_404(Subject, pk=subject_id, lecturer=lecturer)
    date    = timezone.datetime.strptime(date_str, '%Y-%m-%d').date()

    if date > timezone.now().date():
        messages.error(request, "Cannot mark attendance for a future date.")
        return redirect('attendance:mark')

    students = Student.objects.filter(
        department=lecturer.department,
        semester=subject.semester,
        is_active=True,
    )

    saved, updated = 0, 0
    with transaction.atomic():
        for student in students:
            status  = request.POST.get(f'status_{student.pk}', 'absent')
            remarks = request.POST.get(f'remarks_{student.pk}', '')
            obj, created = AttendanceRecord.objects.update_or_create(
                student=student,
                subject=subject,
                date=date,
                defaults={'status': status, 'remarks': remarks, 'lecturer': lecturer},
            )
            if created:
                saved += 1
            else:
                updated += 1

    ActivityLog.log(
        request.user,
        ActivityLog.Action.ATTENDANCE,
        f"Attendance marked: {subject.code} on {date} — {saved} new, {updated} updated",
        request=request,
        extra_data={'subject': subject.code, 'date': str(date), 'saved': saved, 'updated': updated},
    )
    messages.success(request, f"Attendance saved: {saved} new, {updated} updated.")
    return redirect('attendance:mark')


# ─── LECTURER: EDIT ATTENDANCE ────────────────────────────────────────────────

@lecturer_required
def edit_attendance(request):
    lecturer = request.user.lecturer_profile
    records  = AttendanceRecord.objects.filter(lecturer=lecturer).select_related('student__user', 'subject')
    return render(request, 'attendance/edit_attendance.html', {'records': records})


@lecturer_required
@require_POST
def update_record(request, pk):
    record = get_object_or_404(AttendanceRecord, pk=pk, lecturer=request.user.lecturer_profile)
    new_status  = request.POST.get('status')
    new_remarks = request.POST.get('remarks', '')
    if new_status in [s[0] for s in AttendanceRecord.Status.choices]:
        record.status  = new_status
        record.remarks = new_remarks
        record.save()
        messages.success(request, "Attendance record updated.")
    return redirect('attendance:edit')


# ─── HOD/ADMIN: REPORTS ───────────────────────────────────────────────────────

@admin_or_hod_required
def attendance_report(request):
    if request.user.is_hod:
        dept     = request.user.hod_profile.department
        students = Student.objects.filter(department=dept, is_active=True).select_related('user')
        subjects = Subject.objects.filter(department=dept, is_active=True)
    else:
        students = Student.objects.filter(is_active=True).select_related('user', 'department')
        subjects = Subject.objects.filter(is_active=True)

    # Summary per student
    summary = [{'student': s, 'overall': s.attendance_percentage} for s in students]
    return render(request, 'attendance/report.html', {
        'summary':  summary,
        'subjects': subjects,
    })


# ─── SUBJECT MANAGEMENT ───────────────────────────────────────────────────────

@admin_or_hod_required
def manage_subjects(request):
    if request.user.is_hod:
        subjects = Subject.objects.filter(department=request.user.hod_profile.department)
    else:
        subjects = Subject.objects.all()
    return render(request, 'attendance/subjects.html', {'subjects': subjects})
@admin_or_hod_required
def add_subject(request):

    if request.method == 'POST':
        form = SubjectForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Subject added successfully.")
            return redirect('attendance:subjects')

    else:
        form = SubjectForm()

    return render(
        request,
        'attendance/subject_form.html',
        {'form': form, 'title': 'Add Subject'}
    )


@admin_or_hod_required
def edit_subject(request, pk):

    subject = get_object_or_404(
        Subject,
        pk=pk
    )

    if request.user.is_hod:
        if subject.department != request.user.hod_profile.department:
            messages.error(request, "Access denied.")
            return redirect('attendance:subjects')

    if request.method == 'POST':
        form = SubjectForm(
            request.POST,
            instance=subject
        )

        if form.is_valid():
            form.save()
            messages.success(request, "Subject updated successfully.")
            return redirect('attendance:subjects')

    else:
        form = SubjectForm(instance=subject)

    return render(
        request,
        'attendance/subject_form.html',
        {
            'form': form,
            'title': 'Edit Subject'
        }
    )


@admin_or_hod_required
def delete_subject(request, pk):

    subject = get_object_or_404(
        Subject,
        pk=pk
    )

    if request.user.is_hod:
        if subject.department != request.user.hod_profile.department:
            messages.error(request, "Access denied.")
            return redirect('attendance:subjects')

    subject.delete()

    messages.success(
        request,
        "Subject deleted successfully."
    )

    return redirect('attendance:subjects')
