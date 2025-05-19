from django.urls import path
from . import views

urlpatterns = [
    path('data/', views.data_display, name='data_display'),
    path('add_profile/', views.add_profile, name='add_profile'),
    path('<str:identifiant>/', views.portfolio, name='portfolio'),
]
