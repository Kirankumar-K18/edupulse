from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    path('',              views.student_attendance, name='student'),
    path('mark/',         views.mark_attendance,    name='mark'),
    path('submit/',       views.submit_attendance,  name='submit'),
    path('edit/',         views.edit_attendance,    name='edit'),
    path('update/<int:pk>/', views.update_record,  name='update_record'),
    path('report/',       views.attendance_report,  name='report'),
    path('subjects/',     views.manage_subjects,    name='subjects'),
]
