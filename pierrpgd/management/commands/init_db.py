from django.core.management.base import BaseCommand
import json
from pierrpgd.models import Profile, About, Experience, Education, Project, Skill, ProfileSkill, Color
import os

class Command(BaseCommand):
    help = 'Initialize database with JSON data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force', 
            action='store_true',
            help='Force reset database before initialization'
        )

    def handle(self, *args, **options):
        if options['force']:
            self.stdout.write("Force resetting database...")
            Profile.objects.all().delete()
            About.objects.all().delete()
            Experience.objects.all().delete()
            Education.objects.all().delete()
            Project.objects.all().delete()
            Skill.objects.all().delete()
            Color.objects.all().delete()

        try:
            # Charger les données depuis le fichier JSON
            with open(os.path.join(os.path.dirname(__file__), 'init_db.json'), 'r', encoding='utf-8') as f:
                data = json.load(f)

            for person in data:

                # Vérifier si le profil existe déjà
                if Profile.objects.filter(identifiant=person["profile"]["identifiant"]).exists():
                    self.stdout.write("Profile already exists")
                    return

                # Création du profil
                self.stdout.write("Création du profil...")
                profile = Profile.objects.create(
                    name=person["profile"]["name"],
                    identifiant=person["profile"]["identifiant"],
                    title=person["profile"]["title"]
                )
                self.stdout.write(f"Profil créé avec l'ID: {profile.id}")

                # Création des couleurs
                self.stdout.write("Création des couleurs...")
                for color in person["colors"]:
                    color = Color.objects.create(
                        profile=profile,
                        red=color["red"],
                        green=color["green"],
                        blue=color["blue"],
                        transparency=color["transparency"]
                    )
                    self.stdout.write(f"Couleur créée (ID: {color.id})")

                # Création des compétences
                self.stdout.write("Création des compétences...")
                for skill_data in person["skills"]:
                    if not Skill.objects.filter(name=skill_data["name"], category=skill_data["category"]).exists():
                        Skill.objects.create(category=skill_data["category"], name=skill_data["name"])
                    skill = Skill.objects.get(name=skill_data["name"], category=skill_data["category"])
                    ProfileSkill.objects.create(profile=profile, skill=skill, level=skill_data["level"])
                    self.stdout.write(f"Compétence créée: {skill.name} (ID: {skill.id})")

                # Création des sections A propos
                self.stdout.write("Création des sections À propos...")
                for content in person["about"]:
                    about = About.objects.create(profile=profile, content=content)
                    self.stdout.write(f"Section À propos créée (ID: {about.id})")

                # Création des expériences
                self.stdout.write("Création des expériences...")
                for exp_data in person["experiences"]:
                    exp = Experience.objects.create(
                        profile=profile,
                        dates=exp_data["dates"],
                        position=exp_data["position"],
                        company=exp_data["company"],
                        location=exp_data["location"],
                        description=exp_data["description"],
                        details=exp_data["details"],
                        url=exp_data["url"]
                    )
                    skill_ids = [Skill.objects.get(name=skill_name).id for skill_name in exp_data["skills"]]
                    exp.skills.add(*skill_ids)
                    self.stdout.write(f"Expérience créée (ID: {exp.id})")

                # Création des éducations
                self.stdout.write("Création des éducations...")
                for edu_data in person["educations"]:
                    edu = Education.objects.create(
                        profile=profile,
                        dates=edu_data["dates"],
                        title=edu_data["title"],
                        institution=edu_data["institution"],
                        field=edu_data["field"],
                        location=edu_data["location"],
                        description=edu_data["description"],
                        details=edu_data["details"],
                        url=edu_data["url"]
                    )
                    skill_ids = [Skill.objects.get(name=skill_name).id for skill_name in edu_data["skills"]]
                    edu.skills.add(*skill_ids)
                    self.stdout.write(f"Éducation créée (ID: {edu.id})")

                # Création des projets
                self.stdout.write("Création des projets...")
                for project_data in person["projects"]:
                    project = Project.objects.create(
                        profile=profile,
                        title=project_data["title"],
                        description=project_data["description"],
                        details=project_data["details"],
                        image_url=project_data["image_url"],
                        url=project_data["url"]
                    )
                    skill_ids = [Skill.objects.get(name=skill_name).id for skill_name in project_data["skills"]]
                    project.skills.add(*skill_ids)
                    self.stdout.write(f"Projet créé (ID: {project.id})")

                self.stdout.write("Initialisation de la base de données terminée avec succès!")

        except Exception as e:
            self.stderr.write(f"Error: {str(e)}")