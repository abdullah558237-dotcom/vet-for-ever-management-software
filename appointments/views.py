from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Appointment
from .forms import AppointmentBookingForm, QuickWalkInForm

@login_required
def daily_queue(request):
    today = timezone.now().date()
    queue = Appointment.objects.select_related('patient', 'patient__owner', 'veterinarian').filter(
        scheduled_date=today,
        status__in=[Appointment.Status.WAITING, Appointment.Status.IN_CONSULTATION]
    ).order_by('status', 'token_number')

    completed_today = Appointment.objects.filter(
        scheduled_date=today,
        status=Appointment.Status.COMPLETED
    ).count()

    context = {
        'today': today,
        'queue': queue,
        'waiting_count': queue.filter(status=Appointment.Status.WAITING).count(),
        'in_consult_count': queue.filter(status=Appointment.Status.IN_CONSULTATION).count(),
        'completed_today': completed_today,
        'walkin_form': QuickWalkInForm(),
    }
    return render(request, 'appointments/queue.html', context)


@login_required
def appointment_list(request):
    date_str = request.GET.get('date')
    selected_date = date_str if date_str else timezone.now().date()
    appointments = Appointment.objects.select_related('patient', 'patient__owner', 'veterinarian').filter(
        scheduled_date=selected_date
    )

    return render(request, 'appointments/appointment_list.html', {
        'appointments': appointments,
        'selected_date': str(selected_date),
    })


@login_required
def appointment_create(request):
    if request.method == 'POST':
        form = AppointmentBookingForm(request.POST)
        if form.is_valid():
            appt = form.save()
            messages.success(request, f"Appointment booked for {appt.patient.name} on {appt.scheduled_date}!")
            return redirect('appointment_list')
    else:
        form = AppointmentBookingForm(initial={'scheduled_date': timezone.now().date()})
    return render(request, 'appointments/appointment_form.html', {'form': form, 'title': 'Book Appointment'})


@login_required
def quick_walkin(request):
    if request.method == 'POST':
        form = QuickWalkInForm(request.POST)
        if form.is_valid():
            appt = form.save(commit=False)
            appt.scheduled_date = timezone.now().date()
            appt.visit_type = Appointment.VisitType.WALK_IN
            appt.status = Appointment.Status.WAITING
            appt.save()
            messages.success(request, f"Walk-In registered! Token assigned: #{appt.token_number} ({appt.patient.name})")
    return redirect('daily_queue')


@login_required
def update_status(request, pk, new_status):
    appt = get_object_or_404(Appointment, pk=pk)
    if new_status in Appointment.Status.values:
        appt.status = new_status
        appt.save()
        messages.success(request, f"Patient #{appt.token_number} {appt.patient.name} marked as {appt.get_status_display()}.")
    return redirect(request.META.get('HTTP_REFERER', 'daily_queue'))

# Create your views here.
