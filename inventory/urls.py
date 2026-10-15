from django.urls import path
from . import views

urlpatterns = [
    path('', views.inventory_list, name='inventory_list'),
    path('add/', views.medicine_create, name='medicine_create'),
    path('<int:pk>/edit/', views.medicine_update, name='medicine_update'),
    path('<int:pk>/restock/', views.medicine_restock, name='medicine_restock'),
    path('movements/', views.stock_movements, name='stock_movements'),
]
