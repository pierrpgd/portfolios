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
        name = 'TEST'
        about = 'TEST'
        context = {'name':name,'about':about}
        response = home(request, context)
        soup = BeautifulSoup(response.content, "html.parser")
        self.assertEqual(soup.find(id="name").text, name, 'The name on the homepage is not a variable.')
        self.assertEqual(soup.find(id="about").text, about, "The 'About' part on the homepage is not a variable.")