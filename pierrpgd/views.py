from django.shortcuts import render, redirect
from django.http import JsonResponse, Http404
from .models import Profile, About, Experience, Project
from django.conf import settings

def portfolio(request, identifiant):
    try:
        # Récupérer le profil correspondant à l'identifiant
        try:
            profile = Profile.objects.get(identifiant=identifiant)
            about = profile.about.all()
            experience = profile.experience.all()
            projects = profile.projects.all()
        except Profile.DoesNotExist:
            raise Http404("Le profil demandé n'existe pas")

        context = {
            'profile': profile,
            'about': about,
            'experience': experience,
            'projects': projects,
        }
        
        return render(request, 'portfolio.html', context)
    
    except Exception as e:
        settings.DEBUG and print(f"Erreur dans la vue portfolio: {str(e)}")
        raise

def data_display(request):
    """Vue pour afficher toutes les données de la base"""
    profiles = Profile.objects.all()
    context = {
        'profiles': profiles,
    }
    return render(request, 'data_display.html', context)

def load_profile_data(request):
    """Vue pour charger les données liées à un profil spécifique"""
    if request.method == 'GET':
        identifiant = request.GET.get('identifiant')
        if identifiant:
            try:
                profile = Profile.objects.get(identifiant=identifiant)
                abouts = profile.about.all()
                experiences = profile.experience.all()
                projects = profile.projects.all()
                
                data = {
                    'profile': {
                        'name': profile.name,
                        'identifiant': profile.identifiant
                    },
                    'about': [
                        {
                            'order': about.order,
                            'content': about.content
                        } for about in abouts
                    ],
                    'experience': [
                        {
                            'order': exp.order,
                            'dates': exp.dates,
                            'position': exp.position,
                            'company': exp.company,
                            'location': exp.location,
                            'description': exp.description
                        } for exp in experiences
                    ],
                    'projects': [
                        {
                            'order': project.order,
                            'title': project.title,
                            'description': project.description
                        } for project in projects
                    ]
                }
                
                return JsonResponse(data)
            except Profile.DoesNotExist:
                return JsonResponse({'error': 'Profil non trouvé'}, status=404)
    return JsonResponse({'error': 'Aucun profil sélectionné'}, status=400)

def add_profile(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        identifiant = request.POST.get('identifiant')
        
        # Vérifier que l'identifiant ne contient pas d'espace
        if ' ' in identifiant:
            return render(request, 'add_profile.html', {
                'error_message': 'L\'identifiant ne doit pas contenir d\'espace'
            })
        
        try:
            # Vérifier si l'identifiant existe déjà
            Profile.objects.get(identifiant=identifiant)
            return render(request, 'add_profile.html', {
                'error_message': 'Cet identifiant est déjà utilisé'
            })
        except Profile.DoesNotExist:
            # Créer le profil
            Profile.objects.create(name=name, identifiant=identifiant)
            return redirect('data_display')
    
    return render(request, 'add_profile.html')
