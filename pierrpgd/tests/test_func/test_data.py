from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from pierrpgd.models import Profile, About, Experience, Project
from selenium.webdriver.common.keys import Keys
from django.test import Client
from django.conf import settings

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
        """
        Sets up the test for the portfolio page.

        Opens the portfolio page and logs in with the test user.
        """
        self.getData()
        self.url = f"{self.live_server_url}/{self.profile.identifiant}"
        self.browser.get(self.url)

    def setUpData(self):
        """
        Sets up the test for the data page.

        Opens the data page and logs in with the test user.
        """     
        self.getData()
        self.url = f"{self.live_server_url}/data"
        self.browser.get(self.url)

        self.client = Client()
        self.client.login(username='testuser', password='testpassword')

        session = self.client.session
        self.browser.add_cookie({
            'name': settings.SESSION_COOKIE_NAME,
            'value': session.session_key,
            'path': '/',
        })

    def getData(self):
        self.profile = Profile.objects.get(identifiant='test-profile')
        self.abouts = About.objects.filter(profile=self.profile).order_by('order')
        self.experiences = Experience.objects.filter(profile=self.profile).order_by('order')
        self.projects = Project.objects.filter(profile=self.profile).order_by('order')

class ProfileTest(BaseTest):

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
        self.browser.execute_script("arguments[0].click();", profile_row)
        
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
        self.browser.execute_script("arguments[0].click();", profile_row)
        
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

