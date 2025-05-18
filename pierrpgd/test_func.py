from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from selenium import webdriver
from selenium.webdriver.common.by import By

class HomePageTest(TestCase):

    def setUp(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        self.browser = webdriver.Chrome(options=options)

    def tearDown(self):
        self.browser.quit()

    def test_project_is_installed_and_working(self):
        self.browser.get('http://localhost:8000')
        self.assertIn("Pierrick Pagaud | Portfolio", self.browser.title)

    def test_homepage_contains_a_navbar(self):
        self.browser.get('http://localhost:8000')
        navbar = self.browser.find_element(By.TAG_NAME, "nav")
        self.assertIsNotNone(navbar)

    def test_boostrap_is_charged(self):
        self.browser.get('http://localhost:8000')
        links = self.browser.find_elements(By.TAG_NAME, "link")
        bootstrap_loaded = any(
            "bootstrap" in link.get_attribute("href") for link in links if link.get_attribute("rel") == "stylesheet"
        )
        self.assertTrue(bootstrap_loaded, "Bootstrap CSS is not charged.")

    def test_two_columns(self):
        self.browser.get('http://localhost:8000')
        cols = self.browser.find_elements(By.CSS_SELECTOR, "[id*='col']")

        self.assertEqual(len(cols), 2, "Homepage doesn't have 2 columns.")

    def test_visible_title_is_my_name(self):
        self.browser.get('http://localhost:8000')
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
        self.browser.get('http://localhost:8000')
        navbar = self.browser.find_element(By.TAG_NAME, "nav")

        links = navbar.find_elements(By.TAG_NAME, "a")
        self.assertEqual(len(links), 4, "Navigation bar doesn't have 4 links.")

        self.assertEqual(links[0].get_attribute('href'), 'http://localhost:8000/', "Navigation bar doesn't have my name.")
        self.assertEqual(links[1].get_attribute('href'), 'http://localhost:8000/#about', "Navigation bar doesn't have an 'About' item.")
        self.assertEqual(links[2].get_attribute('href'), 'http://localhost:8000/#experience', "Navigation bar doesn't have an 'Experience' item.")
        self.assertEqual(links[3].get_attribute('href'), 'http://localhost:8000/#projects', "Navigation bar doesn't have an 'Projects' item.")

class DataDisplayTest(TestCase):
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
    
    def tearDown(self):
        # Supprimer le superuser à la fin des tests
        if hasattr(self, 'user'):
            self.user.delete()

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