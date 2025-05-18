from django.test import TestCase, Client
from django.urls import resolve, reverse
from django.http import HttpRequest
from .views import home
from .models import Profile, About, Experience, Project
from bs4 import BeautifulSoup
from django.contrib.auth.models import User

class HomeTest(TestCase):
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

class DataDisplayViewTest(TestCase):
    def setUp(self):
        # Vérifier si le superuser existe déjà
        if not User.objects.filter(username='testuser').exists():
            self.user = User.objects.create_superuser(
                username='testuser',
                email='test@example.com',
                password='testpassword'
            )
        else:
            self.user = User.objects.get(username='testuser')
        
        self.client = Client()
        self.client.login(username='testuser', password='testpassword')
        
        # Créer des objets de test
        self.profile = Profile.objects.create(name='Test Profile')
        self.about = About.objects.create(
            profile=self.profile,
            content='Test About Content',
            order=0
        )
        self.experience = Experience.objects.create(
            profile=self.profile,
            dates='2020-2023',
            company='Test Company',
            position='Test Position',
            location='Test Location',
            description='Test Description',
            order=0
        )
        self.project = Project.objects.create(
            profile=self.profile,
            title='Test Project',
            description='Test Project Description',
            order=0
        )
    
    def tearDown(self):
        # Supprimer le superuser à la fin des tests
        if hasattr(self, 'user'):
            self.user.delete()

    def test_data_display_view(self):
        response = self.client.get(reverse('data_display'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'data_display.html')

    def test_profile_display(self):
        response = self.client.get(reverse('data_display'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.profile.name)
        created_at = self.profile.created_at.strftime('%B %d, %Y, %-I:%M p.m.')
        updated_at = self.profile.updated_at.strftime('%B %d, %Y, %-I:%M p.m.')
        self.assertContains(response, created_at)
        self.assertContains(response, updated_at)

    def test_about_display(self):
        response = self.client.get(reverse('data_display'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.about.content)
        self.assertContains(response, str(self.about.order))
        self.assertContains(response, self.profile.name)

    def test_experience_display(self):
        response = self.client.get(reverse('data_display'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.experience.dates)
        self.assertContains(response, self.experience.company)
        self.assertContains(response, self.experience.position)
        self.assertContains(response, self.experience.location)
        self.assertContains(response, self.experience.description)
        self.assertContains(response, str(self.experience.order))
        self.assertContains(response, self.profile.name)

    def test_project_display(self):
        response = self.client.get(reverse('data_display'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.project.title)
        self.assertContains(response, self.project.description)
        self.assertContains(response, str(self.project.order))
        self.assertContains(response, self.profile.name)

    def test_profile_deletion(self):
        # Supprimer le profil et vérifier que les données associées sont supprimées
        Profile.objects.all().delete()

        response = self.client.get(reverse('data_display'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.profile.name)
        self.assertNotContains(response, self.about.content)
        self.assertNotContains(response, self.experience.company)
        self.assertNotContains(response, self.project.title)
        self.assertContains(response, 'Aucun profil trouvé')
        self.assertContains(response, 'Aucune section About trouvée')
        self.assertContains(response, 'Aucune expérience trouvée')
        self.assertContains(response, 'Aucun projet trouvé')

    def test_about_deletion(self):
        # Supprimer toutes les sections About
        about_id = self.about.id
        About.objects.all().delete()
        
        response = self.client.get(reverse('data_display'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.about.content)
        self.assertContains(response, 'Aucune section About trouvée')
        self.assertFalse(About.objects.filter(id=about_id).exists())

    def test_experience_deletion(self):
        # Supprimer toutes les expériences
        exp_id = self.experience.id
        Experience.objects.all().delete()
        
        response = self.client.get(reverse('data_display'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.experience.company)
        self.assertNotContains(response, self.experience.position)
        self.assertContains(response, 'Aucune expérience trouvée')
        self.assertFalse(Experience.objects.filter(id=exp_id).exists())

    def test_project_deletion(self):
        # Supprimer toutes les projets
        project_id = self.project.id
        Project.objects.all().delete()
        
        response = self.client.get(reverse('data_display'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.project.title)
        self.assertNotContains(response, self.project.description)
        self.assertContains(response, 'Aucun projet trouvé')
        self.assertFalse(Project.objects.filter(id=project_id).exists())

    def test_about_ordering(self):
        # Créer des objets avec différents ordres
        profile2 = Profile.objects.create(name='Test Profile 2')
        About.objects.create(profile=profile2, content='About 2', order=0)
        About.objects.create(profile=profile2, content='About 1', order=1)
        
        response = self.client.get(reverse('data_display'))
        self.assertEqual(response.status_code, 200)
        # Vérifier que les éléments sont ordonnés correctement
        content = response.content.decode('utf-8')
        about1_index = content.find('About 1')
        about2_index = content.find('About 2')
        self.assertTrue(about2_index < about1_index)  # About 2 devrait apparaître avant About 1

    def test_experience_ordering(self):
        # Créer des expériences avec différents ordres
        profile2 = Profile.objects.create(name='Test Profile 2')
        Experience.objects.create(
            profile=profile2,
            dates='2020-2023',
            company='Company 1',
            position='Position 1',
            location='Location 1',
            description='Description 1',
            order=1
        )
        Experience.objects.create(
            profile=profile2,
            dates='2023-2025',
            company='Company 2',
            position='Position 2',
            location='Location 2',
            description='Description 2',
            order=0
        )
        
        response = self.client.get(reverse('data_display'))
        self.assertEqual(response.status_code, 200)
        # Vérifier que les expériences sont ordonnées correctement
        content = response.content.decode('utf-8')
        position1_index = content.find('Position 1')
        position2_index = content.find('Position 2')
        self.assertTrue(position2_index < position1_index)  # Expérience 2 devrait apparaître avant Expérience 1

    def test_project_ordering(self):
        # Créer des projets avec différents ordres
        profile2 = Profile.objects.create(name='Test Profile 2')
        Project.objects.create(
            profile=profile2,
            title='Project 1',
            description='Description 1',
            order=1
        )
        Project.objects.create(
            profile=profile2,
            title='Project 2',
            description='Description 2',
            order=0
        )
        
        response = self.client.get(reverse('data_display'))
        self.assertEqual(response.status_code, 200)
        # Vérifier que les projets sont ordonnés correctement
        content = response.content.decode('utf-8')
        project1_index = content.find('Project 1')
        project2_index = content.find('Project 2')
        self.assertTrue(project2_index < project1_index)  # Project 2 devrait apparaître avant Project 1