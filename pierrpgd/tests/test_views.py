from django.test import TestCase
from django.urls import resolve, reverse
from django.http import HttpRequest
from django.utils.html import escape
from pierrpgd.views import portfolio
from pierrpgd.models import Profile, About, Experience, Project
from bs4 import BeautifulSoup

class BaseTest(TestCase):
    fixtures = ['test_fixtures.json']

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.profile = Profile.objects.get(identifiant='test-profile')
        cls.abouts = About.objects.filter(profile=cls.profile)
        cls.experiences = Experience.objects.filter(profile=cls.profile)
        cls.projects = Project.objects.filter(profile=cls.profile)

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
        self.assertEqual(about_content.strip(), self.abouts[0].content)

    def test_experience_display(self):
        """Teste l'affichage des expériences"""
        experience_section = self.soup.find(id="experience")
        self.assertIsNotNone(experience_section)
        
        exp_text = experience_section.get_text(strip=True, separator='.')
        self.assertIn(self.experiences[0].dates, exp_text)
        self.assertIn(self.experiences[0].position, exp_text)
        self.assertIn(self.experiences[0].company, exp_text)
        self.assertIn(self.experiences[0].description, exp_text)

    def test_projects_display(self):
        """Teste l'affichage des projets"""
        projects_section = self.soup.find(id="projects")
        self.assertIsNotNone(projects_section)
        
        # Vérifier que les informations du projet sont présentes
        project_title = projects_section.find_all('p')[0].text
        project_description = projects_section.find_all('p')[1].text
        
        self.assertEqual(project_title.strip(), self.projects[0].title)
        self.assertEqual(project_description.strip(), self.projects[0].description)

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
        self.response = self.client.get(reverse('load_data') + f'?identifiant={self.profile.identifiant}')
        self.assertEqual(self.response.status_code, 200)
        
        # Vérifier que les données sont correctement chargées
        data = self.response.json()
        self.assertIn('about', data)
        self.assertIn('experience', data)
        self.assertIn('projects', data)
        
        # Vérifier que les données correspondent
        self.assertEqual(len(data['about']), self.abouts.count())
        self.assertEqual(data['about'][0]['content'], self.abouts[0].content)
        
        self.assertEqual(len(data['experience']), self.experiences.count())
        self.assertEqual(data['experience'][0]['company'], self.experiences[0].company)
        
        self.assertEqual(len(data['projects']), self.projects.count())
        self.assertEqual(data['projects'][0]['title'], self.projects[0].title)

