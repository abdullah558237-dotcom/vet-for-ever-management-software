from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Patient, Owner
from .forms import PatientForm, OwnerForm

@login_required
def patient_list(request):
    query = request.GET.get('q', '').strip()
    species_filter = request.GET.get('species', '').strip()

    patients = Patient.objects.select_related('owner').all()

    if query:
        patients = patients.filter(
            Q(name__icontains=query) |
            Q(breed__icontains=query) |
            Q(microchip_number__icontains=query) |
            Q(owner__first_name__icontains=query) |
            Q(owner__last_name__icontains=query) |
            Q(owner__phone__icontains=query)
        )

    if species_filter:
        patients = patients.filter(species=species_filter)

    paginator = Paginator(patients, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'query': query,
        'species_filter': species_filter,
        'species_choices': Patient.Species.choices,
        'total_count': patients.count(),
    }
    return render(request, 'patients/patient_list.html', context)


@login_required
def patient_detail(request, pk):
    patient = get_object_or_404(Patient.objects.select_related('owner'), pk=pk)
    return render(request, 'patients/patient_detail.html', {'patient': patient})


@login_required
def patient_create(request):
    if request.method == 'POST':
        form = PatientForm(request.POST, request.FILES)
        if form.is_valid():
            patient = form.save()
            messages.success(request, f"Patient '{patient.name}' successfully registered!")
            return redirect('patient_detail', pk=patient.pk)
    else:
        initial = {}
        owner_id = request.GET.get('owner')
        if owner_id:
            initial['owner'] = owner_id
        form = PatientForm(initial=initial)

    return render(request, 'patients/patient_form.html', {'form': form, 'title': 'Register New Pet'})


@login_required
def patient_update(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        form = PatientForm(request.POST, request.FILES, instance=patient)
        if form.is_valid():
            form.save()
            messages.success(request, f"Patient '{patient.name}' updated successfully!")
            return redirect('patient_detail', pk=patient.pk)
    else:
        form = PatientForm(instance=patient)
    return render(request, 'patients/patient_form.html', {'form': form, 'title': f'Edit {patient.name}', 'patient': patient})


@login_required
def owner_create(request):
    if request.method == 'POST':
        form = OwnerForm(request.POST)
        if form.is_valid():
            owner = form.save()
            messages.success(request, f"Owner '{owner.get_full_name()}' registered! Now register their pet.")
            return redirect(f"{reverse('patient_create')}?owner={owner.pk}")
    else:
        form = OwnerForm()
    return render(request, 'patients/owner_form.html', {'form': form})

# Create your views here.
