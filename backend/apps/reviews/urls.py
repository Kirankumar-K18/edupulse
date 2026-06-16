from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('submit/',          views.submit_review,   name='submit'),
    path('my/',              views.my_reviews,       name='my_reviews'),
    path('lecturer/',        views.lecturer_reviews, name='lecturer'),
    path('hod/',             views.hod_reviews,      name='hod'),
    path('admin/',           views.admin_reviews,    name='admin_reviews'),
    path('unblock/<int:pk>/', views.unblock_review,  name='unblock'),
]