class LoadDataViewTest(BaseTest):

    def test_create_profile(self):
        """Teste la création d'un profil"""
        
        # Vérifier que l'objet a été créé
        self.assertTrue(Profile.objects.filter(identifiant=self.profile.identifiant).exists())
        
        # Vérifier que la section apparaît dans l'interface
        self.response = self.client.get(reverse('load_data'), {'identifiant': self.profile.identifiant})
        self.assertEqual(self.response.status_code, 200)
        
        data = self.response.json()
        self.assertIn('profile', data)
        self.assertEqual(data['profile']['name'], self.profile.name)
        self.assertEqual(data['profile']['identifiant'], self.profile.identifiant)

    def test_update_profile(self):
        """Teste la mise à jour d'un profil"""
        
        # Données pour la mise à jour
        updated_data = {
            'name': 'Nom mis à jour',
            'identifiant': 'identifiant mis à jour'
        }
        
        # Mettre à jour la section About
        Profile.objects.filter(id=self.profile.id).update(**updated_data)
        self.profile.refresh_from_db()
        
        # Vérifier que les modifications ont été sauvegardées
        self.assertEqual(self.profile.name, 'Nom mis à jour')
        self.assertEqual(self.profile.identifiant, 'identifiant mis à jour')
        
        # Vérifier que les changements apparaissent dans l'interface via load_data
        self.response = self.client.get(reverse('load_data'), {'identifiant': self.profile.identifiant})
        self.assertEqual(self.response.status_code, 200)
        
        data = self.response.json()
        self.assertIn('profile', data)
        self.assertEqual(data['profile']['name'], 'Nom mis à jour')
        self.assertEqual(data['profile']['identifiant'], 'identifiant mis à jour')

    def test_delete_profile(self):
        """Teste la suppression d'un profil"""

        id_profile = self.profile.id
        
        # Supprimer le profil
        self.profile.delete()
        
        # Vérifier que l'objet a été supprimé
        self.assertFalse(Profile.objects.filter(id=id_profile).exists())
        
        # Vérifier que la section ne s'affiche plus
        self.response = self.client.get(reverse('load_data'), {'identifiant': self.profile.identifiant})
        self.assertEqual(self.response.status_code, 404)

    def test_create_about(self):
        """Teste la création d'une section About"""
        
        # Vérifier que l'objet a été créé
        self.assertTrue(About.objects.filter(content=self.abouts[0].content).exists())
        
        # Vérifier que la section apparaît dans l'interface
        self.response = self.client.get(reverse('load_data'), {'identifiant': self.profile.identifiant})
        self.assertEqual(self.response.status_code, 200)
        
        data = self.response.json()
        self.assertIn('about', data)
        self.assertEqual(len(data['about']), self.abouts.count())
        self.assertEqual(data['about'][0]['content'], self.abouts[0].content)

    def test_update_about(self):
        """Teste la mise à jour d'une section About"""
        
        # Données pour la mise à jour
        updated_data = {
            'content': 'Contenu mis à jour',
            'order': 1
        }
        
        # Mettre à jour la section About
        About.objects.filter(id=self.abouts[0].id).update(**updated_data)
        self.abouts[0].refresh_from_db()
        
        # Vérifier que les modifications ont été sauvegardées
        self.assertEqual(self.abouts[0].content, 'Contenu mis à jour')
        self.assertEqual(self.abouts[0].order, 1)
        
        # Vérifier que les changements apparaissent dans l'interface via load_data
        self.response = self.client.get(reverse('load_data'), {'identifiant': self.profile.identifiant})
        self.assertEqual(self.response.status_code, 200)
        
        data = self.response.json()
        self.assertIn('about', data)
        self.assertEqual(len(data['about']), self.abouts.count())
        self.assertEqual(data['about'][0]['content'], 'Contenu mis à jour')
        self.assertEqual(data['about'][0]['order'], 1)

    def test_delete_about(self):
        """Teste la suppression d'une section About"""

        id_about = self.abouts[0].id
        
        # Supprimer la section About
        self.abouts[0].delete()
        
        # Vérifier que l'objet a été supprimé
        self.assertFalse(About.objects.filter(id=id_about).exists())
        
        # Vérifier que la section ne s'affiche plus
        self.response = self.client.get(reverse('load_data'), {'identifiant': self.profile.identifiant})
        self.assertEqual(self.response.status_code, 200)
        
        data = self.response.json()
        self.assertIn('about', data)
        self.assertEqual(len(data['about']), self.abouts.count())

    def test_create_experience(self):
        """Teste la création d'une expérience"""

        # Vérifier que l'objet a été créé
        self.assertTrue(Experience.objects.filter(company=self.experiences[0].company).exists())
        
        # Vérifier que l'expérience apparaît dans l'interface
        self.response = self.client.get(reverse('load_data'), {'identifiant': self.profile.identifiant})
        self.assertEqual(self.response.status_code, 200)
        
        data = self.response.json()
        self.assertIn('experience', data)
        self.assertEqual(len(data['experience']), self.experiences.count())
        self.assertEqual(data['experience'][0]['company'], self.experiences[0].company)

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
        Experience.objects.filter(id=self.experiences[0].id).update(**updated_data)
        self.experiences[0].refresh_from_db()
        
        # Vérifier que les modifications ont été sauvegardées
        self.assertEqual(self.experiences[0].company, 'Entreprise mise à jour')
        self.assertEqual(self.experiences[0].order, 1)
        
        # Vérifier que les changements apparaissent dans l'interface via load_data
        self.response = self.client.get(reverse('load_data'), {'identifiant': self.profile.identifiant})
        self.assertEqual(self.response.status_code, 200)
        
        data = self.response.json()
        self.assertIn('experience', data)
        self.assertEqual(len(data['experience']), self.experiences.count())
        self.assertEqual(data['experience'][0]['company'], 'Entreprise mise à jour')
        self.assertEqual(data['experience'][0]['order'], 1)

    def test_delete_experience(self):
        """Teste la suppression d'une expérience"""

        id_experience = self.experiences[0].id
        
        # Supprimer l'expérience
        self.experiences[0].delete()
        
        # Vérifier que l'objet a été supprimé
        self.assertFalse(Experience.objects.filter(id=id_experience).exists())
        
        # Vérifier que l'expérience ne s'affiche plus
        self.response = self.client.get(reverse('load_data'), {'identifiant': self.profile.identifiant})
        self.assertEqual(self.response.status_code, 200)
        
        data = self.response.json()
        self.assertIn('experience', data)
        self.assertEqual(len(data['experience']), self.experiences.count())

    def test_create_project(self):
        """Teste la création d'un projet"""

        # Vérifier que l'objet a été créé
        self.assertTrue(Project.objects.filter(title=self.projects[0].title).exists())
        
        # Vérifier que le projet apparaît dans l'interface
        self.response = self.client.get(reverse('load_data'), {'identifiant': self.profile.identifiant})
        self.assertEqual(self.response.status_code, 200)
        
        data = self.response.json()
        self.assertIn('projects', data)
        self.assertEqual(len(data['projects']), self.projects.count())
        self.assertEqual(data['projects'][0]['title'], self.projects[0].title)

    def test_update_project(self):
        """Teste la mise à jour d'un projet"""
        
        # Données pour la mise à jour
        updated_data = {
            'title': 'Titre mis à jour',
            'description': 'Description mise à jour',
            'order': 1
        }
        
        # Mettre à jour le projet
        Project.objects.filter(id=self.projects[0].id).update(**updated_data)
        self.projects[0].refresh_from_db()
        
        # Vérifier que les modifications ont été sauvegardées
        self.assertEqual(self.projects[0].title, 'Titre mis à jour')
        self.assertEqual(self.projects[0].order, 1)
        
        # Vérifier que les changements apparaissent dans l'interface via load_data
        self.response = self.client.get(reverse('load_data'), {'identifiant': self.profile.identifiant})
        self.assertEqual(self.response.status_code, 200)
        
        data = self.response.json()
        self.assertIn('projects', data)
        self.assertEqual(len(data['projects']), self.projects.count())
        self.assertEqual(data['projects'][0]['title'], 'Titre mis à jour')
        self.assertEqual(data['projects'][0]['order'], 1)

    def test_delete_project(self):
        """Teste la suppression d'un projet"""
        id_project = self.projects[0].id

        # Supprimer le projet
        self.projects[0].delete()
        
        # Vérifier que l'objet a été supprimé
        self.assertFalse(Project.objects.filter(id=id_project).exists())
        
        # Vérifier que le projet ne s'affiche plus
        self.response = self.client.get(reverse('load_data'), {'identifiant': self.profile.identifiant})
        self.assertEqual(self.response.status_code, 200)
        
        data = self.response.json()
        self.assertIn('projects', data)
        self.assertEqual(len(data['projects']), self.projects.count())

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
        
        # Vérifier l'ordre via load_data
        self.response = self.client.get(reverse('load_data'), {'identifiant': self.profile.identifiant})
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

