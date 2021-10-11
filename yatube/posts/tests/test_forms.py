import tempfile
import shutil

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from ..models import Post, Comment


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.user = User.objects.create(username='EmptyName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )

    def test_creating_post_by_form(self):
        """Форма корректно создаёт новую запись в БД."""
        posts_count = Post.objects.count()
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=self.small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Post for testing forms (post_create)',
            'image': uploaded,
        }
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        new_post = Post.objects.last()

        self.assertEqual(
            posts_count + 1,
            Post.objects.count(),
            'При создании поста количество постов в БД не изменилось'
        )
        self.assertEqual(
            new_post.text,
            form_data['text'],
            'При создании поста поле text не соответсвует ожидаемому'
        )
        self.assertIsNone(
            new_post.group,
            'При создании поста поле group не соответсвует ожидаемому'
        )
        self.assertEqual(
            new_post.author,
            self.user,
            'При создании поста поле author не соответсвует ожидаемому'
        )
        self.assertEqual(
            str(new_post.image),
            'posts/small.gif',
            'При создании поста поле image не соответсвует ожидаемому'
        )

    def test_editing_post_by_form(self):
        """Форма корректно редактирует запись в БД."""
        post = Post.objects.create(
            text='Post for testing forms (post_edit)',
            author=self.user,
        )
        uploaded = SimpleUploadedFile(
            name='second_small.gif',
            content=self.small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Editing',
            'image': uploaded,
        }
        self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post.pk}),
            data=form_data,
            follow=True
        )
        updating_post = Post.objects.get(pk=post.pk)

        self.assertEqual(
            updating_post.text,
            form_data['text'],
            'При обновлении поста поле text не соответсвует ожидаемому'
        )
        self.assertIsNone(
            updating_post.group,
            'При обновлении поста поле group не соответсвует ожидаемому'
        )
        self.assertEqual(
            updating_post.author,
            self.user,
            'При обновлении поста поле author не соответсвует ожидаемому'
        )
        self.assertEqual(
            str(updating_post.image),
            'posts/second_small.gif',
            'При обновлении поста поле image не соответсвует ожидаемому'
        )


class CommentFormTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

        self.user = User.objects.create(username='NoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        self.post = Post.objects.create(
            text='Post for testing CommentForm',
            author=self.user,
        )

    def test_creating_comment_by_authorized_client(self):
        """Авторизованный пользователь может оставлять комментарии"""
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'Testing comment',
        }
        self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )
        new_comment = Comment.objects.last()

        self.assertEqual(
            comments_count + 1,
            Comment.objects.count(),
            ('При создании комментария количество '
             'комментариев в БД не изменилось')
        )
        self.assertEqual(
            new_comment.text,
            form_data['text'],
            'При создании клмментария поле text не соответсвует ожидаемому'
        )
        self.assertEqual(
            new_comment.author,
            self.user,
            'При создании комментария поле author не соответсвует ожидаемому'
        )
        self.assertEqual(
            new_comment.post,
            self.post,
            'При создании комментария поле post не соответсвует ожидаемому'
        )

    def test_creating_comment_by_guest_client(self):
        """Неавторизованный пользователь не может оставлять комментарии"""
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'New testing comment',
        }
        self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )
        self.assertEqual(
            comments_count,
            Comment.objects.count(),
            'Комментарий может оставлять неавторизованный пользователь'
        )
