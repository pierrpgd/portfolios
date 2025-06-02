from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from pierrpgd.models import Profile, About, Experience, Education, Project

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
        cls.browser.set_window_size(1200, 800)

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
        self.educations = Education.objects.filter(profile=self.profile).order_by('order')
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
        self.assertEqual(len(links), 5, "Navigation bar doesn't have 4 links.")

        self.assertEqual(links[0].get_attribute('href'), f'{self.url}/', "Navigation bar doesn't have my name.")
        self.assertEqual(links[1].get_attribute('href'), f'{self.url}/#about', "Navigation bar doesn't have an 'About' item.")
        self.assertEqual(links[2].get_attribute('href'), f'{self.url}/#experience', "Navigation bar doesn't have an 'Experience' item.")
        self.assertEqual(links[3].get_attribute('href'), f'{self.url}/#education', "Navigation bar doesn't have an 'Education' item.")
        self.assertEqual(links[4].get_attribute('href'), f'{self.url}/#projects', "Navigation bar doesn't have an 'Projects' item.")

    def test_profile_title_is_visible(self):
        title = self.browser.find_element(By.ID, "title")
        self.assertEqual(title.text, self.profile.title, "Profile title doesn't appear on the portfolio.")

    def test_experience_data_is_visible(self):
        experience_section = self.browser.find_element(By.ID, 'experience')

        experience_containers = experience_section.find_elements(By.CLASS_NAME, 'tile-link')
        self.assertEqual(experience_containers[0].find_element(By.CLASS_NAME, 'tile-title').text, self.experiences[0].position, "Experience title doesn't appear on the portfolio.")
        self.assertEqual(experience_containers[0].find_element(By.CLASS_NAME, 'tile-description').text, self.experiences[0].description, "Experience description doesn't appear on the portfolio.")
        self.assertEqual(experience_containers[0].find_element(By.CLASS_NAME, 'company').text, self.experiences[0].company, "Experience company doesn't appear on the portfolio.")
        self.assertEqual(experience_containers[0].find_element(By.CLASS_NAME, 'location').text, self.experiences[0].location, "Experience location doesn't appear on the portfolio.")
        self.assertEqual(experience_containers[0].find_element(By.CLASS_NAME, 'tile-details').get_attribute('innerHTML'), self.experiences[0].details, "Experience details doesn't appear on the portfolio.")

        expected_url = self.experiences[0].url if self.experiences[0].url.endswith('/') else f"{self.experiences[0].url}/"
        self.assertEqual(experience_containers[0].get_attribute('href'), expected_url, "Experience URL doesn't appear on the portfolio.")

    def test_education_data_is_visible(self):
        education_section = self.browser.find_element(By.ID, 'education')

        education_containers = education_section.find_elements(By.CLASS_NAME, 'tile-link')
        self.assertEqual(education_containers[0].find_element(By.CLASS_NAME, 'tile-title').text, self.educations[0].title, "Education title doesn't appear on the portfolio.")
        self.assertEqual(education_containers[0].find_element(By.CLASS_NAME, 'tile-description').text, self.educations[0].description, "Education description doesn't appear on the portfolio.")
        self.assertEqual(education_containers[0].find_element(By.CLASS_NAME, 'institution').text, self.educations[0].institution, "Education institution doesn't appear on the portfolio.")
        self.assertEqual(education_containers[0].find_element(By.CLASS_NAME, 'location').text, self.educations[0].location, "Education location doesn't appear on the portfolio.")

        expected_url = self.educations[0].url if self.educations[0].url.endswith('/') else f"{self.educations[0].url}/"
        self.assertEqual(education_containers[0].get_attribute('href'), expected_url, "Education URL doesn't appear on the portfolio.")

    def test_project_data_is_visible(self):
        project_section = self.browser.find_element(By.ID, 'projects')

        project_containers = project_section.find_elements(By.CLASS_NAME, 'tile-link')
        self.assertEqual(project_containers[0].find_element(By.CLASS_NAME, 'tile-title').text, self.projects[0].title, "Project title doesn't appear on the portfolio.")
        self.assertEqual(project_containers[0].find_element(By.CLASS_NAME, 'tile-description').text, self.projects[0].description, "Project description doesn't appear on the portfolio.")
        self.assertEqual(project_containers[0].find_element(By.TAG_NAME, 'img').get_attribute('src').replace(self.live_server_url, ''), self.projects[0].image_url, "Project image doesn't appear on the portfolio.")

        expected_url = self.projects[0].url if self.projects[0].url.endswith('/') else f"{self.projects[0].url}/"
        self.assertEqual(project_containers[0].get_attribute('href'), expected_url, "Project URL doesn't appear on the portfolio.")
        