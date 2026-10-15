from django.db import models
from django.conf import settings
from django.utils import timezone
from patients.models import Patient

class Appointment(models.Model):
    class VisitType(models.TextChoices):
        SCHEDULED = 'SCHEDULED', 'Scheduled Booking'
        WALK_IN = 'WALK_IN', 'Walk-In'
        EMERGENCY = 'EMERGENCY', 'Emergency'

    class Status(models.TextChoices):
        SCHEDULED = 'SCHEDULED', 'Scheduled'
        WAITING = 'WAITING', 'Waiting in Clinic'
        IN_CONSULTATION = 'IN_CONSULTATION', 'In Consultation'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELLED = 'CANCELLED', 'Cancelled'
        NO_SHOW = 'NO_SHOW', 'No Show'

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    veterinarian = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_appointments'
    )
    scheduled_date = models.DateField(default=timezone.now, db_index=True)
    scheduled_time = models.TimeField(null=True, blank=True)
    visit_type = models.CharField(max_length=20, choices=VisitType.choices, default=VisitType.SCHEDULED)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.WAITING, db_index=True)
    token_number = models.PositiveIntegerField(null=True, blank=True)
    reason = models.TextField(help_text="Symptoms, routine checkup, vaccination, etc.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['scheduled_date', 'token_number', 'scheduled_time', 'created_at']

    def save(self, *args, **kwargs):
        # Aaj ke din ka agla token auto-assign karein
        if not self.token_number and self.status in [self.Status.WAITING, self.Status.IN_CONSULTATION]:
            today_max = Appointment.objects.filter(
                scheduled_date=self.scheduled_date
            ).aggregate(models.Max('token_number'))['token_number__max']
            self.token_number = (today_max or 0) + 1
        super().save(*args, **kwargs)

    @property
    def badge_class(self):
        mapping = {
            self.Status.WAITING: 'bg-warning text-dark',
            self.Status.IN_CONSULTATION: 'bg-primary text-white',
            self.Status.COMPLETED: 'bg-success text-white',
            self.Status.SCHEDULED: 'bg-info text-dark',
            self.Status.CANCELLED: 'bg-danger text-white',
            self.Status.NO_SHOW: 'bg-secondary text-white',
        }
        return mapping.get(self.status, 'bg-secondary')

    def __str__(self):
        token_str = f"#{self.token_number} " if self.token_number else ""
        return f"{token_str}{self.patient.name} ({self.get_status_display()}) - {self.scheduled_date}"
