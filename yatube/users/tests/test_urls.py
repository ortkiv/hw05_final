from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()

TESTS_DATA = {
    "pub_url_status_code": {
        reverse("users:signup"): HTTPStatus.OK,
        reverse("users:login"): HTTPStatus.OK,
        reverse("users:logout"): HTTPStatus.OK,
        reverse("users:password_reset_form"): HTTPStatus.OK,
        reverse("users:password_reset_done"): HTTPStatus.OK,
        reverse("users:password_reset_complete"): HTTPStatus.OK,
        reverse(
            "users:password_reset_confirm",
            kwargs={"uidb64": "NA", "token": "token"}): HTTPStatus.OK
    },
    "priv_url_status_code": {
        reverse("users:password_change_form"): HTTPStatus.OK,
        reverse("users:password_change_done"): HTTPStatus.OK,
    },
    "pub_url_redirect": {
        reverse("users:password_change_form"):
        "/auth/login/?next=/auth/password_change/",
        reverse("users:password_change_done"):
        "/auth/login/?next=/auth/password_change/done/",
    }
}


class UserURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username="auth")
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_user_urls_guests(self):
        """Проверка доступности адресов
        для неавторизованных юзеров
        "/auth/signup/"
        "/auth/login/"
        "/auth/password_reset/"
        "/auth/password_reset/done/"
        "/auth/reset/done/"
        "/auth/reset/<uidb64>/<token>/".
        """
        for url, expected_value in TESTS_DATA["pub_url_status_code"].items():
            with self.subTest(url=url):
                self.assertEqual(
                    self.guest_client.get(url).status_code,
                    expected_value
                )

    def test_user_url_guests_redirect(self):
        """Страницы по адресам
        "/auth/password_change/"
        "/auth/password_change/done/"
        перенаправят анонимного
        пользователя на страницу логина.
        """
        for url, expected_value in TESTS_DATA["pub_url_redirect"].items():
            with self.subTest(url=url):
                self.assertRedirects(
                    self.guest_client.get(url, follow=True),
                    expected_value
                )

    def test_user_urls_authorized(self):
        """Проверка доступности адресов
        для авторизованных юзеров
        "/auth/password_change/"
        "/auth/password_change/done/".
        """
        for url, expected_value in TESTS_DATA["priv_url_status_code"].items():
            with self.subTest(url=url):
                self.assertEqual(
                    self.authorized_client.get(url).status_code,
                    expected_value
                )
