from django.contrib import admin
from .models import Medicine, StockMovement

class StockMovementInline(admin.TabularInline):
    model = StockMovement
    extra = 0
    readonly_fields = ('created_at',)

@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ('name', 'generic_name', 'category', 'quantity_in_stock', 'reorder_threshold', 'cost_price', 'selling_price', 'expiry_date')
    list_filter = ('category', 'unit_type', 'expiry_date')
    search_fields = ('name', 'generic_name', 'batch_number', 'supplier')
    inlines = [StockMovementInline]

@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ('medicine', 'movement_type', 'quantity_changed', 'balance_after', 'performed_by', 'created_at')
    list_filter = ('movement_type', 'created_at')
