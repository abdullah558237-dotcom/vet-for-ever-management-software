from django import forms
from django.forms import inlineformset_factory
from .models import Invoice, InvoiceItem

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['discount', 'payment_method', 'paid_amount', 'notes']
        widgets = {
            'discount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
            'paid_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
            'notes': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional invoice remarks'}),
        }

class PaymentCollectionForm(forms.ModelForm):
    additional_payment = forms.DecimalField(
        max_digits=10, decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Enter amount paid'})
    )

    class Meta:
        model = Invoice
        fields = ['payment_method']
        widgets = {
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
        }

InvoiceItemFormSet = inlineformset_factory(
    Invoice,
    InvoiceItem,
    fields=['item_type', 'description', 'quantity', 'unit_price'],
    extra=4,
    can_delete=True,
    widgets={
        'item_type': forms.Select(attrs={'class': 'form-select form-select-sm'}),
        'description': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Service or Item name'}),
        'quantity': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'value': 1, 'min': 1}),
        'unit_price': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Price (Rs.)', 'step': '0.01'}),
    }
)
