from django import forms
from django.utils import timezone
from .models import Appointment
from django.contrib.auth import get_user_model

User = get_user_model()

class AppointmentBookingForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['patient', 'veterinarian', 'scheduled_date', 'scheduled_time', 'visit_type', 'reason']
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-select'}),
            'veterinarian': forms.Select(attrs={'class': 'form-select'}),
            'scheduled_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'scheduled_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'visit_type': forms.Select(attrs={'class': 'form-select'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Reason for consultation...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if hasattr(User, 'Role'):
            self.fields['veterinarian'].queryset = User.objects.filter(role=User.Role.VET) | User.objects.filter(is_superuser=True)


class QuickWalkInForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['patient', 'veterinarian', 'reason']
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-select'}),
            'veterinarian': forms.Select(attrs={'class': 'form-select'}),
            'reason': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Symptoms / Quick reason'}),
        }
