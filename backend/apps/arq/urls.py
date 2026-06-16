from django.urls import path
from . import views

app_name = 'arq'

urlpatterns = [
    path('',              views.arq_home,        name='home'),
    path('run/',          views.run_arq,          name='run'),
    path('result/<int:pk>/',      views.arq_result,      name='result'),
    path('result/<int:pk>/json/', views.arq_result_json, name='result_json'),
]
