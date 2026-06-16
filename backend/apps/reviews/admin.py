from django.contrib import admin
from .models import Review, BlockedReview

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display  = ['student', 'lecturer', 'rating', 'is_blocked', 'submitted_at']
    list_filter   = ['is_blocked', 'rating', 'lecturer__department']
    search_fields = ['student__usn', 'lecturer__employee_id']

@admin.register(BlockedReview)
class BlockedReviewAdmin(admin.ModelAdmin):
    list_display = ['review', 'blocked_at', 'reason']
    readonly_fields = ['blocked_at', 'matched_words']
