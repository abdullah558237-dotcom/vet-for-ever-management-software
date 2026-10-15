from django import forms
from .models import Medicine

class MedicineForm(forms.ModelForm):
    class Meta:
        model = Medicine
        fields = [
            'name', 'generic_name', 'category', 'unit_type',
            'batch_number', 'cost_price', 'selling_price',
            'quantity_in_stock', 'reorder_threshold', 'expiry_date', 'supplier'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Amoxil 250mg'}),
            'generic_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Amoxicillin Trihydrate'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'unit_type': forms.Select(attrs={'class': 'form-select'}),
            'batch_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. B-90214'}),
            'cost_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'selling_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'quantity_in_stock': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'reorder_threshold': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'supplier': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Distributor Name'}),
        }


class RestockForm(forms.Form):
    quantity_to_add = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Units to add', 'value': 10})
    )
    new_batch_number = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'New Batch/Lot (Optional)'})
    )
    new_expiry_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    notes = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Supplier invoice or notes'})
    )
