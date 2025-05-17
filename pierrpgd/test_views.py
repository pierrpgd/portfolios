from django.test import TestCase
from django.urls import resolve
from pierrpgd.views import home
from django.http import HttpRequest
from bs4 import BeautifulSoup

class HomeMapTest(TestCase):

    def test_root_url_resolves_to_homepage_view(self):
        found = resolve('/')
        self.assertEqual(found.func, home)

    def test_variable_elements(self):
        request = HttpRequest()
        name = 'TEST1'
        about = ['TEST2']
        experience = [{
            'dates':'TEST3',
            'company':'TEST4',
            'location':'TEST5',
            'position':'TEST6',
            'description':'TEST7'
        }]
        projects = 'TEST8'
        context = {'name':name,'about':about, 'experience':experience, 'projects':projects}
        response = home(request, context)
        soup = BeautifulSoup(response.content, "html.parser")
        self.assertEqual(soup.find(id="name").text, name, 'The name on the homepage is not a variable.')
        self.assertEqual(soup.find(id="about").get_text(strip=True), about[0], "The 'About' part on the homepage is not a variable.")
        self.assertEqual(soup.find(id="experience").get_text(strip=True, separator='.'),
                         experience[0]['dates']+'.'+experience[0]['position']+'.'+experience[0]['company']+' - '+experience[0]['location']+'.'+experience[0]['description'],
                         "The 'Experience' part on the homepage is not a variable.")
        self.assertEqual(soup.find(id="projects").text, projects, "The 'Projects' part on the homepage is not a variable.")