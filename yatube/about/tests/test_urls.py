from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

TESTS_DATA = {
    "status_code": {
        reverse("about:author"): HTTPStatus.OK,
        reverse("about:tech"): HTTPStatus.OK
    },
    "templates": {
        reverse("about:author"): "about/author.html",
        reverse("about:tech"): "about/tech.html"
    }
}


class StaticPagesURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_urls_avalible(self):
        """Проверка доступности адресов
        /about/author
        /about/tech.
        """
        for url, expected_value in TESTS_DATA["status_code"].items():
            with self.subTest(url=url):
                self.assertEqual(
                    self.guest_client.get(url).status_code,
                    expected_value
                )

    def test_about_template_avalible(self):
        """Проверка шаблонов для адресов
        /about/author
        /about/tech.
        """
        for url, expected_value in TESTS_DATA["templates"].items():
            with self.subTest(url=url):
                self.assertTemplateUsed(
                    self.guest_client.get(url),
                    expected_value
                )
