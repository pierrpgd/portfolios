from django.urls import path
from . import views

urlpatterns = [
    path('data/', views.data_display, name='data_display'),
    path('add_profile/', views.add_profile, name='add_profile'),
    path('load_profile_data/', views.load_profile_data, name='load_profile_data'),
    path('save_modal_content/', views.save_modal_content, name='save_modal_content'),
    path('delete_about/<int:about_id>/', views.delete_about, name='delete_about'),
    path('delete_experience/<int:experience_id>/', views.delete_experience, name='delete_experience'),
    path('delete_project/<int:project_id>/', views.delete_project, name='delete_project'),
    path('<str:identifiant>/', views.portfolio, name='portfolio'),
]
