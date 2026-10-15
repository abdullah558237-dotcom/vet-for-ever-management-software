from django.contrib import admin
from .models import Invoice, InvoiceItem

class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'patient', 'owner', 'total_amount', 'paid_amount', 'balance_due', 'status', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('invoice_number', 'patient__name', 'owner__first_name', 'owner__phone')
    inlines = [InvoiceItemInline]
