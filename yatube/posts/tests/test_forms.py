import shutil
import tempfile
from xml.etree.ElementTree import Comment
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Comment, Group, Post

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="auth")
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostCreateFormTests.user)

    def test_post_create_form(self):
        """При отправке валидной формы со страницы создания поста
        reverse('posts:create_post')
        создаётся новая запись в базе данных.
        """
        post_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            "text": "Тестовый пост_1",
            "group": PostCreateFormTests.group.id,
            "image": uploaded
        }
        self.authorized_client.post(
            reverse("posts:post_create"),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый пост_1',
                group=PostCreateFormTests.post.group.id,
                image=PostCreateFormTests.post.image
            ).exists()
        )

    def test_post_edit_form(self):
        """При отправке валидной формы со страницы редактирования поста
        происходит изменение поста с post_id в базе данных.
        """
        post_count = Post.objects.count()
        form_data = {
            "text": "Изменённый тестовый пост",
            "group": PostCreateFormTests.group.id
        }
        self.authorized_client.post(
            reverse(
                "posts:post_edit",
                kwargs={"post_id": 1}
            ),
            data=form_data,
            follow=True
        )
        post = Post.objects.get(pk=1)
        self.assertEqual(
            (post.text, post.author, post.group.id),
            (form_data["text"], self.user, form_data["group"])
        )
        self.assertEqual(Post.objects.count(), post_count)

    def test_post_comment_in(self):
        """Тест пост создаётся."""
        comment_count = PostCreateFormTests.post.comments.count()
        form_data = {
            "text": "Первый коментарий"
        }
        self.authorized_client.post(
            reverse(
                "posts:add_comment",
                kwargs={"post_id": PostCreateFormTests.post.pk}
            ),
            data=form_data,
            follow=True
        )
        self.assertEqual(
            PostCreateFormTests.post.comments.count(),
            comment_count + 1
        )
        self.assertTrue(
            Comment.objects.filter(
                text="Первый коментарий",
                author=PostCreateFormTests.user,
                post=PostCreateFormTests.post
            )
        )
