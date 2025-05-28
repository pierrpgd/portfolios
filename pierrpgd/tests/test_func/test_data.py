from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from pierrpgd.models import Profile, About, Experience, Project, Skill
from selenium.webdriver.common.keys import Keys
from django.test import Client
from django.conf import settings
import time
class BaseTest(LiveServerTestCase):
    fixtures = ['test_fixtures.json']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        cls.browser = webdriver.Chrome(options=options)

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super().tearDownClass()

    def setUpPortfolio(self):
        """
        Sets up the test for the portfolio page.

        Opens the portfolio page and logs in with the test user.
        """
        self.getData()
        self.url = f"{self.live_server_url}/{self.profile.identifiant}"
        self.browser.get(self.url)

    def setUpData(self):
        """
        Sets up the test for the data page.

        Opens the data page and logs in with the test user.
        """     
        self.getData()
        self.url = f"{self.live_server_url}/data"
        self.browser.get(self.url)

        self.client = Client()
        self.client.login(username='testuser', password='testpassword')

        session = self.client.session
        self.browser.add_cookie({
            'name': settings.SESSION_COOKIE_NAME,
            'value': session.session_key,
            'path': '/',
        })

    def getData(self):
        self.profile = Profile.objects.get(identifiant='test-profile')
        self.abouts = About.objects.filter(profile=self.profile).order_by('order')
        self.experiences = Experience.objects.filter(profile=self.profile).order_by('order')
        self.projects = Project.objects.filter(profile=self.profile).order_by('order')
        self.skills = Skill.objects.filter(profile=self.profile).order_by('id')

class ProfileTest(BaseTest):

    def setUp(self):
        super().setUp()
        self.setUpData()

    def test_profile_data_is_visible(self):
        """
        Teste l'affichage des données d'un profil avec Selenium
        """
        
        # Trouver la ligne du profil dans le tableau
        profile_row = self.browser.find_element(By.XPATH, f"//table[contains(@id, 'profile-table')]//td[contains(text(), '{self.profile.name}')]/..")

        profile_identifiant = profile_row.find_element(By.XPATH, './td[1]').text
        profile_name = profile_row.find_element(By.XPATH, './td[2]').text
        profile_title = profile_row.find_element(By.XPATH, './td[3]').text
        profile_creation_date = profile_row.find_element(By.XPATH, './td[4]').text
        profile_modification_date = profile_row.find_element(By.XPATH, './td[5]').text

        self.assertEqual(profile_identifiant, self.profile.identifiant, "Profile identifiant doesn't match.")
        self.assertEqual(profile_name, self.profile.name, "Profile name doesn't match.")
        self.assertEqual(profile_title, self.profile.title, "Profile title doesn't match.")
        self.assertEqual(profile_creation_date[:-5], self.profile.created_at.strftime('%B %d, %Y, à %-I:%M'), "Profile creation date doesn't match.")
        self.assertEqual(profile_modification_date[:-5], self.profile.updated_at.strftime('%B %d, %Y, à %-I:%M'), "Profile modification date doesn't match.")

    def test_profile_selection_toggle_and_data_display_or_hide(self):
        """
        Teste la sélection d'un profil et l'affichage des données liées avec Selenium
        """

        # Trouver la ligne du profil dans le tableau
        profile_row = self.browser.find_element(By.XPATH, f"//table[contains(@id, 'profile-table')]//td[contains(text(), '{self.profile.name}')]/..")

        # Cliquer sur la ligne du profil
        self.browser.execute_script("arguments[0].click();", profile_row)
        
        # Attendre que les données soient chargées
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@id='profile-data']//h2[text()='À propos']"))
        )

        # Vérifier l'affichage des données Compétences
        skill_name = self.browser.find_element(By.XPATH, "//div[@id='profile-data']//table[contains(@id, 'skill-table')]//td[contains(text(), 'Test Skill')]")
        skill_category = self.browser.find_element(By.XPATH, "//div[@id='profile-data']//table[contains(@id, 'skill-table')]//td[contains(text(), 'Test Category')]")
        self.assertTrue(skill_name.is_displayed())
        self.assertTrue(skill_category.is_displayed())

        # Vérifier l'affichage des données About
        about_content = self.browser.find_element(By.XPATH, "//div[@id='profile-data']//table[contains(@id, 'about-table')]//td[contains(text(), 'Test About Content')]")
        self.assertTrue(about_content.is_displayed())

        # Vérifier l'affichage des données Experience
        experience_dates = self.browser.find_element(By.XPATH, "//div[@id='profile-data']//table[contains(@id, 'experience-table')]//td[contains(text(), '2023-2024')]")
        experience_company = self.browser.find_element(By.XPATH, "//div[@id='profile-data']//table[contains(@id, 'experience-table')]//td[contains(text(), 'Test Company')]")
        experience_location = self.browser.find_element(By.XPATH, "//div[@id='profile-data']//table[contains(@id, 'experience-table')]//td[contains(text(), 'Test Location')]")
        experience_position = self.browser.find_element(By.XPATH, "//div[@id='profile-data']//table[contains(@id, 'experience-table')]//td[contains(text(), 'Test Position')]")
        experience_description = self.browser.find_element(By.XPATH, "//div[@id='profile-data']//table[contains(@id, 'experience-table')]//td[contains(text(), 'Test Description')]")
        experience_url = self.browser.find_element(By.XPATH, "//div[@id='profile-data']//table[contains(@id, 'experience-table')]//td[contains(text(), 'https://testurl.com')]")
        self.assertTrue(experience_dates.is_displayed())
        self.assertTrue(experience_company.is_displayed())
        self.assertTrue(experience_location.is_displayed())
        self.assertTrue(experience_position.is_displayed())
        self.assertTrue(experience_description.is_displayed())
        self.assertTrue(experience_url.is_displayed())

        # Vérifier l'affichage des données Project
        project_title = self.browser.find_element(By.XPATH, "//div[@id='profile-data']//table[contains(@id, 'projects-table')]//td[contains(text(), 'Test Project')]")
        project_description = self.browser.find_element(By.XPATH, "//div[@id='profile-data']//table[contains(@id, 'projects-table')]//td[contains(text(), 'Test Project Description')]")
        project_image_url = self.browser.find_element(By.XPATH, "//div[@id='profile-data']//table[contains(@id, 'projects-table')]//td[contains(text(), '/static/portfolio-example.png')]")
        project_url = self.browser.find_element(By.XPATH, "//div[@id='profile-data']//table[contains(@id, 'projects-table')]//td[contains(text(), 'https://testurl3.com')]")
        self.assertTrue(project_title.is_displayed())
        self.assertTrue(project_description.is_displayed())
        self.assertTrue(project_image_url.is_displayed())
        self.assertTrue(project_url.is_displayed())

        # Cliquer à nouveau sur la ligne du profil pour le désélectionner
        self.browser.execute_script("arguments[0].click();", profile_row)
        
        # Attendre que les données soient masquées
        WebDriverWait(self.browser, 10).until(
            EC.invisibility_of_element_located((By.XPATH, "//div[@id='profile-data']//h2[text()='À propos']"))
        )
        
        # Vérifier que les données sont masquées
        about_content = self.browser.find_elements(By.XPATH, "//div[@id='profile-data']//table[contains(@id, 'about-table')]//td[contains(text(), 'Test About Content')]")
        self.assertEqual(len(about_content), 0)
        
        experience_company = self.browser.find_elements(By.XPATH, "//div[@id='profile-data']//table[contains(@id, 'experience-table')]//td[contains(text(), 'Test Company')]")
        self.assertEqual(len(experience_company), 0)
        
        project_title = self.browser.find_elements(By.XPATH, "//div[@id='profile-data']//table[contains(@id, 'projects-table')]//td[contains(text(), 'Test Project')]")
        self.assertEqual(len(project_title), 0)

