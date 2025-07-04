from django.test import TestCase
from django.urls import resolve, reverse
from django.http import HttpRequest
from pierrpgd.views import portfolio, data_display
from pierrpgd.models import Profile, About, Experience, Education,Project, Skill, ProfileSkill, Color
from bs4 import BeautifulSoup
from datetime import datetime

class BaseTest(TestCase):
    fixtures = ['test_fixtures.json']

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.profile = Profile.objects.get(identifiant='test-profile')
        cls.abouts = About.objects.filter(profile=cls.profile)
        cls.experiences = Experience.objects.filter(profile=cls.profile)
        cls.educations = Education.objects.filter(profile=cls.profile)
        cls.projects = Project.objects.filter(profile=cls.profile)
        cls.skills = Skill.objects.all()
        cls.colors = Color.objects.filter(profile=cls.profile)
        cls.profile_skills = ProfileSkill.objects.filter(profile=cls.profile)

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
        title_element = self.soup.find(id="title")
        self.assertIsNotNone(name_element)
        self.assertEqual(name_element.text.strip(), self.profile.name)
        self.assertIsNotNone(title_element)
        self.assertEqual(title_element.text.strip(), self.profile.title)

    def test_about_display(self):
        """Teste l'affichage des sections About"""
        about_section = self.soup.find(id="about")
        self.assertIsNotNone(about_section)
        
        about_content = about_section.find_all('p')[0].text
        self.assertEqual(about_content.strip(), self.abouts[0].content)

    def test_skills_display(self):
        """Teste l'affichage des sections Skills"""
        skills_section = self.soup.find(id="skills")
        self.assertIsNotNone(skills_section)

        skills_names = skills_section.find_all(class_="skill-badge")
        skills_values = skills_section.find_all(class_="skill-level")
        self.assertIn(self.profile_skills[0].skill.name, [skill_name.text for skill_name in skills_names])
        self.assertIn(str(self.profile_skills[0].level), [skill_value.text for skill_value in skills_values])

    def test_experience_display(self):
        """Teste l'affichage des expériences"""
        experience_section = self.soup.find(id="experience")
        self.assertIsNotNone(experience_section)

        exp_url = experience_section.find('a')
        self.assertIsNotNone(exp_url)
        self.assertEqual(exp_url['href'], self.experiences[0].url)

        rows = experience_section.find_all('div', class_='row')
        
        self.assertEqual(self.experiences[0].dates, rows[0].find('div', class_='tile-dates').text.strip())
        self.assertEqual(self.experiences[0].position, rows[0].find('div', class_='tile-title').text.strip())
        self.assertEqual(self.experiences[0].location, rows[0].find('div', class_='tile-subtitle').find('span', class_='location').text.strip())
        self.assertEqual(self.experiences[0].company, rows[0].find('div', class_='tile-subtitle').find('span', class_='company').text.strip())
        self.assertEqual(self.experiences[0].description, rows[0].find('div', class_='tile-description').text.strip())

        skills = [skill.name for skill in self.experiences[0].skills.all()]
        self.assertEqual(skills, [exp.text for exp in rows[0].find_all('span', class_='skill-badge')])

    def test_education_display(self):
        """Teste l'affichage des éducations"""
        education_section = self.soup.find(id="education")
        self.assertIsNotNone(education_section)

        exp_url = education_section.find('a')
        self.assertIsNotNone(exp_url)
        self.assertEqual(exp_url['href'], self.educations[0].url)

        rows = education_section.find_all('div', class_='row')
        
        self.assertEqual(self.educations[0].dates, rows[0].find('div', class_='tile-dates').text.strip())
        self.assertEqual(self.educations[0].title, rows[0].find('div', class_='tile-title').text.strip())
        self.assertEqual(self.educations[0].location, rows[0].find('div', class_='tile-subtitle').find('span', class_='location').text.strip())
        self.assertEqual(self.educations[0].institution, rows[0].find('div', class_='tile-subtitle').find('span', class_='institution').text.strip())
        self.assertEqual(self.educations[0].description, rows[0].find('div', class_='tile-description').text.strip())

        skills = [skill.name for skill in self.educations[0].skills.all()]
        self.assertEqual(skills, [exp.text for exp in rows[0].find_all('span', class_='skill-badge')])

    def test_projects_display(self):
        """Teste l'affichage des projets"""
        projects_section = self.soup.find(id="projects")
        self.assertIsNotNone(projects_section)

        project_url = projects_section.find('a')['href']
        self.assertEqual(project_url, self.projects[0].url)
        
        rows = projects_section.find_all('div', class_='row')
        
        self.assertEqual(self.projects[0].title, rows[0].find('div', class_='tile-title').text.strip())
        self.assertEqual(self.projects[0].description, rows[0].find('div', class_='tile-description').text.strip())
        
        skills = [skill.name for skill in self.projects[0].skills.all()]
        self.assertEqual(skills, [skill.text for skill in rows[0].find_all('span', class_='skill-badge')])

    def test_nonexistent_profile(self):
        """Test que l'accès à un profil inexistant renvoie une erreur 404"""
        self.response = self.client.get(reverse('portfolio', args=['non-existent']))
        self.assertEqual(self.response.status_code, 404)

