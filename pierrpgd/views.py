from django.shortcuts import render, redirect
from django.http import JsonResponse, Http404
from .models import Profile, About, Experience, Project
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import json

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
                            'id': about.id,
                            'order': about.order,
                            'content': about.content
                        } for about in abouts
                    ],
                    'experience': [
                        {
                            'id': exp.id,
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
                            'id': project.id,
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

@csrf_exempt
def save_modal_content(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            modalId = data.get('modalId')
            content = data.get('data')
            
            # Trouver l'objet à mettre à jour
            obj = None
            if modalId == 'aboutModal':
                obj = About.objects.get(id=content.get('id'))
                obj.content = content.get('content', obj.content)
                obj.order = content.get('order', obj.order)
            elif modalId == 'experienceModal':
                obj = Experience.objects.get(id=content.get('id'))
                obj.dates = content.get('dates', obj.dates)
                obj.position = content.get('position', obj.position)
                obj.company = content.get('company', obj.company)
                obj.location = content.get('location', obj.location)
                obj.description = content.get('description', obj.description)
                obj.order = content.get('order', obj.order)
            elif modalId == 'projectModal':
                obj = Project.objects.get(id=content.get('id'))
                obj.title = content.get('title', obj.title)
                obj.description = content.get('description', obj.description)
                obj.order = content.get('order', obj.order)
            
            if obj:
                obj.save()
                return JsonResponse({'success': True})
        except Exception as e:
            print(f"Erreur lors de la sauvegarde: {str(e)}")
    
    return JsonResponse({'success': False})