class PopupTest(BaseTest):

    def setUp(self):
        super().setUp()
        self.setUpData()

    def test_double_click_profile(self):
        """Teste le comportement du double clic sur une ligne du tableau Profil"""
        
        # Sélectionner le profil
        profile_row = self.browser.find_element(By.XPATH, f"//table[contains(@id, 'profile-table')]//td[contains(text(), '{self.profile.identifiant}')]/..")
        
        # Effectuer un double clic
        action = ActionChains(self.browser)
        action.double_click(profile_row).perform()

        # Attendre que la popup soit visible
        WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.ID, 'profileModal'))
        )

        # Vérifier que la popup est visible
        modal = self.browser.find_element(By.ID, 'profileModal')
        self.assertTrue(modal.is_displayed())
        
        # Vérifier que le contenu de la popup est correct
        modal_content = self.browser.find_element(By.CSS_SELECTOR, '#profileModal .modal-content')
        identifiant = modal_content.find_element(By.CSS_SELECTOR, '.modal-content-info .editable-field .editable-content[data-field="identifiant"]').text
        name = modal_content.find_element(By.CSS_SELECTOR, '.modal-content-info .editable-field .editable-content[data-field="name"]').text
        title = modal_content.find_element(By.CSS_SELECTOR, '.modal-content-info .editable-field .editable-content[data-field="title"]').text
        self.assertEqual(identifiant, self.profile.identifiant)
        self.assertEqual(name, self.profile.name)
        self.assertEqual(title, self.profile.title)
        
        # Fermer la popup
        close_button = self.browser.find_element(By.CSS_SELECTOR, '#profileModal .modal-header button.close')
        self.browser.execute_script("arguments[0].click();", close_button)
        
        # Attendre que la popup soit masquée
        try:
            WebDriverWait(self.browser, 10).until(
                EC.invisibility_of_element_located((By.ID, 'profileModal'))
            )
        except:
            # La modal a été supprimée, donc elle n'est plus dans le DOM
            pass
        
        # Vérifier que la modal n'est plus présente dans le DOM
        with self.assertRaises(NoSuchElementException):
            self.browser.find_element(By.ID, 'profileModal')

    def test_double_click_skill(self):
        """Teste le comportement du double clic sur une ligne du tableau Compétences"""
        
        # Sélectionner le profil
        profile_row = self.browser.find_element(By.XPATH, f"//table[contains(@id, 'profile-table')]//td[contains(text(), '{self.profile.identifiant}')]/..")
        self.browser.execute_script("arguments[0].click();", profile_row)
        
        # Attendre que les données soient chargées
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@id='profile-data']//h2[text()='Compétences']"))
        )
        
        # Trouver la ligne du tableau Compétences
        skill_row = self.browser.find_element(By.XPATH, "//div[@id='profile-data']//table[contains(@id, 'skill-table')]//td[contains(text(), 'Test Skill')]/..")
        
        # Effectuer un double clic
        action = ActionChains(self.browser)
        action.double_click(skill_row).perform()
        
        # Attendre que la popup soit visible
        WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.ID, 'skillModal'))
        )
        
        # Vérifier que la popup est visible
        try:
            modal = self.browser.find_element(By.ID, 'skillModal')
            self.assertTrue(modal.is_displayed())
            
            # Vérifier que le contenu de la popup est correct
            modal_content = self.browser.find_element(By.CSS_SELECTOR, '#skillModal .modal-content')
            category = modal_content.find_element(By.CSS_SELECTOR, '[data-field="category"]').text
            name = modal_content.find_element(By.CSS_SELECTOR, '[data-field="name"]').text
            self.assertEqual(category, 'Test Category')
            self.assertEqual(name, 'Test Skill')
            
            # Fermer la popup
            close_button = self.browser.find_element(By.CSS_SELECTOR, '#skillModal .modal-header button.close')
            self.browser.execute_script("arguments[0].click();", close_button)
            
            # Attendre que la popup soit masquée
            try:
                WebDriverWait(self.browser, 10).until(
                    EC.invisibility_of_element_located((By.ID, 'skillModal'))
                )
            except:
                # La modal a été supprimée, donc elle n'est plus dans le DOM
                pass
            
            # Vérifier que la modal n'est plus présente dans le DOM
            with self.assertRaises(NoSuchElementException):
                self.browser.find_element(By.ID, 'skillModal')
            
            # Trouver la ligne du tableau Compétences pour la deuxième section
            skill_row = self.browser.find_element(By.XPATH, f"//div[@id='profile-data']//table[contains(@id, 'skill-table')]//td[contains(text(), 'Second Skill')]/..")

            # Effectuer un double clic
            action = ActionChains(self.browser)
            action.double_click(skill_row).perform()
            
            # Attendre que la popup soit visible
            WebDriverWait(self.browser, 10).until(
                EC.visibility_of_element_located((By.ID, 'skillModal'))
            )
            
            # Vérifier que la popup est visible
            modal = self.browser.find_element(By.ID, 'skillModal')
            self.assertTrue(modal.is_displayed())

            # Vérifier le contenu de la popup
            modal_content = self.browser.find_element(By.CSS_SELECTOR, '#skillModal .modal-content')
            category = modal_content.find_element(By.CSS_SELECTOR, '[data-field="category"]').text
            name = modal_content.find_element(By.CSS_SELECTOR, '[data-field="name"]').text
            self.assertEqual(category, 'Second Category')
            self.assertEqual(name, 'Second Skill')
            
            # Fermer la popup
            close_button = self.browser.find_element(By.CSS_SELECTOR, '#skillModal .modal-header button.close')
            self.browser.execute_script("arguments[0].click();", close_button)
            
            # Attendre que la popup soit masquée
            try:
                WebDriverWait(self.browser, 10).until(
                    EC.invisibility_of_element_located((By.ID, 'skillModal'))
                )
            except:
                # La modal a été supprimée, donc elle n'est plus dans le DOM
                pass
            
        except NoSuchElementException:
            self.fail("La popup n'a pas été trouvée")

    def test_double_click_about(self):
        """Teste le comportement du double clic sur une ligne du tableau À propos"""
        
        # Sélectionner le profil
        profile_row = self.browser.find_element(By.XPATH, f"//table[contains(@id, 'profile-table')]//td[contains(text(), '{self.profile.identifiant}')]/..")
        self.browser.execute_script("arguments[0].click();", profile_row)
        
        # Attendre que les données soient chargées
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@id='profile-data']//h2[text()='À propos']"))
        )
        
        # Trouver la ligne du tableau À propos
        about_row = self.browser.find_element(By.XPATH, "//div[@id='profile-data']//table[contains(@id, 'about-table')]//td[contains(text(), 'Test About Content')]/..")
        
        # Effectuer un double clic
        action = ActionChains(self.browser)
        action.double_click(about_row).perform()
        
        # Attendre que la popup soit visible
        WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.ID, 'aboutModal'))
        )
        
        # Vérifier que la popup est visible
        try:
            modal = self.browser.find_element(By.ID, 'aboutModal')
            self.assertTrue(modal.is_displayed())
            
            # Vérifier que le contenu de la popup est correct
            modal_content = self.browser.find_element(By.CSS_SELECTOR, '#aboutModal .modal-content')
            content = modal_content.find_element(By.CSS_SELECTOR, '[data-field="content"]').text
            self.assertEqual(content, 'Test About Content')
            
            # Fermer la popup
            close_button = self.browser.find_element(By.CSS_SELECTOR, '#aboutModal .modal-header button.close')
            self.browser.execute_script("arguments[0].click();", close_button)
            
            # Attendre que la popup soit masquée
            try:
                WebDriverWait(self.browser, 10).until(
                    EC.invisibility_of_element_located((By.ID, 'aboutModal'))
                )
            except:
                # La modal a été supprimée, donc elle n'est plus dans le DOM
                pass
            
            # Vérifier que la modal n'est plus présente dans le DOM
            with self.assertRaises(NoSuchElementException):
                self.browser.find_element(By.ID, 'aboutModal')
            
            # Trouver la ligne du tableau About pour la deuxième section
            about_row = self.browser.find_element(By.XPATH, f"//div[@id='profile-data']//table[contains(@id, 'about-table')]//td[contains(text(), '{self.abouts[1].content}')]/..")

            # Effectuer un double clic
            action = ActionChains(self.browser)
            action.double_click(about_row).perform()
            
            # Attendre que la popup soit visible
            WebDriverWait(self.browser, 10).until(
                EC.visibility_of_element_located((By.ID, 'aboutModal'))
            )
            
            # Vérifier que la popup est visible
            modal = self.browser.find_element(By.ID, 'aboutModal')
            self.assertTrue(modal.is_displayed())

            # Vérifier le contenu de la popup
            modal_content = self.browser.find_element(By.CSS_SELECTOR, '#aboutModal .modal-content')
            self.assertIn(self.abouts[1].content, modal_content.text)
            
            # Fermer la popup
            close_button = self.browser.find_element(By.CSS_SELECTOR, '#aboutModal .modal-header button.close')
            self.browser.execute_script("arguments[0].click();", close_button)
            
            # Attendre que la popup soit masquée
            try:
                WebDriverWait(self.browser, 10).until(
                    EC.invisibility_of_element_located((By.ID, 'aboutModal'))
                )
            except:
                # La modal a été supprimée, donc elle n'est plus dans le DOM
                pass
            
        except NoSuchElementException:
            self.fail("La popup n'a pas été trouvée")

    def test_double_click_experience(self):
        """Teste le comportement du double clic sur une ligne du tableau Expériences"""
        
        # Sélectionner le profil
        profile_row = self.browser.find_element(By.XPATH, f"//table[contains(@id, 'profile-table')]//td[contains(text(), '{self.profile.identifiant}')]/..")
        self.browser.execute_script("arguments[0].click();", profile_row)
        
        # Attendre que les données soient chargées
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@id='profile-data']//h2[text()='Expériences']"))
        )
        
        # Trouver la ligne du tableau Expériences
        experience_row = self.browser.find_element(By.XPATH, f"//div[@id='profile-data']//table[contains(@id, 'experience-table')]//td[contains(text(), '{self.experiences[0].description}')]/..")
        
        # Effectuer un double clic
        action = ActionChains(self.browser)
        action.double_click(experience_row).perform()
        
        # Attendre que la popup soit visible
        WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.ID, 'experienceModal'))
        )
        
        # Vérifier que la popup est visible
        modal = self.browser.find_element(By.ID, 'experienceModal')
        self.assertTrue(modal.is_displayed())
        
        # Vérifier le contenu de la popup
        modal_content = self.browser.find_element(By.CSS_SELECTOR, '#experienceModal .modal-content')

        dates = modal_content.find_element(By.CSS_SELECTOR, '[data-field="dates"]').text
        company = modal_content.find_element(By.CSS_SELECTOR, '[data-field="company"]').text
        position = modal_content.find_element(By.CSS_SELECTOR, '[data-field="position"]').text
        location = modal_content.find_element(By.CSS_SELECTOR, '[data-field="location"]').text
        description = modal_content.find_element(By.CSS_SELECTOR, '[data-field="description"]').text
        experience_url = modal_content.find_element(By.CSS_SELECTOR, '[data-field="url"]').text
        skills_elements = modal_content.find_elements(By.CLASS_NAME, 'skill-badge')
        skills = [skill.text for skill in skills_elements]

        self.assertEqual(dates, '2023-2024')
        self.assertEqual(position, 'Test Position')
        self.assertEqual(company, 'Test Company')
        self.assertEqual(description, 'Test Description')
        self.assertEqual(location, 'Test Location')
        self.assertEqual(experience_url, 'https://testurl.com')
        self.assertEqual(skills, ['Test Skill', 'Second Skill'])
        
        # Fermer la popup
        close_button = self.browser.find_element(By.CSS_SELECTOR, '#experienceModal .modal-header button.close')
        self.browser.execute_script("arguments[0].click();", close_button)
        
        # Attendre que la popup soit masquée
        try:
            WebDriverWait(self.browser, 10).until(
                EC.invisibility_of_element_located((By.ID, 'experienceModal'))
            )
        except:
            # La modal a été supprimée, donc elle n'est plus dans le DOM
            pass
        
        # Vérifier que la modal n'est plus présente dans le DOM
        with self.assertRaises(NoSuchElementException):
            self.browser.find_element(By.ID, 'experienceModal')
        
        # Trouver la ligne du tableau Expériences pour la deuxième expérience
        experience_row = self.browser.find_element(By.XPATH, f"//div[@id='profile-data']//table[contains(@id, 'experience-table')]//td[contains(text(), '{self.experiences[1].description}')]/..")

        # Effectuer un double clic
        action = ActionChains(self.browser)
        action.double_click(experience_row).perform()
        
        # Attendre que la popup soit visible
        WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.ID, 'experienceModal'))
        )
        
        # Vérifier que la popup est visible
        modal = self.browser.find_element(By.ID, 'experienceModal')
        self.assertTrue(modal.is_displayed())

        # Vérifier le contenu de la popup
        modal_content = self.browser.find_element(By.CSS_SELECTOR, '#experienceModal .modal-content')

        dates = modal_content.find_element(By.CSS_SELECTOR, '[data-field="dates"]').text
        company = modal_content.find_element(By.CSS_SELECTOR, '[data-field="company"]').text
        position = modal_content.find_element(By.CSS_SELECTOR, '[data-field="position"]').text
        location = modal_content.find_element(By.CSS_SELECTOR, '[data-field="location"]').text
        description = modal_content.find_element(By.CSS_SELECTOR, '[data-field="description"]').text
        experience_url = modal_content.find_element(By.CSS_SELECTOR, '[data-field="url"]').text
        skills = modal_content.find_element(By.ID, 'skills-name').text

        self.assertEqual(dates, '2022-2023')
        self.assertEqual(position, 'Test Position 2')
        self.assertEqual(company, 'Test Company 2')
        self.assertEqual(description, 'Test Description 2')
        self.assertEqual(location, 'Test Location 2')
        self.assertEqual(experience_url, 'https://testurl2.com')
        self.assertEqual(skills, 'Test Skill')
        
        # Vérifier les informations de l'expérience
        info = self.browser.find_element(By.CSS_SELECTOR, '#experienceModal .modal-content-info')
        self.assertIn(self.experiences[1].dates, info.text)
        self.assertIn(self.experiences[1].position, info.text)
        self.assertIn(self.experiences[1].company, info.text)
        self.assertIn(self.experiences[1].location, info.text)
        
        # Fermer la popup
        close_button = self.browser.find_element(By.CSS_SELECTOR, '#experienceModal .modal-header button.close')
        self.browser.execute_script("arguments[0].click();", close_button)
        
        # Attendre que la popup soit masquée
        try:
            WebDriverWait(self.browser, 10).until(
                EC.invisibility_of_element_located((By.ID, 'experienceModal'))
            )
        except:
            # La modal a été supprimée, donc elle n'est plus dans le DOM
            pass

    def test_double_click_project(self):
        """Teste le comportement du double clic sur une ligne du tableau Projets"""
        
        # Sélectionner le profil
        profile_row = self.browser.find_element(By.XPATH, f"//table[contains(@id, 'profile-table')]//td[contains(text(), '{self.profile.identifiant}')]/..")
        self.browser.execute_script("arguments[0].click();", profile_row)
        
        # Attendre que les données soient chargées
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@id='profile-data']//h2[text()='Projets']"))
        )
        
        # Trouver la ligne du tableau Projets
        project_row = self.browser.find_element(By.XPATH, f"//div[@id='profile-data']//table[contains(@id, 'projects-table')]//td[contains(text(), '{self.projects[0].title}')]/..")
        
        # Effectuer un double clic
        action = ActionChains(self.browser)
        action.double_click(project_row).perform()
        
        # Attendre que la popup soit visible
        WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.ID, 'projectModal'))
        )
        
        # Vérifier que la popup est visible
        modal = self.browser.find_element(By.ID, 'projectModal')
        self.assertTrue(modal.is_displayed())
        
        # Vérifier le contenu de la popup
        modal_content = self.browser.find_element(By.CSS_SELECTOR, '#projectModal .modal-content')

        title = modal_content.find_element(By.CSS_SELECTOR, '[data-field="title"]').text
        description = modal_content.find_element(By.CSS_SELECTOR, '[data-field="description"]').text
        image_url = modal_content.find_element(By.CSS_SELECTOR, '[data-field="image_url"]').text
        url = modal_content.find_element(By.CSS_SELECTOR, '[data-field="url"]').text
        skills_elements = modal_content.find_elements(By.CLASS_NAME, 'skill-badge')
        skills = [skill.text for skill in skills_elements]

        self.assertEqual(title, 'Test Project')
        self.assertEqual(description, 'Test Project Description')
        self.assertEqual(image_url, '/static/portfolio-example.png')
        self.assertEqual(url, 'https://testurl3.com')
        self.assertEqual(skills, ['Second Skill', 'Third Skill'])
    
        # Vérifier le titre du projet
        title = self.browser.find_element(By.CSS_SELECTOR, '#projectModal .modal-content-info')
        self.assertIn(self.projects[0].title, title.text)
        
        # Fermer la popup
        close_button = self.browser.find_element(By.CSS_SELECTOR, '#projectModal .modal-header button.close')
        self.browser.execute_script("arguments[0].click();", close_button)
        
        # Attendre que la popup soit masquée
        try:
            WebDriverWait(self.browser, 10).until(
                EC.invisibility_of_element_located((By.ID, 'projectModal'))
            )
        except:
            # La modal a été supprimée, donc elle n'est plus dans le DOM
            pass
        
        # Vérifier que la modal n'est plus présente dans le DOM
        with self.assertRaises(NoSuchElementException):
            self.browser.find_element(By.ID, 'projectModal')
        
        # Trouver la ligne du tableau Projets pour la deuxième ligne
        project_row = self.browser.find_element(By.XPATH, f"//div[@id='profile-data']//table[contains(@id, 'projects-table')]//td[contains(text(), '{self.projects[1].title}')]/..")

        # Effectuer un double clic
        action = ActionChains(self.browser)
        action.double_click(project_row).perform()
        
        # Attendre que la popup soit visible
        WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.ID, 'projectModal'))
        )
        
        # Vérifier que la popup est visible
        modal = self.browser.find_element(By.ID, 'projectModal')
        self.assertTrue(modal.is_displayed())

        # Vérifier le contenu de la popup
        modal_content = self.browser.find_element(By.CSS_SELECTOR, '#projectModal .modal-content')

        title = modal_content.find_element(By.CSS_SELECTOR, '[data-field="title"]').text
        description = modal_content.find_element(By.CSS_SELECTOR, '[data-field="description"]').text
        image_url = modal_content.find_element(By.CSS_SELECTOR, '[data-field="image_url"]').text
        url = modal_content.find_element(By.CSS_SELECTOR, '[data-field="url"]').text
        skills = modal_content.find_element(By.ID, 'skills-name').text

        self.assertEqual(title, 'Second Project')
        self.assertEqual(description, 'Second Project Description')
        self.assertEqual(image_url, '')
        self.assertEqual(url, 'https://testurl4.com')
        self.assertEqual(skills, 'Second Skill')
        
        # Fermer la popup
        close_button = self.browser.find_element(By.CSS_SELECTOR, '#projectModal .modal-header button.close')
        self.browser.execute_script("arguments[0].click();", close_button)
        
        # Attendre que la popup soit masquée
        try:
            WebDriverWait(self.browser, 10).until(
                EC.invisibility_of_element_located((By.ID, 'projectModal'))
            )
        except:
            # La modal a été supprimée, donc elle n'est plus dans le DOM
            pass

    def test_content_is_editable(self):
        """Teste que le contenu de la popup est modifiable par l'utilisateur"""

        # Sélectionner le profil
        profile_row = self.browser.find_element(By.XPATH, f"//table[contains(@id, 'profile-table')]//td[contains(text(), '{self.profile.identifiant}')]/..")
        self.browser.execute_script("arguments[0].click();", profile_row)
        
        # Attendre que les données soient chargées
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@id='profile-data']//h2[text()='Projets']"))
        )
    
        # Trouver la ligne du tableau Projets
        project_row = self.browser.find_element(By.XPATH, f"//div[@id='profile-data']//table[contains(@id, 'projects-table')]//td[contains(text(), '{self.projects[0].title}')]/..")
        
        # Effectuer un double clic
        action = ActionChains(self.browser)
        action.double_click(project_row).perform()
        
        # Attendre que la popup soit visible
        WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.ID, 'projectModal'))
        )
        
        # Vérifier que les champs sont éditables
        editable_fields = self.browser.find_elements(By.CSS_SELECTOR, ".editable-field")
        self.assertGreater(len(editable_fields), 0, "Aucun champ éditable trouvé")

        # Modifier un champ
        first_field = editable_fields[0]
        new_value = "Nouvelle valeur de test"
        
        # Effacer et entrer la nouvelle valeur
        first_field.click()
        action = ActionChains(self.browser)
        action.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
        action.send_keys(new_value).perform()

        # Vérifier que la modification a été sauvegardée
        updated_value = first_field.text
        self.assertEqual(updated_value, f"Titre : {new_value}", "La modification n'a pas été sauvegardée")

