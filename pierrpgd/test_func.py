from django.test import TestCase, Client, LiveServerTestCase
from django.contrib.auth.models import User
from django.urls import reverse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from .models import Profile, About, Experience, Project

url_portfolio = 'http://localhost:8000/pierrpgd'

class PortfolioPageTest(TestCase):

    def setUp(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        self.browser = webdriver.Chrome(options=options)

    def tearDown(self):
        self.browser.quit()

    def test_project_is_installed_and_working(self):
        self.browser.get(url_portfolio)
        self.assertIn("Pierrick Pagaud | Portfolio", self.browser.title)

    def test_portfolio_contains_a_navbar(self):
        self.browser.get(url_portfolio)
        navbar = self.browser.find_element(By.TAG_NAME, "nav")
        self.assertIsNotNone(navbar)

    def test_boostrap_is_charged(self):
        self.browser.get(url_portfolio)
        links = self.browser.find_elements(By.TAG_NAME, "link")
        bootstrap_loaded = any(
            "bootstrap" in link.get_attribute("href") for link in links if link.get_attribute("rel") == "stylesheet"
        )
        self.assertTrue(bootstrap_loaded, "Bootstrap CSS is not charged.")

    def test_two_columns(self):
        self.browser.get(url_portfolio)
        cols = self.browser.find_elements(By.CSS_SELECTOR, "[id*='col']")

        self.assertEqual(len(cols), 2, "Portfolio doesn't have 2 columns.")

    def test_visible_title_is_my_name(self):
        self.browser.get(url_portfolio)
        name = self.browser.find_element(By.ID, "name")
        self.assertEqual(name.text, 'Pierrick Pagaud', "My name doesn't appear on the portfolio.")

class NavBarTest(TestCase):

    def setUp(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        self.browser = webdriver.Chrome(options=options)

    def tearDown(self):
        self.browser.quit()

    def test_navbar_contains_links(self):
        self.browser.get(url_portfolio)
        navbar = self.browser.find_element(By.TAG_NAME, "nav")

        links = navbar.find_elements(By.TAG_NAME, "a")
        self.assertEqual(len(links), 4, "Navigation bar doesn't have 4 links.")

        self.assertEqual(links[0].get_attribute('href'), f'{url_portfolio}/', "Navigation bar doesn't have my name.")
        self.assertEqual(links[1].get_attribute('href'), f'{url_portfolio}/#about', "Navigation bar doesn't have an 'About' item.")
        self.assertEqual(links[2].get_attribute('href'), f'{url_portfolio}/#experience', "Navigation bar doesn't have an 'Experience' item.")
        self.assertEqual(links[3].get_attribute('href'), f'{url_portfolio}/#projects', "Navigation bar doesn't have an 'Projects' item.")

class DataDisplayTest(LiveServerTestCase):
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
        
        # Créer un profil de test avec ses éléments liés
        self.profile = Profile.objects.create(
            name='Test Profile',
            identifiant='test-profile'
        )
        
        self.about = About.objects.create(
            profile=self.profile,
            content='Test About Content',
            order=1
        )
        
        self.experience = Experience.objects.create(
            profile=self.profile,
            dates='2023-2024',
            company='Test Company',
            location='Test Location',
            position='Test Position',
            description='Test Description',
            order=1
        )
        
        self.project = Project.objects.create(
            profile=self.profile,
            title='Test Project',
            description='Test Project Description',
            order=1
        )

        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        self.browser = webdriver.Chrome(options=options)
        
    def tearDown(self):
        # Supprimer le superuser à la fin des tests
        if hasattr(self, 'user'):
            self.user.delete()

    def test_profile_selection_toggle_and_data_display_or_hide(self):
        """
        Teste la sélection d'un profil et l'affichage des données liées avec Selenium
        """
        # Accéder à la page data_display
        self.browser.get(f'{self.live_server_url}/data/')
        
        # Trouver la ligne du profil dans le tableau
        profile_row = self.browser.find_element(By.XPATH, f"//table[contains(@id, 'profile-table')]//td[contains(text(), '{self.profile.name}')]/..")
        
        # Cliquer sur la ligne du profil
        profile_row.click()
        
        # Attendre que les données soient chargées
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@id='profile-data']//h2[text()='À propos']"))
        )

        # Vérifier l'affichage des données About
        about_content = self.browser.find_element(By.XPATH, "//div[@id='profile-data']//table[contains(@id, 'about-table')]//td[contains(text(), 'Test About Content')]")
        self.assertTrue(about_content.is_displayed())

        # Vérifier l'affichage des données Experience
        experience_company = self.browser.find_element(By.XPATH, "//div[@id='profile-data']//table[contains(@id, 'experience-table')]//td[contains(text(), 'Test Company')]")
        self.assertTrue(experience_company.is_displayed())

        # Vérifier l'affichage des données Project
        project_title = self.browser.find_element(By.XPATH, "//div[@id='profile-data']//table[contains(@id, 'projects-table')]//td[contains(text(), 'Test Project')]")
        self.assertTrue(project_title.is_displayed())

        # Cliquer à nouveau sur la ligne du profil pour le désélectionner
        profile_row.click()
        
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

    def test_profile_add_button_exists(self):
        response = self.client.get(reverse('data_display'))
        self.assertEqual(response.status_code, 200)
        
        # Vérifier la présence du bouton d'ajout
        self.assertContains(response, 'Ajouter un profil')
        
        # Vérifier l'existence du lien vers la page d'ajout
        add_profile_url = reverse('add_profile')
        self.assertContains(response, f'href="{add_profile_url}"')
        
        # Vérifier que le bouton est dans la section des profils
        content = response.content.decode('utf-8')
        profiles_section_start = content.find('<div class="card mb-4">')
        profiles_section_end = content.find('</div>', profiles_section_start)
        profiles_section = content[profiles_section_start:profiles_section_end]
        
        self.assertIn('Ajouter un profil', profiles_section)

    def test_double_click_about(self):
        """Teste le comportement du double clic sur une ligne du tableau À propos"""
        
        # Accéder à la page data_display
        self.browser.get(f'{self.live_server_url}/data/')
        
        # Sélectionner le profil
        profile_row = self.browser.find_element(By.XPATH, f"//table[contains(@id, 'profile-table')]//td[contains(text(), '{self.profile.identifiant}')]/..")
        profile_row.click()
        
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
            modal_content = self.browser.find_element(By.ID, 'aboutModalContent')
            self.assertIn('Test About Content', modal_content.text)
            
            # Fermer la popup
            close_button = self.browser.find_element(By.CSS_SELECTOR, '#aboutModal button.close')
            close_button.click()
            
            # Attendre que la popup soit masquée
            WebDriverWait(self.browser, 10).until(
                EC.invisibility_of_element_located((By.ID, 'aboutModal'))
            )
            
            # Vérifier que la popup est masquée (display: none)
            modal = self.browser.find_element(By.ID, 'aboutModal')
            display_style = modal.value_of_css_property('display')
            self.assertEqual(display_style, 'none')
            
        except NoSuchElementException:
            self.fail("La popup n'a pas été trouvée")

    def test_double_click_experience(self):
        """Teste le comportement du double clic sur une ligne du tableau Expériences"""
        
        # Accéder à la page data_display
        self.browser.get(f'{self.live_server_url}/data/')
        
        # Sélectionner le profil
        profile_row = self.browser.find_element(By.XPATH, f"//table[contains(@id, 'profile-table')]//td[contains(text(), '{self.profile.identifiant}')]/..")
        profile_row.click()
        
        # Attendre que les données soient chargées
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@id='profile-data']//h2[text()='Expériences']"))
        )
        
        # Trouver la ligne du tableau Expériences
        experience_row = self.browser.find_element(By.XPATH, f"//div[@id='profile-data']//table[contains(@id, 'experience-table')]//td[contains(text(), '{self.experience.description}')]/..")
        
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
        modal_content = self.browser.find_element(By.ID, 'experienceModalContent')
        self.assertIn(self.experience.description, modal_content.text)
        
        # Vérifier les informations de l'expérience
        info = self.browser.find_element(By.CSS_SELECTOR, '#experienceModal .modal-content-info')
        self.assertIn(self.experience.dates, info.text)
        self.assertIn(self.experience.company, info.text)
        self.assertIn(self.experience.location, info.text)
        
        # Fermer la popup
        close_button = self.browser.find_element(By.CSS_SELECTOR, '#experienceModal button.close')
        close_button.click()
        
        # Attendre que la popup soit masquée
        WebDriverWait(self.browser, 10).until(
            EC.invisibility_of_element_located((By.ID, 'experienceModal'))
        )
        
        # Vérifier que la popup est masquée
        display_style = modal.value_of_css_property('display')
        self.assertEqual(display_style, 'none')

    def test_double_click_project(self):
        """Teste le comportement du double clic sur une ligne du tableau Projets"""
        
        # Accéder à la page data_display
        self.browser.get(f'{self.live_server_url}/data/')
        
        # Sélectionner le profil
        profile_row = self.browser.find_element(By.XPATH, f"//table[contains(@id, 'profile-table')]//td[contains(text(), '{self.profile.identifiant}')]/..")
        profile_row.click()
        
        # Attendre que les données soient chargées
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@id='profile-data']//h2[text()='Projets']"))
        )
        
        # Trouver la ligne du tableau Projets
        project_row = self.browser.find_element(By.XPATH, f"//div[@id='profile-data']//table[contains(@id, 'projects-table')]//td[contains(text(), '{self.project.title}')]/..")
        
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
        modal_content = self.browser.find_element(By.ID, 'projectModalContent')
        self.assertIn(self.project.description, modal_content.text)
        
        # Vérifier le titre du projet
        title = self.browser.find_element(By.CSS_SELECTOR, '#projectModal .modal-content-info')
        self.assertIn(self.project.title, title.text)
        
        # Fermer la popup
        close_button = self.browser.find_element(By.CSS_SELECTOR, '#projectModal button.close')
        close_button.click()
        
        # Attendre que la popup soit masquée
        WebDriverWait(self.browser, 10).until(
            EC.invisibility_of_element_located((By.ID, 'projectModal'))
        )
        
        # Vérifier que la popup est masquée
        display_style = modal.value_of_css_property('display')
        self.assertEqual(display_style, 'none')