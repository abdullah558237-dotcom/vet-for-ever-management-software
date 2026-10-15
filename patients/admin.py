from django.contrib import admin
from django.utils.html import format_html
from .models import Owner, Patient

class PatientInline(admin.TabularInline):
    model = Patient
    extra = 0
    fields = ('name', 'species', 'breed', 'gender', 'date_of_birth')

@admin.register(Owner)
class OwnerAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'phone', 'email', 'patient_count', 'created_at')
    search_fields = ('first_name', 'last_name', 'phone', 'email')
    inlines = [PatientInline]

    def patient_count(self, obj):
        return obj.patients.count()
    patient_count.short_description = 'Pets'

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('photo_preview', 'name', 'species', 'breed', 'owner', 'age_display', 'microchip_number')
    list_filter = ('species', 'gender', 'created_at')
    search_fields = ('name', 'breed', 'microchip_number', 'owner__first_name', 'owner__phone')

    def photo_preview(self, obj):
        if obj.photo:
            return format_html('<img src="{}" width="40" height="40" style="object-fit:cover; border-radius:50%;" />', obj.photo.url)
        return "No photo"
    photo_preview.short_description = 'Photo'
