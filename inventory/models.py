from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

class Medicine(models.Model):
    class Category(models.TextChoices):
        ANTIBIOTIC = 'ANTIBIOTIC', 'Antibiotic'
        PAIN_RELIEF = 'PAIN_RELIEF', 'Pain Relief / NSAID'
        VACCINE = 'VACCINE', 'Vaccine'
        DEWORMER = 'DEWORMER', 'Dewormer / Parasiticide'
        SURGICAL = 'SURGICAL', 'Surgical & Wound Care'
        NUTRITION = 'NUTRITION', 'Supplements & Diet'
        OTHER = 'OTHER', 'General Consumable'

    class UnitType(models.TextChoices):
        TABLET = 'TABLET', 'Tablet(s)'
        VIAL_ML = 'VIAL_ML', 'Vial (ml)'
        BOTTLE = 'BOTTLE', 'Bottle / Syrup'
        TUBE = 'TUBE', 'Tube (Ointment)'
        PACK = 'PACK', 'Pack / Strip'
        AMPOULE = 'AMPOULE', 'Ampoule'

    name = models.CharField(max_length=150, help_text="Brand / Trade name")
    generic_name = models.CharField(max_length=150, blank=True, help_text="Active salt (e.g. Amoxicillin)")
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.OTHER)
    unit_type = models.CharField(max_length=20, choices=UnitType.choices, default=UnitType.TABLET)
    batch_number = models.CharField(max_length=50, blank=True, help_text="Batch / Lot number")

    cost_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Purchase price (Rs.)")
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Sale price (Rs.)")

    quantity_in_stock = models.PositiveIntegerField(default=0)
    reorder_threshold = models.PositiveIntegerField(default=10, help_text="Low stock trigger limit")
    expiry_date = models.DateField(null=True, blank=True, db_index=True)
    supplier = models.CharField(max_length=100, blank=True, help_text="Distributor / Supplier")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    @property
    def is_low_stock(self):
        return self.quantity_in_stock <= self.reorder_threshold

    @property
    def stock_status(self):
        if self.quantity_in_stock == 0:
            return {'label': 'Out of Stock', 'badge': 'bg-danger text-white'}
        elif self.is_low_stock:
            return {'label': f'Low Stock ({self.quantity_in_stock})', 'badge': 'bg-warning text-dark'}
        else:
            return {'label': f'{self.quantity_in_stock} in stock', 'badge': 'bg-success text-white'}

    @property
    def expiry_status(self):
        if not self.expiry_date:
            return {'label': 'No Expiry', 'badge': 'bg-secondary text-white'}
        today = timezone.now().date()
        if today > self.expiry_date:
            return {'label': 'EXPIRED', 'badge': 'bg-danger text-white'}
        elif (self.expiry_date - today).days <= 30:
            days = (self.expiry_date - today).days
            return {'label': f'Expires in {days}d', 'badge': 'bg-warning text-dark'}
        else:
            return {'label': self.expiry_date.strftime('%b %Y'), 'badge': 'bg-light text-dark border'}

    def __str__(self):
        return f"{self.name} ({self.quantity_in_stock} {self.get_unit_type_display()})"


class StockMovement(models.Model):
    class MovementType(models.TextChoices):
        RESTOCK = 'RESTOCK', 'Restock (Purchase)'
        DISPENSED = 'DISPENSED', 'Dispensed to Patient'
        ADJUSTMENT = 'ADJUSTMENT', 'Manual Correction'
        DAMAGED_EXPIRED = 'DAMAGED_EXPIRED', 'Damaged / Expired Discard'

    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name='movements')
    movement_type = models.CharField(max_length=20, choices=MovementType.choices, default=MovementType.RESTOCK)
    quantity_changed = models.IntegerField(help_text="Positive for add (+), negative for deduct (-)")
    balance_after = models.PositiveIntegerField()
    performed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        sign = "+" if self.quantity_changed > 0 else ""
        return f"{self.medicine.name}: {sign}{self.quantity_changed} ({self.get_movement_type_display()})"
