from selenium import webdriver
from selenium.webdriver.common.by import By
import unittest

class HomePageTest(unittest.TestCase):

    def setUp(self):
        self.browser = webdriver.Chrome()

    def tearDown(self):
        self.browser.quit()

    def test_project_is_installed_and_working(self):
        self.browser.get('http://localhost:8000')
        self.assertIn("Portfolio de Pierrick Pagaud", self.browser.title)

    def test_homepage_contains_a_navbar(self):
        self.browser.get('http://localhost:8000')
        navbar = self.browser.find_element(By.CLASS_NAME, "navbar")
        self.assertIsNotNone(navbar)

    def test_boostrap_is_charged(self):
        self.browser.get('http://localhost:8000')
        links = self.browser.find_elements(By.TAG_NAME, "link")
        bootstrap_loaded = any(
            "bootstrap" in link.get_attribute("href") for link in links if link.get_attribute("rel") == "stylesheet"
        )
        self.assertTrue(bootstrap_loaded, "Bootstrap CSS is not charged.")

class NavBarTest(unittest.TestCase):

    def setUp(self):
        self.browser = webdriver.Chrome()

    def tearDown(self):
        self.browser.quit()

    def test_navbar_contains_items(self):
        self.browser.get('http://localhost:8000')
        navbar = self.browser.find_element(By.CLASS_NAME, "navbar")

        items = navbar.find_elements(By.CLASS_NAME, "nav-item")
        self.assertEqual(len(items), 3, "Navigation bar doesn't have 3 items.")

        self.assertEqual(items[0].text, 'About', "Navigation bar doesn't have an 'About' item.")
        self.assertEqual(items[1].text, 'Experience', "Navigation bar doesn't have an 'Experience' item.")
        self.assertEqual(items[2].text, 'Projects', "Navigation bar doesn't have an 'Projects' item.")