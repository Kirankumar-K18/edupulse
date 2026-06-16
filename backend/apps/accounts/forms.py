"""
accounts/forms.py
All authentication and user management forms with strong validation.
"""

import re
from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.conf import settings
from .models import User, Student, Lecturer, HOD, Department


COLLEGE_DOMAIN = getattr(settings, 'COLLEGE_EMAIL_DOMAIN', 'college.edu')


def validate_college_email(email):
    if not email.lower().endswith(f'@{COLLEGE_DOMAIN}'):
        raise forms.ValidationError(f"Only @{COLLEGE_DOMAIN} email addresses are allowed.")
    return email.lower()


def validate_strong_password(password):
    if len(password) < 8:
        raise forms.ValidationError("Password must be at least 8 characters.")
    if not re.search(r'[A-Z]', password):
        raise forms.ValidationError("Password must contain at least one uppercase letter.")
    if not re.search(r'[a-z]', password):
        raise forms.ValidationError("Password must contain at least one lowercase letter.")
    if not re.search(r'\d', password):
        raise forms.ValidationError("Password must contain at least one digit.")
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise forms.ValidationError("Password must contain at least one special character.")
    return password


# ─── LOGIN ────────────────────────────────────────────────────────────────────

class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'your@college.edu',
            'autocomplete': 'email',
        }),
        label='College Email',
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Password',
            'autocomplete': 'current-password',
        }),
    )
    remember_me = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

    def clean_email(self):
        email = self.cleaned_data.get('email', '').lower()

        from .models import User

        # Allow admin accounts to use any email
        if User.objects.filter(
            email=email,
            role=User.Role.ADMIN
        ).exists():
            return email

        return validate_college_email(email)

# ─── STUDENT LOGIN (USN-based) ────────────────────────────────────────────────

class StudentLoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'your@college.edu',
        }),
        label='College Email',
    )
    usn = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'e.g. 1XX21CS001',
        }),
        label='USN',
    )
    department = forms.ModelChoiceField(
        queryset=Department.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-select form-select-lg'}),
        empty_label='Select Department',
    )
    section = forms.CharField(
        max_length=5,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'e.g. A',
        }),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Password',
        }),
    )

    def clean_email(self):
        return validate_college_email(self.cleaned_data.get('email', ''))


# ─── REGISTER STUDENT ─────────────────────────────────────────────────────────

class StudentRegistrationForm(forms.Form):
    full_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'your@college.edu'}),
    )
    usn = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'USN'}),
        label='USN',
    )
    department = forms.ModelChoiceField(
        queryset=Department.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label='Select Department',
    )
    section = forms.CharField(
        max_length=5,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Section (A/B/C)'}),
    )
    semester = forms.IntegerField(
        min_value=1, max_value=8,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '1-8'}),
    )
    batch_year = forms.IntegerField(
        min_value=2015, max_value=2030,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '2023'}),
    )
    phone = forms.CharField(
        max_length=15, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone (optional)'}),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}),
    )

    def clean_email(self):
        return validate_college_email(self.cleaned_data.get('email', ''))

    def clean_password(self):
        return validate_strong_password(self.cleaned_data.get('password', ''))

    def clean_usn(self):
        usn = self.cleaned_data.get('usn', '').upper()
        if Student.objects.filter(usn=usn).exists():
            raise forms.ValidationError("A student with this USN already exists.")
        return usn

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password')
        p2 = cleaned.get('confirm_password')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords do not match.")
        email = cleaned.get('email', '')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return cleaned


# ─── HOD/LECTURER CREATION (by admin/hod) ────────────────────────────────────

class LecturerCreationForm(forms.Form):
    full_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    employee_id = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-control'}), label='Employee ID')
    department = forms.ModelChoiceField(
        queryset=Department.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label='Select Department',
    )
    designation = forms.CharField(max_length=100, initial='Assistant Professor', widget=forms.TextInput(attrs={'class': 'form-control'}))
    qualification = forms.CharField(max_length=200, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    experience_years = forms.IntegerField(min_value=0, initial=0, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(max_length=15, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def clean_email(self):
        return validate_college_email(self.cleaned_data.get('email', ''))

    def clean_employee_id(self):
        eid = self.cleaned_data.get('employee_id', '').upper()
        if Lecturer.objects.filter(employee_id=eid).exists():
            raise forms.ValidationError("Employee ID already exists.")
        return eid

    def clean(self):
        cleaned = super().clean()
        email = cleaned.get('email', '')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return cleaned


class HODCreationForm(forms.Form):
    full_name  = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email      = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    department = forms.ModelChoiceField(
        queryset=Department.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label='Select Department',
    )
    phone    = forms.CharField(max_length=15, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def clean_email(self):
        return validate_college_email(self.cleaned_data.get('email', ''))

    def clean_department(self):
        dept = self.cleaned_data.get('department')
        if dept and HOD.objects.filter(department=dept, is_active=True).exists():
            raise forms.ValidationError(f"{dept.name} already has an active HOD.")
        return dept

    def clean(self):
        cleaned = super().clean()
        email = cleaned.get('email', '')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return cleaned


# ─── DEPARTMENT FORM ──────────────────────────────────────────────────────────

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'code', 'description', 'is_active']
        widgets = {
            'name':        forms.TextInput(attrs={'class': 'form-control'}),
            'code':        forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active':   forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


# ─── PROFILE UPDATE ───────────────────────────────────────────────────────────

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['full_name', 'phone', 'profile_pic']
        widgets = {
            'full_name':   forms.TextInput(attrs={'class': 'form-control'}),
            'phone':       forms.TextInput(attrs={'class': 'form-control'}),
            'profile_pic': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


# ─── CHANGE PASSWORD ──────────────────────────────────────────────────────────

class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
