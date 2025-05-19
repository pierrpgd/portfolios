from django.test import TestCase, Client, LiveServerTestCase
from django.contrib.auth.models import User
from django.urls import reverse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
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

        # # Configurer Selenium
        # options = webdriver.ChromeOptions()
        # options.add_argument('--headless')  # Mode sans interface graphique
        # options.add_argument('--no-sandbox')
        # options.add_argument('--disable-dev-shm-usage')
        # self.selenium = webdriver.Chrome(options=options)
        
        # # Se connecter
        # self.selenium.get(f'{self.live_server_url}/accounts/login/')
        # username_input = self.selenium.find_element(By.NAME, 'username')
        # password_input = self.selenium.find_element(By.NAME, 'password')
        # username_input.send_keys('testuser')
        # password_input.send_keys('12345')
        # password_input.send_keys(Keys.RETURN)

        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        self.browser = webdriver.Chrome(options=options)
        
        # Attendre que la page soit chargée
        # WebDriverWait(self.browser, 10).until(
        #     EC.presence_of_element_located((By.ID, 'profile-data'))
        # )

    def tearDown(self):
        # Supprimer le superuser à la fin des tests
        if hasattr(self, 'user'):
            self.user.delete()

    def test_profile_selection_and_data_display(self):
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