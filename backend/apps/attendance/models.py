"""
attendance/models.py
Subject, AttendanceRecord with duplicate guard, percentage calc, eligibility.
"""

from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from apps.accounts.models import Student, Lecturer, Department


class Subject(models.Model):
    name       = models.CharField(max_length=150)
    code       = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='subjects')
    lecturer   = models.ForeignKey(Lecturer, on_delete=models.SET_NULL, null=True, blank=True, related_name='subjects')
    semester   = models.PositiveSmallIntegerField(default=1)
    credits    = models.PositiveSmallIntegerField(default=3)
    is_active  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('code', 'department')
        ordering = ['name']

    def __str__(self):
        return f"{self.code} - {self.name}"


class AttendanceRecord(models.Model):

    class Status(models.TextChoices):
        PRESENT = 'present', 'Present'
        ABSENT  = 'absent',  'Absent'
        LATE    = 'late',    'Late'

    student   = models.ForeignKey(Student,  on_delete=models.CASCADE, related_name='attendance_records')
    subject   = models.ForeignKey(Subject,  on_delete=models.CASCADE, related_name='attendance_records')
    lecturer  = models.ForeignKey(Lecturer, on_delete=models.SET_NULL, null=True, related_name='attendance_records')
    date      = models.DateField(default=timezone.now)
    status    = models.CharField(max_length=10, choices=Status.choices, default=Status.PRESENT)
    remarks   = models.CharField(max_length=200, blank=True)
    marked_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'subject', 'date')   # duplicate guard
        ordering = ['-date']
        indexes = [
            models.Index(fields=['student', 'subject']),
            models.Index(fields=['lecturer', 'date']),
        ]

    def __str__(self):
        return f"{self.student.usn} | {self.subject.code} | {self.date} | {self.status}"

    def clean(self):
        if self.date and self.date > timezone.now().date():
            raise ValidationError("Attendance date cannot be in the future.")

    @classmethod
    def get_percentage(cls, student, subject=None):
        qs = cls.objects.filter(student=student)
        if subject:
            qs = qs.filter(subject=subject)
        total   = qs.count()
        present = qs.filter(status__in=[cls.Status.PRESENT, cls.Status.LATE]).count()
        return round((present / total * 100), 1) if total > 0 else 0.0

    @classmethod
    def get_subject_summary(cls, student):
        """Return list of {subject, total, present, percentage} dicts."""
        subjects = Subject.objects.filter(
            department=student.department,
            semester=student.semester,
            is_active=True,
        )
        summary = []
        for subj in subjects:
            total   = cls.objects.filter(student=student, subject=subj).count()
            present = cls.objects.filter(student=student, subject=subj,
                                          status__in=[cls.Status.PRESENT, cls.Status.LATE]).count()
            pct = round((present / total * 100), 1) if total > 0 else 0.0
            summary.append({
                'subject': subj,
                'total':   total,
                'present': present,
                'percentage': pct,
                'status': 'good' if pct >= 75 else ('warning' if pct >= 60 else 'critical'),
            })
        return summary
