from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('pyq/', views.pyq_redirect, name='pyq'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('dashboard/add/', views.company_create_view, name='company_create'),
    path('dashboard/edit/<int:pk>/', views.company_edit_view, name='company_edit'),
    path('dashboard/delete/<int:pk>/', views.company_delete_view, name='company_delete'),
    path('dashboard/update-pyq-link/', views.update_pyq_link_view, name='update_pyq_link'),
]