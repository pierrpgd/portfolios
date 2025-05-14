from django.test import TestCase
from django.urls import resolve
from pierrpgd.views import home
from django.http import HttpRequest
from bs4 import BeautifulSoup

class HomeMapTest(TestCase):

    def test_root_url_resolves_to_homepage_view(self):
        found = resolve('/')
        self.assertEqual(found.func, home)

    def test_name_is_a_variable(self):
        request = HttpRequest()
        name = 'TEST'
        response = home(request, name)
        soup = BeautifulSoup(response.content, "html.parser")
        self.assertEqual(soup.find(class_="name").text, name, 'The name on the homepage is not a variable.')