from django.test import TestCase
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from pierrpgd.models import Profile, About, Experience, Education, Project, Skill

class BaseTest(TestCase):
    fixtures = ['test_fixtures.json']

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.profile = Profile.objects.get(identifiant='test-profile')
        cls.abouts = About.objects.filter(profile=cls.profile)
        cls.experiences = Experience.objects.filter(profile=cls.profile)
        cls.educations = Education.objects.filter(profile=cls.profile)
        cls.projects = Project.objects.filter(profile=cls.profile)
        cls.skills = Skill.objects.all()

class ProfileModelTest(BaseTest):
    def test_profile_creation(self):
        """Test la création d'un profil"""
        self.assertEqual(self.profile.name, 'Test Profile')
        self.assertEqual(self.profile.identifiant, 'test-profile')
        self.assertEqual(self.profile.title, 'Test Title')
        self.assertIsNotNone(self.profile.created_at)
        self.assertIsNotNone(self.profile.updated_at)
        skills = list(self.profile.skills.all())
        self.assertIn(self.skills[0], skills)
        self.assertIn(self.skills[1], skills)
        self.assertIn(self.skills[2], skills)

    def test_profile_creation_with_same_identifiant(self):
        """Test que la création d'un profil avec un identifiant déjà existant échoue"""
        with self.assertRaises(IntegrityError):
            Profile.objects.create(name='Another Profile', identifiant='test-profile', title='Another Title')

    def test_profile_string_representation(self):
        """Test la représentation en chaîne de caractères"""
        self.assertEqual(str(self.profile), 'Test Profile')

    def test_profile_update(self):
        """Test la mise à jour d'un profil"""
        self.profile.name = 'Updated Profile'
        self.profile.identifiant = 'updated-identifiant'
        self.profile.title = 'Updated Title'
        self.profile.skills.remove(self.skills[0])
        self.profile.save()
        updated_profile = Profile.objects.get(id=self.profile.id)
        self.assertEqual(updated_profile.name, 'Updated Profile')
        self.assertEqual(updated_profile.identifiant, 'updated-identifiant')
        self.assertEqual(updated_profile.title, 'Updated Title')
        skills = list(self.profile.skills.all())
        self.assertNotIn(self.skills[0], skills)

    def test_profile_deletion(self):
        """Test la suppression d'un profil"""
        profile_id = self.profile.id
        self.profile.delete()
        with self.assertRaises(Profile.DoesNotExist):
            Profile.objects.get(id=profile_id)

class AboutModelTest(BaseTest):
    def test_about_creation(self):
        """Test la création d'une section About"""
        self.assertEqual(self.abouts[0].content, 'Test About Content')
        self.assertEqual(self.abouts[0].order, 0)
        self.assertEqual(self.abouts[0].profile, self.profile)

        self.assertEqual(self.abouts[1].content, 'Second About Content')
        self.assertEqual(self.abouts[1].order, 1)
        self.assertEqual(self.abouts[1].profile, self.profile)

    def test_about_string_representation(self):
        """Test la représentation en chaîne de caractères"""
        expected_str = f"About {self.abouts[0].order} for {self.profile.name}"
        self.assertEqual(str(self.abouts[0]), expected_str)

    def test_about_ordering(self):
        """Test le tri des sections About"""
        abouts = About.objects.filter(profile=self.profile)
        self.assertEqual(abouts[0], self.abouts[0])
        self.assertEqual(abouts[1], self.abouts[1])

    def test_about_deletion(self):
        """Test la suppression d'une section About"""
        about_id = self.abouts[0].id
        self.abouts[0].delete()
        with self.assertRaises(About.DoesNotExist):
            About.objects.get(id=about_id)

    def test_about_cascade_deletion(self):
        """Test la suppression en cascade quand un Profile est supprimé"""
        profile_id = self.profile.id
        self.profile.delete()
        with self.assertRaises(About.DoesNotExist):
            About.objects.get(profile=profile_id)

