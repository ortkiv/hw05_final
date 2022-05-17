from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

from .data import URL_TEMPLATES

User = get_user_model()

FIELD_PAGES = {
    "pub_url_status_code": {
        reverse("posts:index"): HTTPStatus.OK,
        reverse(
            "posts:group_list",
            kwargs={"slug": "slug"}): HTTPStatus.OK,
        reverse(
            "posts:profile",
            kwargs={"username": "auth"}): HTTPStatus.OK,
        reverse(
            "posts:post_detail",
            kwargs={"post_id": 1}): HTTPStatus.OK,
        "/unexisting_page/": HTTPStatus.NOT_FOUND
    },
    "pub_url_redirect": {
        reverse("posts:post_create"): "/auth/login/?next=/create/",
        reverse(
            "posts:post_edit",
            kwargs={"post_id": 1}): "/auth/login/?next=/posts/1/edit/",
        reverse(
            "posts:add_comment",
            kwargs={"post_id": 1}): "/auth/login/?next=/posts/1/comment/",
        reverse("posts:follow_index"): "/auth/login/?next=/follow/",
        reverse(
            "posts:profile_follow",
            kwargs={"username": "auth"}
        ): "/auth/login/?next=/profile/auth/follow/",
        reverse(
            "posts:profile_unfollow",
            kwargs={"username": "auth"}
        ): "/auth/login/?next=/profile/auth/unfollow/"
    },
    "priv_url_status_code": {
        reverse("posts:post_create"): HTTPStatus.OK,
        reverse("posts:post_edit", kwargs={"post_id": 1}): HTTPStatus.OK,
        reverse("posts:follow_index"): HTTPStatus.OK
    }
}


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="auth")
        cls.user_two = User.objects.create_user(username="auth_two")
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост Тестовый пост',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client_two = Client()
        self.authorized_client.force_login(PostURLTests.user)
        self.authorized_client_two.force_login(PostURLTests.user_two)

    def test_post_urls_guests(self):
        """Проверка доступности адресов
        для неавторизованных юзеров
        "/"
        "/group/slug/"
        "/profile/auth/"
        "/posts/1/"
        "/unexisting_page/".
        """
        for url, expected_value in FIELD_PAGES["pub_url_status_code"].items():
            with self.subTest(url=url):
                self.assertEqual(
                    self.guest_client.get(url).status_code,
                    expected_value
                )

    def test_post_url_guests_redirect(self):
        """Страницы по адресам
        "/create/"
        "/posts/<int:post_id>/edit/"
        "posts/<int:post_id>/comment/"
        "follow/"
        "profile/<str:username>/follow/"
        "profile/<str:username>/unfollow/"
        перенаправят анонимного
        пользователя на страницу логина.
        """
        for url, expected_value in FIELD_PAGES["pub_url_redirect"].items():
            with self.subTest(url=url):
                self.assertRedirects(
                    self.guest_client.get(url, follow=True),
                    expected_value
                )

    def test_post_urls_authorized(self):
        """Проверка доступности адресов
        для авторизованных юзеров
        "/create/"
        "/posts/1/edit/"
        "/follow/".
        Для "...edit/" юзер должен быть
        автором редактируемого поста.
        """
        for url, expected_value in FIELD_PAGES["priv_url_status_code"].items():
            with self.subTest(url=url):
                self.assertEqual(
                    self.authorized_client.get(url).status_code,
                    expected_value
                )

    def test_post_urls_not_author_redirect(self):
        """Проверка редиректа авторизованного неавтора поста
        на страницу этого поста.
        """
        url = reverse("posts:post_edit", kwargs={"post_id": 1})
        self.assertRedirects(
            self.authorized_client_two.get(url, follow=True),
            reverse("posts:post_detail", kwargs={"post_id": 1})
        )

    def test_post_template_authorized(self):
        """Проверка шаблонов для адресов
        "/"
        "/group/slug/"
        "/profile/auth/"
        "/posts/1/"
        "/create/"
        "/posts/1/edit/"
        "/unexisting_page/"
        "/follow/".
        Для "...edit/" юзер должен быть
        автором редактируемого поста.
        """
        for url, expected_value in URL_TEMPLATES.items():
            with self.subTest(url=url):
                self.assertTemplateUsed(
                    self.authorized_client.get(url),
                    expected_value
                )
