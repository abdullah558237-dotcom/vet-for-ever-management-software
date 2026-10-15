from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Consultation
from .forms import ConsultationForm, PrescriptionFormSet
from patients.models import Patient
from appointments.models import Appointment

@login_required
def consultation_start(request, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)
    appointment_id = request.GET.get('appointment')
    appointment = None

    if appointment_id:
        appointment = get_object_or_404(Appointment, pk=appointment_id)
        if appointment.status == Appointment.Status.WAITING:
            appointment.status = Appointment.Status.IN_CONSULTATION
            appointment.veterinarian = request.user
            appointment.save()

    initial_data = {}
    if appointment and appointment.reason:
        initial_data['symptoms'] = appointment.reason

    if request.method == 'POST':
        form = ConsultationForm(request.POST)
        formset = PrescriptionFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            consultation = form.save(commit=False)
            consultation.patient = patient
            consultation.veterinarian = request.user
            if appointment:
                consultation.appointment = appointment
            consultation.save()

            formset.instance = consultation
            formset.save()

            if appointment:
                appointment.status = Appointment.Status.COMPLETED
                appointment.save()

            messages.success(request, f"Clinical examination completed for {patient.name}!")
            return redirect('consultation_detail', pk=consultation.pk)
    else:
        form = ConsultationForm(initial=initial_data)
        formset = PrescriptionFormSet()

    last_consult = patient.consultations.first()

    context = {
        'patient': patient,
        'appointment': appointment,
        'form': form,
        'formset': formset,
        'last_consult': last_consult,
    }
    return render(request, 'clinical/consultation_form.html', context)


@login_required
def consultation_detail(request, pk):
    consultation = get_object_or_404(
        Consultation.objects.select_related('patient', 'patient__owner', 'veterinarian'),
        pk=pk
    )
    prescriptions = consultation.prescriptions.all()
    return render(request, 'clinical/consultation_detail.html', {
        'consultation': consultation,
        'prescriptions': prescriptions,
    })


@login_required
def prescription_print(request, pk):
    consultation = get_object_or_404(
        Consultation.objects.select_related('patient', 'patient__owner', 'veterinarian'),
        pk=pk
    )
    prescriptions = consultation.prescriptions.all()
    return render(request, 'clinical/prescription_print.html', {
        'consultation': consultation,
        'prescriptions': prescriptions,
    })
# Create your views here.
from datetime import timedelta
from .models import VaccineRecord
from .forms import VaccineRecordForm

@login_required
def vaccination_center(request):
    """
    Clinic-wide vaccination reminder dashboard
    """
    today = timezone.now().date()
    thirty_days = today + timedelta(days=30)

    overdue_list = VaccineRecord.objects.select_related('patient', 'patient__owner').filter(
        next_due_date__lt=today
    ).order_by('next_due_date')

    upcoming_list = VaccineRecord.objects.select_related('patient', 'patient__owner').filter(
        next_due_date__gte=today,
        next_due_date__lte=thirty_days
    ).order_by('next_due_date')

    recent_administered = VaccineRecord.objects.select_related('patient', 'patient__owner').filter(
        administered_date__gte=today - timedelta(days=14)
    ).order_by('-administered_date')

    context = {
        'today': today,
        'overdue_list': overdue_list,
        'upcoming_list': upcoming_list,
        'recent_administered': recent_administered,
        'overdue_count': overdue_list.count(),
        'upcoming_count': upcoming_list.count(),
    }
    return render(request, 'clinical/vaccination_center.html', context)


@login_required
def vaccine_create(request, patient_id):
    """
    Record vaccination for a pet with smart default next due dates (1 Year)
    """
    patient = get_object_or_404(Patient, pk=patient_id)
    today = timezone.now().date()

    if request.method == 'POST':
        form = VaccineRecordForm(request.POST)
        if form.is_valid():
            vaccine = form.save(commit=False)
            vaccine.patient = patient
            vaccine.administered_by = request.user
            vaccine.save()
            messages.success(request, f"Vaccination '{vaccine.get_vaccine_name_display()}' recorded for {patient.name}!")
            return redirect('patient_detail', pk=patient.pk)
    else:
        default_next_due = today + timedelta(days=365)
        form = VaccineRecordForm(initial={
            'administered_date': today,
            'next_due_date': default_next_due
        })

    return render(request, 'clinical/vaccination_form.html', {'form': form, 'patient': patient})


@login_required
def vaccine_passport_print(request, patient_id):
    """
    Official Printable Pet Vaccination Passport & Certificate
    """
    patient = get_object_or_404(Patient.objects.select_related('owner'), pk=patient_id)
    vaccines = patient.vaccinations.order_by('-administered_date')

    return render(request, 'clinical/vaccination_passport.html', {
        'patient': patient,
        'vaccines': vaccines,
        'today': timezone.now().date(),
    })
