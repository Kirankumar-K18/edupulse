"""
accounts/views.py
All authentication views: login (role-aware), register, logout,
profile, admin management of departments/HODs/lecturers/students.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST, require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.db import transaction
from django.conf import settings
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.conf import settings
from django.core.mail import send_mail
from .models import User, Student, Lecturer, HOD, Department, ActivityLog, BadWord
from .forms import (
    LoginForm, StudentLoginForm, StudentRegistrationForm,
    LecturerCreationForm, HODCreationForm, DepartmentForm, ProfileUpdateForm,
    CustomPasswordChangeForm,
)
from .decorators import admin_required, hod_required, lecturer_required, student_required, admin_or_hod_required


# ─── HOME ─────────────────────────────────────────────────────────────────────

def home(request):
    if request.user.is_authenticated:
        return redirect(request.user.get_dashboard_url())
    return redirect('accounts:login')


# ─── LOGIN ────────────────────────────────────────────────────────────────────

@require_http_methods(['GET', 'POST'])
def login_view(request):
    if request.user.is_authenticated:
        return redirect(request.user.get_dashboard_url())

    # Check if this is student login (query param or form field)
    login_type = request.GET.get('type', 'staff')

    if request.method == 'POST':
        login_type = request.POST.get('login_type', 'staff')

        if login_type == 'student':
            form = StudentLoginForm(request.POST)
            if form.is_valid():
                email     = form.cleaned_data['email']
                usn       = form.cleaned_data['usn'].upper()
                dept      = form.cleaned_data['department']
                section   = form.cleaned_data['section'].upper()
                password  = form.cleaned_data['password']

                user = authenticate(request, email=email, password=password)
                if user and user.role == User.Role.STUDENT:
                    try:
                        profile = user.student_profile
                        if (profile.usn == usn and
                                profile.department == dept and
                                profile.section.upper() == section):
                            _do_login(request, user)
                            ActivityLog.log(user, ActivityLog.Action.LOGIN,
                                            f"Student login: {email}", request=request)
                            return redirect(user.get_dashboard_url())
                        else:
                            messages.error(request, "USN, department, or section does not match.")
                    except Student.DoesNotExist:
                        messages.error(request, "Student profile not found.")
                else:
                    messages.error(request, "Invalid credentials or not a student account.")
                    ActivityLog.log(None, ActivityLog.Action.LOGIN_FAILED,
                                    f"Failed student login: {email}", request=request, is_success=False)
        else:
            form = LoginForm(request.POST)
            if form.is_valid():
                email    = form.cleaned_data['email']
                password = form.cleaned_data['password']
                user = authenticate(request, email=email, password=password)
                if user and user.is_active:
                    _do_login(request, user)
                    ActivityLog.log(user, ActivityLog.Action.LOGIN,
                                    f"Login: {email}", request=request)
                    return redirect(user.get_dashboard_url())
                else:
                    messages.error(request, "Invalid email or password.")
                    ActivityLog.log(None, ActivityLog.Action.LOGIN_FAILED,
                                    f"Failed login: {email}", request=request, is_success=False)
    else:
        form = StudentLoginForm() if login_type == 'student' else LoginForm()

    return render(request, 'accounts/login.html', {
        'form': form,
        'login_type': login_type,
    })


def _do_login(request, user):
    login(request, user)
    if not request.POST.get('remember_me'):
        request.session.set_expiry(0)  # session expires on browser close


# ─── LOGOUT ───────────────────────────────────────────────────────────────────

@login_required
def logout_view(request):
    ActivityLog.log(request.user, ActivityLog.Action.LOGOUT,
                    f"Logout: {request.user.email}", request=request)
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('accounts:login')


# ─── REGISTER STUDENT ─────────────────────────────────────────────────────────

@require_http_methods(['GET', 'POST'])
def register_student(request):
    if request.user.is_authenticated:
        return redirect(request.user.get_dashboard_url())

    form = StudentRegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        try:
            with transaction.atomic():
                cd = form.cleaned_data
                user = User.objects.create_user(
                    email=cd['email'],
                    password=cd['password'],
                    full_name=cd['full_name'],
                    role=User.Role.STUDENT,
                    phone=cd.get('phone', ''),
                )
                Student.objects.create(
                    user=user,
                    usn=cd['usn'],
                    department=cd['department'],
                    section=cd['section'].upper(),
                    semester=cd['semester'],
                    batch_year=cd['batch_year'],
                )
                ActivityLog.log(None, ActivityLog.Action.USER_CREATED,
                                f"Student registered: {user.email}", request=request)
                messages.success(request, "Account created! Please login.")
                return redirect('accounts:login')
        except Exception as e:
            messages.error(request, f"Registration failed: {e}")

    return render(request, 'accounts/register.html', {'form': form})


# ─── PROFILE ──────────────────────────────────────────────────────────────────

@login_required
def profile_view(request):
    form = ProfileUpdateForm(request.POST or None, request.FILES or None, instance=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        ActivityLog.log(request.user, ActivityLog.Action.USER_UPDATED,
                        "Profile updated", request=request)
        messages.success(request, "Profile updated successfully.")
        return redirect('accounts:profile')
    return render(request, 'accounts/profile.html', {'form': form})


@login_required
def change_password(request):
    form = CustomPasswordChangeForm(request.user, request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        ActivityLog.log(request.user, ActivityLog.Action.PASSWORD_CHANGE,
                        "Password changed", request=request)
        messages.success(request, "Password changed. Please log in again.")
        return redirect('accounts:login')
    return render(request, 'accounts/change_password.html', {'form': form})


# ─── ADMIN: DEPARTMENTS ───────────────────────────────────────────────────────

@admin_required
def manage_departments(request):
    departments = Department.objects.all().order_by('name')
    return render(request, 'accounts/manage_departments.html', {'departments': departments})


@admin_required
def create_department(request):
    form = DepartmentForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        dept = form.save()
        ActivityLog.log(request.user, ActivityLog.Action.DEPT_CREATED,
                        f"Department created: {dept.name}", request=request)
        messages.success(request, f"Department '{dept.name}' created.")
        return redirect('accounts:manage_departments')
    return render(request, 'accounts/department_form.html', {'form': form, 'title': 'Create Department'})


@admin_required
def edit_department(request, pk):
    dept = get_object_or_404(Department, pk=pk)
    form = DepartmentForm(request.POST or None, instance=dept)
    if request.method == 'POST' and form.is_valid():
        form.save()
        ActivityLog.log(request.user, ActivityLog.Action.DEPT_UPDATED,
                        f"Department updated: {dept.name}", request=request)
        messages.success(request, "Department updated.")
        return redirect('accounts:manage_departments')
    return render(request, 'accounts/department_form.html', {'form': form, 'title': 'Edit Department', 'dept': dept})


@admin_required
@require_POST
def delete_department(request, pk):
    dept = get_object_or_404(Department, pk=pk)
    name = dept.name
    dept.delete()
    ActivityLog.log(request.user, ActivityLog.Action.DEPT_UPDATED,
                    f"Department deleted: {name}", request=request)
    messages.success(request, f"Department '{name}' deleted.")
    return redirect('accounts:manage_departments')


# ─── ADMIN: HODs ──────────────────────────────────────────────────────────────

@admin_required
def manage_hods(request):
    hods = HOD.objects.select_related('user', 'department').all()
    return render(request, 'accounts/manage_hods.html', {'hods': hods})


@admin_required
def create_hod(request):
    form = HODCreationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        try:
            with transaction.atomic():
                cd = form.cleaned_data
                user = User.objects.create_user(
                    email=cd['email'],
                    password=cd['password'],
                    full_name=cd['full_name'],
                    role=User.Role.HOD,
                    phone=cd.get('phone', ''),
                    is_staff=True,
                )
                HOD.objects.create(user=user, department=cd['department'])
                ActivityLog.log(request.user, ActivityLog.Action.USER_CREATED,
                                f"HOD created: {user.email} for {cd['department']}", request=request)
                messages.success(request, f"HOD account created for {user.full_name}.")
                return redirect('accounts:manage_hods')
        except Exception as e:
            messages.error(request, f"Error: {e}")
    return render(request, 'accounts/user_form.html', {'form': form, 'title': 'Create HOD', 'role': 'HOD'})


@admin_required
@require_POST
def delete_hod(request, pk):
    hod = get_object_or_404(HOD, pk=pk)
    name = hod.user.full_name
    hod.user.is_active = False
    hod.user.save()
    hod.is_active = False
    hod.save()
    ActivityLog.log(request.user, ActivityLog.Action.USER_DELETED,
                    f"HOD deactivated: {name}", request=request)
    messages.success(request, f"HOD '{name}' deactivated.")
    return redirect('accounts:manage_hods')


# ─── HOD/ADMIN: LECTURERS ─────────────────────────────────────────────────────

@admin_or_hod_required
def manage_lecturers(request):
    qs = Lecturer.objects.select_related('user', 'department')
    if request.user.is_hod:
        qs = qs.filter(department=request.user.hod_profile.department)
    return render(request, 'accounts/manage_lecturers.html', {'lecturers': qs})


@admin_or_hod_required
def create_lecturer(request):
    form = LecturerCreationForm(request.POST or None)
    # Lock department for HOD
    if request.user.is_hod:
        form.fields['department'].queryset = Department.objects.filter(
            pk=request.user.hod_profile.department.pk)
        form.fields['department'].initial = request.user.hod_profile.department
    if request.method == 'POST' and form.is_valid():
        try:
            with transaction.atomic():
                cd = form.cleaned_data
                # Ensure HOD can only create in their dept
                if request.user.is_hod and cd['department'] != request.user.hod_profile.department:
                    messages.error(request, "You can only create lecturers in your department.")
                    return render(request, 'accounts/user_form.html', {'form': form, 'title': 'Create Lecturer'})
                user = User.objects.create_user(
                    email=cd['email'],
                    password=cd['password'],
                    full_name=cd['full_name'],
                    role=User.Role.LECTURER,
                    phone=cd.get('phone', ''),
                )
                Lecturer.objects.create(
                    user=user,
                    employee_id=cd['employee_id'],
                    department=cd['department'],
                    designation=cd.get('designation', 'Assistant Professor'),
                    qualification=cd.get('qualification', ''),
                    experience_years=cd.get('experience_years', 0),
                )
                ActivityLog.log(request.user, ActivityLog.Action.USER_CREATED,
                                f"Lecturer created: {user.email}", request=request)
                messages.success(request, f"Lecturer account created for {user.full_name}.")
                return redirect('accounts:manage_lecturers')
        except Exception as e:
            messages.error(request, f"Error: {e}")
    return render(request, 'accounts/user_form.html', {'form': form, 'title': 'Create Lecturer', 'role': 'Lecturer'})


@admin_or_hod_required
@require_POST
def delete_lecturer(request, pk):
    lec = get_object_or_404(Lecturer, pk=pk)
    if request.user.is_hod and lec.department != request.user.hod_profile.department:
        messages.error(request, "Access denied.")
        return redirect('accounts:manage_lecturers')
    name = lec.user.full_name
    lec.user.is_active = False
    lec.user.save()
    lec.is_active = False
    lec.save()
    ActivityLog.log(request.user, ActivityLog.Action.USER_DELETED,
                    f"Lecturer deactivated: {name}", request=request)
    messages.success(request, f"Lecturer '{name}' deactivated.")
    return redirect('accounts:manage_lecturers')


# ─── HOD/ADMIN: STUDENTS ──────────────────────────────────────────────────────

@admin_or_hod_required
def manage_students(request):
    qs = Student.objects.select_related('user', 'department')
    if request.user.is_hod:
        qs = qs.filter(department=request.user.hod_profile.department)
    paginator = Paginator(qs, 25)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'accounts/manage_students.html', {'students': page})


@admin_or_hod_required
@require_POST
def delete_student(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.user.is_hod and student.department != request.user.hod_profile.department:
        messages.error(request, "Access denied.")
        return redirect('accounts:manage_students')
    name = student.user.full_name
    student.user.is_active = False
    student.user.save()
    student.is_active = False
    student.save()
    ActivityLog.log(request.user, ActivityLog.Action.USER_DELETED,
                    f"Student deactivated: {name}", request=request)
    messages.success(request, f"Student '{name}' deactivated.")
    return redirect('accounts:manage_students')


# ─── ADMIN: BAD WORDS ─────────────────────────────────────────────────────────

@admin_required
def manage_bad_words(request):
    words = BadWord.objects.all()
    if request.method == 'POST':
        word = request.POST.get('word', '').strip().lower()
        if word:
            bw, created = BadWord.objects.get_or_create(word=word)
            if created:
                bw.added_by = request.user
                bw.save()
                ActivityLog.log(request.user, ActivityLog.Action.BADWORD_ADDED,
                                f"Bad word added: {word}", request=request)
                messages.success(request, f"Word '{word}' added to filter list.")
            else:
                messages.warning(request, f"Word '{word}' already exists.")
        return redirect('accounts:manage_bad_words')
    return render(request, 'accounts/manage_bad_words.html', {'words': words})


@admin_required
@require_POST
def delete_bad_word(request, pk):
    bw = get_object_or_404(BadWord, pk=pk)
    bw.delete()
    messages.success(request, f"Word '{bw.word}' removed.")
    return redirect('accounts:manage_bad_words')


# ─── ADMIN: ACTIVITY LOGS ─────────────────────────────────────────────────────

@admin_required
def activity_logs(request):
    logs = ActivityLog.objects.select_related('user').all()
    # Filtering
    action_filter = request.GET.get('action', '')
    if action_filter:
        logs = logs.filter(action=action_filter)
    success_filter = request.GET.get('success', '')
    if success_filter:
        logs = logs.filter(is_success=(success_filter == '1'))

    paginator = Paginator(logs, 50)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'accounts/activity_logs.html', {
        'logs': page,
        'action_choices': ActivityLog.Action.choices,
        'current_action': action_filter,
    })
def email_debug(request):
    return HttpResponse(
        f"HOST={settings.EMAIL_HOST}<br>"
        f"PORT={settings.EMAIL_PORT}<br>"
        f"USER={settings.EMAIL_HOST_USER}<br>"
        f"TLS={settings.EMAIL_USE_TLS}"
    )


from django.core.mail import send_mail
from django.http import HttpResponse
from django.conf import settings
import traceback

def test_email(request):
    try:
        send_mail(
            "Test Email",
            "Hello from EduPulse",
            settings.DEFAULT_FROM_EMAIL,
            ["smartlecturerreview18@gmail.com"],
            fail_silently=False,
        )
        return HttpResponse("SUCCESS")
    except Exception as e:
        return HttpResponse(
            f"<pre>{type(e).__name__}\n\n{str(e)}\n\n{traceback.format_exc()}</pre>"
        )