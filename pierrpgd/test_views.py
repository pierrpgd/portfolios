from django.test import TestCase, Client
from django.urls import resolve, reverse
from django.http import HttpRequest
from django.utils.html import escape
from .views import portfolio
from .models import Profile, About, Experience, Project
from bs4 import BeautifulSoup
from django.contrib.auth.models import User

class PortfolioViewTest(TestCase):
    def setUp(self):
        self.request = HttpRequest()

        # Créer un profil de test
        self.profile = Profile.objects.create(
            name='Test Profile',
            identifiant='test-identifiant'
        )
        
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

        self.response = portfolio(self.request, self.profile.identifiant)
        self.soup = BeautifulSoup(self.response.content, "html.parser")

    def test_url_resolves_to_portfolio(self):
        """Teste que l'URL racine résout vers la vue portfolio"""
        found = resolve(f'/{self.profile.identifiant}/')
        self.assertEqual(found.func, portfolio)

    def test_portfolio_returns_correct_html(self):
        """Teste que la page d'accueil retourne le bon HTML"""
        client = Client()
        response = client.get(f'/{self.profile.identifiant}/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'portfolio.html')

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

    def test_nonexistent_profile(self):
        """Test que l'accès à un profil inexistant renvoie une erreur 404"""
        response = self.client.get(reverse('portfolio', args=['non-existent']))
        self.assertEqual(response.status_code, 404)

class DataDisplayViewTest(TestCase):
    def setUp(self):
        """Configuration commune pour tous les tests"""
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
        
        # Créer un profil de test avec ses éléments liés
        self.profile = Profile.objects.create(
            name='Test Profile',
            identifiant='test-profile'
        )
        
        # Créer une section About de test
        self.about = About.objects.create(
            profile=self.profile,
            content='Test About Content',
            order=0
        )
        
        # Créer une expérience de test
        self.experience = Experience.objects.create(
            profile=self.profile,
            dates='2020-2023',
            company='Test Company',
            position='Test Position',
            location='Test Location',
            description='Test Description',
            order=0
        )
        
        # Créer un projet de test
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
        """Teste la vue data_display"""
        response = self.client.get(reverse('data_display'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'data_display.html')

    def test_profile_display(self):
        """Teste l'affichage des profils"""
        response = self.client.get(reverse('data_display'))
        self.assertEqual(response.status_code, 200)
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

    def test_profile_selection_and_data_display(self):
        """
        Teste la sélection d'un profil et l'affichage des données liées
        """
        # Accéder à la page data_display
        response = self.client.get(reverse('data_display'))
        self.assertEqual(response.status_code, 200)
        
        # Simuler le clic sur la ligne du profil
        response = self.client.get(reverse('load_profile_data') + f'?identifiant={self.profile.identifiant}')
        self.assertEqual(response.status_code, 200)
        
        # Vérifier que les données sont correctement chargées
        data = response.json()
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

class LoadDataViewTest(TestCase):
    def setUp(self):
        """Configuration commune pour tous les tests"""
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
        
        # Créer un profil de test
        self.profile = Profile.objects.create(
            name='Test Profile',
            identifiant='test-profile'
        )

    def tearDown(self):
        # Supprimer le superuser à la fin des tests
        if hasattr(self, 'user'):
            self.user.delete()

    def test_create_about(self):
        """Teste la création d'une section About"""
        # Données pour la création
        about_data = {
            'profile': self.profile,
            'content': 'Nouvelle section About',
            'order': 0
        }
        
        # Créer une nouvelle section About
        About.objects.create(**about_data)
        
        # Vérifier que l'objet a été créé
        self.assertTrue(About.objects.filter(content='Nouvelle section About').exists())
        
        # Vérifier que la section apparaît dans l'interface
        response = self.client.get(reverse('load_profile_data'), {'identifiant': self.profile.identifiant})
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('about', data)
        self.assertEqual(len(data['about']), 1)
        self.assertEqual(data['about'][0]['content'], 'Nouvelle section About')

    def test_update_about(self):
        """Teste la mise à jour d'une section About"""
        # Créer une section About pour le test
        about = About.objects.create(
            profile=self.profile,
            content='Contenu initial',
            order=0
        )
        
        # Données pour la mise à jour
        updated_data = {
            'content': 'Contenu mis à jour',
            'order': 1
        }
        
        # Mettre à jour la section About en utilisant les méthodes natives
        About.objects.filter(id=about.id).update(**updated_data)
        
        # Vérifier que les modifications ont été sauvegardées
        about.refresh_from_db()
        self.assertEqual(about.content, 'Contenu mis à jour')
        self.assertEqual(about.order, 1)
        
        # Vérifier que les changements apparaissent dans l'interface via load_profile_data
        response = self.client.get(reverse('load_profile_data'), {'identifiant': self.profile.identifiant})
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('about', data)
        self.assertEqual(len(data['about']), 1)
        self.assertEqual(data['about'][0]['content'], 'Contenu mis à jour')
        self.assertEqual(data['about'][0]['order'], 1)

    def test_delete_about(self):
        """Teste la suppression d'une section About"""
        # Créer une section About pour le test
        about = About.objects.create(
            profile=self.profile,
            content='Contenu à supprimer',
            order=0
        )
        
        # Supprimer la section About
        About.objects.filter(id=about.id).delete()
        
        # Vérifier que l'objet a été supprimé
        self.assertFalse(About.objects.filter(id=about.id).exists())
        
        # Vérifier que la section ne s'affiche plus
        response = self.client.get(reverse('load_profile_data'), {'identifiant': self.profile.identifiant})
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('about', data)
        self.assertEqual(len(data['about']), 0)

    def test_create_experience(self):
        """Teste la création d'une expérience"""
        # Données pour la création
        experience_data = {
            'profile': self.profile,
            'dates': '2023-2024',
            'company': 'Nouvelle entreprise',
            'location': 'Nouveau lieu',
            'position': 'Nouveau poste',
            'description': 'Nouvelle description',
            'order': 0
        }
        
        # Créer une nouvelle expérience
        Experience.objects.create(**experience_data)
        
        # Vérifier que l'objet a été créé
        self.assertTrue(Experience.objects.filter(company='Nouvelle entreprise').exists())
        
        # Vérifier que l'expérience apparaît dans l'interface
        response = self.client.get(reverse('load_profile_data'), {'identifiant': self.profile.identifiant})
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('experience', data)
        self.assertEqual(len(data['experience']), 1)
        self.assertEqual(data['experience'][0]['company'], 'Nouvelle entreprise')

    def test_update_experience(self):
        """Teste la mise à jour d'une expérience"""
        # Créer une expérience pour le test
        experience = Experience.objects.create(
            profile=self.profile,
            dates='2023-2024',
            company='Entreprise initiale',
            location='Lieu initial',
            position='Poste initial',
            description='Description initiale',
            order=0
        )
        
        # Données pour la mise à jour
        updated_data = {
            'dates': '2024-2025',
            'company': 'Entreprise mise à jour',
            'location': 'Lieu mis à jour',
            'position': 'Poste mis à jour',
            'description': 'Description mise à jour',
            'order': 1
        }
        
        # Mettre à jour l'expérience en utilisant les méthodes natives
        Experience.objects.filter(id=experience.id).update(**updated_data)
        
        # Vérifier que les modifications ont été sauvegardées
        experience.refresh_from_db()
        self.assertEqual(experience.company, 'Entreprise mise à jour')
        self.assertEqual(experience.order, 1)
        
        # Vérifier que les changements apparaissent dans l'interface via load_profile_data
        response = self.client.get(reverse('load_profile_data'), {'identifiant': self.profile.identifiant})
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('experience', data)
        self.assertEqual(len(data['experience']), 1)
        self.assertEqual(data['experience'][0]['company'], 'Entreprise mise à jour')
        self.assertEqual(data['experience'][0]['order'], 1)

    def test_delete_experience(self):
        """Teste la suppression d'une expérience"""
        # Créer une expérience pour le test
        experience = Experience.objects.create(
            profile=self.profile,
            dates='2023-2024',
            company='Entreprise à supprimer',
            location='Lieu à supprimer',
            position='Poste à supprimer',
            description='Description à supprimer',
            order=0
        )
        
        # Supprimer l'expérience
        experience.delete()
        
        # Vérifier que l'objet a été supprimé
        self.assertFalse(Experience.objects.filter(id=experience.id).exists())
        
        # Vérifier que l'expérience ne s'affiche plus
        response = self.client.get(reverse('load_profile_data'), {'identifiant': self.profile.identifiant})
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('experience', data)
        self.assertEqual(len(data['experience']), 0)

    def test_create_project(self):
        """Teste la création d'un projet"""
        # Données pour la création
        project_data = {
            'profile': self.profile,
            'title': 'Nouveau projet',
            'description': 'Description du nouveau projet',
            'order': 0
        }
        
        # Créer un nouveau projet
        Project.objects.create(**project_data)
        
        # Vérifier que l'objet a été créé
        self.assertTrue(Project.objects.filter(title='Nouveau projet').exists())
        
        # Vérifier que le projet apparaît dans l'interface
        response = self.client.get(reverse('load_profile_data'), {'identifiant': self.profile.identifiant})
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('projects', data)
        self.assertEqual(len(data['projects']), 1)
        self.assertEqual(data['projects'][0]['title'], 'Nouveau projet')

    def test_update_project(self):
        """Teste la mise à jour d'un projet"""
        # Créer un projet pour le test
        project = Project.objects.create(
            profile=self.profile,
            title='Titre initial',
            description='Description initiale',
            order=0
        )
        
        # Données pour la mise à jour
        updated_data = {
            'title': 'Titre mis à jour',
            'description': 'Description mise à jour',
            'order': 1
        }
        
        # Mettre à jour le projet en utilisant les méthodes natives
        Project.objects.filter(id=project.id).update(**updated_data)
        
        # Vérifier que les modifications ont été sauvegardées
        project.refresh_from_db()
        self.assertEqual(project.title, 'Titre mis à jour')
        self.assertEqual(project.order, 1)
        
        # Vérifier que les changements apparaissent dans l'interface via load_profile_data
        response = self.client.get(reverse('load_profile_data'), {'identifiant': self.profile.identifiant})
        self.assertEqual(response.status_code, 200)
        
        # Vérifier que les données retournées correspondent aux changements
        data = response.json()
        self.assertIn('projects', data)
        self.assertEqual(len(data['projects']), 1)
        self.assertEqual(data['projects'][0]['title'], 'Titre mis à jour')
        self.assertEqual(data['projects'][0]['order'], 1)

    def test_delete_project(self):
        """Teste la suppression d'un projet"""
        # Créer un projet pour le test
        project = Project.objects.create(
            profile=self.profile,
            title='Projet à supprimer',
            description='Description à supprimer',
            order=0
        )
        
        # Supprimer le projet
        project.delete()
        
        # Vérifier que l'objet a été supprimé
        self.assertFalse(Project.objects.filter(id=project.id).exists())
        
        # Vérifier que le projet ne s'affiche plus
        response = self.client.get(reverse('load_profile_data'), {'identifiant': self.profile.identifiant})
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('projects', data)
        self.assertEqual(len(data['projects']), 0)

    def test_ordering(self):
        """Teste l'ordre des About, Projets et Expériences"""
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
        response = self.client.get(reverse('load_profile_data'), {'identifiant': self.profile.identifiant})
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        
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

class AddProfileViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('add_profile')
        
        # Créer un superuser pour les tests
        self.user = User.objects.create_superuser(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        self.client.login(username='testuser', password='testpassword')

    def tearDown(self):
        # Supprimer le superuser à la fin des tests
        if hasattr(self, 'user'):
            self.user.delete()

    def test_add_profile_view_get(self):
        """Teste que la vue add_profile affiche le formulaire"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'add_profile.html')
        self.assertContains(response, 'Ajouter un profil')
        self.assertContains(response, 'Identifiant')
        self.assertContains(response, 'Nom')

    def test_add_profile_success(self):
        """Teste la création réussie d'un profil"""
        data = {
            'identifiant': 'new-profile',
            'name': 'New Profile'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)  # Redirection
        self.assertRedirects(response, reverse('data_display'))
        
        # Vérifier que le profil a été créé
        profile = Profile.objects.get(identifiant='new-profile')
        self.assertEqual(profile.name, 'New Profile')

    def test_add_profile_invalid_identifiant(self):
        """Teste la création avec un identifiant invalide (contient des espaces)"""
        data = {
            'identifiant': 'invalid identifiant',
            'name': 'Test Profile'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'add_profile.html')
        self.assertContains(response, escape('L\'identifiant ne doit pas contenir d\'espace'))

    def test_add_profile_duplicate_identifiant(self):
        """Teste la création avec un identifiant déjà existant"""
        # Créer un profil avec un identifiant existant
        Profile.objects.create(identifiant='existing', name='Existing Profile')
        
        data = {
            'identifiant': 'existing',
            'name': 'Test Profile'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'add_profile.html')
        self.assertContains(response, 'Cet identifiant est déjà utilisé')
