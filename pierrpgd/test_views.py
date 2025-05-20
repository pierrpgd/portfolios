from django.test import TestCase
from django.urls import resolve, reverse
from django.http import HttpRequest
from django.utils.html import escape
from .views import portfolio
from .models import Profile, About, Experience, Project
from bs4 import BeautifulSoup

class BaseTest(TestCase):
    fixtures = ['test_fixtures.json']

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.profile = Profile.objects.get(identifiant='test-profile')
        cls.about = About.objects.get(profile=cls.profile)
        cls.experience = Experience.objects.get(profile=cls.profile)
        cls.project = Project.objects.get(profile=cls.profile)

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'user'):
            cls.user.delete()
        super().tearDownClass()

class PortfolioViewTest(BaseTest):
    def setUp(self):
        self.request = HttpRequest()
        self.response = portfolio(self.request, self.profile.identifiant)
        self.soup = BeautifulSoup(self.response.content, "html.parser")

    def test_url_resolves_to_portfolio(self):
        """Teste que l'URL racine résout vers la vue portfolio"""
        found = resolve(f'/{self.profile.identifiant}/')
        self.assertEqual(found.func, portfolio)

    def test_portfolio_returns_correct_html(self):
        """Teste que la page d'accueil retourne le bon HTML"""
        self.response = self.client.get(f'/{self.profile.identifiant}/')
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, 'portfolio.html')

    def test_profile_display(self):
        """Teste l'affichage du profil"""
        name_element = self.soup.find(id="name")
        self.assertIsNotNone(name_element)
        self.assertEqual(name_element.text.strip(), self.profile.name)

    def test_about_display(self):
        """Teste l'affichage des sections About"""
        about_section = self.soup.find(id="about")
        self.assertIsNotNone(about_section)
        
        about_content = about_section.find_all('p')[0].text
        self.assertEqual(about_content.strip(), self.about.content)

    def test_experience_display(self):
        """Teste l'affichage des expériences"""
        experience_section = self.soup.find(id="experience")
        self.assertIsNotNone(experience_section)
        
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

    def test_nonexistent_profile(self):
        """Test que l'accès à un profil inexistant renvoie une erreur 404"""
        self.response = self.client.get(reverse('portfolio', args=['non-existent']))
        self.assertEqual(self.response.status_code, 404)

class DataDisplayViewTest(BaseTest):
    def setUp(self):
        self.response = self.client.get(reverse('data_display'))

    def test_data_display_view(self):
        """Teste la vue data_display"""
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, 'data_display.html')

    def test_profile_display(self):
        """Teste l'affichage des profils"""
        self.response = self.client.get(reverse('data_display'))
        self.assertEqual(self.response.status_code, 200)
        self.assertContains(self.response, self.profile.name)

    def test_profile_deletion(self):
        # Supprimer le profil et vérifier que les données associées sont supprimées
        Profile.objects.all().delete()

        self.response = self.client.get(reverse('data_display'))
        self.assertEqual(self.response.status_code, 200)
        self.assertNotContains(self.response, self.profile.name)
        self.assertNotContains(self.response, self.about.content)
        self.assertNotContains(self.response, self.experience.company)
        self.assertNotContains(self.response, self.project.title)
        self.assertContains(self.response, 'Aucun profil trouvé')
        self.assertContains(self.response, 'Aucune section About trouvée')
        self.assertContains(self.response, 'Aucune expérience trouvée')
        self.assertContains(self.response, 'Aucun projet trouvé')

    def test_profile_selection_and_data_display(self):
        """
        Teste la sélection d'un profil et l'affichage des données liées
        """
        # Accéder à la page data_display
        self.response = self.client.get(reverse('data_display'))
        self.assertEqual(self.response.status_code, 200)
        
        # Simuler le clic sur la ligne du profil
        self.response = self.client.get(reverse('load_profile_data') + f'?identifiant={self.profile.identifiant}')
        self.assertEqual(self.response.status_code, 200)
        
        # Vérifier que les données sont correctement chargées
        data = self.response.json()
        self.assertIn('about', data)
        self.assertIn('experience', data)
        self.assertIn('projects', data)
        
        # Vérifier que les données correspondent
        self.assertEqual(len(data['about']), 1)
        self.assertEqual(data['about'][0]['content'], self.about.content)
        
        self.assertEqual(len(data['experience']), 1)
        self.assertEqual(data['experience'][0]['company'], self.experience.company)
        
        self.assertEqual(len(data['projects']), 1)
        self.assertEqual(data['projects'][0]['title'], self.project.title)