class ExperienceModelTest(BaseTest):

    def test_experience_creation(self):
        """Test la création d'une expérience"""
        self.assertEqual(self.experiences[0].dates, '2023-2024')
        self.assertEqual(self.experiences[0].company, 'Test Company')
        self.assertEqual(self.experiences[0].position, 'Test Position')
        self.assertEqual(self.experiences[0].location, 'Test Location')
        self.assertEqual(self.experiences[0].description, 'Test Description')
        self.assertEqual(self.experiences[0].details, 'Test Details')
        self.assertEqual(self.experiences[0].order, 0)
        self.assertEqual(self.experiences[0].url, 'https://testurl.com')
        self.assertEqual(self.experiences[0].skills.count(), 2)
        skills = list(self.experiences[0].skills.all())
        self.assertIn(self.skills[0], skills)
        self.assertIn(self.skills[1], skills)
        
        self.assertEqual(self.experiences[1].dates, '2022-2023')
        self.assertEqual(self.experiences[1].company, 'Test Company 2')
        self.assertEqual(self.experiences[1].position, 'Test Position 2')
        self.assertEqual(self.experiences[1].location, 'Test Location 2')
        self.assertEqual(self.experiences[1].description, 'Test Description 2')
        self.assertEqual(self.experiences[1].details, 'Test Details 2')
        self.assertEqual(self.experiences[1].order, 1)
        self.assertEqual(self.experiences[1].url, 'https://testurl2.com')
        self.assertEqual(self.experiences[1].skills.count(), 1)
        skills = list(self.experiences[1].skills.all())
        self.assertIn(self.skills[0], skills)

    def test_experience_string_representation(self):
        """Test la représentation en chaîne de caractères"""
        expected_str = f"{self.experiences[0].position} at {self.experiences[0].company}"
        self.assertEqual(str(self.experiences[0]), expected_str)

    def test_experience_ordering(self):
        """Test le tri des expériences"""
        experiences = Experience.objects.filter(profile=self.profile)
        self.assertEqual(experiences[0], self.experiences[0])
        self.assertEqual(experiences[1], self.experiences[1])

    def test_experience_deletion(self):
        """Test la suppression d'une expérience"""
        experience_id = self.experiences[0].id
        self.experiences[0].delete()
        with self.assertRaises(Experience.DoesNotExist):
            Experience.objects.get(id=experience_id)

    def test_experience_cascade_deletion(self):
        """Test la suppression en cascade quand un Profile est supprimé"""
        profile_id = self.profile.id
        self.profile.delete()
        with self.assertRaises(Experience.DoesNotExist):
            Experience.objects.get(profile=profile_id)

class EducationModelTest(BaseTest):

    def test_education_creation(self):
        """Test la création d'une éducation"""
        self.assertEqual(self.educations[0].dates, '2016-2019')
        self.assertEqual(self.educations[0].title, 'Test Title')
        self.assertEqual(self.educations[0].institution, 'Test Institution')
        self.assertEqual(self.educations[0].field, 'Test Field')
        self.assertEqual(self.educations[0].description, 'Test Description')
        self.assertEqual(self.educations[0].details, 'Test Details')
        self.assertEqual(self.educations[0].order, 0)
        self.assertEqual(self.educations[0].url, 'https://testurl.com')
        self.assertEqual(self.educations[0].skills.count(), 2)
        skills = list(self.educations[0].skills.all())
        self.assertIn(self.skills[0], skills)
        self.assertIn(self.skills[1], skills)
        
        self.assertEqual(self.educations[1].dates, '2015-2016')
        self.assertEqual(self.educations[1].title, 'Test Title 2')
        self.assertEqual(self.educations[1].institution, 'Test Institution 2')
        self.assertEqual(self.educations[1].field, 'Test Field 2')
        self.assertEqual(self.educations[1].description, 'Test Description 2')
        self.assertEqual(self.educations[1].details, 'Test Details 2')
        self.assertEqual(self.educations[1].order, 1)
        self.assertEqual(self.educations[1].url, 'https://testurl2.com')
        self.assertEqual(self.educations[1].skills.count(), 1)
        skills = list(self.educations[1].skills.all())
        self.assertIn(self.skills[0], skills)

    def test_education_string_representation(self):
        """Test la représentation en chaîne de caractères"""
        expected_str = f"{self.educations[0].title} at {self.educations[0].institution}"
        self.assertEqual(str(self.educations[0]), expected_str)

    def test_education_ordering(self):
        """Test le tri des educations"""
        educations = Education.objects.filter(profile=self.profile)
        self.assertEqual(educations[0], self.educations[0])
        self.assertEqual(educations[1], self.educations[1])

    def test_education_deletion(self):
        """Test la suppression d'une éducation"""
        education_id = self.educations[0].id
        self.educations[0].delete()
        with self.assertRaises(Education.DoesNotExist):
            Education.objects.get(id=education_id)

    def test_education_cascade_deletion(self):
        """Test la suppression en cascade quand un Profile est supprimé"""
        profile_id = self.profile.id
        self.profile.delete()
        with self.assertRaises(Education.DoesNotExist):
            Education.objects.get(profile=profile_id)

