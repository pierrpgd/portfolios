from django.shortcuts import render, redirect
from django.http import JsonResponse, Http404
from .models import Profile, About, Experience, Project
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
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
        raise

def data_display(request):
    """Vue pour afficher toutes les données de la base"""
    profiles = Profile.objects.all()
    context = {
        'profiles': profiles,
    }
    return render(request, 'data_display.html', context)

def load_data(request):
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
                        'identifiant': profile.identifiant,
                        'title': profile.title,
                        'id': profile.id,
                        'created_at': profile.created_at,
                        'updated_at': profile.updated_at
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
                            'image_url': project.image_url,
                            'description': project.description
                        } for project in projects
                    ]
                }
                
                return JsonResponse(data)
            except Profile.DoesNotExist:
                return JsonResponse({'error': 'Profil non trouvé'}, status=404)
    return JsonResponse({'error': 'Aucun profil sélectionné'}, status=400)

@csrf_exempt
def save_data(request):
    if request.method == 'POST':
        try:
            # Parsing et validation
            data = json.loads(request.body)

            modalId = data.get('modalId')
            if not modalId:
                return JsonResponse({'success': False, 'error': 'modalId manquant'}, status=400)
            
            isNew = data.get('isNew', False)
            content = data.get('data', {})
            
            # Gestion du profil
            profile_id = content.get('profile')
            if isNew and modalId != 'profileModal':
                if not profile_id:
                    return JsonResponse({'success': False, 'error': 'Profile ID manquant'}, status=400)
                else:
                    try:
                        profile = Profile.objects.get(identifiant=profile_id)
                    except Profile.DoesNotExist:
                        return JsonResponse({'success': False, 'error': 'Profil introuvable'}, status=404)
                    except Exception as e:
                        return JsonResponse({'success': False, 'error': e}, status=400)
            
            # Création/mise à jour
            obj = None
            type = ''
            if modalId == 'profileModal':
                type = 'profile'
                identifiant = content.get('identifiant')
                
                # Vérifier que l'identifiant ne contient pas d'espace
                if ' ' in identifiant:
                    return JsonResponse({'success': False, 'error': 'L\'identifiant ne doit pas contenir d\'espace'}, status=400)

                if isNew:
                    obj = Profile.objects.create(identifiant=content.get('identifiant', ''), name=content.get('name', ''), title=content.get('title', ''))
                else:
                    obj = Profile.objects.get(id=content.get('id'))
                    obj.identifiant = content.get('identifiant', obj.identifiant)
                    obj.name = content.get('name', obj.name)
                    obj.title = content.get('title', obj.title)

            elif modalId == 'aboutModal':
                type = 'about'
                if isNew:
                    obj = About.objects.create(content=content.get('content', ''), profile=profile)
                else:
                    obj = About.objects.get(id=content.get('id'))
                    obj.content = content.get('content', obj.content)
            elif modalId == 'experienceModal':
                type = 'experience'
                if isNew:
                    obj = Experience.objects.create(
                        dates=content.get('dates', ''),
                        position=content.get('position', ''),
                        company=content.get('company', ''),
                        location=content.get('location', ''),
                        description=content.get('description', ''),
                        profile=profile
                    )
                else:
                    obj = Experience.objects.get(id=content.get('id'))
                    obj.dates = content.get('dates', obj.dates)
                    obj.position = content.get('position', obj.position)
                    obj.company = content.get('company', obj.company)
                    obj.location = content.get('location', obj.location)
                    obj.description = content.get('description', obj.description)
            elif modalId == 'projectModal':
                type = 'project'
                if isNew:
                    obj = Project.objects.create(
                        title=content.get('title', ''),
                        description=content.get('description', ''),
                        image_url=content.get('image_url', ''),
                        profile=profile
                    )
                else:
                    obj = Project.objects.get(id=content.get('id'))
                    obj.title = content.get('title', obj.title)
                    obj.description = content.get('description', obj.description)
                    obj.image_url = content.get('image_url', obj.image_url)
            else:
                return JsonResponse({'success': False, 'error': 'Type de modal inconnu'}, status=400)

            if obj:
                obj.save()
                data = {
                    field.name: getattr(obj, field.name).id if field.name == 'profile' else getattr(obj, field.name)
                    for field in obj._meta.fields
                }
                return JsonResponse({'success': True, 'type': type, 'data': data})
                
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Données JSON invalides'}, status=400)
            
        except Exception as e:
            return JsonResponse({
                'success': False, 
                'error': str(e)
            }, status=500)
    
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée'}, status=405)

@require_http_methods(["DELETE"])
def delete_profile(request, profile_id):
    try:
        profile = Profile.objects.get(id=profile_id)
        profile.delete()
        return JsonResponse({'success': True})
    except Profile.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Profile not found'}, status=404)

@require_http_methods(["DELETE"])
def delete_about(request, about_id):
    try:
        about = About.objects.get(id=about_id)
        about.delete()
        return JsonResponse({'success': True})
    except About.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'About not found'}, status=404)

@require_http_methods(["DELETE"])
def delete_experience(request, experience_id):
    try:
        experience = Experience.objects.get(id=experience_id)
        experience.delete()
        return JsonResponse({'success': True})
    except Experience.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Experience not found'}, status=404)

@require_http_methods(["DELETE"])
def delete_project(request, project_id):
    try:
        project = Project.objects.get(id=project_id)
        project.delete()
        return JsonResponse({'success': True})
    except Project.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Project not found'}, status=404)