from django.urls import path
from . import views

urlpatterns = [
    # Consultations
    path('start/<int:patient_id>/', views.consultation_start, name='consultation_start'),
    path('<int:pk>/', views.consultation_detail, name='consultation_detail'),
    path('<int:pk>/print/', views.prescription_print, name='prescription_print'),

    # Vaccinations & Follow-Ups
    path('vaccines/', views.vaccination_center, name='vaccination_center'),
    path('vaccines/record/<int:patient_id>/', views.vaccine_create, name='vaccine_create'),
    path('vaccines/passport/<int:patient_id>/', views.vaccine_passport_print, name='vaccine_passport_print'),
]
