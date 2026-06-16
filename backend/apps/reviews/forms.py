from django import forms
from .models import Review
from apps.accounts.models import Lecturer


class ReviewForm(forms.ModelForm):
    lecturer = forms.ModelChoiceField(
        queryset=Lecturer.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-select form-select-lg'}),
        empty_label='Select Lecturer',
    )
    rating = forms.ChoiceField(
        choices=[(i, f'{i} Star{"s" if i > 1 else ""}') for i in range(1, 6)],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input rating-radio'}),
    )
    comment = forms.CharField(
        max_length=1000,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Write your honest review here… (max 1000 characters)',
        }),
    )

    class Meta:
        model  = Review
        fields = ['lecturer', 'rating', 'comment']

    def __init__(self, *args, student=None, **kwargs):
        super().__init__(*args, **kwargs)
        if student:
            self.fields['lecturer'].queryset = Lecturer.objects.filter(
                department=student.department, is_active=True)
