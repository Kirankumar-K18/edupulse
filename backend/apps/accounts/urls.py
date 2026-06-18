from django.urls import path, reverse_lazy
from . import views
from django.contrib.auth import views as auth_views
app_name = 'accounts'

urlpatterns = [
    # Auth
    path('login/',    views.login_view,    name='login'),
    path('logout/',   views.logout_view,   name='logout'),
    path('register/', views.register_student, name='register'),

    # Profile
    path('profile/',          views.profile_view,    name='profile'),
    path('change-password/',  views.change_password, name='change_password'),

    # Admin: Departments
    path('departments/',              views.manage_departments, name='manage_departments'),
    path('departments/create/',       views.create_department,  name='create_department'),
    path('departments/<int:pk>/edit/',   views.edit_department,  name='edit_department'),
    path('departments/<int:pk>/delete/', views.delete_department, name='delete_department'),

    # Admin: HODs
    path('hods/',              views.manage_hods,  name='manage_hods'),
    path('hods/create/',       views.create_hod,   name='create_hod'),
    path('hods/<int:pk>/delete/', views.delete_hod, name='delete_hod'),

    # Admin/HOD: Lecturers
    path('lecturers/',               views.manage_lecturers,  name='manage_lecturers'),
    path('lecturers/create/',        views.create_lecturer,   name='create_lecturer'),
    path('lecturers/<int:pk>/delete/', views.delete_lecturer, name='delete_lecturer'),

    # Admin/HOD: Students
    path('students/',               views.manage_students,  name='manage_students'),
    path('students/<int:pk>/delete/', views.delete_student, name='delete_student'),

    # Admin: Bad words
    path('bad-words/',              views.manage_bad_words, name='manage_bad_words'),
    path('bad-words/<int:pk>/delete/', views.delete_bad_word, name='delete_bad_word'),

    # Admin: Activity logs
    path('activity-logs/', views.activity_logs, name='activity_logs'),
    path(
        'password-reset/',
        views.brevo_password_reset,
        name='password_reset',
    ),

    path(
        'password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='accounts/password_reset_done.html'
        ),
        name='password_reset_done',
    ),

    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='accounts/password_reset_confirm.html',
            success_url=reverse_lazy('accounts:password_reset_complete'),
        ),
        name='password_reset_confirm',
    ),

    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='accounts/password_reset_complete.html'
        ),
        name='password_reset_complete',
    ),
]
