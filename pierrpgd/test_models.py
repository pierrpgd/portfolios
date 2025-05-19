from django.test import TestCase
from django.db import IntegrityError
from .models import Profile, About, Experience, Project

class ProfileModelTest(TestCase):
    def setUp(self):
        self.profile = Profile.objects.create(name='Test Profile', identifiant='test-identifiant')

    def test_profile_creation(self):
        """Test la création d'un profil"""
        self.assertEqual(self.profile.name, 'Test Profile')
        self.assertEqual(self.profile.identifiant, 'test-identifiant')
        self.assertIsNotNone(self.profile.created_at)
        self.assertIsNotNone(self.profile.updated_at)

    def test_profile_creation_with_same_identifiant(self):
        """Test que la création d'un profil avec un identifiant déjà existant échoue"""
        with self.assertRaises(IntegrityError):
            Profile.objects.create(name='Another Profile', identifiant='test-identifiant')

    def test_profile_string_representation(self):
        """Test la représentation en chaîne de caractères"""
        self.assertEqual(str(self.profile), 'Test Profile')

    def test_profile_update(self):
        """Test la mise à jour d'un profil"""
        self.profile.name = 'Updated Profile'
        self.profile.identifiant = 'updated-identifiant'
        self.profile.save()
        updated_profile = Profile.objects.get(id=self.profile.id)
        self.assertEqual(updated_profile.name, 'Updated Profile')
        self.assertEqual(updated_profile.identifiant, 'updated-identifiant')

    def test_profile_deletion(self):
        """Test la suppression d'un profil"""
        profile_id = self.profile.id
        self.profile.delete()
        with self.assertRaises(Profile.DoesNotExist):
            Profile.objects.get(id=profile_id)


class AboutModelTest(TestCase):
    def setUp(self):
        self.profile = Profile.objects.create(
            name='Test Profile',
            identifiant='test-identifiant'
        )
        self.about = About.objects.create(
            profile=self.profile,
            content='Test content',
            order=1
        )

    def test_about_creation(self):
        """Test la création d'une section About"""
        self.assertEqual(self.about.content, 'Test content')
        self.assertEqual(self.about.order, 1)
        self.assertEqual(self.about.profile, self.profile)

    def test_about_string_representation(self):
        """Test la représentation en chaîne de caractères"""
        expected_str = f"About {self.about.order} for {self.profile.name}"
        self.assertEqual(str(self.about), expected_str)

    def test_about_ordering(self):
        """Test le tri des sections About"""
        about2 = About.objects.create(
            profile=self.profile,
            content='Second content',
            order=2
        )
        abouts = About.objects.all()
        self.assertEqual(abouts[0], self.about)
        self.assertEqual(abouts[1], about2)

    def test_about_deletion(self):
        """Test la suppression d'une section About"""
        about_id = self.about.id
        self.about.delete()
        with self.assertRaises(About.DoesNotExist):
            About.objects.get(id=about_id)

    def test_about_cascade_deletion(self):
        """Test la suppression en cascade quand un Profile est supprimé"""
        profile_id = self.profile.id
        self.profile.delete()
        with self.assertRaises(About.DoesNotExist):
            About.objects.get(id=self.about.id)


class ExperienceModelTest(TestCase):
    def setUp(self):
        self.profile = Profile.objects.create(
            name='Test Profile',
            identifiant='test-identifiant'
        )
        self.experience = Experience.objects.create(
            profile=self.profile,
            dates='2023-2024',
            company='Test Company',
            location='Test Location',
            position='Test Position',
            description='Test description',
            order=1
        )

    def test_experience_creation(self):
        """Test la création d'une expérience"""
        self.assertEqual(self.experience.dates, '2023-2024')
        self.assertEqual(self.experience.company, 'Test Company')
        self.assertEqual(self.experience.position, 'Test Position')
        self.assertEqual(self.experience.order, 1)

    def test_experience_string_representation(self):
        """Test la représentation en chaîne de caractères"""
        expected_str = f"{self.experience.position} at {self.experience.company}"
        self.assertEqual(str(self.experience), expected_str)

    def test_experience_ordering(self):
        """Test le tri des expériences"""
        exp2 = Experience.objects.create(
            profile=self.profile,
            dates='2022-2023',
            company='Second Company',
            position='Second Position',
            order=2
        )
        experiences = Experience.objects.all()
        self.assertEqual(experiences[0], self.experience)
        self.assertEqual(experiences[1], exp2)

    def test_experience_deletion(self):
        """Test la suppression d'une expérience"""
        experience_id = self.experience.id
        self.experience.delete()
        with self.assertRaises(Experience.DoesNotExist):
            Experience.objects.get(id=experience_id)

    def test_experience_cascade_deletion(self):
        """Test la suppression en cascade quand un Profile est supprimé"""
        profile_id = self.profile.id
        self.profile.delete()
        with self.assertRaises(Experience.DoesNotExist):
            Experience.objects.get(id=self.experience.id)


class ProjectModelTest(TestCase):
    def setUp(self):
        self.profile = Profile.objects.create(
            name='Test Profile',
            identifiant='test-identifiant'
        )
        self.project = Project.objects.create(
            profile=self.profile,
            title='Test Project',
            description='Test description',
            order=1
        )

    def test_project_creation(self):
        """Test la création d'un projet"""
        self.assertEqual(self.project.title, 'Test Project')
        self.assertEqual(self.project.description, 'Test description')
        self.assertEqual(self.project.order, 1)

    def test_project_string_representation(self):
        """Test la représentation en chaîne de caractères"""
        self.assertEqual(str(self.project), 'Test Project')

    def test_project_ordering(self):
        """Test le tri des projets"""
        project2 = Project.objects.create(
            profile=self.profile,
            title='Second Project',
            description='Second description',
            order=2
        )
        projects = Project.objects.all()
        self.assertEqual(projects[0], self.project)
        self.assertEqual(projects[1], project2)

    def test_project_deletion(self):
        """Test la suppression d'un projet"""
        project_id = self.project.id
        self.project.delete()
        with self.assertRaises(Project.DoesNotExist):
            Project.objects.get(id=project_id)

    def test_project_cascade_deletion(self):
        """Test la suppression en cascade quand un Profile est supprimé"""
        profile_id = self.profile.id
        self.profile.delete()
        with self.assertRaises(Project.DoesNotExist):
            Project.objects.get(id=self.project.id)
