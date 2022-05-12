from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост Тестовый пост',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        field_strings = {
            PostModelTest.post.text[:15]: str(PostModelTest.post),
            PostModelTest.group.title: str(PostModelTest.group)
        }
        for string, expected_value in field_strings.items():
            with self.subTest(string=string):
                self.assertEqual(
                    string,
                    expected_value
                )

    def test_verbose_name(self):
        """Проверяем, что verbose_name в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        group = PostModelTest.group
        verbose_name = {
            post: {
                "text": "Текст поста",
                "pub_date": "Дата публикации",
                "author": "Автор"
            },
            group: {
                "title": "Название",
                "slug": "URL",
                "description": "Описание"
            }
        }
        for model, value in verbose_name.items():
            for m_key, m_value in value.items():
                with self.subTest(model=type(model).__name__, m_key=m_key):
                    self.assertEqual(
                        model._meta.get_field(m_key).verbose_name,
                        m_value
                    )

    def test_help_text(self):
        """Проверяем, что help_text в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        group = PostModelTest.group
        help_texts = {
            post: {
                "text": "Введите текст поста",
                "group": "Группа, к которой будет относиться пост"
            },
            group: {
                "title": "Введите название группы",
                "slug": ("Укажите адрес для страницы группы. "
                         "Используйте только латиницу, цифры, "
                         "дефисы и знаки подчёркивания"),
                "description": "Краткое описание"
            }
        }
        for model, value in help_texts.items():
            for m_key, m_value in value.items():
                with self.subTest(model=type(model).__name__, m_key=m_key):
                    self.assertEqual(
                        model._meta.get_field(m_key).help_text,
                        m_value
                    )
