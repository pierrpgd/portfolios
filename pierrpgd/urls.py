from django.urls import path
from . import views

urlpatterns = [
    path('data/', views.data_display, name='data_display'),
    path('load_data/', views.load_data, name='load_data'),
    path('save_data/', views.save_data, name='save_data'),
    path('delete_profile/<int:profile_id>/', views.delete_profile, name='delete_profile'),
    path('delete_color/<int:color_id>/', views.delete_color, name='delete_color'),
    path('delete_about/<int:about_id>/', views.delete_about, name='delete_about'),
    path('delete_experience/<int:experience_id>/', views.delete_experience, name='delete_experience'),
    path('delete_education/<int:education_id>/', views.delete_education, name='delete_education'),
    path('delete_project/<int:project_id>/', views.delete_project, name='delete_project'),
    path('delete_skill/<str:profile_identifiant>/<int:skill_id>/', views.delete_skill, name='delete_skill'),
    path('<str:identifiant>/', views.portfolio, name='portfolio'),
]
