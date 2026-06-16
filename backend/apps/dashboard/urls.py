from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('',          views.dashboard_redirect, name='redirect'),
    path('admin/',    views.admin_dashboard,     name='admin'),
    path('hod/',      views.hod_dashboard,       name='hod'),
    path('lecturer/', views.lecturer_dashboard,  name='lecturer'),
    path('student/',  views.student_dashboard,   name='student'),
]
