from django.test import TestCase, Client
from django.urls import resolve
from django.http import HttpRequest
from .views import home
from .models import Profile, About, Experience, Project
from bs4 import BeautifulSoup

class HomeMapTest(TestCase):
    def setUp(self):
        self.request = HttpRequest()

        # Créer un profil de test
        self.profile = Profile.objects.create(name='Test Profile')
        
        # Créer une section About de test
        self.about = About.objects.create(
            profile=self.profile,
            content='Test About Content',
            order=1
        )
        
        # Créer une expérience de test
        self.experience = Experience.objects.create(
            profile=self.profile,
            dates='2023-2024',
            company='Test Company',
            location='Test Location',
            position='Test Position',
            description='Test Description',
            order=1
        )
        
        # Créer un projet de test
        self.project = Project.objects.create(
            profile=self.profile,
            title='Test Project',
            description='Test Project Description',
            order=1
        )

        self.context = {
            'profile': self.profile,
            'about': self.profile.about.all(),
            'experience': self.profile.experience.all(),
            'projects': self.profile.projects.all()
        }

        self.response = home(self.request, self.context)
        self.soup = BeautifulSoup(self.response.content, "html.parser")

    def test_root_url_resolves_to_homepage_view(self):
        """Teste que l'URL racine résout vers la vue home"""
        found = resolve('/')
        self.assertEqual(found.func, home)

    def test_homepage_returns_correct_html(self):
        """Teste que la page d'accueil retourne le bon HTML"""
        client = Client()
        response = client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_profile_display(self):
        """Teste l'affichage du profil"""
        
        # Vérifier le nom du profil
        name_element = self.soup.find(id="name")
        self.assertIsNotNone(name_element)
        self.assertEqual(name_element.text.strip(), self.profile.name)

    def test_about_display(self):
        """Teste l'affichage des sections About"""
        
        about_section = self.soup.find(id="about")
        self.assertIsNotNone(about_section)
        
        # Vérifier que le contenu About est présent
        about_content = about_section.find_all('p')[0].text
        self.assertEqual(about_content.strip(), self.about.content)

    def test_experience_display(self):
        """Teste l'affichage des expériences"""
        
        experience_section = self.soup.find(id="experience")
        self.assertIsNotNone(experience_section)
        
        # Vérifier que les informations de l'expérience sont présentes
        exp_text = experience_section.get_text(strip=True, separator='.')
        self.assertIn(self.experience.dates, exp_text)
        self.assertIn(self.experience.position, exp_text)
        self.assertIn(self.experience.company, exp_text)
        self.assertIn(self.experience.description, exp_text)

    def test_projects_display(self):
        """Teste l'affichage des projets"""
        
        projects_section = self.soup.find(id="projects")
        self.assertIsNotNone(projects_section)
        
        # Vérifier que les informations du projet sont présentes
        project_title = projects_section.find_all('p')[0].text
        project_description = projects_section.find_all('p')[1].text
        
        self.assertEqual(project_title.strip(), self.project.title)
        self.assertEqual(project_description.strip(), self.project.description)