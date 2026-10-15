from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # 1. Login, Logout & Register
    path('login/', auth_views.LoginView.as_view(
        template_name='pets/login.html',
        redirect_authenticated_user=True,
    ), name='login'),

    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', views.register, name='register'),

    # 2. Staff Profile & Password
    path('profile/', views.profile_view, name='profile'),
    path('password-change/', views.change_password, name='change_password'),

    # 3. Staff Management (Admin Only)
    path('staff/', views.staff_list, name='staff_list'),
    path('staff/add/', views.staff_create, name='staff_create'),
    path('staff/<int:pk>/toggle/', views.toggle_staff_status, name='toggle_staff_status'),
]
