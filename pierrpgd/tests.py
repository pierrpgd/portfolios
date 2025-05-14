from selenium import webdriver
import unittest

class HomePageTest(unittest.TestCase):

    def setUp(self):
        self.browser = webdriver.Chrome()

    def tearDown(self):
        self.browser.quit()

    def test_project_is_installed_and_working(self):
        self.browser.get('http://localhost:8000')
        self.assertIn("Portfolio de Pierrick Pagaud", self.browser.title)