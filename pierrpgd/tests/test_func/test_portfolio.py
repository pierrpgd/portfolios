from django.test import LiveServerTestCase
from django.urls import reverse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from pierrpgd.models import Profile, About, Experience, Project
from selenium.webdriver.common.keys import Keys

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
        self.getData()
        self.url = f"{self.live_server_url}/{self.profile.identifiant}"
        self.browser.get(self.url)

    def setUpData(self):
        self.getData()
        self.url = f"{self.live_server_url}/data"
        self.browser.get(self.url)

    def getData(self):
        self.profile = Profile.objects.get(identifiant='test-profile')
        self.abouts = About.objects.filter(profile=self.profile).order_by('order')
        self.experiences = Experience.objects.filter(profile=self.profile).order_by('order')
        self.projects = Project.objects.filter(profile=self.profile).order_by('order')

class PortfolioPageTest(BaseTest):

    def setUp(self):
        super().setUpClass()
        self.setUpPortfolio()

    def test_project_is_installed_and_working(self):
        self.assertIn(f"{self.profile.name} | Portfolio", self.browser.title)

    def test_portfolio_contains_a_navbar(self):
        navbar = self.browser.find_element(By.TAG_NAME, "nav")
        self.assertIsNotNone(navbar)

    def test_boostrap_is_charged(self):
        links = self.browser.find_elements(By.TAG_NAME, "link")
        bootstrap_loaded = any(
            "bootstrap" in link.get_attribute("href") for link in links if link.get_attribute("rel") == "stylesheet"
        )
        self.assertTrue(bootstrap_loaded, "Bootstrap CSS is not charged.")

    def test_two_columns(self):
        cols = self.browser.find_elements(By.CSS_SELECTOR, "[id*='col']")
        self.assertEqual(len(cols), 2, "Portfolio doesn't have 2 columns.")

    def test_visible_title_is_my_name(self):
        name = self.browser.find_element(By.ID, "name")
        self.assertEqual(name.text, self.profile.name, "Profile name doesn't appear on the portfolio.")

    def test_navbar_contains_links(self):
        navbar = self.browser.find_element(By.TAG_NAME, "nav")

        links = navbar.find_elements(By.TAG_NAME, "a")
        self.assertEqual(len(links), 4, "Navigation bar doesn't have 4 links.")

        self.assertEqual(links[0].get_attribute('href'), f'{self.url}/', "Navigation bar doesn't have my name.")
        self.assertEqual(links[1].get_attribute('href'), f'{self.url}/#about', "Navigation bar doesn't have an 'About' item.")
        self.assertEqual(links[2].get_attribute('href'), f'{self.url}/#experience', "Navigation bar doesn't have an 'Experience' item.")
        self.assertEqual(links[3].get_attribute('href'), f'{self.url}/#projects', "Navigation bar doesn't have an 'Projects' item.")
