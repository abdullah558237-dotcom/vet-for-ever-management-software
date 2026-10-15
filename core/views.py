from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from appointments.models import Appointment
from patients.models import Patient
from inventory.models import Medicine

@login_required
def dashboard(request):
    today = timezone.now().date()

    # 1. Pehle in_queue_qs define karein
    in_queue_qs = Appointment.objects.select_related('patient', 'patient__owner').filter(
        scheduled_date=today,
        status__in=[Appointment.Status.WAITING, Appointment.Status.IN_CONSULTATION]
    ).order_by('status', 'token_number')

    # 2. Phir stats mein use karein
    stats = {
        'in_queue': in_queue_qs.filter(status=Appointment.Status.WAITING).count(),
        'today_consults': Appointment.objects.filter(scheduled_date=today, status=Appointment.Status.COMPLETED).count(),
        'today_appointments': Appointment.objects.filter(scheduled_date=today).count(),
        'low_stock': len([m for m in Medicine.objects.all() if m.is_low_stock]),
    }

    upcoming_visits = Appointment.objects.select_related('patient', 'patient__owner').filter(
        scheduled_date=today,
        status=Appointment.Status.SCHEDULED
    ).order_by('scheduled_time')[:5]

    context = {
        'today': today,
        'stats': stats,
        'queue_patients': in_queue_qs,
        'upcoming_visits': upcoming_visits,
        'total_patients': Patient.objects.count(),
    }
    return render(request, 'core/dashboard.html', context)

import csv
from django.http import HttpResponse
from django.db.models import Sum, Count
from datetime import timedelta
from accounts.decorators import admin_required
from clinical.models import Consultation
from billing.models import Invoice, InvoiceItem

@login_required
@admin_required
def reports_dashboard(request):
    today = timezone.now().date()
    this_month = today.replace(day=1)

    # Financials
    total_revenue = Invoice.objects.filter(status=Invoice.Status.PAID).aggregate(Sum('paid_amount'))['paid_amount__sum'] or 0.00
    monthly_revenue = Invoice.objects.filter(
        created_at__gte=this_month,
        status__in=[Invoice.Status.PAID, Invoice.Status.PARTIALLY_PAID]
    ).aggregate(Sum('paid_amount'))['paid_amount__sum'] or 0.00

    outstanding_balance = Invoice.objects.filter(
        status__in=[Invoice.Status.PENDING, Invoice.Status.PARTIALLY_PAID]
    ).aggregate(Sum('balance_due'))['balance_due__sum'] or 0.00

    category_revenue = InvoiceItem.objects.values('item_type').annotate(
        total_sales=Sum('total_price'),
        count=Count('id')
    ).order_by('-total_sales')

    # Species Breakdown
    species_breakdown = Patient.objects.values('species').annotate(
        total=Count('id')
    ).order_by('-total')

    context = {
        'total_revenue': total_revenue,
        'monthly_revenue': monthly_revenue,
        'outstanding_balance': outstanding_balance,
        'category_revenue': category_revenue,
        'species_breakdown': species_breakdown,
        'total_patients': Patient.objects.count(),
        'total_consultations': Consultation.objects.count(),
        'monthly_consultations': Consultation.objects.filter(created_at__gte=this_month).count(),
        'total_invoices': Invoice.objects.count(),
    }
    return render(request, 'core/reports.html', context)


@login_required
@admin_required
def export_invoices_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="vetcare_financial_report_{timezone.now().date()}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Invoice #', 'Date', 'Patient', 'Owner', 'Phone', 'Total (Rs.)', 'Paid (Rs.)', 'Balance (Rs.)', 'Status', 'Payment Method'])

    invoices = Invoice.objects.select_related('patient', 'owner').all().order_by('-created_at')
    for inv in invoices:
        writer.writerow([
            inv.invoice_number,
            inv.created_at.strftime('%Y-%m-%d'),
            inv.patient.name if inv.patient else 'Walk-in',
            inv.owner.get_full_name() if inv.owner else 'Unknown',
            inv.owner.phone if inv.owner else '-',
            inv.total_amount,
            inv.paid_amount,
            inv.balance_due,
            inv.get_status_display(),
            inv.get_payment_method_display(),
        ])

    return response