class PopupTest(BaseTest):

    def setUp(self):
        super().setUp()
        self.setUpData()

    def test_double_click_about(self):
        """Teste le comportement du double clic sur une ligne du tableau À propos"""
        
        # Sélectionner le profil
        profile_row = self.browser.find_element(By.XPATH, f"//table[contains(@id, 'profile-table')]//td[contains(text(), '{self.profile.identifiant}')]/..")
        self.browser.execute_script("arguments[0].click();", profile_row)
        
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
            modal_content = self.browser.find_element(By.CSS_SELECTOR, '#aboutModal .modal-content')
            self.assertIn('Test About Content', modal_content.text)
            
            # Fermer la popup
            close_button = self.browser.find_element(By.CSS_SELECTOR, '#aboutModal .modal-header button.close')
            self.browser.execute_script("arguments[0].click();", close_button)
            
            # Attendre que la popup soit masquée
            try:
                WebDriverWait(self.browser, 10).until(
                    EC.invisibility_of_element_located((By.ID, 'aboutModal'))
                )
            except:
                # La modal a été supprimée, donc elle n'est plus dans le DOM
                pass
            
            # Vérifier que la modal n'est plus présente dans le DOM
            with self.assertRaises(NoSuchElementException):
                self.browser.find_element(By.ID, 'aboutModal')
            
            # Trouver la ligne du tableau Expériences pour la deuxième expérience
            about_row = self.browser.find_element(By.XPATH, f"//div[@id='profile-data']//table[contains(@id, 'about-table')]//td[contains(text(), '{self.abouts[1].content}')]/..")

            # Effectuer un double clic
            action = ActionChains(self.browser)
            action.double_click(about_row).perform()
            
            # Attendre que la popup soit visible
            WebDriverWait(self.browser, 10).until(
                EC.visibility_of_element_located((By.ID, 'aboutModal'))
            )
            
            # Vérifier que la popup est visible
            modal = self.browser.find_element(By.ID, 'aboutModal')
            self.assertTrue(modal.is_displayed())

            # Vérifier le contenu de la popup
            modal_content = self.browser.find_element(By.CSS_SELECTOR, '#aboutModal .modal-content')
            self.assertIn(self.abouts[1].content, modal_content.text)
            
            # Fermer la popup
            close_button = self.browser.find_element(By.CSS_SELECTOR, '#aboutModal .modal-header button.close')
            self.browser.execute_script("arguments[0].click();", close_button)
            
            # Attendre que la popup soit masquée
            try:
                WebDriverWait(self.browser, 10).until(
                    EC.invisibility_of_element_located((By.ID, 'aboutModal'))
                )
            except:
                # La modal a été supprimée, donc elle n'est plus dans le DOM
                pass
            
        except NoSuchElementException:
            self.fail("La popup n'a pas été trouvée")

    def test_double_click_experience(self):
        """Teste le comportement du double clic sur une ligne du tableau Expériences"""
        
        # Sélectionner le profil
        profile_row = self.browser.find_element(By.XPATH, f"//table[contains(@id, 'profile-table')]//td[contains(text(), '{self.profile.identifiant}')]/..")
        self.browser.execute_script("arguments[0].click();", profile_row)
        
        # Attendre que les données soient chargées
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@id='profile-data']//h2[text()='Expériences']"))
        )
        
        # Trouver la ligne du tableau Expériences
        experience_row = self.browser.find_element(By.XPATH, f"//div[@id='profile-data']//table[contains(@id, 'experience-table')]//td[contains(text(), '{self.experiences[0].description}')]/..")
        
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
        modal_content = self.browser.find_element(By.CSS_SELECTOR, '#experienceModal .modal-content')
        self.assertIn(self.experiences[0].description, modal_content.text)
        
        # Vérifier les informations de l'expérience
        info = self.browser.find_element(By.CSS_SELECTOR, '#experienceModal .modal-content-info')
        self.assertIn(self.experiences[0].dates, info.text)
        self.assertIn(self.experiences[0].company, info.text)
        self.assertIn(self.experiences[0].location, info.text)
        
        # Fermer la popup
        close_button = self.browser.find_element(By.CSS_SELECTOR, '#experienceModal .modal-header button.close')
        self.browser.execute_script("arguments[0].click();", close_button)
        
        # Attendre que la popup soit masquée
        try:
            WebDriverWait(self.browser, 10).until(
                EC.invisibility_of_element_located((By.ID, 'experienceModal'))
            )
        except:
            # La modal a été supprimée, donc elle n'est plus dans le DOM
            pass
        
        # Vérifier que la modal n'est plus présente dans le DOM
        with self.assertRaises(NoSuchElementException):
            self.browser.find_element(By.ID, 'experienceModal')
        
        # Trouver la ligne du tableau Expériences pour la deuxième expérience
        experience_row = self.browser.find_element(By.XPATH, f"//div[@id='profile-data']//table[contains(@id, 'experience-table')]//td[contains(text(), '{self.experiences[1].description}')]/..")

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
        modal_content = self.browser.find_element(By.CSS_SELECTOR, '#experienceModal .modal-content')
        self.assertIn(self.experiences[1].description, modal_content.text)
        
        # Vérifier les informations de l'expérience
        info = self.browser.find_element(By.CSS_SELECTOR, '#experienceModal .modal-content-info')
        self.assertIn(self.experiences[1].dates, info.text)
        self.assertIn(self.experiences[1].company, info.text)
        self.assertIn(self.experiences[1].location, info.text)
        
        # Fermer la popup
        close_button = self.browser.find_element(By.CSS_SELECTOR, '#experienceModal .modal-header button.close')
        self.browser.execute_script("arguments[0].click();", close_button)
        
        # Attendre que la popup soit masquée
        try:
            WebDriverWait(self.browser, 10).until(
                EC.invisibility_of_element_located((By.ID, 'experienceModal'))
            )
        except:
            # La modal a été supprimée, donc elle n'est plus dans le DOM
            pass

    def test_double_click_project(self):
        """Teste le comportement du double clic sur une ligne du tableau Projets"""
        
        # Sélectionner le profil
        profile_row = self.browser.find_element(By.XPATH, f"//table[contains(@id, 'profile-table')]//td[contains(text(), '{self.profile.identifiant}')]/..")
        self.browser.execute_script("arguments[0].click();", profile_row)
        
        # Attendre que les données soient chargées
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@id='profile-data']//h2[text()='Projets']"))
        )
        
        # Trouver la ligne du tableau Projets
        project_row = self.browser.find_element(By.XPATH, f"//div[@id='profile-data']//table[contains(@id, 'projects-table')]//td[contains(text(), '{self.projects[0].title}')]/..")
        
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
        modal_content = self.browser.find_element(By.CSS_SELECTOR, '#projectModal .modal-content')
        self.assertIn(self.projects[0].description, modal_content.text)
        
        # Vérifier le titre du projet
        title = self.browser.find_element(By.CSS_SELECTOR, '#projectModal .modal-content-info')
        self.assertIn(self.projects[0].title, title.text)
        
        # Fermer la popup
        close_button = self.browser.find_element(By.CSS_SELECTOR, '#projectModal .modal-header button.close')
        self.browser.execute_script("arguments[0].click();", close_button)
        
        # Attendre que la popup soit masquée
        try:
            WebDriverWait(self.browser, 10).until(
                EC.invisibility_of_element_located((By.ID, 'projectModal'))
            )
        except:
            # La modal a été supprimée, donc elle n'est plus dans le DOM
            pass
        
        # Vérifier que la modal n'est plus présente dans le DOM
        with self.assertRaises(NoSuchElementException):
            self.browser.find_element(By.ID, 'projectModal')
        
        # Trouver la ligne du tableau Projets pour la deuxième expérience
        project_row = self.browser.find_element(By.XPATH, f"//div[@id='profile-data']//table[contains(@id, 'projects-table')]//td[contains(text(), '{self.projects[1].title}')]/..")

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
        modal_content = self.browser.find_element(By.CSS_SELECTOR, '#projectModal .modal-content')
        self.assertIn(self.projects[1].description, modal_content.text)
        
        # Fermer la popup
        close_button = self.browser.find_element(By.CSS_SELECTOR, '#projectModal .modal-header button.close')
        self.browser.execute_script("arguments[0].click();", close_button)
        
        # Attendre que la popup soit masquée
        try:
            WebDriverWait(self.browser, 10).until(
                EC.invisibility_of_element_located((By.ID, 'projectModal'))
            )
        except:
            # La modal a été supprimée, donc elle n'est plus dans le DOM
            pass

    def test_content_is_editable(self):
        """Teste que le contenu de la popup est modifiable par l'utilisateur"""

        # Sélectionner le profil
        profile_row = self.browser.find_element(By.XPATH, f"//table[contains(@id, 'profile-table')]//td[contains(text(), '{self.profile.identifiant}')]/..")
        self.browser.execute_script("arguments[0].click();", profile_row)
        
        # Attendre que les données soient chargées
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@id='profile-data']//h2[text()='Projets']"))
        )
    
        # Trouver la ligne du tableau Projets
        project_row = self.browser.find_element(By.XPATH, f"//div[@id='profile-data']//table[contains(@id, 'projects-table')]//td[contains(text(), '{self.projects[0].title}')]/..")
        
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

