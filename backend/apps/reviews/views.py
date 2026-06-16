"""
reviews/views.py
Submit reviews (student), view own reviews, lecturer view ratings,
HOD view all reviews + blocked, Admin full access.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db import transaction
from django.core.paginator import Paginator

from .models import Review, BlockedReview
from .forms import ReviewForm
from apps.accounts.models import Lecturer, BadWord, ActivityLog, Student
from apps.accounts.decorators import (
    student_required, lecturer_required,
    hod_required, admin_required, admin_or_hod_required,
)


# ─── STUDENT: SUBMIT REVIEW ───────────────────────────────────────────────────

@student_required
def submit_review(request):
    student = request.user.student_profile

    # Global attendance eligibility
    if not student.can_submit_review:
        from django.conf import settings
        threshold = getattr(settings, 'MIN_ATTENDANCE_FOR_REVIEW', 75)
        messages.error(
            request,
            f"Your overall attendance ({student.attendance_percentage}%) is below "
            f"the required {threshold}% to submit reviews."
        )
        return redirect('attendance:student')

    form = ReviewForm(request.POST or None, student=student)

    if request.method == 'POST' and form.is_valid():
        lecturer = form.cleaned_data['lecturer']
        comment  = form.cleaned_data['comment']
        rating   = int(form.cleaned_data['rating'])

        # Per-lecturer eligibility check
        can, reason = Review.can_student_review(student, lecturer)
        if not can:
            messages.error(request, reason)
            return render(request, 'reviews/submit.html', {'form': form})

        # Bad-word check
        is_clean, matched = BadWord.contains_bad_word(comment)

        with transaction.atomic():
            review = Review.objects.create(
                student=student,
                lecturer=lecturer,
                rating=rating,
                comment=comment,
                semester=student.semester,
                academic_year=Review.get_current_academic_year(),
                is_blocked=not is_clean,
            )

            if not is_clean:
                BlockedReview.objects.create(
                    review=review,
                    reason=f"Profanity detected: {', '.join(matched)}",
                    matched_words=matched,
                )
                ActivityLog.log(
                    request.user, ActivityLog.Action.REVIEW_BLOCKED,
                    f"Review blocked for profanity — lecturer: {lecturer.employee_id}",
                    request=request,
                    extra_data={'matched_words': matched, 'lecturer': lecturer.employee_id},
                )
                messages.warning(
                    request,
                    "Your review was submitted but flagged for inappropriate language "
                    "and is pending HOD review."
                )
            else:
                ActivityLog.log(
                    request.user, ActivityLog.Action.REVIEW,
                    f"Review submitted — lecturer: {lecturer.employee_id}, rating: {rating}★",
                    request=request,
                    extra_data={'lecturer': lecturer.employee_id, 'rating': rating},
                )
                messages.success(request, "Review submitted successfully. Thank you!")

        return redirect('reviews:my_reviews')

    return render(request, 'reviews/submit.html', {'form': form, 'student': student})


# ─── STUDENT: MY REVIEWS ──────────────────────────────────────────────────────

@student_required
def my_reviews(request):
    reviews = Review.objects.filter(
        student=request.user.student_profile
    ).select_related('lecturer__user').order_by('-submitted_at')
    return render(request, 'reviews/my_reviews.html', {'reviews': reviews})


# ─── LECTURER: VIEW RATINGS ───────────────────────────────────────────────────

@lecturer_required
def lecturer_reviews(request):
    lecturer = request.user.lecturer_profile
    reviews  = Review.objects.filter(
        lecturer=lecturer, is_blocked=False
    ).select_related('student__user').order_by('-submitted_at')

    paginator = Paginator(reviews, 10)
    page = paginator.get_page(request.GET.get('page'))

    avg = lecturer.average_rating
    distribution = {i: reviews.filter(rating=i).count() for i in range(1, 6)}

    return render(request, 'reviews/lecturer_reviews.html', {
        'reviews':      page,
        'avg_rating':   avg,
        'total':        lecturer.total_reviews,
        'distribution': distribution,
    })


# ─── HOD: ALL REVIEWS ─────────────────────────────────────────────────────────

@hod_required
def hod_reviews(request):
    dept     = request.user.hod_profile.department
    lecturers = Lecturer.objects.filter(department=dept, is_active=True)

    reviews  = Review.objects.filter(
        lecturer__in=lecturers, is_blocked=False
    ).select_related('student__user', 'lecturer__user').order_by('-submitted_at')

    blocked = BlockedReview.objects.filter(
        review__lecturer__in=lecturers
    ).select_related('review__student__user', 'review__lecturer__user').order_by('-blocked_at')

    return render(request, 'reviews/hod_reviews.html', {
        'reviews':    reviews,
        'blocked':    blocked,
        'lecturers':  lecturers,
    })


# ─── ADMIN: ALL REVIEWS ───────────────────────────────────────────────────────

@admin_required
def admin_reviews(request):
    reviews = Review.objects.select_related(
        'student__user', 'lecturer__user', 'lecturer__department'
    ).all().order_by('-submitted_at')

    blocked = BlockedReview.objects.select_related(
        'review__student__user', 'review__lecturer__user'
    ).all().order_by('-blocked_at')

    paginator = Paginator(reviews, 20)
    page = paginator.get_page(request.GET.get('page'))

    return render(request, 'reviews/admin_reviews.html', {
        'reviews': page,
        'blocked': blocked,
        'total_reviews':  Review.objects.count(),
        'total_blocked':  BlockedReview.objects.count(),
    })


# ─── ADMIN: UNBLOCK A REVIEW ──────────────────────────────────────────────────

@admin_required
@require_POST
def unblock_review(request, pk):
    review = get_object_or_404(Review, pk=pk, is_blocked=True)
    review.is_blocked = False
    review.save()
    BlockedReview.objects.filter(review=review).delete()
    messages.success(request, "Review unblocked successfully.")
    return redirect('reviews:admin_reviews')