class ModifyAndSaveTest(BaseTest):

    def setUp(self):
        super().setUp()
        self.setUpData()

    def test_modify_and_save_profile(self):
        """Teste la modification et la sauvegarde d'un élément Profil"""
        # Sélectionner le profil
        profile_row = self.browser.find_element(By.XPATH, f"//table[contains(@id, 'profile-table')]//td[contains(text(), '{self.profile.identifiant}')]/..")
        self.browser.execute_script("arguments[0].click();", profile_row)

        # Effectuer un double clic
        action = ActionChains(self.browser)
        action.double_click(profile_row).perform()
        
        # Attendre que la popup soit visible
        WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.ID, 'profileModal'))
        )
        
        # Vérifier que la popup est visible
        modal = self.browser.find_element(By.ID, 'profileModal')
        self.assertTrue(modal.is_displayed())
        
        # Modifier le contenu
        identifiant_field = modal.find_element(By.CSS_SELECTOR, 'span.editable-content[data-field="identifiant"]')
        new_content = "Nouveau-test-identifiant"
        
        # Effacer le contenu existant
        identifiant_field.click()
        action = ActionChains(self.browser)
        action.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
        action.send_keys(new_content).perform()

        # Modifier le contenu
        name_field = modal.find_element(By.CSS_SELECTOR, 'span.editable-content[data-field="name"]')
        old_content = name_field.text
        new_content = "Nouveau-test-nom"
        
        # Effacer le contenu existant
        name_field.click()
        action = ActionChains(self.browser)
        action.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
        action.send_keys(new_content).perform()
        
        # Enregistrer et vérifier
        save_button = modal.find_element(By.CSS_SELECTOR, '.btn-primary')
        self.browser.execute_script("arguments[0].click();", save_button)
        
        # Vérifier que la modal commence à se fermer
        WebDriverWait(self.browser, 10).until(
            EC.invisibility_of_element_located((By.ID, 'profileModal'))
        )
        
        # Vérifier côté serveur que la modification est enregistrée
        profile_obj = Profile.objects.get(id=self.profile.id)
        self.assertEqual(profile_obj.name, new_content)
        
        # Vérifier que le tableau est mis à jour
        updated_row = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.XPATH, 
                f"//table[@id='profile-table']//td[contains(., '{new_content}')]"))
        )
        self.assertTrue(updated_row.is_displayed())

        # Vérifier que le contenu précedent ne s'affiche plus
        try:
            old_row = self.browser.find_element(By.XPATH, f"//table[@id='profile-table']//td[contains(., '{old_content}')]")
            self.assertFalse(old_row.is_displayed())
        except:
            pass

    def test_modify_and_save_skill(self):
        """Teste la modification et la sauvegarde d'un élément Compétences"""

        new_content = Skill(
            category="Nouvelle catégorie",
            name="Nouveau nom"
        )

        # Sélectionner le profil
        profile_row = self.browser.find_element(By.XPATH, f"//table[contains(@id, 'profile-table')]//td[contains(text(), '{self.profile.identifiant}')]/..")
        self.browser.execute_script("arguments[0].click();", profile_row)
        
        # Attendre le chargement des données
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.ID, "skill-table"))
        )
        
        # Trouver la ligne du tableau Compétences
        about_row = self.browser.find_element(By.XPATH, f"//div[@id='profile-data']//table[contains(@id, 'skill-table')]//td[contains(text(), '{self.skills[0].category}')]/..")
        
        # Effectuer un double clic
        action = ActionChains(self.browser)
        action.double_click(about_row).perform()
        
        # Attendre que la popup soit visible
        WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.ID, 'skillModal'))
        )
        
        # Vérifier que la popup est visible
        modal = self.browser.find_element(By.ID, 'skillModal')
        self.assertTrue(modal.is_displayed())
        
        # Modifier la catégorie
        category_field = modal.find_element(By.CSS_SELECTOR, 'span.editable-content[data-field="category"]')
        category_field.click()
        action = ActionChains(self.browser)
        action.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
        action.send_keys(new_content.category).perform()

        # Modifier le nom
        name_field = modal.find_element(By.CSS_SELECTOR, 'span.editable-content[data-field="name"]')
        name_field.click()
        action = ActionChains(self.browser)
        action.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
        action.send_keys(new_content.name).perform()
        
        # Enregistrer et vérifier
        save_button = modal.find_element(By.CSS_SELECTOR, '.btn-primary')
        self.browser.execute_script("arguments[0].click();", save_button)
        
        # Vérifier que la modal commence à se fermer
        WebDriverWait(self.browser, 10).until(
            EC.invisibility_of_element_located((By.ID, 'skillModal'))
        )
        
        # Vérifier côté serveur que la modification est enregistrée
        skill_obj = Skill.objects.get(id=self.skills[0].id)
        self.assertEqual(skill_obj.category, new_content.category)
        self.assertEqual(skill_obj.name, new_content.name)
        
        # Vérifier que le tableau est mis à jour
        updated_row = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.XPATH, 
                f"//div[@id='profile-data']//table[@id='skill-table']//td[contains(., '{new_content.category}')]/.."))
        )
        self.assertTrue(updated_row.is_displayed())

    def test_modify_and_save_about(self):
        """Teste la modification et la sauvegarde d'un élément À propos"""
        # Sélectionner le profil
        profile_row = self.browser.find_element(By.XPATH, f"//table[contains(@id, 'profile-table')]//td[contains(text(), '{self.profile.identifiant}')]/..")
        self.browser.execute_script("arguments[0].click();", profile_row)
        
        # Attendre le chargement des données
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.ID, "about-table"))
        )
        
        # Trouver la ligne du tableau À propos
        about_row = self.browser.find_element(By.XPATH, f"//div[@id='profile-data']//table[contains(@id, 'about-table')]//td[contains(text(), '{self.abouts[0].content}')]/..")
        
        # Effectuer un double clic
        action = ActionChains(self.browser)
        action.double_click(about_row).perform()
        
        # Attendre que la popup soit visible
        WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.ID, 'aboutModal'))
        )
        
        # Vérifier que la popup est visible
        modal = self.browser.find_element(By.ID, 'aboutModal')
        self.assertTrue(modal.is_displayed())
        
        # Modifier le contenu
        editable_content = modal.find_element(By.CSS_SELECTOR, '.editable-content')
        new_content = "Nouveau contenu de test"
        
        # Effacer le contenu existant
        editable_content.click()
        action = ActionChains(self.browser)
        action.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
        action.send_keys(new_content).perform()
        
        # Enregistrer et vérifier
        save_button = modal.find_element(By.CSS_SELECTOR, '.btn-primary')
        self.browser.execute_script("arguments[0].click();", save_button)
        
        # Vérifier que la modal commence à se fermer
        WebDriverWait(self.browser, 10).until(
            EC.invisibility_of_element_located((By.ID, 'aboutModal'))
        )
        
        # Vérifier côté serveur que la modification est enregistrée
        about_obj = About.objects.get(id=self.abouts[0].id)
        self.assertEqual(about_obj.content, new_content)
        
        # Vérifier que le tableau est mis à jour
        updated_row = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.XPATH, 
                f"//div[@id='profile-data']//table[@id='about-table']//td[contains(., '{new_content}')]"))
        )
        self.assertTrue(updated_row.is_displayed())

    def test_modify_and_save_experience(self):
        """Teste la modification et la sauvegarde d'un élément Experience"""

        # Créer un nouveau contenu pour l'expérience
        new_content = Experience(
            profile=self.profile,
            dates="2024-2025",
            company="Nouvelle entreprise",
            position="Nouveau poste",
            location="Nouveau lieu",
            description="Nouvelle description",
            url="https://nouvelleurl.com"
        )
        
        # Sélectionner le profil
        profile_row = self.browser.find_element(By.XPATH, f"//table[contains(@id, 'profile-table')]//td[contains(text(), '{self.profile.identifiant}')]/..")
        self.browser.execute_script("arguments[0].click();", profile_row)
        
        # Attendre le chargement des données
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.ID, "experience-table"))
        )
        
        # Trouver la ligne du tableau Experience
        experience_row = self.browser.find_element(By.XPATH, f"//div[@id='profile-data']//table[contains(@id, 'experience-table')]//td[contains(text(), '{self.experiences[0].company}')]/..")
        
        # Effectuer un double clic
        action = ActionChains(self.browser)
        action.double_click(experience_row).perform()
        
        # Attendre que la popup soit visible
        WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.ID, 'experienceModal'))
        )
        
        # Vérifier que la popup est visible
        modal = self.browser.find_element(By.ID, 'experienceModal')
        self.assertTrue(modal.is_displayed())

        # Modifier les dates
        dates_field = modal.find_element(By.CSS_SELECTOR, 'span.editable-content[data-field="dates"]')
        dates_field.click()
        action = ActionChains(self.browser)
        action.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
        action.send_keys(new_content.dates).perform()

        # Modifier l'entreprise
        company_field = modal.find_element(By.CSS_SELECTOR, 'span.editable-content[data-field="company"]')
        company_field.click()
        action = ActionChains(self.browser)
        action.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
        action.send_keys(new_content.company).perform()

        # Modifier le poste
        position_field = modal.find_element(By.CSS_SELECTOR, 'span.editable-content[data-field="position"]')
        position_field.click()
        action = ActionChains(self.browser)
        action.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
        action.send_keys(new_content.position).perform()

        # Modifier le lieu
        location_field = modal.find_element(By.CSS_SELECTOR, 'span.editable-content[data-field="location"]')
        location_field.click()
        action = ActionChains(self.browser)
        action.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
        action.send_keys(new_content.location).perform()

        # Modifier la description
        description_field = modal.find_element(By.CSS_SELECTOR, 'div.editable-content[data-field="description"]')
        description_field.click()
        action = ActionChains(self.browser)
        action.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
        action.send_keys(new_content.description).perform()

        # Modifier l'URL
        experience_url_field = modal.find_element(By.CSS_SELECTOR, 'span.editable-content[data-field="url"]')
        experience_url_field.click()
        action = ActionChains(self.browser)
        action.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
        action.send_keys(new_content.url).perform()
        
        # Enregistrer et vérifier
        save_button = modal.find_element(By.CSS_SELECTOR, '.btn-primary')
        self.browser.execute_script("arguments[0].click();", save_button)
        
        # Vérifier que la modal commence à se fermer
        WebDriverWait(self.browser, 10).until(
            EC.invisibility_of_element_located((By.ID, 'experienceModal'))
        )
        
        # Vérifier côté serveur que la modification est enregistrée
        experience_obj = Experience.objects.get(id=self.experiences[0].id)
        self.assertEqual(experience_obj.dates, new_content.dates)
        self.assertEqual(experience_obj.company, new_content.company)
        self.assertEqual(experience_obj.position, new_content.position)
        self.assertEqual(experience_obj.location, new_content.location)
        self.assertEqual(experience_obj.description, new_content.description)
        self.assertEqual(experience_obj.url, new_content.url)
        
        # Vérifier que le tableau est mis à jour
        updated_row = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.XPATH, 
                f"//div[@id='profile-data']//table[@id='experience-table']//td[contains(., '{new_content.description}')]"))
        )
        self.assertTrue(updated_row.is_displayed())

    def test_modify_and_save_experience_skills(self):
        """
        Teste la modification et le sauvegarde des compétences d'une expérience via l'interface
        1. Ouvre la page data_display
        2. Double clique sur une expérience
        3. Ajoute une compétence
        4. Valide et vérifie l'affichage
        """

        new_skill = Skill(
            category='New special category',
            name='New special name'
        )

        # Sélectionner le profil
        profile_row = self.browser.find_element(By.XPATH, f"//table[contains(@id, 'profile-table')]//td[contains(text(), '{self.profile.identifiant}')]/..")
        self.browser.execute_script("arguments[0].click();", profile_row)
        
        # Attendre le chargement des données
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.ID, "experience-table"))
        )

        # Ajout de la nouvelle compétence au profil
        add_button = self.browser.find_element(By.ID, "addSkillSectionButton")
        self.browser.execute_script("arguments[0].scrollIntoView(true);", add_button)
        
        # Attendre que l'élément soit cliquable
        WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.ID, "addSkillSectionButton"))
        )
        
        # Cliquer via JavaScript pour éviter les problèmes d'interception
        self.browser.execute_script("arguments[0].click();", add_button)
        
        # Attendre que la modal soit visible
        modal = WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.ID, "skillModal"))
        )
        
        # Remplir le champ catégorie
        category_field = modal.find_element(By.CSS_SELECTOR, "[data-field='category']")
        category_field.send_keys(new_skill.category)

        # Remplir le champ nom
        name_field = modal.find_element(By.CSS_SELECTOR, "[data-field='name']")
        name_field.send_keys(new_skill.name)
        
        # Cliquer sur valider
        validate_button = modal.find_element(By.ID, "skillModalValidateButton")
        self.browser.execute_script("arguments[0].click();", validate_button)
        
        # Vérifier l'affichage dans le tableau
        WebDriverWait(self.browser, 20).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "#skill-table tbody"), 
                new_skill.category
            )
        )

        # Vérifier l'affichage dans le tableau
        WebDriverWait(self.browser, 20).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "#skill-table tbody"), 
                new_skill.name
            )
        )
        
        time.sleep(0.5)
        
        # Trouver la ligne du tableau Experience
        experience_row = self.browser.find_element(By.XPATH, f"//div[@id='profile-data']//table[contains(@id, 'experience-table')]//td[contains(text(), '{self.experiences[0].company}')]/..")
        
        # Effectuer un double clic
        action = ActionChains(self.browser)
        action.double_click(experience_row).perform()
        
        # Attendre que la popup soit visible
        WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.ID, 'experienceModal'))
        )
        
        # Vérifier que la popup est visible
        modal = self.browser.find_element(By.ID, 'experienceModal')
        self.assertTrue(modal.is_displayed())
        
        # Ouvrir la popup de création de compétence
        skills_field = modal.find_element(By.ID, "experienceSkillsButton")
        self.browser.execute_script("arguments[0].click();", skills_field)

        # Attendre que la modal soit visible
        skillModal = WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.ID, "skillModal"))
        )

        # Attendre que la liste déroulante soit présente
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-field='category']"))
        )
        
        # Sélection de la catégorie
        category_select = Select(skillModal.find_element(By.CSS_SELECTOR, "[data-field='category']"))
        category_select.select_by_visible_text(new_skill.category)
        
        # Attendre que les options de compétences soient chargées
        WebDriverWait(self.browser, 5).until(
            lambda d: len(Select(d.find_element(By.CSS_SELECTOR, "[data-field='name']")).options) > 1
        )
        
        # Sélection de la compétence
        skill_select = Select(skillModal.find_element(By.CSS_SELECTOR, "[data-field='name']"))
        skill_select.select_by_visible_text(new_skill.name)

        # Cliquer sur valider
        validate_button = skillModal.find_element(By.ID, "skillModalValidateButton")
        self.browser.execute_script("arguments[0].click();", validate_button)

        max_attempts = 50  # 50 * 0.2s = 10s max
        attempts = 0
        while attempts < max_attempts:
            attempts += 1
            try:
                new_skill = Skill.objects.get(category=new_skill.category, name=new_skill.name)
                if new_skill:
                    break
            except:
                time.sleep(0.2)
            if attempts >= max_attempts:
                self.fail("Timeout waiting for skill creation")

        # Vérifier l'affichage de la nouvelle compétence
        WebDriverWait(self.browser, 10).until(
            EC.text_to_be_present_in_element(
                (By.ID, "skills-name"), 
                new_skill.name
            )
        )

        skill_name = self.browser.find_element(By.ID, "skills-name")
        self.assertIn(new_skill.name, skill_name.text)

        # Cliquer sur valider
        validate_button = modal.find_element(By.ID, "experienceModalValidateButton")
        self.browser.execute_script("arguments[0].click();", validate_button)

        time.sleep(0.5)

        # Vérification en base de données
        experience = Experience.objects.get(id=self.experiences[0].id)
        self.assertIn(new_skill.name, [skill.name for skill in experience.skills.all()])

        ## Supprimer la compétence

        # Trouver la ligne du tableau Experience
        project_row = self.browser.find_element(By.XPATH, f"//div[@id='profile-data']//table[contains(@id, 'experience-table')]//td[contains(text(), '{self.experiences[0].description}')]/..")
        
        # Effectuer un double clic
        action = ActionChains(self.browser)
        action.double_click(project_row).perform()
        
        # Attendre que la popup soit visible
        WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.ID, 'experienceModal'))
        )
        
        # Trouver le champ compétence
        modal = self.browser.find_element(By.ID, "experienceModal")
        skills_field = modal.find_element(By.ID, "skills-name")
        skills_name = skills_field.find_elements(By.CLASS_NAME, "skill-badge")
        self.assertTrue(any(new_skill.name in skill_name.text for skill_name in skills_name), "La compétence n'est pas dans la liste")

        skill_to_delete = None
        for skill_name in skills_name:
            if skill_name.text == new_skill.name:
                skill_to_delete = skill_name
                break
        
        if skill_to_delete:
            # Cliquer sur supprimer
            delete_button = skill_to_delete.find_element(By.CLASS_NAME, "deleteSkill")
            self.browser.execute_script("arguments[0].click();", delete_button)

        # Après avoir cliqué sur le bouton delete, rafraîchir la référence aux éléments
        skills_field = modal.find_element(By.ID, "skills-name")
        skills_name = skills_field.find_elements(By.CLASS_NAME, "skill-badge")

        # Vérifier la suppression de la compétence
        self.assertFalse(any(new_skill.name in skill_name.text for skill_name in skills_name), "La compétence n'a pas été supprimée")

        # Cliquer sur valider
        validate_button = modal.find_element(By.ID, "experienceModalValidateButton")
        self.browser.execute_script("arguments[0].click();", validate_button)

        # Attendre le chargement des données
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#experience-table tbody"))
        )

        # Vérifier l'affichage dans le tableau
        WebDriverWait(self.browser, 20).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "#experience-table tbody"), 
                str(self.experiences[0].skills.all().count())
            )
        )

        time.sleep(0.5)

        # Vérification en base de données
        experience = Experience.objects.get(id=self.experiences[0].id)
        self.assertNotIn(new_skill.name, [skill.name for skill in experience.skills.all()])

        # Trouver la ligne du tableau Experience
        experience_row = self.browser.find_element(By.XPATH, f"//div[@id='profile-data']//table[contains(@id, 'experience-table')]//td[contains(text(), '{self.experiences[0].description}')]/..")
        
        # Effectuer un double clic
        action = ActionChains(self.browser)
        action.double_click(experience_row).perform()
        
        # Attendre que la popup soit visible
        WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.ID, 'experienceModal'))
        )

        # Trouver le champ compétence
        modal = self.browser.find_element(By.ID, 'experienceModal')
        skills_field = modal.find_element(By.ID, "skills-name")
        skills_name = skills_field.find_elements(By.CLASS_NAME, "skill-badge")
        self.assertFalse(any(new_skill.name in skill_name.text for skill_name in skills_name), "La compétence est toujours dans la liste")

    def test_modify_and_save_project(self):
        """Teste la modification et la sauvegarde d'un élément Project"""

        new_content = Project(
            profile=self.profile,
            title='New Project',
            description='New Project Description',
            image_url='/static/portfolio-example.png',
            url='https://newurl.com'
        )

        # Sélectionner le profil
        profile_row = self.browser.find_element(By.XPATH, f"//table[contains(@id, 'profile-table')]//td[contains(text(), '{self.profile.identifiant}')]/..")
        self.browser.execute_script("arguments[0].click();", profile_row)
        
        # Attendre le chargement des données
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.ID, "projects-table"))
        )
        
        # Trouver la ligne du tableau Projects
        project_row = self.browser.find_element(By.XPATH, f"//div[@id='profile-data']//table[contains(@id, 'projects-table')]//td[contains(text(), '{self.projects[0].title}')]/..")
        
        # Effectuer un double clic
        action = ActionChains(self.browser)
        action.double_click(project_row).perform()
        
        # Attendre que la popup soit visible
        WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.ID, 'projectModal'))
        )
        
        # Vérifier que la popup est visible
        modal = self.browser.find_element(By.ID, 'projectModal')
        self.assertTrue(modal.is_displayed())
        
        # Modifier le titre
        title_field = modal.find_element(By.CSS_SELECTOR, 'span.editable-content[data-field="title"]')
        title_field.click()
        action = ActionChains(self.browser)
        action.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
        action.send_keys(new_content.title).perform()

        # Modifier la description
        description_field = modal.find_element(By.CSS_SELECTOR, 'div.editable-content[data-field="description"]')
        description_field.click()
        action = ActionChains(self.browser)
        action.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
        action.send_keys(new_content.description).perform()

        # Modifier l'image
        image_field = modal.find_element(By.CSS_SELECTOR, 'span.editable-content[data-field="image_url"]')
        image_field.click()
        action = ActionChains(self.browser)
        action.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
        action.send_keys(new_content.image_url).perform()
        
        # Modifier l'URL
        url_field = modal.find_element(By.CSS_SELECTOR, 'span.editable-content[data-field="url"]')
        url_field.click()
        action = ActionChains(self.browser)
        action.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
        action.send_keys(new_content.url).perform()
        
        # Enregistrer et vérifier
        save_button = modal.find_element(By.CSS_SELECTOR, '.btn-primary')
        self.browser.execute_script("arguments[0].click();", save_button)
        
        # Vérifier que la modal commence à se fermer
        WebDriverWait(self.browser, 10).until(
            EC.invisibility_of_element_located((By.ID, 'projectModal'))
        )
        
        # Vérifier côté serveur que la modification est enregistrée
        project_obj = Project.objects.get(id=self.projects[0].id)
        self.assertEqual(project_obj.title, new_content.title)
        self.assertEqual(project_obj.description, new_content.description)
        self.assertEqual(project_obj.image_url, new_content.image_url)
        self.assertEqual(project_obj.url, new_content.url)
        
        # Vérifier que le tableau est mis à jour
        updated_row = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.XPATH, 
                f"//div[@id='profile-data']//table[@id='projects-table']//td[contains(., '{new_content.title}')]"))
        )
        self.assertTrue(updated_row.is_displayed())

    def test_modify_and_save_project_skills(self):
        """
        Teste la modification et le sauvegarde des compétences d'un projet via l'interface
        1. Ouvre la page data_display
        2. Double clique sur un projet
        3. Ajoute une compétence
        4. Valide et vérifie l'affichage
        """

        new_skill = Skill(
            category='New special category',
            name='New special name'
        )

        # Sélectionner le profil
        profile_row = self.browser.find_element(By.XPATH, f"//table[contains(@id, 'profile-table')]//td[contains(text(), '{self.profile.identifiant}')]/..")
        self.browser.execute_script("arguments[0].click();", profile_row)
        
        # Attendre le chargement des données
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.ID, "projects-table"))
        )

        # Ajout de la nouvelle compétence au profil
        add_button = self.browser.find_element(By.ID, "addSkillSectionButton")
        self.browser.execute_script("arguments[0].scrollIntoView(true);", add_button)
        
        # Attendre que l'élément soit cliquable
        WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.ID, "addSkillSectionButton"))
        )
        
        # Cliquer via JavaScript pour éviter les problèmes d'interception
        self.browser.execute_script("arguments[0].click();", add_button)
        
        # Attendre que la modal soit visible
        modal = WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.ID, "skillModal"))
        )
        
        # Remplir le champ catégorie
        category_field = modal.find_element(By.CSS_SELECTOR, "[data-field='category']")
        category_field.send_keys(new_skill.category)

        # Remplir le champ nom
        name_field = modal.find_element(By.CSS_SELECTOR, "[data-field='name']")
        name_field.send_keys(new_skill.name)
        
        # Cliquer sur valider
        validate_button = modal.find_element(By.ID, "skillModalValidateButton")
        self.browser.execute_script("arguments[0].click();", validate_button)
        
        # Vérifier l'affichage dans le tableau
        WebDriverWait(self.browser, 20).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "#skill-table tbody"), 
                new_skill.category
            )
        )

        # Vérifier l'affichage dans le tableau
        WebDriverWait(self.browser, 20).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "#skill-table tbody"), 
                new_skill.name
            )
        )
        
        time.sleep(0.5)
        
        # Trouver la ligne du tableau Projects
        project_row = self.browser.find_element(By.XPATH, f"//div[@id='profile-data']//table[contains(@id, 'projects-table')]//td[contains(text(), '{self.projects[0].title}')]/..")
        
        # Effectuer un double clic
        action = ActionChains(self.browser)
        action.double_click(project_row).perform()
        
        # Attendre que la popup soit visible
        WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.ID, 'projectModal'))
        )
        
        # Vérifier que la popup est visible
        modal = self.browser.find_element(By.ID, 'projectModal')
        self.assertTrue(modal.is_displayed())
        
        # Ouvrir la popup de création de compétence
        skills_field = modal.find_element(By.ID, "projectSkillsButton")
        self.browser.execute_script("arguments[0].click();", skills_field)

        # Attendre que la modal soit visible
        skillModal = WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.ID, "skillModal"))
        )

        # Sélection de la catégorie
        category_select = Select(skillModal.find_element(By.CSS_SELECTOR, "[data-field='category']"))
        category_select.select_by_visible_text(new_skill.category)
        
        # Attendre que les options de compétences soient chargées
        WebDriverWait(self.browser, 5).until(
            lambda d: len(Select(d.find_element(By.CSS_SELECTOR, "[data-field='name']")).options) > 1
        )
        
        # Sélection de la compétence
        skill_select = Select(skillModal.find_element(By.CSS_SELECTOR, "[data-field='name']"))
        skill_select.select_by_visible_text(new_skill.name)

        # Cliquer sur valider
        validate_button = skillModal.find_element(By.ID, "skillModalValidateButton")
        self.browser.execute_script("arguments[0].click();", validate_button)

        max_attempts = 50  # 50 * 0.2s = 10s max
        attempts = 0
        while attempts < max_attempts:
            attempts += 1
            try:
                new_skill = Skill.objects.get(category=new_skill.category, name=new_skill.name)
                if new_skill:
                    break
            except:
                time.sleep(0.2)
            if attempts >= max_attempts:
                self.fail("Timeout waiting for skill creation")

        # Vérifier l'affichage de la nouvelle compétence
        WebDriverWait(self.browser, 10).until(
            EC.text_to_be_present_in_element(
                (By.ID, "skills-name"), 
                new_skill.name
            )
        )

        skill_name = self.browser.find_element(By.ID, "skills-name")
        self.assertIn(new_skill.name, skill_name.text)

        # Cliquer sur valider
        validate_button = modal.find_element(By.ID, "projectModalValidateButton")
        self.browser.execute_script("arguments[0].click();", validate_button)

        time.sleep(0.5)

        # Vérification en base de données
        project = Project.objects.get(id=self.projects[0].id)
        self.assertIn(new_skill.name, [skill.name for skill in project.skills.all()])

        ## Supprimer la compétence

        # Trouver la ligne du tableau Projects
        project_row = self.browser.find_element(By.XPATH, f"//div[@id='profile-data']//table[contains(@id, 'projects-table')]//td[contains(text(), '{self.projects[0].title}')]/..")
        
        # Effectuer un double clic
        action = ActionChains(self.browser)
        action.double_click(project_row).perform()
        
        # Attendre que la popup soit visible
        WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.ID, 'projectModal'))
        )

        # Trouver le champ compétence
        modal = self.browser.find_element(By.ID, 'projectModal')
        skills_field = modal.find_element(By.ID, "skills-name")
        skills_name = skills_field.find_elements(By.CLASS_NAME, "skill-badge")
        self.assertTrue(any(new_skill.name in skill_name.text for skill_name in skills_name), "La compétence n'est pas dans la liste")

        skill_to_delete = None
        for skill_name in skills_name:
            if skill_name.text == new_skill.name:
                skill_to_delete = skill_name
                break
        
        if skill_to_delete:
            # Cliquer sur supprimer
            delete_button = skill_to_delete.find_element(By.CLASS_NAME, "deleteSkill")
            self.browser.execute_script("arguments[0].click();", delete_button)

        # Après avoir cliqué sur le bouton delete, rafraîchir la référence aux éléments
        skills_field = self.browser.find_element(By.ID, "skills-name")
        skills_name = skills_field.find_elements(By.CLASS_NAME, "skill-badge")

        # Vérifier la suppression de la compétence
        self.assertFalse(any(new_skill.name in skill_name.text for skill_name in skills_name), "La compétence n'a pas été supprimée")

        # Cliquer sur valider
        validate_button = modal.find_element(By.ID, "projectModalValidateButton")
        self.browser.execute_script("arguments[0].click();", validate_button)

        time.sleep(0.5)

        # Vérification en base de données
        project = Project.objects.get(id=self.projects[0].id)
        self.assertNotIn(new_skill.name, [skill.name for skill in project.skills.all()])

        # Trouver la ligne du tableau Projects
        project_row = self.browser.find_element(By.XPATH, f"//div[@id='profile-data']//table[contains(@id, 'projects-table')]//td[contains(text(), '{self.projects[0].title}')]/..")
        
        # Effectuer un double clic
        action = ActionChains(self.browser)
        action.double_click(project_row).perform()
        
        # Attendre que la popup soit visible
        WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.ID, 'projectModal'))
        )

        # Trouver le champ compétence
        modal = self.browser.find_element(By.ID, 'projectModal')
        skills_field = modal.find_element(By.ID, "skills-name")
        skills_name = skills_field.find_elements(By.CLASS_NAME, "skill-badge")
        self.assertFalse(any(new_skill.name in skill_name.text for skill_name in skills_name), "La compétence est toujours dans la liste")

