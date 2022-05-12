import shutil
import tempfile
from django.core.files.uploadedfile import SimpleUploadedFile
from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Follow, Group, Post

from .data import URL_TEMPLATES

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()

PUBLIC_URLS = [
    reverse("posts:index"),
    reverse("posts:group_list", kwargs={"slug": "slug"}),
    reverse("posts:profile", kwargs={"username": "auth"})
]
PRIVAT_URLS = [
    reverse("posts:post_create"),
    reverse("posts:post_edit", kwargs={"post_id": 1})
]


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.user_two = User.objects.create_user(username='auth_2')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='slug',
            description='Тестовое описание',
        )
        cls.group_two = Group.objects.create(
            title='Тестовая группа два',
            slug='slug_2',
            description='Тестовое описание два',
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост Тестовый пост',
            group=cls.group,
            image=cls.uploaded
        )
        cls.follow = Follow.objects.create(
            user=cls.user,
            author=cls.user_two
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostViewTests.user)

    def post_test(self, post):
        """Функция теста поста"""
        field_post = {
            post.author: PostViewTests.post.author,
            post.text: "Тестовый пост Тестовый пост",
            post.pub_date: PostViewTests.post.pub_date,
            post.group: PostViewTests.post.group,
            post.image: PostViewTests.post.image
        }
        for field, expected_value in field_post.items():
            with self.subTest(field=field):
                self.assertEqual(field, expected_value)

    def test_post_in(self):
        """Проверка что новый пост появляется
        на страницах:
        "posts:index"
        "posts:group_list"
        "posts:profile".
        """
        for url in PUBLIC_URLS:
            response = self.authorized_client.get(url)
            with self.subTest(url=url):
                self.assertIn(PostViewTests.post, response.context["page_obj"])

    def test_post_not_in(self):
        """Проверка что пост не появляется
        на странице не своей группы
        и не в своём профиле.
        """
        field_address = [
            reverse("posts:group_list", kwargs={"slug": "slug_2"}),
            reverse("posts:profile", kwargs={"username": "auth_2"})
        ]
        for url in field_address:
            response = self.authorized_client.get(url)
            with self.subTest(url=url):
                self.assertNotIn(
                    PostViewTests.post,
                    response.context["page_obj"]
                )

    def test_post_views_template(self):
        """URL-адрес использует корректный шаблон."""
        for url, expected_value in URL_TEMPLATES.items():
            with self.subTest(url=url):
                self.assertTemplateUsed(
                    self.authorized_client.get(url),
                    expected_value
                )

    def test_post_form_correct_context(self):
        """Шаблоны
        create_post
        post_edit
        сформированы с правильным контекстом.
        """
        for url in PRIVAT_URLS:
            response = self.authorized_client.get(url)
            form_fields = {
                "text": forms.fields.CharField,
                "group": forms.fields.ChoiceField
            }
            for field, expected_value in form_fields.items():
                with self.subTest(field=field):
                    self.assertIsInstance(
                        response.context.get("form").fields.get(field),
                        expected_value
                    )

    def test_post_detail_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse("posts:post_detail", kwargs={"post_id": 1}))
        part = response.context.get("post")
        attr_post = {
            part.pub_date: PostViewTests.post.pub_date,
            part.group: PostViewTests.post.group,
            part.author: PostViewTests.post.author,
            part.text: PostViewTests.post.text,
            part.image: PostViewTests.post.image
        }
        for field, expected_value in attr_post.items():
            with self.subTest(field=field):
                self.assertEqual(field, expected_value)

    def test_post_list_index_correct_context(self):
        """Шаблон index формирован с правильным контекстом."""
        response = self.authorized_client.get(reverse("posts:index"))
        post = response.context["page_obj"][0]
        self.post_test(post)

    def test_post_list_group_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse("posts:group_list", kwargs={"slug": "slug"})
        )
        post = response.context["page_obj"][0]
        self.post_test(post)
        self.assertIn(
            PostViewTests.group.id,
            response.context
        )

    def test_post_list_profile_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse("posts:profile", kwargs={"username": "auth"})
        )
        post = response.context["page_obj"][0]
        self.post_test(post)
        self.assertIn(
            PostViewTests.user.id,
            response.context
        )

    def test_post_follow_in(self):
        """Проверка что новый пост пользователя появляется
        в ленте тех, кто на него подписан.
        """
        self.authorized_client.force_login(PostViewTests.user_two)
        Follow.objects.create(
            user=PostViewTests.user_two,
            author=PostViewTests.user
        )
        response = self.authorized_client.get(reverse("posts:follow_index"))
        self.assertIn(PostViewTests.post, response.context["page_obj"])

    def test_post_not_follow_not_in(self):
        """Проверка что новый пост пользователя не появляется
        в ленте тех, кто на него не подписан.
        """
        response = self.authorized_client.get(reverse("posts:follow_index"))
        self.assertNotIn(PostViewTests.post, response.context["page_obj"])

    def test_auth_client_can_subscribe(self):
        """Проверка авторизованный пользователь может
        подписываться на других авторов.
        """
        a = Follow.objects.count()
        print(a)
        self.authorized_client.get(reverse(
            "posts:profile_follow",
            kwargs={"username": PostViewTests.user_two}
        ))
        a = Follow.objects.count()
        print(a)
        self.assertTrue(
            Follow.objects.filter(
                user=PostViewTests.user,
                author=PostViewTests.user_two
            ).exists()
        )

    def test_auth_client_can_unsubscribe(self):
        """Проверка авторизованный пользователь может
        отписываться от других авторов.
        """
        a = Follow.objects.count()
        print(a)
        self.authorized_client.get(reverse(
            "posts:profile_unfollow",
            kwargs={"username": PostViewTests.user_two}
        ))
        a = Follow.objects.count()
        print(a)
        self.assertFalse(
            Follow.objects.filter(
                user=PostViewTests.user,
                author=PostViewTests.user_two
            ).exists()
        )

    def test_can_not_subscribe_yourself(self):
        """Проверка пользователь не может подписаться
        сам на себя.
        """
        self.authorized_client.get(reverse(
            "posts:profile_follow",
            kwargs={"username": PostViewTests.user}
        ))
        self.assertFalse(
            Follow.objects.filter(
                user=PostViewTests.user,
                author=PostViewTests.user
            ).exists()
        )

    def test_can_not_subscribe_twice(self):
        """Проверка пользователь не может подписаться
        дважды на одного пользователя.
        """
        follow_count = Follow.objects.count()
        self.authorized_client.get(reverse(
            "posts:profile_follow",
            kwargs={"username": PostViewTests.user_two}
        ))
        self.assertEqual(
            follow_count,
            Follow.objects.count()
        )


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='slug',
            description='Тестовое описание',
        )
        posts = [Post(
            author=cls.user,
            text='Тестовый пост' + str(i),
            group=cls.group
        ) for i in range(settings.LIMIT_POSTS + settings.SECOND_PAGE)
        ]
        Post.objects.bulk_create(posts)

    def setUp(self):
        self.guest_client = Client()
        self.page_count = {
            "1": settings.LIMIT_POSTS,
            "2": settings.SECOND_PAGE
        }

    def test_paginator_page_contains(self):
        """Проверка пажинатора, должен делить входящий
        список постов на пейджи с ожидаемым количеством
        в каждом.
        """
        for url in PUBLIC_URLS:
            for page, value in self.page_count.items():
                response = self.guest_client.get(url, {"page": page})
                with self.subTest(url=url):
                    self.assertEqual(
                        len(response.context["page_obj"]),
                        value
                    )


class CashViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовый пост",
            group=cls.group
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(CashViewTests.user)

    def test_cash(self):
        """Тест работоспособности кеша"""
        response = self.authorized_client.get(reverse("posts:index"))
        CashViewTests.post.delete()
        response_1 = self.authorized_client.get(reverse("posts:index"))
        self.assertEqual(
            response.content,
            response_1.content
        )
