import sys
import json
from pierrpgd.models import Profile, About, Experience, Project, Skill

try:
    # Charger les données depuis le fichier JSON
    with open('initiate_db.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Vérifier si le profil existe déjà
    if Profile.objects.filter(identifiant=data["profile"]["identifiant"]).exists():
        print("Le profil existe déjà - arrêt du script")
        sys.exit()

    print("Création du profil...")
    profile = Profile.objects.create(
        name=data["profile"]["name"],
        identifiant=data["profile"]["identifiant"],
        title=data["profile"]["title"]
    )
    print(f"Profil créé avec l'ID: {profile.id}")

    # Création des sections A propos
    print("Création des sections À propos...")
    for content in data["about"]:
        about = About.objects.create(profile=profile, content=content)
        print(f"Section À propos créée (ID: {about.id})")

    # Création des compétences
    print("Création des compétences...")
    for skill_data in data["skills"]:
        if Skill.objects.filter(name=skill_data["name"], category=skill_data["category"]).exists():
            continue
        skill = Skill.objects.create(category=skill_data["category"], name=skill_data["name"])
        print(f"Compétence créée: {skill.name} (ID: {skill.id})")

    # Création des expériences
    print("Création des expériences...")
    for exp_data in data["experiences"]:
        exp = Experience.objects.create(
            profile=profile,
            dates=exp_data["dates"],
            position=exp_data["position"],
            company=exp_data["company"],
            location=exp_data["location"],
            description=exp_data["description"],
            url=exp_data["url"]
        )
        skill_ids = [Skill.objects.get(name=skill_name).id for skill_name in exp_data["skills"]]
        exp.skills.add(*skill_ids)
        print(f"Expérience créée (ID: {exp.id})")

    # Création des projets
    print("Création des projets...")
    for project_data in data["projects"]:
        project = Project.objects.create(
            profile=profile,
            title=project_data["title"],
            description=project_data["description"],
            image_url=project_data["image_url"],
            url=project_data["url"]
        )
        skill_ids = [Skill.objects.get(name=skill_name).id for skill_name in project_data["skills"]]
        project.skills.add(*skill_ids)
        print(f"Projet créé (ID: {project.id})")

    print("Initialisation de la base de données terminée avec succès!")
except Exception as e:
    print(f"Erreur lors de l'initialisation: {str(e)}", file=sys.stderr)
    sys.exit(1)