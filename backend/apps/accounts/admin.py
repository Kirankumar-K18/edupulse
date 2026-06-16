from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Student, Lecturer, HOD, Department, ActivityLog, BadWord


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display  = ['email', 'full_name', 'role', 'is_active', 'date_joined']
    list_filter   = ['role', 'is_active']
    search_fields = ['email', 'full_name']
    ordering      = ['-date_joined']
    fieldsets = (
        (None,       {'fields': ('email', 'password')}),
        ('Personal', {'fields': ('full_name', 'phone', 'profile_pic')}),
        ('Role',     {'fields': ('role',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {'fields': ('email', 'full_name', 'role', 'password1', 'password2')}),
    )


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'is_active', 'total_students', 'total_lecturers']


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display  = ['usn', 'user', 'department', 'section', 'semester', 'is_active']
    list_filter   = ['department', 'section', 'is_active']
    search_fields = ['usn', 'user__full_name', 'user__email']


@admin.register(Lecturer)
class LecturerAdmin(admin.ModelAdmin):
    list_display  = ['employee_id', 'user', 'department', 'designation', 'is_active']
    list_filter   = ['department', 'is_active']
    search_fields = ['employee_id', 'user__full_name']


@admin.register(HOD)
class HODAdmin(admin.ModelAdmin):
    list_display = ['user', 'department', 'is_active']


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display  = ['timestamp', 'user', 'action', 'is_success', 'ip_address']
    list_filter   = ['action', 'is_success']
    search_fields = ['user__email', 'description']
    readonly_fields = ['timestamp']


@admin.register(BadWord)
class BadWordAdmin(admin.ModelAdmin):
    list_display = ['word', 'added_by', 'is_active', 'created_at']
