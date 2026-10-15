from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # Authentication
    path('accounts/login/', auth_views.LoginView.as_view(
        template_name='pets/login.html',
        next_page='dashboard'
    ), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('accounts/profile/', RedirectView.as_view(pattern_name='dashboard', permanent=False)),

    # Apps Routing (Dhyan dein: sab mein '.urls' hona chahiye)
    path('patients/', include('patients.urls')),
    path('appointments/', include('appointments.urls')),
    path('', include('core.urls')),
    path('clinical/', include('clinical.urls')),
    path('billing/', include('billing.urls')),
    path('inventory/', include('inventory.urls')),
    path('accounts/staff-admin/', include('accounts.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
