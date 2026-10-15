from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash, login
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.contrib.auth import get_user_model
from .decorators import admin_required
from .forms import StaffCreationForm, StaffProfileForm

User = get_user_model()

# 1. Staff Profile View
@login_required
def profile_view(request):
    if request.method == 'POST':
        form = StaffProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile details have been updated successfully!")
            return redirect('profile')
    else:
        form = StaffProfileForm(instance=request.user)

    return render(request, 'accounts/profile.html', {'form': form})


# 2. Change Password View
@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Your password was successfully updated!")
            return redirect('profile')
    else:
        form = PasswordChangeForm(request.user)

    for field in form.fields.values():
        field.widget.attrs['class'] = 'form-control'

    return render(request, 'accounts/password_change.html', {'form': form})


# 3. Staff List (Admin Only)
@login_required
@admin_required
def staff_list(request):
    staff_members = User.objects.all().order_by('-is_active', 'role', 'username')
    return render(request, 'accounts/staff_list.html', {'staff_members': staff_members})


# 4. Add New Staff Member (Admin Only)
@login_required
@admin_required
def staff_create(request):
    if request.method == 'POST':
        form = StaffCreationForm(request.POST)
        if form.is_valid():
            staff = form.save()
            messages.success(request, f"Staff account for {staff.username} ({staff.get_role_display()}) created successfully!")
            return redirect('staff_list')
    else:
        form = StaffCreationForm()

    return render(request, 'accounts/staff_form.html', {'form': form})


# 5. Toggle Staff Active / Deactivate (Admin Only)
@login_required
@admin_required
def toggle_staff_status(request, pk):
    staff = get_object_or_404(User, pk=pk)
    if staff == request.user:
        messages.error(request, "You cannot deactivate your own account.")
    else:
        staff.is_active = not staff.is_active
        staff.save()
        status_text = "activated" if staff.is_active else "deactivated"
        messages.success(request, f"Staff account {staff.username} has been {status_text}.")
    return redirect('staff_list')


# 6. General Register View (Agar koi sign-up kare)
def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = StaffCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful! Welcome to VetCare Pro.")
            return redirect('dashboard')
    else:
        form = StaffCreationForm()

    return render(request, 'pets/register.html', {'form': form})
