from django import forms
from django.forms import inlineformset_factory
from .models import Consultation, PrescriptionItem

class ConsultationForm(forms.ModelForm):
    class Meta:
        model = Consultation
        fields = [
            'weight_kg', 'temperature_c', 'heart_rate_bpm',
            'symptoms', 'physical_examination', 'diagnosis',
            'treatment_administered', 'home_care_advice', 'follow_up_date'
        ]
        widgets = {
            'weight_kg': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'e.g. 12.5'}),
            'temperature_c': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': 'e.g. 38.5'}),
            'heart_rate_bpm': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 110'}),
            'symptoms': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Chief complaints...'}),
            'physical_examination': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'General exam findings...'}),
            'diagnosis': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Clinical diagnosis...'}),
            'treatment_administered': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'In-clinic meds, injections, fluids...'}),
            'home_care_advice': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Diet and care advice...'}),
            'follow_up_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

PrescriptionFormSet = inlineformset_factory(
    Consultation,
    PrescriptionItem,
    fields=['medicine_name', 'dosage', 'frequency', 'duration_days', 'instructions'],
    extra=3,
    can_delete=True,
    widgets={
        'medicine_name': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Medicine Name'}),
        'dosage': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Dosage (e.g. 1 tab)'}),
        'frequency': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Frequency (e.g. 2x daily)'}),
        'duration_days': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Days'}),
        'instructions': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Instructions'}),
    }
)
from .models import VaccineRecord

class VaccineRecordForm(forms.ModelForm):
    class Meta:
        model = VaccineRecord
        fields = ['vaccine_name', 'batch_number', 'administered_date', 'next_due_date', 'notes']
        widgets = {
            'vaccine_name': forms.Select(attrs={'class': 'form-select'}),
            'batch_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. LOT-98234-A'}),
            'administered_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'next_due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Manufacturer brand, dose number, or remarks'}),
        }