class ModifyAndSaveTest(BaseTest):

    def setUp(self):
        super().setUp()
        self.setUpData()

    def test_modify_and_save_profile(self):
        """Teste la modification et la sauvegarde d'un élément Profil"""
        # Sélectionner le profil
        profile_row = self.browser.find_element(By.XPATH, f"//table[contains(@id, 'profile-table')]//td[contains(text(), '{self.profile.identifiant}')]/..")
        self.browser.execute_script("arguments[0].click();", profile_row)

        # Effectuer un double clic
        action = ActionChains(self.browser)
        action.double_click(profile_row).perform()
        
        # Attendre que la popup soit visible
        WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.ID, 'profileModal'))
        )
        
        # Vérifier que la popup est visible
        modal = self.browser.find_element(By.ID, 'profileModal')
        self.assertTrue(modal.is_displayed())
        
        # Modifier le contenu
        identifiant_field = modal.find_element(By.CSS_SELECTOR, 'span.editable-content[data-field="identifiant"]')
        new_content = "Nouveau-test-identifiant"
        
        # Effacer le contenu existant
        identifiant_field.click()
        action = ActionChains(self.browser)
        action.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
        action.send_keys(new_content).perform()

        # Modifier le contenu
        name_field = modal.find_element(By.CSS_SELECTOR, 'span.editable-content[data-field="name"]')
        old_content = name_field.text
        new_content = "Nouveau-test-nom"
        
        # Effacer le contenu existant
        name_field.click()
        action = ActionChains(self.browser)
        action.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
        action.send_keys(new_content).perform()
        
        # Enregistrer et vérifier
        save_button = modal.find_element(By.CSS_SELECTOR, '.btn-primary')
        self.browser.execute_script("arguments[0].click();", save_button)
        
        # Vérifier que la modal commence à se fermer
        WebDriverWait(self.browser, 10).until(
            EC.invisibility_of_element_located((By.ID, 'profileModal'))
        )
        
        # Vérifier côté serveur que la modification est enregistrée
        profile_obj = Profile.objects.get(id=self.profile.id)
        self.assertEqual(profile_obj.name, new_content)
        
        # Vérifier que le tableau est mis à jour
        updated_row = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.XPATH, 
                f"//table[@id='profile-table']//td[contains(., '{new_content}')]"))
        )
        self.assertTrue(updated_row.is_displayed())

        # Vérifier que le contenu précedent ne s'affiche plus
        try:
            old_row = self.browser.find_element(By.XPATH, f"//table[@id='profile-table']//td[contains(., '{old_content}')]")
            self.assertFalse(old_row.is_displayed())
        except:
            pass

    def test_modify_and_save_about(self):
        """Teste la modification et la sauvegarde d'un élément À propos"""
        # Sélectionner le profil
        profile_row = self.browser.find_element(By.XPATH, f"//table[contains(@id, 'profile-table')]//td[contains(text(), '{self.profile.identifiant}')]/..")
        self.browser.execute_script("arguments[0].click();", profile_row)
        
        # Attendre le chargement des données
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.ID, "about-table"))
        )
        
        # Trouver la ligne du tableau À propos
        about_row = self.browser.find_element(By.XPATH, f"//div[@id='profile-data']//table[contains(@id, 'about-table')]//td[contains(text(), '{self.abouts[0].content}')]/..")
        
        # Effectuer un double clic
        action = ActionChains(self.browser)
        action.double_click(about_row).perform()
        
        # Attendre que la popup soit visible
        WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.ID, 'aboutModal'))
        )
        
        # Vérifier que la popup est visible
        modal = self.browser.find_element(By.ID, 'aboutModal')
        self.assertTrue(modal.is_displayed())
        
        # Modifier le contenu
        editable_content = modal.find_element(By.CSS_SELECTOR, '.editable-content')
        new_content = "Nouveau contenu de test"
        
        # Effacer le contenu existant
        editable_content.click()
        action = ActionChains(self.browser)
        action.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
        action.send_keys(new_content).perform()
        
        # Enregistrer et vérifier
        save_button = modal.find_element(By.CSS_SELECTOR, '.btn-primary')
        self.browser.execute_script("arguments[0].click();", save_button)
        
        # Vérifier que la modal commence à se fermer
        WebDriverWait(self.browser, 10).until(
            EC.invisibility_of_element_located((By.ID, 'aboutModal'))
        )
        
        # Vérifier côté serveur que la modification est enregistrée
        about_obj = About.objects.get(id=self.abouts[0].id)
        self.assertEqual(about_obj.content, new_content)
        
        # Vérifier que le tableau est mis à jour
        updated_row = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.XPATH, 
                f"//div[@id='profile-data']//table[@id='about-table']//td[contains(., '{new_content}')]"))
        )
        self.assertTrue(updated_row.is_displayed())

    def test_modify_and_save_experience(self):
        """Teste la modification et la sauvegarde d'un élément Experience"""
        # Sélectionner le profil
        profile_row = self.browser.find_element(By.XPATH, f"//table[contains(@id, 'profile-table')]//td[contains(text(), '{self.profile.identifiant}')]/..")
        self.browser.execute_script("arguments[0].click();", profile_row)
        
        # Attendre le chargement des données
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.ID, "experience-table"))
        )
        
        # Trouver la ligne du tableau Experience
        experience_row = self.browser.find_element(By.XPATH, f"//div[@id='profile-data']//table[contains(@id, 'experience-table')]//td[contains(text(), '{self.experiences[0].company}')]/..")
        
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
        
        # Modifier le contenu
        dates_field = modal.find_element(By.CSS_SELECTOR, 'span.editable-content[data-field="dates"]')
        new_content = "Nouveau contenu de test"
        
        # Effacer le contenu existant
        dates_field.click()
        action = ActionChains(self.browser)
        action.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
        action.send_keys(new_content).perform()
        
        # Enregistrer et vérifier
        save_button = modal.find_element(By.CSS_SELECTOR, '.btn-primary')
        self.browser.execute_script("arguments[0].click();", save_button)
        
        # Vérifier que la modal commence à se fermer
        WebDriverWait(self.browser, 10).until(
            EC.invisibility_of_element_located((By.ID, 'experienceModal'))
        )
        
        # Vérifier côté serveur que la modification est enregistrée
        experience_obj = Experience.objects.get(id=self.experiences[0].id)
        self.assertEqual(experience_obj.dates, new_content)
        
        # Vérifier que le tableau est mis à jour
        updated_row = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.XPATH, 
                f"//div[@id='profile-data']//table[@id='experience-table']//td[contains(., '{new_content}')]"))
        )
        self.assertTrue(updated_row.is_displayed())

    def test_modify_and_save_project(self):
        """Teste la modification et la sauvegarde d'un élément Project"""
        # Sélectionner le profil
        profile_row = self.browser.find_element(By.XPATH, f"//table[contains(@id, 'profile-table')]//td[contains(text(), '{self.profile.identifiant}')]/..")
        self.browser.execute_script("arguments[0].click();", profile_row)
        
        # Attendre le chargement des données
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.ID, "projects-table"))
        )
        
        # Trouver la ligne du tableau Projects
        project_row = self.browser.find_element(By.XPATH, f"//div[@id='profile-data']//table[contains(@id, 'projects-table')]//td[contains(text(), '{self.projects[0].title}')]/..")
        
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
        
        # Modifier le titre
        title_field = modal.find_element(By.CSS_SELECTOR, 'span.editable-content[data-field="title"]')
        new_content = "Nouveau contenu de test"
        
        # Effacer le contenu existant
        title_field.click()
        action = ActionChains(self.browser)
        action.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
        action.send_keys(new_content).perform()
        
        # Enregistrer et vérifier
        save_button = modal.find_element(By.CSS_SELECTOR, '.btn-primary')
        self.browser.execute_script("arguments[0].click();", save_button)
        
        # Vérifier que la modal commence à se fermer
        WebDriverWait(self.browser, 10).until(
            EC.invisibility_of_element_located((By.ID, 'projectModal'))
        )
        
        # Vérifier côté serveur que la modification est enregistrée
        project_obj = Project.objects.get(id=self.projects[0].id)
        self.assertEqual(project_obj.title, new_content)
        
        # Vérifier que le tableau est mis à jour
        updated_row = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.XPATH, 
                f"//div[@id='profile-data']//table[@id='projects-table']//td[contains(., '{new_content}')]"))
        )
        self.assertTrue(updated_row.is_displayed())

