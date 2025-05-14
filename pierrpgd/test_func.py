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

    def test_two_columns(self):
        self.browser.get('http://localhost:8000')
        cols = self.browser.find_elements(By.CSS_SELECTOR, "[class*='col']")

        self.assertEqual(len(cols), 2, "Homepage doesn't have 2 columns.")

        self.assertEqual(cols[0].get_attribute("class"), 'col-5', "The left column doesn't match the expected size (3/12).")
        self.assertEqual(cols[1].get_attribute("class"), 'col-7', "The right column doesn't match the expected size (9/12).")

    def test_visible_title_is_my_name(self):
        self.browser.get('http://localhost:8000')
        name = self.browser.find_element(By.ID, "name")
        self.assertEqual(name.text, 'Pierrick Pagaud', "My name doesn't appear on the portfolio.")

    def test_top_margin(self):
        self.browser.get('http://localhost:8000')
        body = self.browser.find_element(By.TAG_NAME, "body")
        divs = body.find_elements(By.TAG_NAME, "div")
        self.assertGreaterEqual(len(divs), 2, "The number of div elements in the body is low.")
        self.assertIn('p-4', divs[0].get_attribute("class"), "The first div element in the body is not a p-4 class.")
        self.assertIn('mt-5', divs[1].get_attribute("class"), "The second div element in the body is not a mt-5 class.")

    def test_side_margins(self):
        self.browser.get('http://localhost:8000')
        body = self.browser.find_element(By.TAG_NAME, "body")
        
        container = body.find_elements(By.TAG_NAME, "div")[1]
        self.assertIn('container-fluid', container.get_attribute("class"), "The second div element in the body is not a container-fluid class.")
        
        row = body.find_elements(By.TAG_NAME, "div")[2]
        self.assertIn('margin-left: 5vw;', row.get_attribute("style"), "The third div element in the body doesn't have margins on the left side.")
        self.assertIn('margin-right: 5vw;', row.get_attribute("style"), "The third div element in the body doesn't have margins on the right side.")

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

    def test_navbar_is_vertical(self):
        self.browser.get('http://localhost:8000')
        navbar = self.browser.find_element(By.CLASS_NAME, "navbar")
        self.assertIn("flex-direction: column;", navbar.get_attribute("style"), "Navigation bar is not vertical")
    
    def test_navbar_is_left_aligned(self):
        self.browser.get('http://localhost:8000')
        navbar = self.browser.find_element(By.CLASS_NAME, "navbar")
        self.assertIn("align-items: flex-start;", navbar.get_attribute("style"), "Navigation bar is not left-aligned")