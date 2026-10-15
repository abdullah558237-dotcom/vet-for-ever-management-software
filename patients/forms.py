from django import forms
from .models import Owner, Patient

class OwnerForm(forms.ModelForm):
    class Meta:
        model = Owner
        fields = ['first_name', 'last_name', 'phone', 'email', 'address', 'emergency_contact']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '0300-1234567'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'client@example.com'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Street Address / City'}),
            'emergency_contact': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Secondary Contact'}),
        }


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = [
            'owner', 'name', 'species', 'breed', 'gender',
            'date_of_birth', 'color_markings', 'microchip_number',
            'photo', 'allergies_notes'
        ]
        widgets = {
            'owner': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Pet Name (e.g. Max)'}),
            'species': forms.Select(attrs={'class': 'form-select'}),
            'breed': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Golden Retriever, Persian'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'color_markings': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. White with brown spots'}),
            'microchip_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '15-digit Microchip ID'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
            'allergies_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Allergies or temperament'}),
        }