class LoadDataViewTest(BaseTest):

    def test_create_about(self):
        """Teste la création d'une section About"""
        
        # Vérifier que l'objet a été créé
        self.assertTrue(About.objects.filter(content=self.about.content).exists())
        
        # Vérifier que la section apparaît dans l'interface
        self.response = self.client.get(reverse('load_profile_data'), {'identifiant': self.profile.identifiant})
        self.assertEqual(self.response.status_code, 200)
        
        data = self.response.json()
        self.assertIn('about', data)
        self.assertEqual(len(data['about']), 1)
        self.assertEqual(data['about'][0]['content'], self.about.content)

    def test_update_about(self):
        """Teste la mise à jour d'une section About"""
        
        # Données pour la mise à jour
        updated_data = {
            'content': 'Contenu mis à jour',
            'order': 1
        }
        
        # Mettre à jour la section About
        About.objects.filter(id=self.about.id).update(**updated_data)
        self.about.refresh_from_db()
        
        # Vérifier que les modifications ont été sauvegardées
        self.assertEqual(self.about.content, 'Contenu mis à jour')
        self.assertEqual(self.about.order, 1)
        
        # Vérifier que les changements apparaissent dans l'interface via load_profile_data
        self.response = self.client.get(reverse('load_profile_data'), {'identifiant': self.profile.identifiant})
        self.assertEqual(self.response.status_code, 200)
        
        data = self.response.json()
        self.assertIn('about', data)
        self.assertEqual(len(data['about']), 1)
        self.assertEqual(data['about'][0]['content'], 'Contenu mis à jour')
        self.assertEqual(data['about'][0]['order'], 1)

    def test_delete_about(self):
        """Teste la suppression d'une section About"""
        
        # Supprimer la section About
        self.about.delete()
        
        # Vérifier que l'objet a été supprimé
        self.assertFalse(About.objects.filter(id=self.about.id).exists())
        
        # Vérifier que la section ne s'affiche plus
        self.response = self.client.get(reverse('load_profile_data'), {'identifiant': self.profile.identifiant})
        self.assertEqual(self.response.status_code, 200)
        
        data = self.response.json()
        self.assertIn('about', data)
        self.assertEqual(len(data['about']), 0)

    def test_create_experience(self):
        """Teste la création d'une expérience"""

        # Vérifier que l'objet a été créé
        self.assertTrue(Experience.objects.filter(company=self.experience.company).exists())
        
        # Vérifier que l'expérience apparaît dans l'interface
        self.response = self.client.get(reverse('load_profile_data'), {'identifiant': self.profile.identifiant})
        self.assertEqual(self.response.status_code, 200)
        
        data = self.response.json()
        self.assertIn('experience', data)
        self.assertEqual(len(data['experience']), 1)
        self.assertEqual(data['experience'][0]['company'], self.experience.company)

    def test_update_experience(self):
        """Teste la mise à jour d'une expérience"""
        
        # Données pour la mise à jour
        updated_data = {
            'dates': '2024-2025',
            'company': 'Entreprise mise à jour',
            'location': 'Endroit mis à jour',
            'position': 'Poste mis à jour',
            'description': 'Description mise à jour',
            'order': 1
        }
        
        # Mettre à jour l'expérience
        Experience.objects.filter(id=self.experience.id).update(**updated_data)
        self.experience.refresh_from_db()
        
        # Vérifier que les modifications ont été sauvegardées
        self.assertEqual(self.experience.company, 'Entreprise mise à jour')
        self.assertEqual(self.experience.order, 1)
        
        # Vérifier que les changements apparaissent dans l'interface via load_profile_data
        self.response = self.client.get(reverse('load_profile_data'), {'identifiant': self.profile.identifiant})
        self.assertEqual(self.response.status_code, 200)
        
        data = self.response.json()
        self.assertIn('experience', data)
        self.assertEqual(len(data['experience']), 1)
        self.assertEqual(data['experience'][0]['company'], 'Entreprise mise à jour')
        self.assertEqual(data['experience'][0]['order'], 1)

    def test_delete_experience(self):
        """Teste la suppression d'une expérience"""
        
        # Supprimer l'expérience
        self.experience.delete()
        
        # Vérifier que l'objet a été supprimé
        self.assertFalse(Experience.objects.filter(id=self.experience.id).exists())
        
        # Vérifier que l'expérience ne s'affiche plus
        self.response = self.client.get(reverse('load_profile_data'), {'identifiant': self.profile.identifiant})
        self.assertEqual(self.response.status_code, 200)
        
        data = self.response.json()
        self.assertIn('experience', data)
        self.assertEqual(len(data['experience']), 0)

    def test_create_project(self):
        """Teste la création d'un projet"""

        # Vérifier que l'objet a été créé
        self.assertTrue(Project.objects.filter(title=self.project.title).exists())
        
        # Vérifier que le projet apparaît dans l'interface
        self.response = self.client.get(reverse('load_profile_data'), {'identifiant': self.profile.identifiant})
        self.assertEqual(self.response.status_code, 200)
        
        data = self.response.json()
        self.assertIn('projects', data)
        self.assertEqual(len(data['projects']), 1)
        self.assertEqual(data['projects'][0]['title'], self.project.title)

    def test_update_project(self):
        """Teste la mise à jour d'un projet"""
        
        # Données pour la mise à jour
        updated_data = {
            'title': 'Titre mis à jour',
            'description': 'Description mise à jour',
            'order': 1
        }
        
        # Mettre à jour le projet
        Project.objects.filter(id=self.project.id).update(**updated_data)
        self.project.refresh_from_db()
        
        # Vérifier que les modifications ont été sauvegardées
        self.assertEqual(self.project.title, 'Titre mis à jour')
        self.assertEqual(self.project.order, 1)
        
        # Vérifier que les changements apparaissent dans l'interface via load_profile_data
        self.response = self.client.get(reverse('load_profile_data'), {'identifiant': self.profile.identifiant})
        self.assertEqual(self.response.status_code, 200)
        
        data = self.response.json()
        self.assertIn('projects', data)
        self.assertEqual(len(data['projects']), 1)
        self.assertEqual(data['projects'][0]['title'], 'Titre mis à jour')
        self.assertEqual(data['projects'][0]['order'], 1)

    def test_delete_project(self):
        """Teste la suppression d'un projet"""
        # Supprimer le projet
        self.project.delete()
        
        # Vérifier que l'objet a été supprimé
        self.assertFalse(Project.objects.filter(id=self.project.id).exists())
        
        # Vérifier que le projet ne s'affiche plus
        self.response = self.client.get(reverse('load_profile_data'), {'identifiant': self.profile.identifiant})
        self.assertEqual(self.response.status_code, 200)
        
        data = self.response.json()
        self.assertIn('projects', data)
        self.assertEqual(len(data['projects']), 0)

    def test_ordering(self):
        """Teste l'ordre des About, Projets et Expériences"""

        About.objects.all().delete()
        Project.objects.all().delete()
        Experience.objects.all().delete()

        # Créer des About avec différents ordres
        about1 = About.objects.create(profile=self.profile, content='About 1', order=2)
        about2 = About.objects.create(profile=self.profile, content='About 2', order=1)
        about3 = About.objects.create(profile=self.profile, content='About 3', order=0)
        
        # Créer des Projets avec différents ordres
        project1 = Project.objects.create(profile=self.profile, title='Project 1', order=2)
        project2 = Project.objects.create(profile=self.profile, title='Project 2', order=1)
        project3 = Project.objects.create(profile=self.profile, title='Project 3', order=0)
        
        # Créer des Expériences avec différents ordres
        experience1 = Experience.objects.create(profile=self.profile, company='Experience 1', order=2, dates='2023')
        experience2 = Experience.objects.create(profile=self.profile, company='Experience 2', order=1, dates='2024')
        experience3 = Experience.objects.create(profile=self.profile, company='Experience 3', order=0, dates='2025')
        
        # Vérifier l'ordre via load_profile_data
        self.response = self.client.get(reverse('load_profile_data'), {'identifiant': self.profile.identifiant})
        self.assertEqual(self.response.status_code, 200)
        
        data = self.response.json()
        
        # Vérifier l'ordre des About
        abouts = data['about']
        self.assertEqual(len(abouts), 3)
        self.assertEqual(abouts[0]['content'], 'About 3')  # Order = 0
        self.assertEqual(abouts[1]['content'], 'About 2')  # Order = 1
        self.assertEqual(abouts[2]['content'], 'About 1')  # Order = 2
        
        # Vérifier l'ordre des Projets
        projects = data['projects']
        self.assertEqual(len(projects), 3)
        self.assertEqual(projects[0]['title'], 'Project 3')  # Order = 0
        self.assertEqual(projects[1]['title'], 'Project 2')  # Order = 1
        self.assertEqual(projects[2]['title'], 'Project 1')  # Order = 2
        
        # Vérifier l'ordre des Expériences
        experiences = data['experience']
        self.assertEqual(len(experiences), 3)
        self.assertEqual(experiences[0]['company'], 'Experience 3')  # Order = 0
        self.assertEqual(experiences[1]['company'], 'Experience 2')  # Order = 1
        self.assertEqual(experiences[2]['company'], 'Experience 1')  # Order = 2

