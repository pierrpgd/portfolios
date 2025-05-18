from selenium import webdriver
from selenium.webdriver.common.by import By
import unittest

class HomePageTest(unittest.TestCase):

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

class NavBarTest(unittest.TestCase):

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