class AddElementTest(BaseTest):

    def setUp(self):
        super().setUp()
        self.setUpData()

    def test_add_profile(self):
        """
        Teste l'ajout d'un profil via l'interface
        1. Ouvre la page data_display
        2. Clique sur 'Ajouter un profil'
        3. Remplit les champs 'Identifiant' et 'Nom'
        4. Valide et vérifie l'affichage
        """

        # Cliquer sur le bouton d'ajout
        add_button = self.browser.find_element(By.ID, "addProfileButton")
        
        # Cliquer via JavaScript pour éviter les problèmes d'interception
        self.browser.execute_script("arguments[0].click();", add_button)
        
        # Attendre que la modal soit visible
        modal = WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.ID, "profileModal"))
        )
        
        # Remplir le champ identifiant
        identifiant_field = modal.find_element(By.CSS_SELECTOR, "[data-field='identifiant']")
        identifiant_field.send_keys("Nouveau_profil")
        
        # Remplir le champ nom
        name_field = modal.find_element(By.CSS_SELECTOR, "[data-field='name']")
        name_field.send_keys("Nouveau_nom")

        # Remplir le champ titre
        title_field = modal.find_element(By.CSS_SELECTOR, "[data-field='title']")
        title_field.send_keys("Nouveau_titre")
        
        # Cliquer sur valider
        validate_button = modal.find_element(By.ID, "profileModalValidateButton")
        self.browser.execute_script("arguments[0].click();", validate_button)
        
        # Vérifier l'affichage dans le tableau
        WebDriverWait(self.browser, 10).until(
            lambda driver: any("Nouveau_profil" in el.text 
                           for el in driver.find_elements(By.CSS_SELECTOR, "#profile-table tbody"))
        )
        
        # Vérification finale
        rows = self.browser.find_elements(By.CSS_SELECTOR, "#profile-table tbody tr")
        self.assertTrue(any("Nouveau_profil" in row.text for row in rows))
        self.assertTrue(any("Nouveau_nom" in row.text for row in rows))
        self.assertTrue(any("Nouveau_titre" in row.text for row in rows))

    def test_add_profile_in_empty_table(self):
        """
        Teste l'ajout d'un profil via l'interface
        1. Ouvre la page data_display
        2. Clique sur 'Ajouter un profil'
        3. Remplit les champs 'Identifiant' et 'Nom'
        4. Valide et vérifie l'affichage
        """

        Profile.objects.all().delete()
        self.browser.refresh()

        # Cliquer sur le bouton d'ajout
        add_button = self.browser.find_element(By.ID, "addProfileButton")
        
        # Cliquer via JavaScript pour éviter les problèmes d'interception
        self.browser.execute_script("arguments[0].click();", add_button)
        
        # Attendre que la modal soit visible
        modal = WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.ID, "profileModal"))
        )
        
        # Remplir le champ identifiant
        identifiant_field = modal.find_element(By.CSS_SELECTOR, "[data-field='identifiant']")
        identifiant_field.send_keys("Nouveau_profil")
        
        # Remplir le champ nom
        name_field = modal.find_element(By.CSS_SELECTOR, "[data-field='name']")
        name_field.send_keys("Nouveau_nom")
        
        # Remplir le champ titre
        title_field = modal.find_element(By.CSS_SELECTOR, "[data-field='title']")
        title_field.send_keys("Nouveau_titre")
        
        # Cliquer sur valider
        validate_button = modal.find_element(By.ID, "profileModalValidateButton")
        self.browser.execute_script("arguments[0].click();", validate_button)
        
        # Vérifier l'affichage dans le tableau
        WebDriverWait(self.browser, 10).until(
            lambda driver: any("Nouveau_profil" in el.text 
                           for el in driver.find_elements(By.CSS_SELECTOR, "#profile-table tbody"))
        )
        
        # Vérification finale
        rows = self.browser.find_elements(By.CSS_SELECTOR, "#profile-table tbody tr")
        self.assertTrue(any("Nouveau_profil" in row.text for row in rows))
        self.assertTrue(any("Nouveau_nom" in row.text for row in rows))
        self.assertTrue(any("Nouveau_titre" in row.text for row in rows))

    def test_add_new_skill(self):
        """
        Teste l'ajout d'une nouvelle compétence via l'interface
        1. Ouvre la page data_display
        2. Clique sur 'Ajouter une compétence'
        3. Remplit les champs 'Catégorie' et 'Intitulé'
        4. Valide et vérifie l'affichage
        """

        # Créer un nouveau contenu pour l'expérience
        new_skill = Skill.objects.create(
            category='New Category',
            name='New Skill'
        )
        
        # Sélectionner le profil
        profile_row = self.browser.find_element(By.XPATH, f"//table[contains(@id, 'profile-table')]//td[contains(text(), '{self.profile.identifiant}')]/..")
        self.browser.execute_script("arguments[0].click();", profile_row)
        
        # Attendre le chargement des données
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.ID, "skill-table"))
        )
        
        # Scroll vers l'élément
        add_button = self.browser.find_element(By.ID, "addSkillSectionButton")
        self.browser.execute_script("arguments[0].scrollIntoView(true);", add_button)
        
        # Attendre que l'élément soit cliquable
        WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.ID, "addSkillSectionButton"))
        )
        
        # Cliquer via JavaScript pour éviter les problèmes d'interception
        self.browser.execute_script("arguments[0].click();", add_button)
        
        # Attendre que la modal soit visible
        modal = WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.ID, "skillModal"))
        )
        
        # Remplir le champ catégorie
        category_field = modal.find_element(By.CSS_SELECTOR, "[data-field='category']")
        category_field.send_keys(new_skill.category)

        # Remplir le champ nom
        name_field = modal.find_element(By.CSS_SELECTOR, "[data-field='name']")
        name_field.send_keys(new_skill.name)
        
        # Cliquer sur valider
        validate_button = modal.find_element(By.ID, "skillModalValidateButton")
        self.browser.execute_script("arguments[0].click();", validate_button)
        
        # Vérifier l'affichage dans le tableau
        WebDriverWait(self.browser, 20).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "#skill-table tbody"), 
                new_skill.category
            )
        )

        # Vérifier l'affichage dans le tableau
        WebDriverWait(self.browser, 20).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "#skill-table tbody"), 
                new_skill.name
            )
        )
        
        time.sleep(0.5)

        # Vérification finale
        rows = self.browser.find_elements(By.CSS_SELECTOR, "#skill-table tbody tr")
        new_row = None
        for row in rows:
            if row.find_elements(By.CSS_SELECTOR, "td")[0].text == new_skill.category and \
               row.find_elements(By.CSS_SELECTOR, "td")[1].text == new_skill.name:
                new_row = row
                break
        if new_row:
            self.assertEqual(new_skill.category, new_row.find_elements(By.CSS_SELECTOR, "td")[0].text)
            self.assertEqual(new_skill.name, new_row.find_elements(By.CSS_SELECTOR, "td")[1].text)
        else:
            self.fail("New row not found")

    def test_add_existing_skill(self):
        """
        Teste l'ajout d'une compétence existante via l'interface
        1. Ouvre la page data_display
        2. Clique sur 'Ajouter une compétence'
        3. Remplit les champs 'Catégorie' et 'Intitulé'
        4. Valide et vérifie l'affichage
        """

        existing_skill = Skill.objects.get(pk=4)
        
        # Sélectionner le profil
        profile_row = self.browser.find_element(By.XPATH, f"//table[contains(@id, 'profile-table')]//td[contains(text(), '{self.profile.identifiant}')]/..")
        self.browser.execute_script("arguments[0].click();", profile_row)
        
        # Attendre le chargement des données
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.ID, "skill-table"))
        )
        
        # Scroll vers l'élément
        add_button = self.browser.find_element(By.ID, "addSkillSectionButton")
        self.browser.execute_script("arguments[0].scrollIntoView(true);", add_button)
        
        # Attendre que l'élément soit cliquable
        WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.ID, "addSkillSectionButton"))
        )
        
        # Cliquer via JavaScript pour éviter les problèmes d'interception
        self.browser.execute_script("arguments[0].click();", add_button)
        
        # Attendre que la modal soit visible
        modal = WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.ID, "skillModal"))
        )
        
        # Remplir le champ catégorie
        category_field = modal.find_element(By.CSS_SELECTOR, "[data-field='category']")
        category_field.send_keys(existing_skill.category)

        # Remplir le champ nom
        name_field = modal.find_element(By.CSS_SELECTOR, "[data-field='name']")
        name_field.send_keys(existing_skill.name)
        
        # Cliquer sur valider
        validate_button = modal.find_element(By.ID, "skillModalValidateButton")
        self.browser.execute_script("arguments[0].click();", validate_button)

        time.sleep(0.5)

        # Vérifier l'existence en base de données avec pk = 4
        self.assertEqual(Skill.objects.filter(category=existing_skill.category, name=existing_skill.name).count(), 1)
        self.assertEqual(Skill.objects.get(category=existing_skill.category, name=existing_skill.name).pk, 4)

        # Vérifier l'affichage dans le tableau
        WebDriverWait(self.browser, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#skill-table tbody"))
        )

        # Vérifier l'affichage dans le tableau
        WebDriverWait(self.browser, 20).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "#skill-table tbody"), 
                existing_skill.name
            )
        )
        
        time.sleep(0.5)

        # Vérification finale
        rows = self.browser.find_elements(By.CSS_SELECTOR, "#skill-table tbody tr")
        new_row = None
        for row in rows:
            if row.find_elements(By.CSS_SELECTOR, "td")[0].text == existing_skill.category and \
               row.find_elements(By.CSS_SELECTOR, "td")[1].text == existing_skill.name:
                new_row = row
                break
        if new_row:
            self.assertEqual(existing_skill.category, new_row.find_elements(By.CSS_SELECTOR, "td")[0].text)
            self.assertEqual(existing_skill.name, new_row.find_elements(By.CSS_SELECTOR, "td")[1].text)
        else:
            self.fail("New row not found")

    def test_add_about_section(self):
        """
        Teste l'ajout d'une section À propos via l'interface
        1. Ouvre la page data_display
        2. Clique sur 'Ajouter une section'
        3. Remplit le champ 'Contenu'
        4. Valide et vérifie l'affichage
        """
        
        # Sélectionner le profil
        profile_row = self.browser.find_element(By.XPATH, f"//table[contains(@id, 'profile-table')]//td[contains(text(), '{self.profile.identifiant}')]/..")
        self.browser.execute_script("arguments[0].click();", profile_row)
        
        # Attendre le chargement des données
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.ID, "about-table"))
        )
        
        # Cliquer sur le bouton d'ajout
        add_button = self.browser.find_element(By.ID, "addAboutSectionButton")
        
        # Cliquer via JavaScript pour éviter les problèmes d'interception
        self.browser.execute_script("arguments[0].click();", add_button)
        
        # Attendre que la modal soit visible
        modal = WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.ID, "aboutModal"))
        )
        
        # Remplir le champ contenu
        content_field = modal.find_element(By.CSS_SELECTOR, "[data-field='content']")
        content_field.send_keys("Nouveau contenu de test")
        
        # Cliquer sur valider
        validate_button = modal.find_element(By.ID, "aboutModalValidateButton")
        self.browser.execute_script("arguments[0].click();", validate_button)
        
        # Vérifier l'affichage dans le tableau
        WebDriverWait(self.browser, 20).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "#about-table tbody"), 
                "Nouveau contenu de test"
            )
        )

        time.sleep(0.2)
        
        # Vérification finale
        rows = self.browser.find_elements(By.CSS_SELECTOR, "#about-table tbody tr")
        self.assertTrue(any("Nouveau contenu de test" in row.text for row in rows))

    def test_add_experience_section(self):
        """
        Teste l'ajout d'une section Expérience via l'interface
        1. Ouvre la page data_display
        2. Clique sur 'Ajouter une section'
        3. Remplit le champ 'Contenu'
        4. Valide et vérifie l'affichage
        """

        # Créer un nouveau contenu pour l'expérience
        new_skill = Skill.objects.create(
            category='New Category',
            name='New Skill'
        )
        new_content = Experience(
            profile=self.profile,
            dates="2024-2025",
            company="Nouvelle entreprise",
            position="Nouveau poste",
            location="Nouveau lieu",
            description="Nouvelle description",
            url="https://nouvelleurl.com",
        )
        
        # Sélectionner le profil
        profile_row = self.browser.find_element(By.XPATH, f"//table[contains(@id, 'profile-table')]//td[contains(text(), '{self.profile.identifiant}')]/..")
        self.browser.execute_script("arguments[0].click();", profile_row)
        
        # Attendre le chargement des données
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.ID, "experience-table"))
        )

        # Ajout de la nouvelle compétence au profil
        add_button = self.browser.find_element(By.ID, "addSkillSectionButton")
        self.browser.execute_script("arguments[0].scrollIntoView(true);", add_button)
        
        # Attendre que l'élément soit cliquable
        WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.ID, "addSkillSectionButton"))
        )
        
        # Cliquer via JavaScript pour éviter les problèmes d'interception
        self.browser.execute_script("arguments[0].click();", add_button)
        
        # Attendre que la modal soit visible
        modal = WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.ID, "skillModal"))
        )
        
        # Remplir le champ catégorie
        category_field = modal.find_element(By.CSS_SELECTOR, "[data-field='category']")
        category_field.send_keys(new_skill.category)

        # Remplir le champ nom
        name_field = modal.find_element(By.CSS_SELECTOR, "[data-field='name']")
        name_field.send_keys(new_skill.name)
        
        # Cliquer sur valider
        validate_button = modal.find_element(By.ID, "skillModalValidateButton")
        self.browser.execute_script("arguments[0].click();", validate_button)
        
        # Vérifier l'affichage dans le tableau
        WebDriverWait(self.browser, 20).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "#skill-table tbody"), 
                new_skill.category
            )
        )

        # Vérifier l'affichage dans le tableau
        WebDriverWait(self.browser, 20).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "#skill-table tbody"), 
                new_skill.name
            )
        )
        
        time.sleep(0.5)
        
        # Scroll vers l'élément
        add_button = self.browser.find_element(By.ID, "addExperienceSectionButton")
        self.browser.execute_script("arguments[0].scrollIntoView(true);", add_button)
        
        # Attendre que l'élément soit cliquable
        WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.ID, "addExperienceSectionButton"))
        )
        
        # Cliquer via JavaScript pour éviter les problèmes d'interception
        self.browser.execute_script("arguments[0].click();", add_button)
        
        # Attendre que la modal soit visible
        modal = WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.ID, "experienceModal"))
        )
        
        # Remplir le champ description
        description_field = modal.find_element(By.CSS_SELECTOR, "[data-field='description']")
        description_field.send_keys(new_content.description)

        # Remplir le champ dates
        dates_field = modal.find_element(By.CSS_SELECTOR, "[data-field='dates']")
        dates_field.send_keys(new_content.dates)

        # Remplir le champ company
        company_field = modal.find_element(By.CSS_SELECTOR, "[data-field='company']")
        company_field.send_keys(new_content.company)

        # Remplir le champ position
        position_field = modal.find_element(By.CSS_SELECTOR, "[data-field='position']")
        position_field.send_keys(new_content.position)

        # Remplir le champ location
        location_field = modal.find_element(By.CSS_SELECTOR, "[data-field='location']")
        location_field.send_keys(new_content.location)

        # Remplir le champ url
        url_field = modal.find_element(By.CSS_SELECTOR, "[data-field='url']")
        url_field.send_keys(new_content.url)

        # Ouvrir la popup de création de compétence
        skills_field = modal.find_element(By.ID, "experienceSkillsButton")
        self.browser.execute_script("arguments[0].click();", skills_field)

        # Attendre que la modal soit visible
        skillModal = WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.ID, "skillModal"))
        )

        # Sélection de la catégorie
        category_select = Select(skillModal.find_element(By.CSS_SELECTOR, "[data-field='category']"))
        category_select.select_by_visible_text(new_skill.category)
        
        # Attendre que les options de compétences soient chargées
        WebDriverWait(self.browser, 5).until(
            lambda d: len(Select(d.find_element(By.CSS_SELECTOR, "[data-field='name']")).options) > 1
        )
        
        # Sélection de la compétence
        skill_select = Select(skillModal.find_element(By.CSS_SELECTOR, "[data-field='name']"))
        skill_select.select_by_visible_text(new_skill.name)

        # Cliquer sur valider
        validate_button = skillModal.find_element(By.ID, "skillModalValidateButton")
        self.browser.execute_script("arguments[0].click();", validate_button)

        # Vérifier l'affichage de la nouvelle compétence
        WebDriverWait(self.browser, 20).until(
            EC.presence_of_element_located((By.ID, "skills-name"))
        )

        # Vérifier l'affichage de la nouvelle compétence
        WebDriverWait(self.browser, 20).until(
            EC.text_to_be_present_in_element(
                (By.ID, "skills-name"), 
                str(new_skill.name)
            )
        )
        
        # Cliquer sur valider
        validate_button = modal.find_element(By.ID, "experienceModalValidateButton")
        self.browser.execute_script("arguments[0].click();", validate_button)
        
        # Vérifier l'affichage dans le tableau
        WebDriverWait(self.browser, 20).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "#experience-table tbody"), 
                new_content.description
            )
        )

        # Vérifier l'affichage dans le tableau
        WebDriverWait(self.browser, 20).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "#experience-table tbody"), 
                new_content.description
            )
        )
        
        time.sleep(0.5)

        # Vérification finale
        rows = self.browser.find_elements(By.CSS_SELECTOR, "#experience-table tbody tr")
        new_row = None
        for row in rows:
            if row.find_elements(By.CSS_SELECTOR, "td")[4].text == new_content.description:
                new_row = row
                break
        if new_row:
            self.assertEqual(new_content.dates, new_row.find_elements(By.CSS_SELECTOR, "td")[0].text)
            self.assertEqual(new_content.position, new_row.find_elements(By.CSS_SELECTOR, "td")[1].text)
            self.assertEqual(new_content.company, new_row.find_elements(By.CSS_SELECTOR, "td")[2].text)
            self.assertEqual(new_content.location, new_row.find_elements(By.CSS_SELECTOR, "td")[3].text)
            self.assertEqual(new_content.description, new_row.find_elements(By.CSS_SELECTOR, "td")[4].text)
            self.assertEqual(new_content.url, new_row.find_elements(By.CSS_SELECTOR, "td")[5].text)
        else:
            self.fail("New row not found")

        experience = Experience.objects.get(profile=new_content.profile,
            dates=new_content.dates,
            position=new_content.position,
            company=new_content.company,
            location=new_content.location,
            description=new_content.description,
            url=new_content.url)
        self.assertEqual(experience.skills.all().count(), 1)

        # Vérifier que la compétence est liée au profil
        profil = Profile.objects.get(identifiant=self.profile.identifiant)
        self.assertIn(new_skill, profil.skills.all())

    def test_add_project_section(self):
        """
        Teste l'ajout d'une section Projets via l'interface
        1. Ouvre la page data_display
        2. Clique sur 'Ajouter une section'
        3. Remplit le champ 'Contenu'
        4. Valide et vérifie l'affichage
        """

        new_skill = Skill.objects.create(
            category='New Category',
            name='New Skill'
        )
        new_content = Project(
            profile=self.profile,
            title='New Project',
            description='New Project Description',
            image_url='/static/portfolio-example.png',
            url='https://newurl.com'
        )
        
        # Sélectionner le profil
        profile_row = self.browser.find_element(By.XPATH, f"//table[contains(@id, 'profile-table')]//td[contains(text(), '{self.profile.identifiant}')]/..")
        self.browser.execute_script("arguments[0].click();", profile_row)

        # Attendre le chargement des données
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.ID, "projects-table"))
        )

        # Ajout de la nouvelle compétence au profil
        add_button = self.browser.find_element(By.ID, "addSkillSectionButton")
        self.browser.execute_script("arguments[0].scrollIntoView(true);", add_button)
        
        # Attendre que l'élément soit cliquable
        WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.ID, "addSkillSectionButton"))
        )
        
        # Cliquer via JavaScript pour éviter les problèmes d'interception
        self.browser.execute_script("arguments[0].click();", add_button)
        
        # Attendre que la modal soit visible
        modal = WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.ID, "skillModal"))
        )
        
        # Remplir le champ catégorie
        category_field = modal.find_element(By.CSS_SELECTOR, "[data-field='category']")
        category_field.send_keys(new_skill.category)

        # Remplir le champ nom
        name_field = modal.find_element(By.CSS_SELECTOR, "[data-field='name']")
        name_field.send_keys(new_skill.name)
        
        # Cliquer sur valider
        validate_button = modal.find_element(By.ID, "skillModalValidateButton")
        self.browser.execute_script("arguments[0].click();", validate_button)
        
        # Vérifier l'affichage dans le tableau
        WebDriverWait(self.browser, 20).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "#skill-table tbody"), 
                new_skill.category
            )
        )

        # Vérifier l'affichage dans le tableau
        WebDriverWait(self.browser, 20).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "#skill-table tbody"), 
                new_skill.name
            )
        )
        
        time.sleep(0.5)
        
        # Cliquer sur le bouton d'ajout
        add_button = self.browser.find_element(By.ID, "addProjectSectionButton")
        
        # Scroll vers l'élément
        self.browser.execute_script("arguments[0].scrollIntoView(true);", add_button)
        
        # Attendre que l'élément soit cliquable
        WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.ID, "addProjectSectionButton"))
        )
        
        # Cliquer via JavaScript pour éviter les problèmes d'interception
        self.browser.execute_script("arguments[0].click();", add_button)
        
        # Attendre que la modal soit visible
        modal = WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.ID, "projectModal"))
        )

        # Remplir le champ titre
        title_field = modal.find_element(By.CSS_SELECTOR, "[data-field='title']")
        title_field.send_keys(new_content.title)
        
        # Remplir le champ description
        description_field = modal.find_element(By.CSS_SELECTOR, "[data-field='description']")
        description_field.send_keys(new_content.description)
        
        # Remplir le champ image_url
        image_url_field = modal.find_element(By.CSS_SELECTOR, "[data-field='image_url']")
        image_url_field.send_keys(new_content.image_url)
        
        # Remplir le champ url
        url_field = modal.find_element(By.CSS_SELECTOR, "[data-field='url']")
        url_field.send_keys(new_content.url)

        # Ouvrir la popup de création de compétence
        skills_field = modal.find_element(By.ID, "projectSkillsButton")
        self.browser.execute_script("arguments[0].click();", skills_field)

        # Attendre que la modal soit visible
        skillModal = WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.ID, "skillModal"))
        )

        # Sélection de la catégorie
        category_select = Select(skillModal.find_element(By.CSS_SELECTOR, "[data-field='category']"))
        category_select.select_by_visible_text(new_skill.category)
        
        # Attendre que les options de compétences soient chargées
        WebDriverWait(self.browser, 5).until(
            lambda d: len(Select(d.find_element(By.CSS_SELECTOR, "[data-field='name']")).options) > 1
        )
        
        # Sélection de la compétence
        skill_select = Select(skillModal.find_element(By.CSS_SELECTOR, "[data-field='name']"))
        skill_select.select_by_visible_text(new_skill.name)

        # Cliquer sur valider
        validate_button = skillModal.find_element(By.ID, "skillModalValidateButton")
        self.browser.execute_script("arguments[0].click();", validate_button)

        # Vérifier l'affichage de la nouvelle compétence
        WebDriverWait(self.browser, 20).until(
            EC.presence_of_element_located((By.ID, "skills-name"))
        )
        
        # Vérifier l'affichage de la nouvelle compétence
        WebDriverWait(self.browser, 20).until(
            EC.text_to_be_present_in_element(
                (By.ID, "skills-name"), 
                str(new_skill.name)
            )
        )

        # Cliquer sur valider
        validate_button = modal.find_element(By.ID, "projectModalValidateButton")
        self.browser.execute_script("arguments[0].click();", validate_button)

        # Attendre le chargement des données
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#projects-table tbody"))
        )

        # Vérifier l'affichage dans le tableau
        WebDriverWait(self.browser, 20).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "#projects-table tbody"), 
                new_content.title
            )
        )
        
        time.sleep(0.5)
        
        # Vérification finale
        rows = self.browser.find_elements(By.CSS_SELECTOR, "#projects-table tbody tr")
        new_row = None
        for row in rows:
            if row.find_elements(By.CSS_SELECTOR, "td")[0].text == new_content.title:
                new_row = row
                break
        if new_row:
            self.assertEqual(new_content.description, new_row.find_elements(By.CSS_SELECTOR, "td")[1].text)
            self.assertEqual(new_content.image_url, new_row.find_elements(By.CSS_SELECTOR, "td")[2].text)
            self.assertEqual(new_content.url, new_row.find_elements(By.CSS_SELECTOR, "td")[3].text)
        else:
            self.fail("New row not found")

        project = Project.objects.get(profile=new_content.profile,
            title=new_content.title,
            description=new_content.description,
            image_url=new_content.image_url,
            url=new_content.url)
        self.assertEqual(project.skills.all().count(), 1)
        
        # Vérifier que la compétence est liée au profil
        profil = Profile.objects.get(identifiant=self.profile.identifiant)
        self.assertIn(new_skill, profil.skills.all())