class AddProfileViewTest(BaseTest):
    def setUp(self):
        self.url = reverse('add_profile')

    def test_add_profile_view_get(self):
        """Teste que la vue add_profile affiche le formulaire"""
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, 'add_profile.html')
        self.assertContains(self.response, 'Ajouter un profil')
        self.assertContains(self.response, 'Identifiant')
        self.assertContains(self.response, 'Nom')

    def test_add_profile_success(self):
        """Teste la création réussie d'un profil"""
        data = {
            'identifiant': 'new-profile',
            'name': 'New Profile'
        }
        self.response = self.client.post(self.url, data)
        self.assertEqual(self.response.status_code, 302)  # Redirection
        self.assertRedirects(self.response, reverse('data_display'))
        
        # Vérifier que le profil a été créé
        profile = Profile.objects.get(identifiant='new-profile')
        self.assertEqual(profile.name, 'New Profile')

    def test_add_profile_invalid_identifiant(self):
        """Teste la création avec un identifiant invalide (contient des espaces)"""
        data = {
            'identifiant': 'invalid identifiant',
            'name': 'Test Profile'
        }
        self.response = self.client.post(self.url, data)
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, 'add_profile.html')
        self.assertContains(self.response, escape('L\'identifiant ne doit pas contenir d\'espace'))

    def test_add_profile_duplicate_identifiant(self):
        """Teste la création avec un identifiant déjà existant"""
        # Créer un profil avec un identifiant existant
        Profile.objects.create(identifiant='existing', name='Existing Profile')
        
        data = {
            'identifiant': 'existing',
            'name': 'Test Profile'
        }
        self.response = self.client.post(self.url, data)
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, 'add_profile.html')
        self.assertContains(self.response, 'Cet identifiant est déjà utilisé')
