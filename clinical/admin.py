from django.contrib import admin
from .models import Consultation, PrescriptionItem

class PrescriptionItemInline(admin.TabularInline):
    model = PrescriptionItem
    extra = 1

@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = ('patient', 'veterinarian', 'diagnosis', 'weight_kg', 'temperature_c', 'created_at')
    list_filter = ('created_at', 'veterinarian')
    search_fields = ('patient__name', 'diagnosis', 'symptoms')
    inlines = [PrescriptionItemInline]
from .models import VaccineRecord

@admin.register(VaccineRecord)
class VaccineRecordAdmin(admin.ModelAdmin):
    list_display = ('patient', 'vaccine_name', 'administered_date', 'next_due_date', 'batch_number')
    list_filter = ('vaccine_name', 'next_due_date', 'administered_date')
    search_fields = ('patient__name', 'vaccine_name', 'batch_number')