class SaveDataTest(BaseTest):

    def test_create_profile(self):
        """Teste la création d'un profil"""
        # Données pour la création
        data = {
            'name': 'Test Profile',
            'identifiant': 'test_identifiant'
        }
        
        # Effectuer la création via l'API
        response = self.client.post(
            reverse('save_data'),
            {
                'modalId': 'profileModal',
                'isNew': True,
                'data': data
            },
            content_type='application/json'
        )
        
        # Vérifier la réponse de l'API
        self.assertEqual(response.status_code, 200)
        result = response.json()
        
        # Vérifier que le profil a été créé
        self.assertEqual(result['success'], True)
        self.assertTrue(Profile.objects.filter(identifiant=data['identifiant']).exists())

    def test_update_profile(self):
        """Teste la mise à jour d'un profil"""
        # Données pour la mise à jour
        updated_data = {
            'name': 'Nouveau nom de test',
            'identifiant': 'new_identifiant',
            'id': self.profile.id
        }
        
        # Effectuer la mise à jour via l'API
        response = self.client.post(
            reverse('save_data'),
            {
                'modalId': 'profileModal',
                'isNew': False,
                'data': updated_data
            },
            content_type='application/json'
        )
        
        # Vérifier la réponse de l'API
        self.assertEqual(response.status_code, 200)
        result = response.json()
        
        # Vérifier que les modifications ont été sauvegardées
        updated_profile = Profile.objects.get(id=self.profile.id)
        self.assertEqual(updated_profile.name, updated_data['name'])
        self.assertEqual(updated_profile.identifiant, updated_data['identifiant'])

    def test_create_about(self):
        """Teste la création d'un élément About via l'API"""
        # Données pour la création
        data = {
            'content': 'Contenu de test',
            'order': 1,
            'profile': self.profile.identifiant
        }
        
        # Effectuer la création via l'API
        response = self.client.post(
            reverse('save_data'),
            {
                'modalId': 'aboutModal',
                'isNew': True,
                'data': data
            },
            content_type='application/json'
        )
        
        # Vérifier la réponse de l'API
        self.assertEqual(response.status_code, 200)
        result = response.json()
        
        # Vérifier que le profil a été créé
        self.assertEqual(result['success'], True)
        self.assertTrue(About.objects.filter(order=data['order']).exists())

    def test_update_about(self):
        """Teste la mise à jour d'un élément About via l'API"""
        # Données pour la mise à jour
        updated_data = {
            'content': 'Nouveau contenu de test',
            'order': 2,
            'id': self.abouts[0].id,
            'profile': self.profile.id
        }
        
        # Effectuer la mise à jour via l'API
        response = self.client.post(
            reverse('save_data'),
            {
                'modalId': 'aboutModal',
                'isNew': False,
                'data': updated_data
            },
            content_type='application/json'
        )
        
        # Vérifier la réponse de l'API
        self.assertEqual(response.status_code, 200)
        result = response.json()
        
        # Vérifier que les modifications ont été sauvegardées
        updated_about = About.objects.get(id=self.abouts[0].id)
        self.assertEqual(updated_about.content, updated_data['content'])
        self.assertEqual(updated_about.order, updated_data['order'])

    def test_create_experience(self):
        """Teste la création d'un élément Experience via l'API"""
        # Données pour la création
        data = {
            'dates': '2024-2025',
            'company': 'Entreprise de test',
            'location': 'Endroit de test',
            'position': 'Poste de test',
            'description': 'Description de test',
            'order': 2,
            'profile': self.profile.identifiant
        }
        
        # Effectuer la création via l'API
        response = self.client.post(
            reverse('save_data'),
            {
                'modalId': 'experienceModal',
                'isNew': True,
                'data': data
            },
            content_type='application/json'
        )
        
        # Vérifier la réponse de l'API
        self.assertEqual(response.status_code, 200)
        result = response.json()
        
        # Vérifier que le profil a été créé
        self.assertEqual(result['success'], True)
        self.assertTrue(Experience.objects.filter(order=data['order']).exists())

    def test_update_experience(self):
        """Teste la mise à jour d'un élément Experience via l'API"""
        # Données pour la mise à jour
        updated_data = {
            'dates': '2024-2025',
            'company': 'Entreprise mise à jour',
            'location': 'Endroit mis à jour',
            'position': 'Poste mis à jour',
            'description': 'Description mise à jour',
            'order': 2,
            'id': self.experiences[0].id
        }
        
        # Effectuer la mise à jour via l'API
        response = self.client.post(
            reverse('save_data'),
            {
                'modalId': 'experienceModal',
                'isNew': False,
                'data': updated_data
            },
            content_type='application/json'
        )
        
        # Vérifier la réponse de l'API
        self.assertEqual(response.status_code, 200)
        result = response.json()
        
        # Vérifier que les modifications ont été sauvegardées
        updated_experience = Experience.objects.get(id=self.experiences[0].id)
        self.assertEqual(updated_experience.company, updated_data['company'])
        self.assertEqual(updated_experience.dates, updated_data['dates'])
        self.assertEqual(updated_experience.location, updated_data['location'])
        self.assertEqual(updated_experience.position, updated_data['position'])
        self.assertEqual(updated_experience.description, updated_data['description'])
        self.assertEqual(updated_experience.order, updated_data['order'])

    def test_create_project(self):
        """Teste la création d'un élément Project via l'API"""
        # Données pour la création
        data = {
            'title': 'Titre de test',
            'description': 'Description de test',
            'order': 2,
            'profile': self.profile.identifiant
        }
        
        # Effectuer la création via l'API
        response = self.client.post(
            reverse('save_data'),
            {
                'modalId': 'projectModal',
                'isNew': True,
                'data': data
            },
            content_type='application/json'
        )
        
        # Vérifier la réponse de l'API
        self.assertEqual(response.status_code, 200)
        result = response.json()
        
        # Vérifier que le profil a été créé
        self.assertEqual(result['success'], True)
        self.assertTrue(Project.objects.filter(order=data['order']).exists())

    def test_update_project(self):
        """Teste la mise à jour d'un élément Project"""
        # Données pour la mise à jour
        updated_data = {
            'title': 'Titre mis à jour',
            'description': 'Description mise à jour',
            'order': 2,
            'id': self.projects[0].id
        }
        
        # Effectuer la mise à jour via l'API
        response = self.client.post(
            reverse('save_data'),
            {
                'modalId': 'projectModal',
                'isNew': False,
                'data': updated_data
            },
            content_type='application/json'
        )
        
        # Vérifier la réponse de l'API
        self.assertEqual(response.status_code, 200)
        result = response.json()
        
        # Vérifier que les modifications ont été sauvegardées
        updated_project = Project.objects.get(id=self.projects[0].id)
        self.assertEqual(updated_project.title, updated_data['title'])
        self.assertEqual(updated_project.description, updated_data['description'])
        self.assertEqual(updated_project.order, updated_data['order'])
        
        # Effectuer la mise à jour via l'API
        response = self.client.post(
            reverse('save_data'),
            {
                'modalId': 'projectModal',
                'isNew': False,
                'data': updated_data
            },
            content_type='application/json'
        )
        
        # Vérifier la réponse de l'API
        self.assertEqual(response.status_code, 200)
        result = response.json()
        
        # Vérifier que les modifications ont été sauvegardées
        updated_project = Project.objects.get(id=self.projects[0].id)
        self.assertEqual(updated_project.title, updated_data['title'])
        self.assertEqual(updated_project.description, updated_data['description'])
        self.assertEqual(updated_project.order, updated_data['order'])

