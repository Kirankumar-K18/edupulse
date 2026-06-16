# context_processors.py
def user_role_context(request):
    if request.user.is_authenticated:
        return {
            'user_role': request.user.role,
            'is_admin': request.user.is_admin,
            'is_hod': request.user.is_hod,
            'is_lecturer': request.user.is_lecturer,
            'is_student': request.user.is_student,
        }
    return {}