class AddElementTest(BaseTest):

    def setUp(self):
        super().setUp()
        self.setUpData()

    def test_add_profile(self):
        """
        Teste l'ajout d'un profil via l'interface
        1. Ouvre la page data_display
        2. Clique sur 'Ajouter un profil'
        3. Remplit les champs 'Identifiant' et 'Nom'
        4. Valide et vérifie l'affichage
        """

        # Cliquer sur le bouton d'ajout
        add_button = self.browser.find_element(By.ID, "addProfileButton")
        
        # Cliquer via JavaScript pour éviter les problèmes d'interception
        self.browser.execute_script("arguments[0].click();", add_button)
        
        # Attendre que la modal soit visible
        modal = WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.ID, "profileModal"))
        )
        
        # Remplir le champ identifiant
        identifiant_field = modal.find_element(By.CSS_SELECTOR, "[data-field='identifiant']")
        identifiant_field.send_keys("Nouveau_profil")
        
        # Remplir le champ nom
        name_field = modal.find_element(By.CSS_SELECTOR, "[data-field='name']")
        name_field.send_keys("Nouveau_profil")
        
        # Cliquer sur valider
        validate_button = modal.find_element(By.ID, "profileModalValidateButton")
        self.browser.execute_script("arguments[0].click();", validate_button)
        
        # Vérifier l'affichage dans le tableau
        WebDriverWait(self.browser, 10).until(
            lambda driver: any("Nouveau_profil" in el.text 
                           for el in driver.find_elements(By.CSS_SELECTOR, "#profile-table tbody tr"))
        )
        
        # Vérification finale
        rows = self.browser.find_elements(By.CSS_SELECTOR, "#profile-table tbody tr")
        self.assertTrue(any("Nouveau_profil" in row.text for row in rows))

    def test_add_profile_in_empty_table(self):
        """
        Teste l'ajout d'un profil via l'interface
        1. Ouvre la page data_display
        2. Clique sur 'Ajouter un profil'
        3. Remplit les champs 'Identifiant' et 'Nom'
        4. Valide et vérifie l'affichage
        """

        Profile.objects.all().delete()
        self.browser.refresh()

        # Cliquer sur le bouton d'ajout
        add_button = self.browser.find_element(By.ID, "addProfileButton")
        
        # Cliquer via JavaScript pour éviter les problèmes d'interception
        self.browser.execute_script("arguments[0].click();", add_button)
        
        # Attendre que la modal soit visible
        modal = WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.ID, "profileModal"))
        )
        
        # Remplir le champ identifiant
        identifiant_field = modal.find_element(By.CSS_SELECTOR, "[data-field='identifiant']")
        identifiant_field.send_keys("Nouveau_profil")
        
        # Remplir le champ nom
        name_field = modal.find_element(By.CSS_SELECTOR, "[data-field='name']")
        name_field.send_keys("Nouveau_profil")
        
        # Cliquer sur valider
        validate_button = modal.find_element(By.ID, "profileModalValidateButton")
        self.browser.execute_script("arguments[0].click();", validate_button)
        
        # Vérifier l'affichage dans le tableau
        WebDriverWait(self.browser, 10).until(
            lambda driver: any("Nouveau_profil" in el.text 
                           for el in driver.find_elements(By.CSS_SELECTOR, "#profile-table tbody tr"))
        )
        
        # Vérification finale
        rows = self.browser.find_elements(By.CSS_SELECTOR, "#profile-table tbody tr")
        self.assertTrue(any("Nouveau_profil" in row.text for row in rows))
        

    def test_add_about_section(self):
        """
        Teste l'ajout d'une section À propos via l'interface
        1. Ouvre la page data_display
        2. Clique sur 'Ajouter une section'
        3. Remplit le champ 'Contenu'
        4. Valide et vérifie l'affichage
        """
        
        # Sélectionner le profil
        profile_row = self.browser.find_element(By.XPATH, f"//table[contains(@id, 'profile-table')]//td[contains(text(), '{self.profile.identifiant}')]/..")
        self.browser.execute_script("arguments[0].click();", profile_row)
        
        # Attendre le chargement des données
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.ID, "about-table"))
        )
        
        # Cliquer sur le bouton d'ajout
        add_button = self.browser.find_element(By.ID, "addAboutSectionButton")
        
        # Cliquer via JavaScript pour éviter les problèmes d'interception
        self.browser.execute_script("arguments[0].click();", add_button)
        
        # Attendre que la modal soit visible
        modal = WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.ID, "aboutModal"))
        )
        
        # Remplir le champ contenu
        content_field = modal.find_element(By.CSS_SELECTOR, "[data-field='content']")
        content_field.send_keys("Nouveau contenu de test")
        
        # Cliquer sur valider
        validate_button = modal.find_element(By.ID, "aboutModalValidateButton")
        self.browser.execute_script("arguments[0].click();", validate_button)
        
        # Vérifier l'affichage dans le tableau
        WebDriverWait(self.browser, 20).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "#about-table tbody tr"), 
                "Nouveau contenu de test"
            )
        )
        
        # Vérification finale
        rows = self.browser.find_elements(By.CSS_SELECTOR, "#about-table tbody tr")
        self.assertTrue(any("Nouveau contenu de test" in row.text for row in rows))

    def test_add_experience_section(self):
        """
        Teste l'ajout d'une section Expérience via l'interface
        1. Ouvre la page data_display
        2. Clique sur 'Ajouter une section'
        3. Remplit le champ 'Contenu'
        4. Valide et vérifie l'affichage
        """
        
        # Sélectionner le profil
        profile_row = self.browser.find_element(By.XPATH, f"//table[contains(@id, 'profile-table')]//td[contains(text(), '{self.profile.identifiant}')]/..")
        self.browser.execute_script("arguments[0].click();", profile_row)
        
        # Attendre le chargement des données
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.ID, "experience-table"))
        )
        
        # Scroll vers l'élément
        add_button = self.browser.find_element(By.ID, "addExperienceSectionButton")
        self.browser.execute_script("arguments[0].scrollIntoView(true);", add_button)
        
        # Attendre que l'élément soit cliquable
        WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.ID, "addExperienceSectionButton"))
        )
        
        # Cliquer via JavaScript pour éviter les problèmes d'interception
        self.browser.execute_script("arguments[0].click();", add_button)
        
        # Attendre que la modal soit visible
        modal = WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.ID, "experienceModal"))
        )
        
        # Remplir le champ contenu
        content_field = modal.find_element(By.CSS_SELECTOR, "[data-field='description']")
        content_field.send_keys("Nouveau contenu de test")
        
        # Cliquer sur valider
        validate_button = modal.find_element(By.ID, "experienceModalValidateButton")
        self.browser.execute_script("arguments[0].click();", validate_button)
        
        # Vérifier l'affichage dans le tableau
        WebDriverWait(self.browser, 20).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "#experience-table tbody tr"), 
                "Nouveau contenu de test"
            )
        )
        
        # Vérification finale
        rows = self.browser.find_elements(By.CSS_SELECTOR, "#experience-table tbody tr")
        self.assertTrue(any("Nouveau contenu de test" in row.text for row in rows))

    def test_add_project_section(self):
        """
        Teste l'ajout d'une section Projets via l'interface
        1. Ouvre la page data_display
        2. Clique sur 'Ajouter une section'
        3. Remplit le champ 'Contenu'
        4. Valide et vérifie l'affichage
        """
        
        # Sélectionner le profil
        profile_row = self.browser.find_element(By.XPATH, f"//table[contains(@id, 'profile-table')]//td[contains(text(), '{self.profile.identifiant}')]/..")
        self.browser.execute_script("arguments[0].click();", profile_row)
        
        # Attendre le chargement des données
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.ID, "projects-table"))
        )
        
        # Cliquer sur le bouton d'ajout
        add_button = self.browser.find_element(By.ID, "addProjectSectionButton")
        
        # Scroll vers l'élément
        self.browser.execute_script("arguments[0].scrollIntoView(true);", add_button)
        
        # Attendre que l'élément soit cliquable
        WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.ID, "addProjectSectionButton"))
        )
        
        # Cliquer via JavaScript pour éviter les problèmes d'interception
        self.browser.execute_script("arguments[0].click();", add_button)
        
        # Attendre que la modal soit visible
        modal = WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.ID, "projectModal"))
        )
        
        # Remplir le champ contenu
        content_field = modal.find_element(By.CSS_SELECTOR, "[data-field='description']")
        content_field.send_keys("Nouveau contenu de test")
        
        # Cliquer sur valider
        validate_button = modal.find_element(By.ID, "projectModalValidateButton")
        self.browser.execute_script("arguments[0].click();", validate_button)
        
        # Vérifier l'affichage dans le tableau
        WebDriverWait(self.browser, 20).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "#projects-table tbody tr"), 
                "Nouveau contenu de test"
            )
        )
        
        # Vérification finale
        rows = self.browser.find_elements(By.CSS_SELECTOR, "#projects-table tbody tr")
        self.assertTrue(any("Nouveau contenu de test" in row.text for row in rows))

