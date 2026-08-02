from django.urls import path
from . import views

urlpatterns = [
    path('cashin/', views.cashin_list, name='cashin_list'),
    path('cashin/add/', views.cashin_create, name='cashin_create'),
    path('cashin/<int:pk>/edit/', views.cashin_edit, name='cashin_edit'),
    path('cashout/', views.cashout_list, name='cashout_list'),
    path('cashout/add/', views.cashout_create, name='cashout_create'),
    path('cashout/<int:pk>/edit/', views.cashout_edit, name='cashout_edit'),
    path('transaction/<int:pk>/delete/', views.transaction_delete, name='transaction_delete'),
]