from django.test import TestCase
from django.urls import resolve, reverse
from django.http import HttpRequest
from django.utils.html import escape
from .models import Profile, About, Experience, Project
from bs4 import BeautifulSoup
from datetime import datetime
from django.shortcuts import render
from django.http import Http404

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

        print(about[0].content)
        
        return render(request, 'portfolio.html', context)
    
    except Exception as e:
        raise

profile = Profile.objects.get(identifiant='test-profile')

request = HttpRequest()
response = portfolio(request, profile.identifiant)
soup = BeautifulSoup(response.content, "html.parser")

print(soup.prettify())
