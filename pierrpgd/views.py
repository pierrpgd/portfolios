from django.shortcuts import render
from django.http import JsonResponse, Http404
from .models import Profile, About, Experience, Education, Project, Skill, ProfileSkill
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

def portfolio(request, identifiant):
    try:
        # Récupérer le profil correspondant à l'identifiant
        try:
            profile = Profile.objects.get(identifiant=identifiant)
            about = profile.about.all()
            experience = profile.experience.all().prefetch_related('skills')
            education = profile.education.all().prefetch_related('skills')
            projects = profile.projects.all().prefetch_related('skills')
            profile_skills = ProfileSkill.objects.filter(profile=profile).order_by('skill__category', '-level')

            skills_data = []
            
            for ps in profile_skills:
                skills_data.append({
                    'id': ps.skill.id,
                    'category': ps.skill.category,
                    'name': ps.skill.name,
                    'level': ps.level
                })

        except Profile.DoesNotExist:
            raise Http404("Le profil demandé n'existe pas")

        context = {
            'profile': profile,
            'about': about,
            'experience': experience,
            'education': education,
            'projects': projects,
            'skills': skills_data,
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
                educations = profile.education.all()
                projects = profile.projects.all()
                profile_skills = ProfileSkill.objects.filter(profile=profile)
                
                # Récupération de toutes les compétences liées au profil
                skills_data = []
                
                for ps in profile_skills:
                    skills_data.append({
                        'id': ps.skill.id,
                        'category': ps.skill.category,
                        'name': ps.skill.name,
                        'level': ps.level
                    })
                
                data = {
                    'profile': {
                        'name': profile.name if profile.name else '',
                        'identifiant': profile.identifiant,
                        'title': profile.title if profile.title else '',
                        'id': profile.id,
                        'created_at': profile.created_at,
                        'updated_at': profile.updated_at,
                    },
                    'about': [
                        {
                            'id': about.id,
                            'order': about.order,
                            'content': about.content if about.content else ''
                        } for about in abouts
                    ],
                    'experience': [
                        {
                            'id': exp.id,
                            'order': exp.order,
                            'dates': exp.dates if exp.dates else '',
                            'position': exp.position if exp.position else '',
                            'company': exp.company if exp.company else '',
                            'location': exp.location if exp.location else '',
                            'description': exp.description if exp.description else '',
                            'url': exp.url if exp.url else '',
                            'skills': [skill.id for skill in exp.skills.all()]
                        } for exp in experiences
                    ],
                    'education': [
                        {
                            'id': edu.id,
                            'order': edu.order,
                            'dates': edu.dates if edu.dates else '',
                            'institution': edu.institution if edu.institution else '',
                            'location': edu.location if edu.location else '',
                            'title': edu.title if edu.title else '',
                            'field': edu.field if edu.field else '',
                            'description': edu.description if edu.description else '',
                            'url': edu.url if edu.url else '',
                            'skills': [skill.id for skill in edu.skills.all()]
                        } for edu in educations
                    ],
                    'projects': [
                        {
                            'id': project.id,
                            'order': project.order,
                            'title': project.title if project.title else '',
                            'image_url': project.image_url if project.image_url else '',
                            'description': project.description if project.description else '',
                            'url': project.url if project.url else '',
                            'skills': [skill.id for skill in project.skills.all()]
                        } for project in projects
                    ],
                    'skills': skills_data
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
            if (isNew and modalId != 'profileModal') or modalId == 'skillModal':
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
                        url=content.get('url', ''),
                        profile=profile
                    )
                    skills = content.get('skills', [])
                else:
                    obj = Experience.objects.get(id=content.get('id'))
                    obj.dates = content.get('dates', obj.dates)
                    obj.position = content.get('position', obj.position)
                    obj.company = content.get('company', obj.company)
                    obj.location = content.get('location', obj.location)
                    obj.description = content.get('description', obj.description)
                    obj.url = content.get('url', obj.url)
                    skills = content.get('skills', [])
                if skills != []:
                    obj.skills.clear()
                    for skill_id in skills:
                        obj.skills.add(skill_id)
            elif modalId == 'educationModal':
                type = 'education'
                if isNew:
                    obj = Education.objects.create(
                        dates=content.get('dates', ''),
                        title=content.get('title', ''),
                        institution=content.get('institution', ''),
                        location=content.get('location', ''),
                        field=content.get('field', ''),
                        description=content.get('description', ''),
                        url=content.get('url', ''),
                        profile=profile
                    )
                    skills = content.get('skills', [])
                else:
                    obj = Education.objects.get(id=content.get('id'))
                    obj.dates = content.get('dates', obj.dates)
                    obj.title = content.get('title', obj.title)
                    obj.institution = content.get('institution', obj.institution)
                    obj.location = content.get('location', obj.location)
                    obj.field = content.get('field', obj.field)
                    obj.description = content.get('description', obj.description)
                    obj.url = content.get('url', obj.url)
                    skills = content.get('skills', [])
                if skills != []:
                    obj.skills.clear()
                    for skill_id in skills:
                        obj.skills.add(skill_id)
            elif modalId == 'projectModal':
                type = 'project'
                if isNew:
                    obj = Project.objects.create(
                        title=content.get('title', ''),
                        description=content.get('description', ''),
                        image_url=content.get('image_url', ''),
                        url=content.get('url', ''),
                        profile=profile
                    )
                    skills = content.get('skills', [])
                else:
                    obj = Project.objects.get(id=content.get('id'))
                    obj.title = content.get('title', obj.title)
                    obj.description = content.get('description', obj.description)
                    obj.image_url = content.get('image_url', obj.image_url)
                    obj.url = content.get('url', obj.url)
                    skills = content.get('skills', [])
                if skills != []:
                    obj.skills.clear()
                    for skill_id in skills:
                        obj.skills.add(skill_id)
            elif modalId == 'skillModal':
                type = 'skill'
                if isNew and not Skill.objects.filter(category=content.get('category'), name=content.get('name')).exists():
                    obj = Skill.objects.create(
                        category=content.get('category', ''),
                        name=content.get('name', '')
                    )
                else:
                    skillId = content.get('id')
                    if skillId:
                        obj = Skill.objects.get(id=skillId)
                        obj.category = content.get('category', obj.category)
                        obj.name = content.get('name', obj.name)
                    else:
                        obj = Skill.objects.get(category=content.get('category'), name=content.get('name'))
                profile.skills.add(obj)
                ProfileSkill.objects.update_or_create(profile=profile, skill=obj, defaults={'level': content.get('level', 5)})
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
def delete_education(request, education_id):
    try:
        education = Education.objects.get(id=education_id)
        education.delete()
        return JsonResponse({'success': True})
    except Education.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Education not found'}, status=404)

@require_http_methods(["DELETE"])
def delete_project(request, project_id):
    try:
        project = Project.objects.get(id=project_id)
        project.delete()
        return JsonResponse({'success': True})
    except Project.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Project not found'}, status=404)

@require_http_methods(["DELETE"])
def delete_skill(request, profile_identifiant, skill_id):
    try:
        skill = Skill.objects.get(id=skill_id)

        # Supprimer la compétence du profil
        profile = Profile.objects.get(identifiant=profile_identifiant)
        profile.skills.remove(skill)

        # Supprimer la compétence des expériences du profil
        experiences = Experience.objects.filter(profile=profile)
        for experience in experiences:
            experience.skills.remove(skill)

        # Supprimer la compétence des projets du profil
        projects = Project.objects.filter(profile=profile)
        for project in projects:
            project.skills.remove(skill)
        
        return JsonResponse({'success': True})
    except Skill.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Skill not found'}, status=404)
    except Profile.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Profile not found'}, status=404)