class DeleteDataTest(BaseTest):

    def test_delete_profile(self):
        """Teste la suppression d'un profil"""

        # Effectuer la suppression
        response = self.client.delete(
            reverse('delete_profile', args=[self.profile.id])
        )
        
        # Vérifier la réponse de l'API
        self.assertEqual(response.status_code, 200)
        result = response.json()
        
        # Vérifier que le profil a été supprimé
        self.assertEqual(result['success'], True)
        self.assertFalse(Profile.objects.filter(id=self.profile.id).exists())

        # Vérifier que les éléments liés ont été supprimés
        self.assertFalse(About.objects.filter(profile=self.profile).exists())
        self.assertFalse(Experience.objects.filter(profile=self.profile).exists())
        self.assertFalse(Project.objects.filter(profile=self.profile).exists())

    def test_delete_about(self):
        """Teste la suppression d'un About"""

        about_id = self.abouts[0].id

        # Effectuer la suppression
        response = self.client.delete(
            reverse('delete_about', args=[about_id])
        )
        
        # Vérifier la réponse de l'API
        self.assertEqual(response.status_code, 200)
        result = response.json()
        
        # Vérifier que le profil a été supprimé
        self.assertEqual(result['success'], True)
        self.assertFalse(About.objects.filter(id=about_id).exists())

    def test_delete_experience(self):
        """Teste la suppression d'une expérience"""

        experience_id = self.experiences[0].id

        # Effectuer la suppression
        response = self.client.delete(
            reverse('delete_experience', args=[experience_id])
        )
        
        # Vérifier la réponse de l'API
        self.assertEqual(response.status_code, 200)
        result = response.json()
        
        # Vérifier que le profil a été supprimé
        self.assertEqual(result['success'], True)
        self.assertFalse(Experience.objects.filter(id=experience_id).exists())

    def test_delete_project(self):
        """Teste la suppression d'un projet"""

        project_id = self.projects[0].id

        # Effectuer la suppression
        response = self.client.delete(
            reverse('delete_project', args=[project_id])
        )
        
        # Vérifier la réponse de l'API
        self.assertEqual(response.status_code, 200)
        result = response.json()
        
        # Vérifier que le profil a été supprimé
        self.assertEqual(result['success'], True)
        self.assertFalse(Project.objects.filter(id=project_id).exists())