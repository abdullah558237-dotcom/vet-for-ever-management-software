from django.contrib import admin
from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'veterinarian' , 'scheduled_date', 'visit_type', 'status')
    list_filter = ('status', 'visit_type')

# Register your models here.
