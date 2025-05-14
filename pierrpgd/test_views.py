from django.test import TestCase
from django.urls import resolve
from pierrpgd.views import home

class HomeMapTest(TestCase):

    def test_root_url_resolves_to_homepage_view(self):
        found = resolve('/')
        self.assertEqual(found.func, home)