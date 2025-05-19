from django.urls import path
from . import views

app_name = 'pierrpgd'

urlpatterns = [
    path('pierrpgd/', views.home, name='home'),
    path('data/', views.data_display, name='data_display'),
    path('add_profile/', views.add_profile, name='add_profile'),
]
