from django.test import LiveServerTestCase
from django.urls import reverse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from .models import Profile, About, Experience, Project
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
        self.about = About.objects.get(profile=self.profile)
        self.experience = Experience.objects.get(profile=self.profile)
        self.project = Project.objects.get(profile=self.profile)

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

class DataDisplayTest(BaseTest):

    def setUp(self):
        super().setUp()
        self.setUpData()

    def test_profile_selection_toggle_and_data_display_or_hide(self):
        """
        Teste la sélection d'un profil et l'affichage des données liées avec Selenium
        """

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
        """Teste la présence du bouton d'ajout de profil"""

        # Vérifier la présence du titre de la page
        page_title = self.browser.find_element(By.CSS_SELECTOR, "h1").text
        self.assertEqual(page_title, "Données de la Base de Données")
        
        # Vérifier la présence du bouton d'ajout
        add_button = self.browser.find_element(By.CSS_SELECTOR, "div.card-header a.btn-primary")
        self.assertIsNotNone(add_button)
        
        # Vérifier que le bouton contient le texte correct
        self.assertIn('Ajouter un profil', add_button.text)
        
        # Vérifier que le bouton contient l'icône Font Awesome
        icon = add_button.find_element(By.CSS_SELECTOR, "i.fas")
        self.assertIsNotNone(icon)
        
        # Vérifier que le bouton pointe vers la bonne URL
        add_profile_url = reverse('add_profile')
        self.assertEqual(add_button.get_attribute('href'), f"{self.live_server_url}{add_profile_url}")

    def test_double_click_about(self):
        """Teste le comportement du double clic sur une ligne du tableau À propos"""
        
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

    def test_content_is_editable(self):
        """Teste que le contenu de la popup est modifiable par l'utilisateur"""

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

