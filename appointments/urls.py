from django.urls import path
from . import views

urlpatterns = [
    path('queue/', views.daily_queue, name='daily_queue'),
    path('schedule/', views.appointment_list, name='appointment_list'),
    path('book/', views.appointment_create, name='appointment_create'),
    path('walkin/', views.quick_walkin, name='quick_walkin'),
    path('<int:pk>/status/<str:new_status>/', views.update_status, name='update_appointment_status'),
]
