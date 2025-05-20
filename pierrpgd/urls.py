from django.urls import path
from . import views

urlpatterns = [
    path('data/', views.data_display, name='data_display'),
    path('add_profile/', views.add_profile, name='add_profile'),
    path('load_profile_data/', views.load_profile_data, name='load_profile_data'),
    path('save_modal_content/', views.save_modal_content, name='save_modal_content'),
    path('<str:identifiant>/', views.portfolio, name='portfolio'),
]