class DeleteElementTest(BaseTest):

    def setUp(self):
        super().setUp()
        self.setUpData()

    def test_delete_profile_and_cancel(self):
        """Vérifie que le clic sur supprimer affiche la modal de confirmation et le bouton d'annulation fonctionne"""

        # Cliquer sur le bouton de suppression du profil de test
        delete_button = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//table[contains(@id, 'profile-table')]//td[contains(text(), '{self.profile.identifiant}')]/..//button[contains(@class, 'delete-profile')]"))
        )
        self.browser.execute_script("arguments[0].click();", delete_button)

        # Vérifier l'affichage de la modal
        WebDriverWait(self.browser, 5).until(
            EC.visibility_of_element_located((By.ID, "confirmDeleteModal")),
            message="La modal de confirmation n'est pas apparue après le clic"
        )
        
        # Vérifier que le bouton d'annulation est présent
        cancel_button = self.browser.find_element(By.ID, "cancelDeleteButton")
        self.assertTrue(cancel_button.is_displayed(), "Le bouton d'annulation n'est pas visible")

        # Cliquer sur le bouton d'annulation
        self.browser.execute_script("arguments[0].click();", cancel_button)

        # Vérifier que la modal est fermée
        WebDriverWait(self.browser, 5).until(
            EC.invisibility_of_element_located((By.ID, "confirmDeleteModal")),
            message="La modal de confirmation n'est pas fermée après le clic"
        )

        #Vérifier que la ligne n'est pas supprimée
        profile_row = self.browser.find_element(By.XPATH, f"//table[contains(@id, 'profile-table')]//td[contains(text(), '{self.profile.identifiant}')]/..")
        self.assertTrue(profile_row.is_displayed(), "La ligne du profil est visible")

    def test_delete_skill_and_cancel(self):
        """Vérifie que le clic sur supprimer affiche la modal de confirmation"""
        # Sélectionner le profil
        profile_row = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//table[contains(@id, 'profile-table')]//td[contains(text(), '{self.profile.identifiant}')]/.."))
        )
        self.browser.execute_script("arguments[0].click();", profile_row)

        # Attendre et cliquer sur le bouton de suppression
        delete_button = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//table[contains(@id, 'skill-table')]//td[contains(text(), '{self.skills[0].name}')]/..//button[contains(@class, 'delete-skill')]"))
        )
        self.browser.execute_script("arguments[0].click();", delete_button)

        # Vérifier l'affichage de la modal
        WebDriverWait(self.browser, 5).until(
            EC.visibility_of_element_located((By.ID, "confirmDeleteModal")),
            message="La modal de confirmation n'est pas apparue après le clic"
        )
        
        # Vérifier que le bouton d'annulation est présent
        cancel_button = self.browser.find_element(By.ID, "cancelDeleteButton")
        self.assertTrue(cancel_button.is_displayed(), "Le bouton d'annulation n'est pas visible")

        # Cliquer sur le bouton d'annulation
        self.browser.execute_script("arguments[0].click();", cancel_button)

        # Vérifier que la modal est fermée
        WebDriverWait(self.browser, 5).until(
            EC.invisibility_of_element_located((By.ID, "confirmDeleteModal")),
            message="La modal de confirmation n'est pas fermée après le clic"
        )

        #Vérifier que la ligne n'est pas supprimée
        skill_row = self.browser.find_element(By.XPATH, f"//table[contains(@id, 'skill-table')]//td[contains(text(), '{self.skills[0].name}')]/..")
        self.assertTrue(skill_row.is_displayed(), "La ligne de la compétence est visible")

    def test_delete_about_and_cancel(self):
        """Vérifie que le clic sur supprimer affiche la modal de confirmation et le bouton d'annulation fonctionne"""

        # Sélectionner le profil
        profile_row = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//table[contains(@id, 'profile-table')]//td[contains(text(), '{self.profile.identifiant}')]/.."))
        )
        self.browser.execute_script("arguments[0].click();", profile_row)

        # Attendre et cliquer sur le bouton de suppression
        delete_button = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//table[contains(@id, 'about-table')]//td[contains(text(), '{self.abouts[0].content}')]/..//button[contains(@class, 'delete-about')]"))
        )
        self.browser.execute_script("arguments[0].click();", delete_button)

        # Vérifier l'affichage de la modal
        WebDriverWait(self.browser, 5).until(
            EC.visibility_of_element_located((By.ID, "confirmDeleteModal")),
            message="La modal de confirmation n'est pas apparue après le clic"
        )
        
        # Vérifier que le bouton d'annulation est présent
        cancel_button = self.browser.find_element(By.ID, "cancelDeleteButton")
        self.assertTrue(cancel_button.is_displayed(), "Le bouton d'annulation n'est pas visible")

        # Cliquer sur le bouton d'annulation
        self.browser.execute_script("arguments[0].click();", cancel_button)

        # Vérifier que la modal est fermée
        WebDriverWait(self.browser, 5).until(
            EC.invisibility_of_element_located((By.ID, "confirmDeleteModal")),
            message="La modal de confirmation n'est pas fermée après le clic"
        )

        #Vérifier que la ligne n'est pas supprimée
        about_row = self.browser.find_element(By.XPATH, f"//table[contains(@id, 'about-table')]//td[contains(text(), '{self.abouts[0].content}')]/..")
        self.assertTrue(about_row.is_displayed(), "La ligne de l'about est visible")

    def test_delete_experience_and_cancel(self):
        """Vérifie que le clic sur supprimer affiche la modal de confirmation"""
        # Sélectionner le profil
        profile_row = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//table[contains(@id, 'profile-table')]//td[contains(text(), '{self.profile.identifiant}')]/.."))
        )
        self.browser.execute_script("arguments[0].click();", profile_row)

        # Attendre et cliquer sur le bouton de suppression
        delete_button = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//table[contains(@id, 'experience-table')]//td[contains(text(), '{self.experiences[0].description}')]/..//button[contains(@class, 'delete-experience')]"))
        )
        self.browser.execute_script("arguments[0].click();", delete_button)

        # Vérifier l'affichage de la modal
        WebDriverWait(self.browser, 5).until(
            EC.visibility_of_element_located((By.ID, "confirmDeleteModal")),
            message="La modal de confirmation n'est pas apparue après le clic"
        )
        
        # Vérifier que le bouton d'annulation est présent
        cancel_button = self.browser.find_element(By.ID, "cancelDeleteButton")
        self.assertTrue(cancel_button.is_displayed(), "Le bouton d'annulation n'est pas visible")

        # Cliquer sur le bouton d'annulation
        self.browser.execute_script("arguments[0].click();", cancel_button)

        # Vérifier que la modal est fermée
        WebDriverWait(self.browser, 5).until(
            EC.invisibility_of_element_located((By.ID, "confirmDeleteModal")),
            message="La modal de confirmation n'est pas fermée après le clic"
        )

        #Vérifier que la ligne n'est pas supprimée
        experience_row = self.browser.find_element(By.XPATH, f"//table[contains(@id, 'experience-table')]//td[contains(text(), '{self.experiences[0].description}')]/..")
        self.assertTrue(experience_row.is_displayed(), "La ligne de l'experience est visible")

    def test_delete_project_and_cancel(self):
        """Vérifie que le clic sur supprimer affiche la modal de confirmation et le bouton d'annulation fonctionne"""

        # Sélectionner le profil
        profile_row = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//table[contains(@id, 'profile-table')]//td[contains(text(), '{self.profile.identifiant}')]/.."))
        )
        self.browser.execute_script("arguments[0].click();", profile_row)

        # Attendre et cliquer sur le bouton de suppression
        delete_button = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//table[contains(@id, 'projects-table')]//td[contains(text(), '{self.projects[0].title}')]/..//button[contains(@class, 'delete-project')]"))
        )
        self.browser.execute_script("arguments[0].click();", delete_button)

        # Vérifier l'affichage de la modal
        WebDriverWait(self.browser, 5).until(
            EC.visibility_of_element_located((By.ID, "confirmDeleteModal")),
            message="La modal de confirmation n'est pas apparue après le clic"
        )
        
        # Vérifier que le bouton d'annulation est présent
        cancel_button = self.browser.find_element(By.ID, "cancelDeleteButton")
        self.assertTrue(cancel_button.is_displayed(), "Le bouton d'annulation n'est pas visible")

        # Cliquer sur le bouton d'annulation
        self.browser.execute_script("arguments[0].click();", cancel_button)

        # Vérifier que la modal est fermée
        WebDriverWait(self.browser, 5).until(
            EC.invisibility_of_element_located((By.ID, "confirmDeleteModal")),
            message="La modal de confirmation n'est pas fermée après le clic"
        )

        #Vérifier que la ligne n'est pas supprimée
        project_row = self.browser.find_element(By.XPATH, f"//table[contains(@id, 'projects-table')]//td[contains(text(), '{self.projects[0].title}')]/..")
        self.assertTrue(project_row.is_displayed(), "La ligne du projet est visible")

    def test_delete_profile_and_confirm(self):
        """Vérifie que le clic sur supprimer affiche la modal de confirmation et le bouton de confirmation fonctionne"""

        first_profile = Profile.objects.order_by('id').first()
        Profile.objects.exclude(pk=first_profile.pk).delete()
        self.browser.refresh()

        # Sélectionner le profil
        profile_row = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//table[contains(@id, 'profile-table')]//td[contains(text(), '{self.profile.identifiant}')]/.."))
        )
        self.browser.execute_script("arguments[0].click();", profile_row)

        # Cliquer sur le bouton de suppression du profil de test
        delete_button = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//table[contains(@id, 'profile-table')]//td[contains(text(), '{self.profile.identifiant}')]/..//button[contains(@class, 'delete-profile')]"))
        )
        self.browser.execute_script("arguments[0].click();", delete_button)

        # Vérifier que la popup est apparue
        WebDriverWait(self.browser, 5).until(
            EC.visibility_of_element_located((By.ID, "confirmDeleteModal")),
            message="La modal de confirmation n'est pas apparue après le clic"
        )

        profile_id = self.profile.id
        profile_identifiant = self.profile.identifiant

        # Cliquer sur le bouton de confirmation
        confirm_button = self.browser.find_element(By.ID, "confirmDeleteButton")
        self.browser.execute_script("arguments[0].click();", confirm_button)

        # Vérifier que la modal est fermée
        WebDriverWait(self.browser, 5).until(
            EC.invisibility_of_element_located((By.ID, "confirmDeleteModal")),
            message="La modal de confirmation n'est pas fermée après le clic"
        )
            
        # Vérifier que le profil est supprimé
        self.assertFalse(Profile.objects.filter(id=profile_id).exists(), "Le profil n'a pas été supprimé")
        
        # Vérifier que la ligne est supprimée
        try:
            profile_row = self.browser.find_element(By.XPATH, f"//table[contains(@id, 'profile-table')]//td[contains(text(), '{profile_identifiant}')]/..")
            self.assertFalse(profile_row.is_displayed(), "La ligne du profil est visible")
        except NoSuchElementException:
            pass  # La ligne a bien été supprimée

        profile_table_container = self.browser.find_element(By.ID, "profile-table-container")
        self.assertIn("Aucun profil trouvé", profile_table_container.text)

        # Vérifier que les tables sont vides
        WebDriverWait(self.browser, 5).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "#profile-data .text-muted"), 
                "Sélectionnez un profil pour voir ses données"
            ),
            message="Le message de sélection n'est pas affiché après suppression"
        )
        
        # Vérifier que les tables ne sont pas visibles
        self.assertFalse(
            self.browser.find_element(By.ID, "profile-data").find_elements(By.TAG_NAME, "table"),
            "Des tables sont encore visibles après suppression"
        )

    def test_delete_skill_and_confirm(self):
        """Vérifie que le clic sur supprimer affiche la modal de confirmation et le bouton de confirmation fonctionne"""

        # Sélectionner le profil
        profile_row = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//table[contains(@id, 'profile-table')]//td[contains(text(), '{self.profile.identifiant}')]/.."))
        )
        self.browser.execute_script("arguments[0].click();", profile_row)

        # Attendre le chargement des données
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.ID, "projects-table"))
        )

        # Cliquer sur le bouton de suppression de la section compétence de test
        delete_button = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//table[contains(@id, 'skill-table')]//td[contains(text(), '{self.skills[1].name}')]/..//button[contains(@class, 'delete-skill')]"))
        )
        self.browser.execute_script("arguments[0].click();", delete_button)

        # Vérifier que la popup est apparue
        WebDriverWait(self.browser, 5).until(
            EC.visibility_of_element_located((By.ID, "confirmDeleteModal")),
            message="La modal de confirmation n'est pas apparue après le clic"
        )

        skill_id = self.skills[1].id
        skill_name = self.skills[1].name

        # Cliquer sur le bouton de confirmation
        confirm_button = self.browser.find_element(By.ID, "confirmDeleteButton")
        self.browser.execute_script("arguments[0].click();", confirm_button)

        # Vérifier que la modal est fermée
        WebDriverWait(self.browser, 5).until(
            EC.invisibility_of_element_located((By.ID, "confirmDeleteModal")),
            message="La modal de confirmation n'est pas fermée après le clic"
        )

        # Vérifier que la competence existe toujours
        self.assertTrue(Skill.objects.filter(id=skill_id).exists(), "La compétence n'a pas été supprimée")
        
        # Vérifier que la compétence n'est plus liée au profil
        profile = Profile.objects.get(id=self.profile.id)
        self.assertFalse(skill_id in profile.skills.values_list('id', flat=True), "La compétence est toujours liée au profil")
        
        # Vérifier que la compétence n'est plus lié aux expériences du profil
        experiences = Experience.objects.filter(profile=self.profile)
        for experience in experiences:
            self.assertFalse(skill_id in experience.skills.values_list('id', flat=True), "La compétence est toujours liée à une expérience")
        
        # Vérifier que la compétence n'est plus lié aux projets du profil
        projects = Project.objects.filter(profile=self.profile)
        for project in projects:
            self.assertFalse(skill_id in project.skills.values_list('id', flat=True), "La compétence est toujours liée à un projet")

        # Vérifier que la ligne est supprimée
        try:
            skill_row = self.browser.find_element(By.XPATH, f"//table[contains(@id, 'skill-table')]//td[contains(text(), '{skill_name}')]/..")
            self.assertFalse(skill_row.is_displayed(), "La ligne de la compétence est visible")
        except NoSuchElementException:
            pass  # La ligne a bien été supprimée

        ## Vérifier que l'expérience liée à la compétence a été mise à jour

        # Trouver la ligne du tableau Projects
        experience_row = self.browser.find_element(By.XPATH, f"//div[@id='profile-data']//table[contains(@id, 'experience-table')]//td[contains(text(), '{self.experiences[0].company}')]/..")
        
        # Effectuer un double clic
        action = ActionChains(self.browser)
        action.double_click(experience_row).perform()
        
        # Attendre que la popup soit visible
        WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.ID, 'experienceModal'))
        )
        
        # Vérifier que la popup est visible
        modal = self.browser.find_element(By.ID, 'experienceModal')

        # Vérifier que la compétence n'est plus liée à l'expérience
        skills = modal.find_elements(By.ID, "skills-name")
        self.assertNotIn(skill_name, [skill.text for skill in skills])

        # Vérifier que le bouton de fermeture est visible
        WebDriverWait(self.browser, 5).until(
            EC.presence_of_element_located((By.ID, "modalCloseButton")),
            message="Le bouton de fermeture n'est pas visible"
        )

        # Cliquer sur le bouton de fermeture
        cancel_button = self.browser.find_element(By.ID, "modalCloseButton")
        self.browser.execute_script("arguments[0].click();", cancel_button)

        # Vérifier que la modal est fermée
        WebDriverWait(self.browser, 5).until(
            EC.invisibility_of_element_located((By.ID, "modalCloseButton")),
            message="La modal n'est pas fermée après le clic"
        )

        # Vérifier que la compétence n'est plus liée à l'expérience en base de données
        experience = Experience.objects.get(id=self.experiences[0].id)
        self.assertFalse(skill_id in experience.skills.values_list('id', flat=True), "La compétence est toujours liée à une expérience")

        ## Vérifier que le projet liée à la compétence a été mis à jour

        # Trouver la ligne du tableau Projects
        project_row = self.browser.find_element(By.XPATH, f"//div[@id='profile-data']//table[contains(@id, 'projects-table')]//td[contains(text(), '{self.projects[0].title}')]/..")
        
        # Effectuer un double clic
        action = ActionChains(self.browser)
        action.double_click(project_row).perform()
        
        # Attendre que la popup soit visible
        WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.ID, 'projectModal'))
        )
        
        # Vérifier que la popup est visible
        modal = self.browser.find_element(By.ID, 'projectModal')

        # Vérifier que la compétence n'est plus liée au projet
        skills = modal.find_elements(By.ID, "skills-name")
        self.assertNotIn(skill_name, [skill.text for skill in skills])

        # Vérifier que la compétence n'est plus liée au projet en base de données
        project = Project.objects.get(id=self.projects[0].id)
        self.assertFalse(skill_id in project.skills.values_list('id', flat=True), "La compétence est toujours liée à un projet")

    def test_delete_about_and_confirm(self):
        """Vérifie que le clic sur supprimer affiche la modal de confirmation et le bouton de confirmation fonctionne"""
        
        # Sélectionner le profil
        profile_row = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//table[contains(@id, 'profile-table')]//td[contains(text(), '{self.profile.identifiant}')]/.."))
        )
        self.browser.execute_script("arguments[0].click();", profile_row)

        # Cliquer sur le bouton de suppression de la section about de test
        delete_button = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//table[contains(@id, 'about-table')]//td[contains(text(), '{self.abouts[0].content}')]/..//button[contains(@class, 'delete-about')]"))
        )
        self.browser.execute_script("arguments[0].click();", delete_button)

        # Vérifier que la popup est apparue
        WebDriverWait(self.browser, 5).until(
            EC.visibility_of_element_located((By.ID, "confirmDeleteModal")),
            message="La modal de confirmation n'est pas apparue après le clic"
        )

        about_id = self.abouts[0].id
        about_content = self.abouts[0].content

        # Cliquer sur le bouton de confirmation
        confirm_button = self.browser.find_element(By.ID, "confirmDeleteButton")
        self.browser.execute_script("arguments[0].click();", confirm_button)

        # Vérifier que la modal est fermée
        WebDriverWait(self.browser, 5).until(
            EC.invisibility_of_element_located((By.ID, "confirmDeleteModal")),
            message="La modal de confirmation n'est pas fermée après le clic"
        )
        
        # Vérifier que l'about est supprimé
        self.assertFalse(About.objects.filter(id=about_id).exists(), "L'about n'a pas été supprimé")
        
        # Vérifier que la ligne est supprimée
        try:
            about_row = self.browser.find_element(By.XPATH, f"//table[contains(@id, 'about-table')]//td[contains(text(), '{about_content}')]/..")
            self.assertFalse(about_row.is_displayed(), "La ligne de l'about est visible")
        except NoSuchElementException:
            pass  # La ligne a bien été supprimée

    def test_delete_experience_and_confirm(self):
        """Vérifie que le clic sur supprimer affiche la modal de confirmation et le bouton de confirmation fonctionne"""
        
        # Sélectionner le profil
        profile_row = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//table[contains(@id, 'profile-table')]//td[contains(text(), '{self.profile.identifiant}')]/.."))
        )
        self.browser.execute_script("arguments[0].click();", profile_row)

        # Cliquer sur le bouton de suppression de la section experience de test
        delete_button = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//table[contains(@id, 'experience-table')]//td[contains(text(), '{self.experiences[1].description}')]/..//button[contains(@class, 'delete-experience')]"))
        )
        self.browser.execute_script("arguments[0].click();", delete_button)

        # Vérifier que la popup est apparue
        WebDriverWait(self.browser, 5).until(
            EC.visibility_of_element_located((By.ID, "confirmDeleteModal")),
            message="La modal de confirmation n'est pas apparue après le clic"
        )

        experience_id = self.experiences[1].id
        experience_description = self.experiences[1].description

        # Cliquer sur le bouton de confirmation
        confirm_button = self.browser.find_element(By.ID, "confirmDeleteButton")
        self.browser.execute_script("arguments[0].click();", confirm_button)

        # Vérifier que la modal est fermée
        WebDriverWait(self.browser, 5).until(
            EC.invisibility_of_element_located((By.ID, "confirmDeleteModal")),
            message="La modal de confirmation n'est pas fermée après le clic"
        )
        
        # Vérifier que l'experience est supprimée
        self.assertFalse(Experience.objects.filter(id=experience_id).exists(), "L'experience n'a pas été supprimée")
        
        # Vérifier que la ligne est supprimée
        try:
            experience_row = self.browser.find_element(By.XPATH, f"//table[contains(@id, 'experience-table')]//td[contains(text(), '{experience_description}')]/..")
            self.assertFalse(experience_row.is_displayed(), "La ligne de l'experience est visible")
        except NoSuchElementException:
            pass  # La ligne a bien été supprimée

    def test_delete_project_and_confirm(self):
        """Vérifie que le clic sur supprimer affiche la modal de confirmation et le bouton de confirmation fonctionne"""
        
        # Sélectionner le profil
        profile_row = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//table[contains(@id, 'profile-table')]//td[contains(text(), '{self.profile.identifiant}')]/.."))
        )
        self.browser.execute_script("arguments[0].click();", profile_row)

        # Cliquer sur le bouton de suppression de la section project de test
        delete_button = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//table[contains(@id, 'projects-table')]//td[contains(text(), '{self.projects[0].title}')]/..//button[contains(@class, 'delete-project')]"))
        )
        self.browser.execute_script("arguments[0].click();", delete_button)

        # Vérifier que la popup est apparue
        WebDriverWait(self.browser, 5).until(
            EC.visibility_of_element_located((By.ID, "confirmDeleteModal")),
            message="La modal de confirmation n'est pas apparue après le clic"
        )

        project_id = self.projects[0].id
        project_title = self.projects[0].title

        # Cliquer sur le bouton de confirmation
        confirm_button = self.browser.find_element(By.ID, "confirmDeleteButton")
        self.browser.execute_script("arguments[0].click();", confirm_button)

        # Vérifier que la modal est fermée
        WebDriverWait(self.browser, 5).until(
            EC.invisibility_of_element_located((By.ID, "confirmDeleteModal")),
            message="La modal de confirmation n'est pas fermée après le clic"
        )
        
        # Vérifier que le project est supprimé
        self.assertFalse(Project.objects.filter(id=project_id).exists(), "Le project n'a pas été supprimé")
        
        # Vérifier que la ligne est supprimée
        try:
            project_row = self.browser.find_element(By.XPATH, f"//table[contains(@id, 'projects-table')]//td[contains(text(), '{project_title}')]/..")
            self.assertFalse(project_row.is_displayed(), "La ligne du project est visible")
        except NoSuchElementException:
            pass  # La ligne a bien été supprimée
