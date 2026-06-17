from django import forms
from .models import Subject

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = [
            'name',
            'code',
            'department',
            'lecturer',
            'semester',
            'credits',
            'is_active'
        ]