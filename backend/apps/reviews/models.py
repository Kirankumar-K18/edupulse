"""
reviews/models.py
Review, BlockedReview models with rating, bad-word integration,
one-review-per-lecturer-per-term guard.
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from apps.accounts.models import Student, Lecturer, BadWord


class Review(models.Model):
    student   = models.ForeignKey(Student,  on_delete=models.CASCADE, related_name='reviews')
    lecturer  = models.ForeignKey(Lecturer, on_delete=models.CASCADE, related_name='reviews')
    rating    = models.PositiveSmallIntegerField(
                    validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment   = models.TextField(max_length=1000)
    semester  = models.PositiveSmallIntegerField()
    academic_year = models.CharField(max_length=9)   # e.g. "2024-2025"
    is_blocked    = models.BooleanField(default=False)
    submitted_at  = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    class Meta:
        # One review per student-lecturer per semester per academic year
        unique_together = ('student', 'lecturer', 'semester', 'academic_year')
        ordering = ['-submitted_at']
        indexes = [
            models.Index(fields=['lecturer', 'is_blocked']),
            models.Index(fields=['student', '-submitted_at']),
        ]

    def __str__(self):
        return f"{self.student.usn} → {self.lecturer.employee_id} | {self.rating}★"

    @classmethod
    def get_current_academic_year(cls):
        now = timezone.now()
        year = now.year
        return f"{year}-{year+1}" if now.month >= 6 else f"{year-1}-{year}"

    @classmethod
    def can_student_review(cls, student, lecturer):
        """Returns (bool, reason_string)."""
        # Attendance check
        if not student.can_submit_review:
            from django.conf import settings
            threshold = getattr(settings, 'MIN_ATTENDANCE_FOR_REVIEW', 75)
            return False, f"Your attendance ({student.attendance_percentage}%) is below the required {threshold}%."

        # Duplicate check
        ay = cls.get_current_academic_year()
        if cls.objects.filter(
            student=student,
            lecturer=lecturer,
            semester=student.semester,
            academic_year=ay,
        ).exists():
            return False, "You have already submitted a review for this lecturer this semester."

        return True, ""


class BlockedReview(models.Model):
    """Stores reviews that were auto-blocked due to profanity."""
    review       = models.OneToOneField(Review, on_delete=models.CASCADE, related_name='block_record')
    blocked_at   = models.DateTimeField(auto_now_add=True)
    reason       = models.TextField()
    matched_words = models.JSONField(default=list)

    class Meta:
        ordering = ['-blocked_at']

    def __str__(self):
        return f"Blocked: {self.review}"
