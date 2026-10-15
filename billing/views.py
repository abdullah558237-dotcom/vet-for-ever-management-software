from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q
from .models import Invoice, InvoiceItem
from .forms import InvoiceForm, InvoiceItemFormSet, PaymentCollectionForm
from patients.models import Patient
from clinical.models import Consultation

@login_required
def invoice_list(request):
    query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '').strip()

    invoices = Invoice.objects.select_related('patient', 'owner', 'billed_by').all()

    if query:
        invoices = invoices.filter(
            Q(invoice_number__icontains=query) |
            Q(patient__name__icontains=query) |
            Q(owner__first_name__icontains=query) |
            Q(owner__phone__icontains=query)
        )

    if status_filter:
        invoices = invoices.filter(status=status_filter)

    total_revenue = Invoice.objects.filter(status=Invoice.Status.PAID).aggregate(Sum('paid_amount'))['paid_amount__sum'] or 0.00
    total_outstanding = Invoice.objects.filter(status__in=[Invoice.Status.PENDING, Invoice.Status.PARTIALLY_PAID]).aggregate(Sum('balance_due'))['balance_due__sum'] or 0.00

    context = {
        'invoices': invoices,
        'query': query,
        'status_filter': status_filter,
        'total_revenue': total_revenue,
        'total_outstanding': total_outstanding,
        'status_choices': Invoice.Status.choices,
    }
    return render(request, 'billing/invoice_list.html', context)


@login_required
def invoice_create(request, patient_id):
    patient = get_object_or_404(Patient.objects.select_related('owner'), pk=patient_id)
    consultation_id = request.GET.get('consultation')
    consultation = None

    if consultation_id:
        consultation = get_object_or_404(Consultation, pk=consultation_id)

    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        formset = InvoiceItemFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            invoice = form.save(commit=False)
            invoice.patient = patient
            invoice.owner = patient.owner
            invoice.billed_by = request.user
            if consultation:
                invoice.consultation = consultation
            invoice.save()

            formset.instance = invoice
            formset.save()

            # Recalculate subtotal
            subtotal = sum(item.total_price for item in invoice.items.all())
            invoice.subtotal = subtotal
            invoice.save()

            messages.success(request, f"Invoice {invoice.invoice_number} created successfully!")
            return redirect('invoice_detail', pk=invoice.pk)
    else:
        form = InvoiceForm()
        initial_items = []
        if consultation:
            initial_items.append({'item_type': InvoiceItem.ItemType.CONSULTATION, 'description': 'Clinical Consultation Fee', 'quantity': 1, 'unit_price': 1500.00})
        formset = InvoiceItemFormSet(initial=initial_items)

    return render(request, 'billing/invoice_form.html', {
        'patient': patient,
        'form': form,
        'formset': formset,
        'consultation': consultation,
    })


@login_required
def invoice_detail(request, pk):
    invoice = get_object_or_404(
        Invoice.objects.select_related('patient', 'owner', 'billed_by'),
        pk=pk
    )
    items = invoice.items.all()
    payment_form = PaymentCollectionForm(instance=invoice)

    if request.method == 'POST':
        payment_form = PaymentCollectionForm(request.POST, instance=invoice)
        if payment_form.is_valid():
            add_amount = payment_form.cleaned_data['additional_payment']
            invoice.paid_amount += add_amount
            invoice.payment_method = payment_form.cleaned_data['payment_method']
            invoice.save()
            messages.success(request, f"Payment of Rs. {add_amount} recorded! Remaining balance: Rs. {invoice.balance_due}")
            return redirect('invoice_detail', pk=invoice.pk)

    return render(request, 'billing/invoice_detail.html', {
        'invoice': invoice,
        'items': items,
        'payment_form': payment_form,
    })


@login_required
def invoice_print(request, pk):
    invoice = get_object_or_404(
        Invoice.objects.select_related('patient', 'owner', 'billed_by'),
        pk=pk
    )
    return render(request, 'billing/invoice_print.html', {
        'invoice': invoice,
        'items': invoice.items.all(),
    })
# Create your views here.
