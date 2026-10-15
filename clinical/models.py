from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from patients.models import Patient
from appointments.models import Appointment

class Consultation(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='consultations')
    veterinarian = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='consultations')
    appointment = models.OneToOneField(Appointment, on_delete=models.SET_NULL, null=True, blank=True, related_name='consultation')

    # 1. Vitals
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Weight in kg")
    temperature_c = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True, help_text="Body Temp in °C")
    heart_rate_bpm = models.PositiveIntegerField(null=True, blank=True, help_text="Heart rate (BPM)")

    # 2. SOAP Clinical Notes
    symptoms = models.TextField(help_text="Presenting complaints reported by owner")
    physical_examination = models.TextField(blank=True, help_text="Eyes, ears, abdomen, heart/lung auscultation")
    diagnosis = models.TextField(help_text="Primary clinical diagnosis")
    treatment_administered = models.TextField(blank=True, help_text="Injections, wound dressing, fluids administered in clinic")

    # 3. Follow-up
    home_care_advice = models.TextField(blank=True, help_text="Home instructions and diet")
    follow_up_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']

    def get_absolute_url(self):
        return reverse('consultation_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return f"Consultation: {self.patient.name} - {self.created_at.strftime('%Y-%m-%d')} by {self.veterinarian.username}"


class PrescriptionItem(models.Model):
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE, related_name='prescriptions')
    medicine_name = models.CharField(max_length=150, help_text="e.g. Amoxicillin, Meloxicam")
    dosage = models.CharField(max_length=100, help_text="e.g. 5ml, 1 tablet")
    frequency = models.CharField(max_length=100, help_text="e.g. Twice daily after meals")
    duration_days = models.PositiveIntegerField(default=5)
    instructions = models.CharField(max_length=255, blank=True, help_text="e.g. Store in fridge")


    def __str__(self):
        return f"{self.medicine_name} ({self.dosage}) - {self.frequency} x {self.duration_days}d"


class VaccineRecord(models.Model):
    COMMON_VACCINES = [
        ('Rabies', 'Rabies (Annual)'),
        ('DHPP', 'DHPP / 5-in-1 (Canine Distemper, Parvo)'),
        ('FVRCP', 'FVRCP / 3-in-1 (Feline Distemper)'),
        ('Bordetella', 'Bordetella (Kennel Cough)'),
        ('Deworming', 'Routine Deworming'),
        ('Leptospirosis', 'Leptospirosis'),
        ('Other', 'Other Specialized Vaccine'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='vaccinations')
    administered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    vaccine_name = models.CharField(max_length=100, choices=COMMON_VACCINES)
    batch_number = models.CharField(max_length=50, blank=True, help_text="Lot/Batch number")
    administered_date = models.DateField(default=timezone.now)
    next_due_date = models.DateField(db_index=True)
    notes = models.TextField(blank=True, help_text="Booster notes or remarks")
    reminder_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['next_due_date']

    @property
    def status_info(self):
        today = timezone.now().date()
        if today > self.next_due_date:
            days = (today - self.next_due_date).days
            return {'label': f'Overdue by {days}d', 'badge': 'bg-danger text-white', 'code': 'OVERDUE'}
        elif (self.next_due_date - today).days <= 14:
            days = (self.next_due_date - today).days
            return {'label': f'Due in {days}d', 'badge': 'bg-warning text-dark', 'code': 'DUE_SOON'}
        else:
            return {'label': 'Up to date', 'badge': 'bg-success text-white', 'code': 'UP_TO_DATE'}

    def __str__(self):
        return f"{self.vaccine_name} - {self.patient.name} (Due: {self.next_due_date})"