class ProjectModelTest(BaseTest):

    def test_project_creation(self):
        """Test la création d'un projet"""
        self.assertEqual(self.projects[0].title, 'Test Project')
        self.assertEqual(self.projects[0].description, 'Test Project Description')
        self.assertEqual(self.projects[0].image_url, '/static/portfolio-example.png')
        self.assertEqual(self.projects[0].order, 0)
        self.assertEqual(self.projects[0].url, 'https://testurl3.com')
        self.assertEqual(self.projects[0].skills.count(), 2)
        skills = list(self.projects[0].skills.all())
        self.assertIn(self.skills[1], skills)
        self.assertIn(self.skills[2], skills)

        self.assertEqual(self.projects[1].title, 'Second Project')
        self.assertEqual(self.projects[1].description, 'Second Project Description')
        self.assertEqual(self.projects[1].order, 1)
        self.assertEqual(self.projects[1].url, 'https://testurl4.com')
        self.assertEqual(self.projects[1].skills.count(), 1)
        skills = list(self.projects[1].skills.all())
        self.assertIn(self.skills[1], skills)

    def test_project_string_representation(self):
        """Test la représentation en chaîne de caractères"""
        self.assertEqual(str(self.projects[0]), 'Test Project')

    def test_project_ordering(self):
        """Test le tri des projets"""
        projects = Project.objects.filter(profile=self.profile)
        self.assertEqual(projects[0], self.projects[0])
        self.assertEqual(projects[1], self.projects[1])

    def test_project_deletion(self):
        """Test la suppression d'un projet"""
        project_id = self.projects[0].id
        self.projects[0].delete()
        with self.assertRaises(Project.DoesNotExist):
            Project.objects.get(id=project_id)

    def test_project_cascade_deletion(self):
        """Test la suppression en cascade quand un Profile est supprimé"""
        profile_id = self.profile.id
        self.profile.delete()
        with self.assertRaises(Project.DoesNotExist):
            Project.objects.get(profile=profile_id)

class SkillModelTest(BaseTest):
    def test_skill_creation(self):
        """Test la création d'une compétence"""
        self.assertEqual(self.skills[0].name, 'Test Skill')
        self.assertEqual(self.skills[0].category, 'Test Category')

        self.assertEqual(self.skills[1].name, 'Second Skill')
        self.assertEqual(self.skills[1].category, 'Second Category')
    
    def test_skill_string_representation(self):
        """Test la représentation en chaîne de caractères"""
        self.assertEqual(str(self.skills[0]), 'Test Category - Test Skill')
        self.assertEqual(str(self.skills[1]), 'Second Category - Second Skill')
    
    def test_skill_update(self):
        """Test la modification d'une compétence"""
        skill = self.skills[0]
        skill.name = 'Compétence Modifiée'
        skill.save()
        
        updated_skill = Skill.objects.get(pk=skill.pk)
        self.assertEqual(updated_skill.name, 'Compétence Modifiée')
    
    def test_skill_deletion(self):
        """Test la suppression d'une compétence"""
        initial_count = Skill.objects.count()
        self.skills[0].delete()
        self.assertEqual(Skill.objects.count(), initial_count - 1)
    
    def test_skill_required_fields(self):
        """Test que les champs requis sont bien validés"""        
        # Test category vide
        with self.assertRaises(ValidationError):
            skill = Skill(category='', name='Test')
            skill.full_clean()
        
        # Test name vide
        with self.assertRaises(ValidationError):
            skill = Skill(category='Test', name='')
            skill.full_clean()
        
        # Test les deux champs vides
        with self.assertRaises(ValidationError):
            skill = Skill(category='', name='')
            skill.full_clean()