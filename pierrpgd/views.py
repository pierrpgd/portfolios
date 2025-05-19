from django.shortcuts import render, redirect
from django.http import Http404
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
    abouts = About.objects.all()
    experiences = Experience.objects.all()
    projects = Project.objects.all()
    
    context = {
        'profiles': profiles,
        'abouts': abouts,
        'experiences': experiences,
        'projects': projects
    }
    return render(request, 'data_display.html', context)

def add_profile(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        Profile.objects.create(name=name)
        return redirect('data_display')
    return render(request, 'add_profile.html')