class DataDisplayViewTest(BaseTest):
    def setUp(self):
        self.request = HttpRequest()
        self.response = data_display(self.request)
        self.soup = BeautifulSoup(self.response.content, 'html.parser')

    def test_url_resolves_to_data_display(self):
        """Teste que l'URL racine résout vers la vue portfolio"""
        found = resolve('/data/')
        self.assertEqual(found.func, data_display)

    def test_data_display_view(self):
        """Teste la vue data_display"""
        self.response_data = self.client.get('/data/')
        self.assertEqual(self.response_data.status_code, 200)
        self.assertTemplateUsed(self.response_data, 'data_display.html')

    def test_profile_display(self):
        """
        Teste l'affichage des profils
        1. Récupère la page data_display
        2. Vérifie que le code HTTP est 200
        3. Vérifie que le nom du profil est affiché
        """
        self.assertEqual(self.response.status_code, 200)
        profile_table_container = self.soup.find(id="profile-table-container")
        profile_elements = [
            [td.text.strip() for td in row.find_all('td')] 
            for row in profile_table_container.find('tbody').find_all('tr')
        ]
        profile_identifiant = profile_elements[0][0]
        profile_name = profile_elements[0][1]
        profile_title = profile_elements[0][2]
        profile_creation_date = profile_elements[0][3]
        profile_last_update_date = profile_elements[0][4]
        
        self.assertEqual(profile_identifiant, self.profile.identifiant)
        self.assertEqual(profile_name, self.profile.name)
        self.assertEqual(profile_title, self.profile.title)
        self.assertEqual(profile_creation_date[:-5], self.profile.created_at.strftime('%B %-d, %Y, à %-I:%M'))
        self.assertEqual(profile_last_update_date[:-5], self.profile.updated_at.strftime('%B %-d, %Y, à %-I:%M'))

    def test_profile_deletion(self):
        # Supprimer le profil et vérifier que les données associées sont supprimées
        Profile.objects.all().delete()

        self.response = data_display(self.request)
        self.soup = BeautifulSoup(self.response.content, 'html.parser')

        profile_table_container = self.soup.find(id="profile-table-container")
        profile_data = self.soup.find(id="profile-data")

        self.assertIn('Aucun profil trouvé', profile_table_container.text)
        self.assertIn('Sélectionnez un profil pour voir ses données', profile_data.text)

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
        self.assertEqual(data['profile']['title'], self.profile.title)
        self.assertEqual(datetime.strptime(data['profile']['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%B %d, %Y, à %I:%M'), self.profile.created_at.strftime('%B %d, %Y, à %I:%M'))
        self.assertEqual(datetime.strptime(data['profile']['updated_at'], '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%B %d, %Y, à %I:%M'), self.profile.updated_at.strftime('%B %d, %Y, à %I:%M'))

    def test_update_profile(self):
        """Teste la mise à jour d'un profil"""
        
        # Données pour la mise à jour
        updated_data = {
            'name': 'Nom mis à jour',
            'identifiant': 'identifiant mis à jour',
            'title': 'Titre mis à jour'
        }
        
        # Mettre à jour la section About
        Profile.objects.filter(id=self.profile.id).update(**updated_data)
        self.profile.refresh_from_db()
        
        # Vérifier que les modifications ont été sauvegardées
        self.assertEqual(self.profile.name, 'Nom mis à jour')
        self.assertEqual(self.profile.identifiant, 'identifiant mis à jour')
        self.assertEqual(self.profile.title, 'Titre mis à jour')
        
        # Vérifier que les changements apparaissent dans l'interface via load_data
        self.response = self.client.get(reverse('load_data'), {'identifiant': self.profile.identifiant})
        self.assertEqual(self.response.status_code, 200)
        
        data = self.response.json()
        self.assertIn('profile', data)
        self.assertEqual(data['profile']['name'], 'Nom mis à jour')
        self.assertEqual(data['profile']['identifiant'], 'identifiant mis à jour')
        self.assertEqual(data['profile']['title'], 'Titre mis à jour')
        self.assertEqual(datetime.strptime(data['profile']['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%B %d, %Y, à %I:%M'), self.profile.created_at.strftime('%B %d, %Y, à %I:%M'))
        self.assertEqual(datetime.strptime(data['profile']['updated_at'], '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%B %d, %Y, à %I:%M'), self.profile.updated_at.strftime('%B %d, %Y, à %I:%M'))

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

    def test_create_skill(self):
        """Teste la création d'une compétence"""
        
        # Vérifier que l'objet a été créé
        self.assertTrue(Skill.objects.filter(name='Test Skill').exists())
        
        # Vérifier que la section apparaît dans l'interface
        self.response = self.client.get(reverse('load_data'), {'identifiant': self.profile.identifiant})
        self.assertEqual(self.response.status_code, 200)
        
        # Vérifier que la compétence a été créée
        data = self.response.json()
        self.assertIn('skills', data)
        self.assertEqual(data['skills'][0]['name'], 'Test Skill')
        self.assertEqual(data['skills'][1]['name'], 'Second Skill')
        self.assertEqual(data['skills'][2]['name'], 'Third Skill')

    def test_update_skill(self):
        """Teste la mise à jour d'une compétence"""
        
        # Données pour la mise à jour
        updated_data = {
            'name': 'Nom mis à jour',
            'category': 'Catégorie mis à jour'
        }
        
        # Mettre à jour la compétence
        Skill.objects.filter(id=self.skills[0].id).update(**updated_data)
        self.skills[0].refresh_from_db()
        
        # Vérifier que les modifications ont été sauvegardées
        self.assertEqual(self.skills[0].name, 'Nom mis à jour')
        self.assertEqual(self.skills[0].category, 'Catégorie mis à jour')
        
        # Vérifier que les changements apparaissent dans l'interface via load_data
        self.response = self.client.get(reverse('load_data'), {'identifiant': self.profile.identifiant})
        self.assertEqual(self.response.status_code, 200)
        
        # Vérifier que la compétence a été mise à jour
        data = self.response.json()
        self.assertIn('skills', data)
        self.assertEqual(data['skills'][0]['name'], 'Nom mis à jour')
        self.assertEqual(data['skills'][0]['category'], 'Catégorie mis à jour')

    def test_delete_skill(self):
        """Teste la suppression d'une compétence"""

        id_skill = self.skills[0].id
        
        # Supprimer la compétence
        self.skills[0].delete()
        
        # Vérifier que l'objet a été supprimé
        self.assertFalse(Skill.objects.filter(id=id_skill).exists())
        
        # Vérifier que la section ne s'affiche plus
        self.response = self.client.get(reverse('load_data'), {'identifiant': self.profile.identifiant})
        self.assertEqual(self.response.status_code, 200)
        
        # Vérifier que la compétence a été supprimée
        data = self.response.json()
        self.assertIn('skills', data)
        self.assertEqual(len(data['skills']), 2)

    def test_create_color(self):
        """Teste la création d'une couleur"""
        
        # Vérifier que l'objet a été créé
        self.assertTrue(Color.objects.filter(red=255, green=0, blue=0, transparency=100, profile=self.profile).exists())
        
        # Vérifier que la section apparaît dans l'interface
        self.response = self.client.get(reverse('load_data'), {'identifiant': self.profile.identifiant})
        self.assertEqual(self.response.status_code, 200)
        
        # Vérifier que la compétence a été créée
        data = self.response.json()
        self.assertIn('colors', data)
        bTrouve = False
        for color in data['colors']:
            if color['red'] == 255 and color['green'] == 0 and color['blue'] == 0 and color['transparency'] == 100:
                bTrouve = True
                break
        self.assertTrue(bTrouve)

    def test_update_color(self):
        """Teste la mise à jour d'une couleur"""
        
        # Données pour la mise à jour
        updated_data = {
            'red': 255,
            'green': 0,
            'blue': 0,
            'transparency': 50
        }
        
        # Mettre à jour la compétence
        Color.objects.filter(id=self.colors[0].id).update(**updated_data)
        self.colors[0].refresh_from_db()
        
        # Vérifier que les modifications ont été sauvegardées
        self.assertEqual(self.colors[0].red, updated_data['red'])
        self.assertEqual(self.colors[0].green, updated_data['green'])
        self.assertEqual(self.colors[0].blue, updated_data['blue'])
        self.assertEqual(self.colors[0].transparency, updated_data['transparency'])
        
        # Vérifier que les changements apparaissent dans l'interface via load_data
        self.response = self.client.get(reverse('load_data'), {'identifiant': self.profile.identifiant})
        self.assertEqual(self.response.status_code, 200)
        
        # Vérifier que la compétence a été mise à jour
        data = self.response.json()
        self.assertIn('colors', data)
        self.assertEqual(data['colors'][0]['red'], updated_data['red'])
        self.assertEqual(data['colors'][0]['green'], updated_data['green'])
        self.assertEqual(data['colors'][0]['blue'], updated_data['blue'])
        self.assertEqual(data['colors'][0]['transparency'], updated_data['transparency'])

    def test_delete_color(self):
        """Teste la suppression d'une couleur"""
        nb_colors = len(self.colors)
        id_color = self.colors[0].id
        
        # Supprimer la compétence
        self.colors[0].delete()
        
        # Vérifier que l'objet a été supprimé
        self.assertFalse(Color.objects.filter(id=id_color).exists())
        
        # Vérifier que la section ne s'affiche plus
        self.response = self.client.get(reverse('load_data'), {'identifiant': self.profile.identifiant})
        self.assertEqual(self.response.status_code, 200)
        
        # Vérifier que la compétence a été supprimée
        data = self.response.json()
        self.assertIn('colors', data)
        self.assertEqual(len(data['colors']), nb_colors-1)

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
        }
        
        # Mettre à jour la section About
        About.objects.filter(id=self.abouts[0].id).update(**updated_data)
        self.abouts[0].refresh_from_db()
        
        # Vérifier que les modifications ont été sauvegardées
        self.assertEqual(self.abouts[0].content, 'Contenu mis à jour')
        
        # Vérifier que les changements apparaissent dans l'interface via load_data
        self.response = self.client.get(reverse('load_data'), {'identifiant': self.profile.identifiant})
        self.assertEqual(self.response.status_code, 200)
        
        data = self.response.json()
        self.assertIn('about', data)
        self.assertEqual(len(data['about']), self.abouts.count())
        self.assertEqual(data['about'][0]['content'], 'Contenu mis à jour')

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
        self.assertEqual(data['experience'][0]['dates'], self.experiences[0].dates)
        self.assertEqual(data['experience'][0]['position'], self.experiences[0].position)
        self.assertEqual(data['experience'][0]['description'], self.experiences[0].description)
        self.assertEqual(data['experience'][0]['details'], self.experiences[0].details)
        self.assertEqual(data['experience'][0]['location'], self.experiences[0].location)
        self.assertEqual(data['experience'][0]['url'], self.experiences[0].url)
        self.assertEqual(data['experience'][0]['skills'], [self.skills[0].id, self.skills[1].id])

    def test_update_experience(self):
        """Teste la mise à jour d'une expérience"""
        
        # Données pour la mise à jour
        updated_data = {
            'dates': '2024-2025',
            'company': 'Entreprise mise à jour',
            'location': 'Endroit mis à jour',
            'position': 'Poste mis à jour',
            'description': 'Description mise à jour',
            'details': 'Details mise à jour',
            'url': 'https://testurl2.com'
        }
        
        # Mettre à jour l'expérience
        Experience.objects.filter(id=self.experiences[0].id).update(**updated_data)
        self.experiences[0].refresh_from_db()
        
        # Vérifier que les modifications ont été sauvegardées
        self.assertEqual(self.experiences[0].company, 'Entreprise mise à jour')
        
        # Vérifier que les changements apparaissent dans l'interface via load_data
        self.response = self.client.get(reverse('load_data'), {'identifiant': self.profile.identifiant})
        self.assertEqual(self.response.status_code, 200)
        
        data = self.response.json()
        self.assertIn('experience', data)
        self.assertEqual(len(data['experience']), self.experiences.count())
        self.assertEqual(data['experience'][0]['company'], 'Entreprise mise à jour')
        self.assertEqual(data['experience'][0]['location'], 'Endroit mis à jour')
        self.assertEqual(data['experience'][0]['position'], 'Poste mis à jour')
        self.assertEqual(data['experience'][0]['description'], 'Description mise à jour')
        self.assertEqual(data['experience'][0]['details'], 'Details mise à jour')
        self.assertEqual(data['experience'][0]['dates'], '2024-2025')
        self.assertEqual(data['experience'][0]['url'], 'https://testurl2.com')
        self.assertEqual(data['experience'][0]['skills'], [self.skills[0].id, self.skills[1].id])

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

    def test_create_education(self):
        """Teste la création d'une éducation"""

        # Vérifier que l'objet a été créé
        self.assertTrue(Education.objects.filter(title=self.educations[0].title).exists())
        
        # Vérifier que l'éducation apparaît dans l'interface
        self.response = self.client.get(reverse('load_data'), {'identifiant': self.profile.identifiant})
        self.assertEqual(self.response.status_code, 200)
        
        data = self.response.json()
        self.assertIn('education', data)
        self.assertEqual(len(data['education']), self.educations.count())
        self.assertEqual(data['education'][0]['title'], self.educations[0].title)
        self.assertEqual(data['education'][0]['dates'], self.educations[0].dates)
        self.assertEqual(data['education'][0]['institution'], self.educations[0].institution)
        self.assertEqual(data['education'][0]['field'], self.educations[0].field)
        self.assertEqual(data['education'][0]['description'], self.educations[0].description)
        self.assertEqual(data['education'][0]['details'], self.educations[0].details)
        self.assertEqual(data['education'][0]['location'], self.educations[0].location)
        self.assertEqual(data['education'][0]['url'], self.educations[0].url)
        self.assertEqual(data['education'][0]['skills'], [self.skills[0].id, self.skills[1].id])

    def test_update_education(self):
        """Teste la mise à jour d'une éducation"""
        
        # Données pour la mise à jour
        updated_data = {
            'dates': '2024-2025',
            'title': 'Nouveau titre',
            'institution': 'Nouvelle institution',
            'field': 'Nouveau domaine',
            'location': 'Endroit mis à jour',
            'description': 'Description mise à jour',
            'details': 'Détails mis à jour',
            'url': 'https://testurl2.com'
        }
        
        # Mettre à jour l'expérience
        Education.objects.filter(id=self.educations[0].id).update(**updated_data)
        self.educations[0].refresh_from_db()
        
        # Vérifier que les modifications ont été sauvegardées
        self.assertEqual(self.educations[0].title, 'Nouveau titre')
        
        # Vérifier que les changements apparaissent dans l'interface via load_data
        self.response = self.client.get(reverse('load_data'), {'identifiant': self.profile.identifiant})
        self.assertEqual(self.response.status_code, 200)
        
        data = self.response.json()
        self.assertIn('education', data)
        self.assertEqual(len(data['education']), self.educations.count())
        self.assertEqual(data['education'][0]['title'], 'Nouveau titre')
        self.assertEqual(data['education'][0]['institution'], 'Nouvelle institution')
        self.assertEqual(data['education'][0]['field'], 'Nouveau domaine')
        self.assertEqual(data['education'][0]['location'], 'Endroit mis à jour')
        self.assertEqual(data['education'][0]['description'], 'Description mise à jour')
        self.assertEqual(data['education'][0]['details'], 'Détails mis à jour')
        self.assertEqual(data['education'][0]['dates'], '2024-2025')
        self.assertEqual(data['education'][0]['url'], 'https://testurl2.com')
        self.assertEqual(data['education'][0]['skills'], [self.skills[0].id, self.skills[1].id])

    def test_delete_education(self):
        """Teste la suppression d'une éducation"""

        id_education = self.educations[0].id
        
        # Supprimer l'éducation
        self.educations[0].delete()
        
        # Vérifier que l'objet a été supprimé
        self.assertFalse(Education.objects.filter(id=id_education).exists())
        
        # Vérifier que l'éducation ne s'affiche plus
        self.response = self.client.get(reverse('load_data'), {'identifiant': self.profile.identifiant})
        self.assertEqual(self.response.status_code, 200)
        
        data = self.response.json()
        self.assertIn('education', data)
        self.assertEqual(len(data['education']), self.educations.count())

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
        self.assertEqual(data['projects'][0]['description'], self.projects[0].description)
        self.assertEqual(data['projects'][0]['details'], self.projects[0].details)
        self.assertEqual(data['projects'][0]['image_url'], self.projects[0].image_url)
        self.assertEqual(data['projects'][0]['url'], self.projects[0].url)
        self.assertEqual(data['projects'][0]['skills'], [self.skills[1].id, self.skills[2].id])

    def test_update_project(self):
        """Teste la mise à jour d'un projet"""
        
        # Données pour la mise à jour
        updated_data = {
            'title': 'Titre mis à jour',
            'description': 'Description mise à jour',
            'details': 'Details mis à jour',
            'image_url': 'image_url',
            'url': 'url',
        }
        
        # Mettre à jour le projet
        Project.objects.filter(id=self.projects[0].id).update(**updated_data)
        self.projects[0].refresh_from_db()
        
        # Vérifier que les modifications ont été sauvegardées
        self.assertEqual(self.projects[0].title, 'Titre mis à jour')
        
        # Vérifier que les changements apparaissent dans l'interface via load_data
        self.response = self.client.get(reverse('load_data'), {'identifiant': self.profile.identifiant})
        self.assertEqual(self.response.status_code, 200)
        
        data = self.response.json()
        self.assertIn('projects', data)
        self.assertEqual(len(data['projects']), self.projects.count())
        self.assertEqual(data['projects'][0]['title'], 'Titre mis à jour')
        self.assertEqual(data['projects'][0]['description'], 'Description mise à jour')
        self.assertEqual(data['projects'][0]['details'], 'Details mis à jour')
        self.assertEqual(data['projects'][0]['image_url'], 'image_url')
        self.assertEqual(data['projects'][0]['url'], 'url')
        self.assertEqual(data['projects'][0]['skills'], [self.skills[1].id, self.skills[2].id])

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
        about1 = About.objects.create(profile=self.profile, content='About 1')
        about2 = About.objects.create(profile=self.profile, content='About 2')
        about3 = About.objects.create(profile=self.profile, content='About 3')
        
        # Créer des Projets avec différents ordres
        project1 = Project.objects.create(profile=self.profile, title='Project 1')
        project2 = Project.objects.create(profile=self.profile, title='Project 2')
        project3 = Project.objects.create(profile=self.profile, title='Project 3')
        
        # Créer des Expériences avec différents ordres
        experience1 = Experience.objects.create(profile=self.profile, company='Experience 1', dates='2023')
        experience2 = Experience.objects.create(profile=self.profile, company='Experience 2', dates='2024')
        experience3 = Experience.objects.create(profile=self.profile, company='Experience 3', dates='2025')
        
        # Vérifier l'ordre via load_data
        self.response = self.client.get(reverse('load_data'), {'identifiant': self.profile.identifiant})
        self.assertEqual(self.response.status_code, 200)
        
        data = self.response.json()
        
        # Vérifier l'ordre des About
        abouts = data['about']
        self.assertEqual(len(abouts), 3)
        self.assertEqual(abouts[0]['content'], 'About 1')  # Order = 0
        self.assertEqual(abouts[1]['content'], 'About 2')  # Order = 1
        self.assertEqual(abouts[2]['content'], 'About 3')  # Order = 2
        
        # Vérifier l'ordre des Projets
        projects = data['projects']
        self.assertEqual(len(projects), 3)
        self.assertEqual(projects[0]['title'], 'Project 1')  # Order = 0
        self.assertEqual(projects[1]['title'], 'Project 2')  # Order = 1
        self.assertEqual(projects[2]['title'], 'Project 3')  # Order = 2
        
        # Vérifier l'ordre des Expériences
        experiences = data['experience']
        self.assertEqual(len(experiences), 3)
        self.assertEqual(experiences[0]['company'], 'Experience 1')  # Order = 0
        self.assertEqual(experiences[1]['company'], 'Experience 2')  # Order = 1
        self.assertEqual(experiences[2]['company'], 'Experience 3')  # Order = 2

class SaveDataTest(BaseTest):

    def test_create_profile(self):
        """Teste la création d'un profil"""
        # Données pour la création
        data = {
            'name': 'Test Profile',
            'identifiant': 'test_identifiant',
            'title': 'Test Title'
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

        # Vérifier que le profil a été créé avec les bonnes données
        profile = Profile.objects.get(identifiant=data['identifiant'])
        self.assertEqual(profile.name, data['name'])
        self.assertEqual(profile.identifiant, data['identifiant'])
        self.assertEqual(profile.title, data['title'])

    def test_update_profile(self):
        """Teste la mise à jour d'un profil"""
        # Données pour la mise à jour
        updated_data = {
            'name': 'Nouveau nom de test',
            'identifiant': 'new_identifiant',
            'title': 'Nouveau titre de test',
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
        self.assertEqual(updated_profile.title, updated_data['title'])

    def test_create_about(self):
        """Teste la création d'un élément About via l'API"""
        # Données pour la création
        data = {
            'content': 'Contenu de test',
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
        self.assertTrue(About.objects.filter(content=data['content']).exists())

    def test_update_about(self):
        """Teste la mise à jour d'un élément About via l'API"""
        # Données pour la mise à jour
        updated_data = {
            'content': 'Nouveau contenu de test',
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

    def test_create_experience(self):
        """Teste la création d'un élément Experience via l'API"""
        # Données pour la création
        data = {
            'dates': '2024-2025',
            'company': 'Entreprise de test',
            'location': 'Endroit de test',
            'position': 'Poste de test',
            'description': 'Description de test',
            'details': 'Details de test',
            'url': 'https://testurl4.com',
            'skills': [self.skills[0].id, self.skills[2].id],
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
        exp = Experience.objects.get(
            dates=data['dates'], 
            company=data['company'], 
            location=data['location'],
            position=data['position'],
            description=data['description'],
            details=data['details'],
            url=data['url']
        )
        self.assertIsNotNone(exp)
        self.assertEqual([skill.id for skill in exp.skills.all()], data['skills'])

    def test_update_experience(self):
        """Teste la mise à jour d'un élément Experience via l'API"""
        # Données pour la mise à jour
        updated_data = {
            'dates': '2024-2025',
            'company': 'Entreprise mise à jour',
            'location': 'Endroit mis à jour',
            'position': 'Poste mis à jour',
            'description': 'Description mise à jour',
            'details': 'Details mise à jour',
            'url': 'https://testurl5.com',
            'skills': [self.skills[0].id, self.skills[2].id],
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
        self.assertEqual(updated_experience.details, updated_data['details'])
        self.assertEqual(updated_experience.url, updated_data['url'])
        self.assertEqual([skill.id for skill in updated_experience.skills.all()], updated_data['skills'])

    def test_create_education(self):
        """Teste la création d'un élément Education via l'API"""
        # Données pour la création
        data = {
            'dates': '2024-2025',
            'title': 'Titre de test',
            'institution': 'Institution de test',
            'field': 'Domaine de test',
            'description': 'Description de test',
            'details': 'Détails de test',
            'url': 'https://testurl4.com',
            'skills': [self.skills[0].id, self.skills[2].id],
            'profile': self.profile.identifiant
        }
        
        # Effectuer la création via l'API
        response = self.client.post(
            reverse('save_data'),
            {
                'modalId': 'educationModal',
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
        edu = Education.objects.get(
            dates=data['dates'], 
            title=data['title'], 
            institution=data['institution'],
            field=data['field'],
            description=data['description'],
            details=data['details'],
            url=data['url']
        )
        self.assertIsNotNone(edu)
        self.assertEqual([skill.id for skill in edu.skills.all()], data['skills'])

    def test_update_education(self):
        """Teste la mise à jour d'un élément Education via l'API"""
        # Données pour la mise à jour
        updated_data = {
            'dates': '2024-2025',
            'title': 'Titre mise à jour',
            'institution': 'Institution mise à jour',
            'field': 'Domaine mise à jour',
            'description': 'Description mise à jour',
            'details': 'Détails mise à jour',
            'url': 'https://testurl5.com',
            'skills': [self.skills[0].id, self.skills[2].id],
            'id': self.experiences[0].id
        }
        
        # Effectuer la mise à jour via l'API
        response = self.client.post(
            reverse('save_data'),
            {
                'modalId': 'educationModal',
                'isNew': False,
                'data': updated_data
            },
            content_type='application/json'
        )
        
        # Vérifier la réponse de l'API
        self.assertEqual(response.status_code, 200)
        result = response.json()
        
        # Vérifier que les modifications ont été sauvegardées
        updated_education = Education.objects.get(id=self.educations[0].id)
        self.assertEqual(updated_education.title, updated_data['title'])
        self.assertEqual(updated_education.dates, updated_data['dates'])
        self.assertEqual(updated_education.institution, updated_data['institution'])
        self.assertEqual(updated_education.field, updated_data['field'])
        self.assertEqual(updated_education.description, updated_data['description'])
        self.assertEqual(updated_education.details, updated_data['details'])
        self.assertEqual(updated_education.url, updated_data['url'])
        self.assertEqual([skill.id for skill in updated_education.skills.all()], updated_data['skills'])

    def test_create_project(self):
        """Teste la création d'un élément Project via l'API"""
        # Données pour la création
        data = {
            'title': 'Titre de test save_data',
            'description': 'Description de test save_data',
            'details': 'Details de test save_data',
            'image_url': 'image_url',
            'url': 'url',
            'skills': [self.skills[1].id, self.skills[2].id],
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

        project = Project.objects.get(
            title=data['title'], 
            description=data['description'],
            details=data['details'],
            image_url=data['image_url'],
            url=data['url']
        )
        self.assertIsNotNone(project)
        self.assertEqual([skill.id for skill in project.skills.all()], data['skills'])

    def test_update_project(self):
        """Teste la mise à jour d'un élément Project"""
        # Données pour la mise à jour
        updated_data = {
            'title': 'Titre mis à jour',
            'description': 'Description mise à jour',
            'details': 'Details mis à jour',
            'image_url': 'image_url',
            'url': 'url',
            'skills': [self.skills[0].id, self.skills[2].id],
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
        self.assertEqual(updated_project.details, updated_data['details'])
        self.assertEqual(updated_project.image_url, updated_data['image_url'])
        self.assertEqual(updated_project.url, updated_data['url'])
        self.assertEqual([skill.id for skill in updated_project.skills.all()], updated_data['skills'])

    def test_create_skill(self):
        """Teste la création d'une compétence"""
        
        # Données pour la création
        data = {
            'category': 'New Test Category',
            'name': 'New Test Skill',
            'profile': self.profile.identifiant,
            'level': 7
        }
        
        # Effectuer la création via l'API
        response = self.client.post(
            reverse('save_data'),
            {
                'modalId': 'skillModal',
                'isNew': True,
                'data': data
            },
            content_type='application/json'
        )
        
        # Vérifier la réponse de l'API
        self.assertEqual(response.status_code, 200)
        result = response.json()
        skill_id = result['data']['id']
        
        # Vérifier que la compétence a été créée
        self.assertEqual(result['success'], True)
        self.assertTrue(Skill.objects.filter(name=data['name']).exists())

        # Vérifier que le profil est lié à la compétence
        profile = Profile.objects.get(identifiant=data['profile'])
        skill = Skill.objects.get(name=data['name'])
        self.assertIn(skill, profile.skills.all())
        profile_skill = ProfileSkill.objects.get(profile=profile, skill=skill)
        self.assertEqual(profile_skill.level, data['level'])

        ## Test de création d'un compétence qui existe déjà

        # Deuxième profil de test
        data['profile'] = "second-profile"
        data["level"] = 2

        # Effectuer la création via l'API
        response = self.client.post(
            reverse('save_data'),
            {
                'modalId': 'skillModal',
                'isNew': True,
                'data': data
            },
            content_type='application/json'
        )
        
        # Vérifier la réponse de l'API
        self.assertEqual(response.status_code, 200)
        result = response.json()
        
        # Vérifier que la compétence n'a pas été créée
        self.assertEqual(result['success'], True)
        self.assertEqual(skill_id, result['data']['id'])

        # Vérifier que le deuxième profil est lié à la compétence
        profile = Profile.objects.get(identifiant=data['profile'])
        self.assertIn(skill, profile.skills.all())
        profile_skill = ProfileSkill.objects.get(profile=profile, skill=skill)
        self.assertEqual(profile_skill.level, data['level'])

    def test_update_skill(self):
        """Teste la mise à jour d'une compétence"""
        # Données pour la mise à jour
        updated_data = {
            'name': 'Nouveau nom de test',
            'category': 'Nouvelle catégorie de test',
            'id': self.skills[0].id,
            'profile': self.profile.identifiant,
            'level': 4
        }
        
        # Effectuer la mise à jour via l'API
        response = self.client.post(
            reverse('save_data'),
            {
                'modalId': 'skillModal',
                'isNew': False,
                'data': updated_data
            },
            content_type='application/json'
        )
        
        # Vérifier la réponse de l'API
        self.assertEqual(response.status_code, 200)
        
        # Vérifier que les modifications ont été sauvegardées
        updated_skill = Skill.objects.get(id=self.skills[0].id)
        self.assertEqual(updated_skill.name, updated_data['name'])
        self.assertEqual(updated_skill.category, updated_data['category'])
        
        # Vérifier que le profil est lié à la compétence
        profile = Profile.objects.get(identifiant=updated_data['profile'])
        skill = Skill.objects.get(name=updated_data['name'])
        self.assertIn(skill, profile.skills.all())

        profile_skill = ProfileSkill.objects.get(profile=profile, skill=skill)
        self.assertEqual(profile_skill.level, updated_data['level'])

        # Vérifier que les autres profils liés à la compétence ont été mis à jour
        profile = Profile.objects.get(identifiant='second-profile')
        skill = Skill.objects.get(name=updated_data['name'])
        self.assertIn(skill, profile.skills.all())

        profile_skill = ProfileSkill.objects.get(profile=profile, skill=skill)
        self.assertEqual(profile_skill.level, 6)

    def test_create_color(self):
        """Teste la création d'une couleur"""
        
        # Données pour la création
        data = {
            'red': 0,
            'green': 0,
            'blue': 255,
            'profile': self.profile.identifiant,
            'transparency': 50
        }
        
        # Effectuer la création via l'API
        response = self.client.post(
            reverse('save_data'),
            {
                'modalId': 'colorModal',
                'isNew': True,
                'data': data
            },
            content_type='application/json'
        )
        
        # Vérifier la réponse de l'API
        self.assertEqual(response.status_code, 200)
        result = response.json()
        
        # Vérifier que la compétence a été créée
        self.assertEqual(result['success'], True)
        self.assertTrue(Color.objects.filter(red=data['red'], green=data['green'], blue=data['blue']).exists())

    def test_update_color(self):
        """Teste la mise à jour d'une couleur"""
        # Données pour la mise à jour
        updated_data = {
            'red': 120,
            'green': 0,
            'blue': 0,
            'transparency': 40,
            'id': self.colors[0].id,
            'profile': self.profile.identifiant,
        }
        
        # Effectuer la mise à jour via l'API
        response = self.client.post(
            reverse('save_data'),
            {
                'modalId': 'colorModal',
                'isNew': False,
                'data': updated_data
            },
            content_type='application/json'
        )
        
        # Vérifier la réponse de l'API
        self.assertEqual(response.status_code, 200)
        
        # Vérifier que les modifications ont été sauvegardées
        updated_color = Color.objects.get(id=self.colors[0].id)
        self.assertEqual(updated_color.red, updated_data['red'])
        self.assertEqual(updated_color.green, updated_data['green'])
        self.assertEqual(updated_color.blue, updated_data['blue'])
        self.assertEqual(updated_color.transparency, updated_data['transparency'])

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

    def test_delete_education(self):
        """Teste la suppression d'une éducation"""

        education_id = self.educations[0].id

        # Effectuer la suppression
        response = self.client.delete(
            reverse('delete_education', args=[education_id])
        )
        
        # Vérifier la réponse de l'API
        self.assertEqual(response.status_code, 200)
        result = response.json()
        
        # Vérifier que le profil a été supprimé
        self.assertEqual(result['success'], True)
        self.assertFalse(Education.objects.filter(id=education_id).exists())

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

    def test_delete_skill(self):
        """Teste la suppression d'une compétence liée au profil"""

        # Effectuer la suppression
        response = self.client.delete(
            reverse('delete_skill', args=[self.profile.identifiant, self.skills[0].id])
        )
        
        # Vérifier la réponse de l'API
        self.assertEqual(response.status_code, 200)
        result = response.json()

        # Vérifier que la compétence existe toujours
        skill = Skill.objects.get(id=self.skills[0].id)
        self.assertTrue(skill)

        # Vérifier que la compétence a été supprimée pour le profil
        self.assertEqual(result['success'], True)
        profile = Profile.objects.get(identifiant=self.profile.identifiant)
        self.assertNotIn(skill, profile.skills.all())

        # Vérifier que la compétence a été supprimée des expériences du profil
        experiences = Experience.objects.filter(profile=profile)
        for experience in experiences:
            self.assertNotIn(skill, experience.skills.all())
        
        # Vérifier que la compétence a été supprimée des projets du profil
        projects = Project.objects.filter(profile=profile)
        for project in projects:
            self.assertNotIn(skill, project.skills.all())

    def test_delete_color(self):
        """Teste la suppression d'une Color"""

        color_id = self.colors[0].id

        # Effectuer la suppression
        response = self.client.delete(
            reverse('delete_color', args=[color_id])
        )
        
        # Vérifier la réponse de l'API
        self.assertEqual(response.status_code, 200)
        result = response.json()
        
        # Vérifier que le profil a été supprimé
        self.assertEqual(result['success'], True)
        self.assertFalse(Color.objects.filter(id=color_id).exists())
