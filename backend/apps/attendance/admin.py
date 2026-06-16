from django.contrib import admin
from .models import Subject, AttendanceRecord

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display  = ['code', 'name', 'department', 'lecturer', 'semester', 'is_active']
    list_filter   = ['department', 'semester', 'is_active']
    search_fields = ['code', 'name']

@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display  = ['student', 'subject', 'date', 'status', 'lecturer']
    list_filter   = ['status', 'subject__department', 'date']
    search_fields = ['student__usn', 'student__user__full_name']
    date_hierarchy = 'date'
