from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta
from .models import Medicine, StockMovement
from .forms import MedicineForm, RestockForm

@login_required
def inventory_list(request):
    query = request.GET.get('q', '').strip()
    category_filter = request.GET.get('category', '').strip()
    tab = request.GET.get('tab', 'all')

    medicines = Medicine.objects.all()

    if query:
        medicines = medicines.filter(
            Q(name__icontains=query) |
            Q(generic_name__icontains=query) |
            Q(batch_number__icontains=query) |
            Q(supplier__icontains=query)
        )

    if category_filter:
        medicines = medicines.filter(category=category_filter)

    today = timezone.now().date()
    thirty_days = today + timedelta(days=30)

    low_stock_items = [m for m in medicines if m.is_low_stock]
    expiring_items = [m for m in medicines if m.expiry_date and m.expiry_date <= thirty_days]

    if tab == 'low_stock':
        display_items = low_stock_items
    elif tab == 'expiring':
        display_items = expiring_items
    else:
        display_items = medicines

    context = {
        'medicines': display_items,
        'query': query,
        'category_filter': category_filter,
        'tab': tab,
        'total_items_count': Medicine.objects.count(),
        'low_stock_count': len([m for m in Medicine.objects.all() if m.is_low_stock]),
        'expiring_count': len([m for m in Medicine.objects.all() if m.expiry_date and m.expiry_date <= thirty_days]),
        'categories': Medicine.Category.choices,
        'restock_form': RestockForm(),
    }
    return render(request, 'inventory/inventory_list.html', context)


@login_required
def medicine_create(request):
    if request.method == 'POST':
        form = MedicineForm(request.POST)
        if form.is_valid():
            medicine = form.save()
            if medicine.quantity_in_stock > 0:
                StockMovement.objects.create(
                    medicine=medicine,
                    movement_type=StockMovement.MovementType.RESTOCK,
                    quantity_changed=medicine.quantity_in_stock,
                    balance_after=medicine.quantity_in_stock,
                    performed_by=request.user,
                    notes="Initial stock upon creation"
                )
            messages.success(request, f"Medicine '{medicine.name}' added to inventory!")
            return redirect('inventory_list')
    else:
        form = MedicineForm()
    return render(request, 'inventory/medicine_form.html', {'form': form, 'title': 'Add New Medicine'})


@login_required
def medicine_update(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk)
    if request.method == 'POST':
        form = MedicineForm(request.POST, instance=medicine)
        if form.is_valid():
            form.save()
            messages.success(request, f"Updated '{medicine.name}' details successfully!")
            return redirect('inventory_list')
    else:
        form = MedicineForm(instance=medicine)
    return render(request, 'inventory/medicine_form.html', {'form': form, 'title': f'Edit {medicine.name}', 'medicine': medicine})


@login_required
def medicine_restock(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk)
    if request.method == 'POST':
        form = RestockForm(request.POST)
        if form.is_valid():
            qty = form.cleaned_data['quantity_to_add']
            medicine.quantity_in_stock += qty

            if form.cleaned_data.get('new_batch_number'):
                medicine.batch_number = form.cleaned_data['new_batch_number']
            if form.cleaned_data.get('new_expiry_date'):
                medicine.expiry_date = form.cleaned_data['new_expiry_date']

            medicine.save()

            StockMovement.objects.create(
                medicine=medicine,
                movement_type=StockMovement.MovementType.RESTOCK,
                quantity_changed=qty,
                balance_after=medicine.quantity_in_stock,
                performed_by=request.user,
                notes=form.cleaned_data.get('notes') or "Restock order"
            )

            messages.success(request, f"Restocked +{qty} units of '{medicine.name}'. Total in stock: {medicine.quantity_in_stock}")
    return redirect('inventory_list')


@login_required
def stock_movements(request):
    movements = StockMovement.objects.select_related('medicine', 'performed_by').all()[:100]
    return render(request, 'inventory/movement_list.html', {'movements': movements})

# Create your views here.
