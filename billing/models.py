from django.db import models
from django.conf import settings
from django.utils import timezone
from patients.models import Patient, Owner
from clinical.models import Consultation

class Invoice(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending (Unpaid)'
        PARTIALLY_PAID = 'PARTIALLY_PAID', 'Partially Paid'
        PAID = 'PAID', 'Fully Paid'
        CANCELLED = 'CANCELLED', 'Cancelled'

    class PaymentMethod(models.TextChoices):
        CASH = 'CASH', 'Cash'
        CARD = 'CARD', 'Credit / Debit Card'
        ONLINE = 'ONLINE', 'Online Transfer / EasyPaisa / JazzCash'
        UNPAID = 'UNPAID', 'Pending Payment'

    invoice_number = models.CharField(max_length=30, unique=True, default='', blank=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='invoices', null=True, blank=True)
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE, related_name='invoices', null=True, blank=True)
    consultation = models.OneToOneField(Consultation, on_delete=models.SET_NULL, null=True, blank=True, related_name='invoice')
    billed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    balance_due = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices, default=PaymentMethod.UNPAID)
    notes = models.TextField(blank=True, default='', help_text="Payment remarks or client notes")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            year = timezone.now().year
            last_inv = Invoice.objects.filter(invoice_number__startswith=f"INV-{year}").order_by('-id').first()
            if last_inv:
                try:
                    last_seq = int(last_inv.invoice_number.split('-')[-1])
                    new_seq = last_seq + 1
                except (ValueError, IndexError):
                    new_seq = 1
            else:
                new_seq = 1
            self.invoice_number = f"INV-{year}-{new_seq:04d}"

        self.total_amount = max(self.subtotal - self.discount, 0.00)
        self.balance_due = max(self.total_amount - self.paid_amount, 0.00)

        if self.paid_amount >= self.total_amount and self.total_amount > 0:
            self.status = self.Status.PAID
        elif self.paid_amount > 0:
            self.status = self.Status.PARTIALLY_PAID
        elif self.status != self.Status.CANCELLED:
            self.status = self.Status.PENDING

        super().save(*args, **kwargs)

    @property
    def badge_class(self):
        mapping = {
            self.Status.PAID: 'bg-success text-white',
            self.Status.PARTIALLY_PAID: 'bg-warning text-dark',
            self.Status.PENDING: 'bg-danger text-white',
            self.Status.CANCELLED: 'bg-secondary text-white',
        }
        return mapping.get(self.status, 'bg-secondary')

    def __str__(self):
        p_name = self.patient.name if self.patient else "Walk-in"
        return f"{self.invoice_number} - {p_name} - Rs. {self.total_amount}"


class InvoiceItem(models.Model):
    class ItemType(models.TextChoices):
        CONSULTATION = 'CONSULTATION', 'Consultation / Exam Fee'
        TREATMENT = 'TREATMENT', 'Treatment / Procedure'
        SURGERY = 'SURGERY', 'Surgery'
        MEDICATION = 'MEDICATION', 'Medicine / Pharmacy'
        VACCINE = 'VACCINE', 'Vaccination'
        LAB = 'LAB', 'Laboratory Test'
        OTHER = 'OTHER', 'Other Service'

    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    item_type = models.CharField(max_length=20, choices=ItemType.choices, default=ItemType.CONSULTATION)
    description = models.CharField(max_length=200, default='', help_text="Item description")
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.description} ({self.quantity} x {self.unit_price})"
