from django.urls import path
from . import views
from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('reports/', views.reports_dashboard, name='reports_dashboard'),
    path('reports/export-csv/', views.export_invoices_csv, name='export_invoices_csv'),
],

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
]
