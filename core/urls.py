from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Auth
    path('', views.dashboard, name='dashboard'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),

    # Projects
    path('projects/', views.project_list, name='project_list'),
    path('projects/create/', views.project_create, name='project_create'),
    path('projects/<int:pk>/', views.project_detail, name='project_detail'),
    path('projects/<int:pk>/update/', views.project_update, name='project_update'),

    # Expenses (categorized view)
    path('expenses/', views.expense_list, name='expense_list'),

    # Cash IN
    path('cashin/', views.cashin_list, name='cashin_list'),
    path('cashin/add/', views.cashin_create, name='cashin_create'),
    path('cashin/<int:pk>/edit/', views.cashin_edit, name='cashin_edit'),

    # Cash OUT
    path('cashout/', views.cashout_list, name='cashout_list'),
    path('cashout/add/', views.cashout_create, name='cashout_create'),
    path('cashout/<int:pk>/edit/', views.cashout_edit, name='cashout_edit'),

    # Delete (admin)
    path('transaction/<int:pk>/delete/', views.transaction_delete, name='transaction_delete'),

    #Reports
    path('reports/', views.report_list, name='report_list'),
    path('reports/pdf/', views.report_pdf, name='report_pdf'),

    #logout
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]