class DeleteElementTest(BaseTest):

    def setUp(self):
        super().setUp()
        self.setUpData()

    def test_delete_profile_and_cancel(self):
        """Vérifie que le clic sur supprimer affiche la modal de confirmation et le bouton d'annulation fonctionne"""

        # Cliquer sur le bouton de suppression du profil de test
        delete_button = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//table[contains(@id, 'profile-table')]//td[contains(text(), '{self.profile.identifiant}')]/..//button[contains(@class, 'delete-profile')]"))
        )
        self.browser.execute_script("arguments[0].click();", delete_button)

        # Vérifier l'affichage de la modal
        WebDriverWait(self.browser, 5).until(
            EC.visibility_of_element_located((By.ID, "confirmDeleteModal")),
            message="La modal de confirmation n'est pas apparue après le clic"
        )
        
        # Vérifier que le bouton d'annulation est présent
        cancel_button = self.browser.find_element(By.ID, "cancelDeleteButton")
        self.assertTrue(cancel_button.is_displayed(), "Le bouton d'annulation n'est pas visible")

        # Cliquer sur le bouton d'annulation
        self.browser.execute_script("arguments[0].click();", cancel_button)

        # Vérifier que la modal est fermée
        WebDriverWait(self.browser, 5).until(
            EC.invisibility_of_element_located((By.ID, "confirmDeleteModal")),
            message="La modal de confirmation n'est pas fermée après le clic"
        )

        #Vérifier que la ligne n'est pas supprimée
        profile_row = self.browser.find_element(By.XPATH, f"//table[contains(@id, 'profile-table')]//td[contains(text(), '{self.profile.identifiant}')]/..")
        self.assertTrue(profile_row.is_displayed(), "La ligne du profil est visible")

    def test_delete_about_and_cancel(self):
        """Vérifie que le clic sur supprimer affiche la modal de confirmation et le bouton d'annulation fonctionne"""

        # Sélectionner le profil
        profile_row = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//table[contains(@id, 'profile-table')]//td[contains(text(), '{self.profile.identifiant}')]/.."))
        )
        self.browser.execute_script("arguments[0].click();", profile_row)

        # Attendre et cliquer sur le bouton de suppression
        delete_button = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//table[contains(@id, 'about-table')]//td[contains(text(), '{self.abouts[0].content}')]/..//button[contains(@class, 'delete-about')]"))
        )
        self.browser.execute_script("arguments[0].click();", delete_button)

        # Vérifier l'affichage de la modal
        WebDriverWait(self.browser, 5).until(
            EC.visibility_of_element_located((By.ID, "confirmDeleteModal")),
            message="La modal de confirmation n'est pas apparue après le clic"
        )
        
        # Vérifier que le bouton d'annulation est présent
        cancel_button = self.browser.find_element(By.ID, "cancelDeleteButton")
        self.assertTrue(cancel_button.is_displayed(), "Le bouton d'annulation n'est pas visible")

        # Cliquer sur le bouton d'annulation
        self.browser.execute_script("arguments[0].click();", cancel_button)

        # Vérifier que la modal est fermée
        WebDriverWait(self.browser, 5).until(
            EC.invisibility_of_element_located((By.ID, "confirmDeleteModal")),
            message="La modal de confirmation n'est pas fermée après le clic"
        )

        #Vérifier que la ligne n'est pas supprimée
        about_row = self.browser.find_element(By.XPATH, f"//table[contains(@id, 'about-table')]//td[contains(text(), '{self.abouts[0].content}')]/..")
        self.assertTrue(about_row.is_displayed(), "La ligne de l'about est visible")

    def test_delete_experience_and_cancel(self):
        """Vérifie que le clic sur supprimer affiche la modal de confirmation"""
        # Sélectionner le profil
        profile_row = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//table[contains(@id, 'profile-table')]//td[contains(text(), '{self.profile.identifiant}')]/.."))
        )
        self.browser.execute_script("arguments[0].click();", profile_row)

        # Attendre et cliquer sur le bouton de suppression
        delete_button = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//table[contains(@id, 'experience-table')]//td[contains(text(), '{self.experiences[0].description}')]/..//button[contains(@class, 'delete-experience')]"))
        )
        self.browser.execute_script("arguments[0].click();", delete_button)

        # Vérifier l'affichage de la modal
        WebDriverWait(self.browser, 5).until(
            EC.visibility_of_element_located((By.ID, "confirmDeleteModal")),
            message="La modal de confirmation n'est pas apparue après le clic"
        )
        
        # Vérifier que le bouton d'annulation est présent
        cancel_button = self.browser.find_element(By.ID, "cancelDeleteButton")
        self.assertTrue(cancel_button.is_displayed(), "Le bouton d'annulation n'est pas visible")

        # Cliquer sur le bouton d'annulation
        self.browser.execute_script("arguments[0].click();", cancel_button)

        # Vérifier que la modal est fermée
        WebDriverWait(self.browser, 5).until(
            EC.invisibility_of_element_located((By.ID, "confirmDeleteModal")),
            message="La modal de confirmation n'est pas fermée après le clic"
        )

        #Vérifier que la ligne n'est pas supprimée
        experience_row = self.browser.find_element(By.XPATH, f"//table[contains(@id, 'experience-table')]//td[contains(text(), '{self.experiences[0].description}')]/..")
        self.assertTrue(experience_row.is_displayed(), "La ligne de l'experience est visible")

    def test_delete_project_and_cancel(self):
        """Vérifie que le clic sur supprimer affiche la modal de confirmation et le bouton d'annulation fonctionne"""

        # Sélectionner le profil
        profile_row = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//table[contains(@id, 'profile-table')]//td[contains(text(), '{self.profile.identifiant}')]/.."))
        )
        self.browser.execute_script("arguments[0].click();", profile_row)

        # Attendre et cliquer sur le bouton de suppression
        delete_button = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//table[contains(@id, 'projects-table')]//td[contains(text(), '{self.projects[0].title}')]/..//button[contains(@class, 'delete-project')]"))
        )
        self.browser.execute_script("arguments[0].click();", delete_button)

        # Vérifier l'affichage de la modal
        WebDriverWait(self.browser, 5).until(
            EC.visibility_of_element_located((By.ID, "confirmDeleteModal")),
            message="La modal de confirmation n'est pas apparue après le clic"
        )
        
        # Vérifier que le bouton d'annulation est présent
        cancel_button = self.browser.find_element(By.ID, "cancelDeleteButton")
        self.assertTrue(cancel_button.is_displayed(), "Le bouton d'annulation n'est pas visible")

        # Cliquer sur le bouton d'annulation
        self.browser.execute_script("arguments[0].click();", cancel_button)

        # Vérifier que la modal est fermée
        WebDriverWait(self.browser, 5).until(
            EC.invisibility_of_element_located((By.ID, "confirmDeleteModal")),
            message="La modal de confirmation n'est pas fermée après le clic"
        )

        #Vérifier que la ligne n'est pas supprimée
        project_row = self.browser.find_element(By.XPATH, f"//table[contains(@id, 'projects-table')]//td[contains(text(), '{self.projects[0].title}')]/..")
        self.assertTrue(project_row.is_displayed(), "La ligne du projet est visible")

    def test_delete_profile_and_confirm(self):
        """Vérifie que le clic sur supprimer affiche la modal de confirmation et le bouton de confirmation fonctionne"""

        first_profile = Profile.objects.order_by('id').first()
        Profile.objects.exclude(pk=first_profile.pk).delete()
        self.browser.refresh()

        # Sélectionner le profil
        profile_row = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//table[contains(@id, 'profile-table')]//td[contains(text(), '{self.profile.identifiant}')]/.."))
        )
        self.browser.execute_script("arguments[0].click();", profile_row)

        # Cliquer sur le bouton de suppression du profil de test
        delete_button = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//table[contains(@id, 'profile-table')]//td[contains(text(), '{self.profile.identifiant}')]/..//button[contains(@class, 'delete-profile')]"))
        )
        self.browser.execute_script("arguments[0].click();", delete_button)

        # Vérifier que la popup est apparue
        WebDriverWait(self.browser, 5).until(
            EC.visibility_of_element_located((By.ID, "confirmDeleteModal")),
            message="La modal de confirmation n'est pas apparue après le clic"
        )

        profile_id = self.profile.id
        profile_identifiant = self.profile.identifiant

        # Cliquer sur le bouton de confirmation
        confirm_button = self.browser.find_element(By.ID, "confirmDeleteButton")
        self.browser.execute_script("arguments[0].click();", confirm_button)

        # Vérifier que la modal est fermée
        WebDriverWait(self.browser, 5).until(
            EC.invisibility_of_element_located((By.ID, "confirmDeleteModal")),
            message="La modal de confirmation n'est pas fermée après le clic"
        )
            
        # Vérifier que le profil est supprimé
        self.assertFalse(Profile.objects.filter(id=profile_id).exists(), "Le profil n'a pas été supprimé")
        
        # Vérifier que la ligne est supprimée
        try:
            profile_row = self.browser.find_element(By.XPATH, f"//table[contains(@id, 'profile-table')]//td[contains(text(), '{profile_identifiant}')]/..")
            self.assertFalse(profile_row.is_displayed(), "La ligne du profil est visible")
        except NoSuchElementException:
            pass  # La ligne a bien été supprimée

        profile_table_container = self.browser.find_element(By.ID, "profile-table-container")
        self.assertIn("Aucun profil trouvé", profile_table_container.text)

        # Vérifier que les tables sont vides
        WebDriverWait(self.browser, 5).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "#profile-data .text-muted"), 
                "Sélectionnez un profil pour voir ses données"
            ),
            message="Le message de sélection n'est pas affiché après suppression"
        )
        
        # Vérifier que les tables ne sont pas visibles
        self.assertFalse(
            self.browser.find_element(By.ID, "profile-data").find_elements(By.TAG_NAME, "table"),
            "Des tables sont encore visibles après suppression"
        )

    def test_delete_about_and_confirm(self):
        """Vérifie que le clic sur supprimer affiche la modal de confirmation et le bouton de confirmation fonctionne"""
        
        # Sélectionner le profil
        profile_row = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//table[contains(@id, 'profile-table')]//td[contains(text(), '{self.profile.identifiant}')]/.."))
        )
        self.browser.execute_script("arguments[0].click();", profile_row)

        # Cliquer sur le bouton de suppression de la section about de test
        delete_button = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//table[contains(@id, 'about-table')]//td[contains(text(), '{self.abouts[0].content}')]/..//button[contains(@class, 'delete-about')]"))
        )
        self.browser.execute_script("arguments[0].click();", delete_button)

        # Vérifier que la popup est apparue
        WebDriverWait(self.browser, 5).until(
            EC.visibility_of_element_located((By.ID, "confirmDeleteModal")),
            message="La modal de confirmation n'est pas apparue après le clic"
        )

        about_id = self.abouts[0].id
        about_content = self.abouts[0].content

        # Cliquer sur le bouton de confirmation
        confirm_button = self.browser.find_element(By.ID, "confirmDeleteButton")
        self.browser.execute_script("arguments[0].click();", confirm_button)

        # Vérifier que la modal est fermée
        WebDriverWait(self.browser, 5).until(
            EC.invisibility_of_element_located((By.ID, "confirmDeleteModal")),
            message="La modal de confirmation n'est pas fermée après le clic"
        )
        
        # Vérifier que l'about est supprimé
        self.assertFalse(About.objects.filter(id=about_id).exists(), "L'about n'a pas été supprimé")
        
        # Vérifier que la ligne est supprimée
        try:
            about_row = self.browser.find_element(By.XPATH, f"//table[contains(@id, 'about-table')]//td[contains(text(), '{about_content}')]/..")
            self.assertFalse(about_row.is_displayed(), "La ligne de l'about est visible")
        except NoSuchElementException:
            pass  # La ligne a bien été supprimée

    def test_delete_experience_and_confirm(self):
        """Vérifie que le clic sur supprimer affiche la modal de confirmation et le bouton de confirmation fonctionne"""
        
        # Sélectionner le profil
        profile_row = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//table[contains(@id, 'profile-table')]//td[contains(text(), '{self.profile.identifiant}')]/.."))
        )
        self.browser.execute_script("arguments[0].click();", profile_row)

        # Cliquer sur le bouton de suppression de la section experience de test
        delete_button = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//table[contains(@id, 'experience-table')]//td[contains(text(), '{self.experiences[1].description}')]/..//button[contains(@class, 'delete-experience')]"))
        )
        self.browser.execute_script("arguments[0].click();", delete_button)

        # Vérifier que la popup est apparue
        WebDriverWait(self.browser, 5).until(
            EC.visibility_of_element_located((By.ID, "confirmDeleteModal")),
            message="La modal de confirmation n'est pas apparue après le clic"
        )

        experience_id = self.experiences[1].id
        experience_description = self.experiences[1].description

        # Cliquer sur le bouton de confirmation
        confirm_button = self.browser.find_element(By.ID, "confirmDeleteButton")
        self.browser.execute_script("arguments[0].click();", confirm_button)

        # Vérifier que la modal est fermée
        WebDriverWait(self.browser, 5).until(
            EC.invisibility_of_element_located((By.ID, "confirmDeleteModal")),
            message="La modal de confirmation n'est pas fermée après le clic"
        )
        
        # Vérifier que l'experience est supprimée
        self.assertFalse(Experience.objects.filter(id=experience_id).exists(), "L'experience n'a pas été supprimée")
        
        # Vérifier que la ligne est supprimée
        try:
            experience_row = self.browser.find_element(By.XPATH, f"//table[contains(@id, 'experience-table')]//td[contains(text(), '{experience_description}')]/..")
            self.assertFalse(experience_row.is_displayed(), "La ligne de l'experience est visible")
        except NoSuchElementException:
            pass  # La ligne a bien été supprimée

    def test_delete_project_and_confirm(self):
        """Vérifie que le clic sur supprimer affiche la modal de confirmation et le bouton de confirmation fonctionne"""
        
        # Sélectionner le profil
        profile_row = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//table[contains(@id, 'profile-table')]//td[contains(text(), '{self.profile.identifiant}')]/.."))
        )
        self.browser.execute_script("arguments[0].click();", profile_row)

        # Cliquer sur le bouton de suppression de la section project de test
        delete_button = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//table[contains(@id, 'projects-table')]//td[contains(text(), '{self.projects[0].title}')]/..//button[contains(@class, 'delete-project')]"))
        )
        self.browser.execute_script("arguments[0].click();", delete_button)

        # Vérifier que la popup est apparue
        WebDriverWait(self.browser, 5).until(
            EC.visibility_of_element_located((By.ID, "confirmDeleteModal")),
            message="La modal de confirmation n'est pas apparue après le clic"
        )

        project_id = self.projects[0].id
        project_title = self.projects[0].title

        # Cliquer sur le bouton de confirmation
        confirm_button = self.browser.find_element(By.ID, "confirmDeleteButton")
        self.browser.execute_script("arguments[0].click();", confirm_button)

        # Vérifier que la modal est fermée
        WebDriverWait(self.browser, 5).until(
            EC.invisibility_of_element_located((By.ID, "confirmDeleteModal")),
            message="La modal de confirmation n'est pas fermée après le clic"
        )
        
        # Vérifier que le project est supprimé
        self.assertFalse(Project.objects.filter(id=project_id).exists(), "Le project n'a pas été supprimé")
        
        # Vérifier que la ligne est supprimée
        try:
            project_row = self.browser.find_element(By.XPATH, f"//table[contains(@id, 'projects-table')]//td[contains(text(), '{project_title}')]/..")
            self.assertFalse(project_row.is_displayed(), "La ligne du project est visible")
        except NoSuchElementException:
            pass  # La ligne a bien été supprimée
