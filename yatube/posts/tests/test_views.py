import tempfile
import shutil

from django.contrib.auth import get_user_model
from django import forms
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from ..models import Post, Group, Comment, Follow
from django.core.cache import cache


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        cache.clear()
        self.author_user = User.objects.create(username='AuthorUser')
        self.user = User.objects.create_user(username='StasBasov')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        self.group = Group.objects.create(
            title='Test group',
            slug='test-group-views',
            description='Group for testing views',
        )

        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=(
                b'\x47\x49\x46\x38\x39\x61\x02\x00'
                b'\x01\x00\x80\x00\x00\x00\x00\x00'
                b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
                b'\x00\x00\x00\x2C\x00\x00\x00\x00'
                b'\x02\x00\x01\x00\x00\x02\x02\x0C'
                b'\x0A\x00\x3B'
            ),
            content_type='image/gif'
        )

        self.post = Post.objects.create(
            text='Тестовый текст',
            author=self.user,
            group=self.group,
            image=uploaded,
        )

    def is_post_exist(self, post):
        self.assertEqual(post.group, self.post.group)
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.image, self.post.image)

    def test_index_page_uses_correct_template(self):
        """URL-адрес использует шаблон posts/index.html."""
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertTemplateUsed(response, 'posts/index.html')

    def test_group_list_page_uses_correct_template(self):
        """URL-адрес использует шаблон posts/group_list.html."""
        slug = self.group.slug
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': slug})
        )
        self.assertTemplateUsed(response, 'posts/group_list.html')

    def test_profile_page_uses_correct_template(self):
        """URL-адрес использует шаблон posts/profile.html."""
        username = self.user.username
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': username})
        )
        self.assertTemplateUsed(response, 'posts/profile.html')

    def test_post_detail_page_uses_correct_template(self):
        """URL-адрес использует шаблон posts/post_detail.html."""
        post_id = self.post.pk
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': post_id})
        )
        self.assertTemplateUsed(response, 'posts/post_detail.html')

    def test_post_edit_page_uses_correct_template(self):
        """URL-адрес использует шаблон posts/post_create.html при
        редатировании существующего поста."""
        post_id = self.post.pk
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': post_id})
        )
        self.assertTemplateUsed(response, 'posts/post_create.html')

    def test_post_create_page_uses_correct_template(self):
        """URL-адрес использует шаблон posts/post_create.html
        при создании нового поста."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        self.assertTemplateUsed(response, 'posts/post_create.html')

    def test_pages_paginator(self):
        """Паджинатор отображается верно."""
        posts = list(
            Post(text=f'{i}', author=self.user, group=self.group)
            for i in range(13)
        )
        Post.objects.bulk_create(posts)
        slug = self.group.slug
        username = self.user.username
        templates_url_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list', kwargs={'slug': slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile', kwargs={'username': username}
            ): 'posts/profile.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(adress=address):
                response = self.authorized_client.get(address)
                self.assertEqual(len(response.context['page_obj']), 10)

                response = self.authorized_client.get(address + '?page=2')
                self.assertEqual(len(response.context['page_obj']), 4)

    def test_post_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = (self.authorized_client.get(reverse('posts:index')))
        self.is_post_exist(response.context['page_obj'][0])

    def test_post_group_list_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = (self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug})
        ))
        self.is_post_exist(response.context['page_obj'][0])
        self.assertEqual(self.group, response.context['group'])

    def test_post_profile_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = (self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.user.username})
        ))
        self.is_post_exist(response.context['page_obj'][0])
        self.assertEqual(self.user, response.context['author'])

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        new_comment = Comment.objects.create(
            text='Comment for testing post_detail',
            author=self.user,
            post=self.post,
        )
        response = (self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk})
        ))
        comment = response.context['comments'].last()
        self.assertEqual(new_comment.text, comment.text)
        self.assertEqual(new_comment.author, comment.author)
        self.assertEqual(new_comment.post, comment.post)
        self.is_post_exist(response.context['post'])

    def test_post_create_show_correct_context(self):
        """Шаблон post_create для создания поста
        сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_create')
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit для редактирования поста
        сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)
        self.is_post_exist(response.context['post'])
        self.assertTrue(response.context['is_edit'])

    def test_creating_post_show_other_group(self):
        """Созданыый пост не отображается в группах,
        для которых не был предназначен"""
        other_group = Group.objects.create(
            title='Test group',
            slug='other-test-group-views',
            description='Group for testing correct creating post',
        )
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': other_group.slug})
        )
        self.assertEqual(
            len(response.context['page_obj']),
            0
        )

    def test_authorized_client_can_follow(self):
        """Авторизованный пользователь может подписываться
        и отписываться от авторов"""
        response = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': self.author_user.username})
        )
        self.assertFalse(response.context['following'])

        self.authorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.author_user.username}
            )
        )
        response = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': self.author_user.username})
        )
        self.assertTrue(response.context['following'])

        self.authorized_client.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': self.author_user.username}
            )
        )
        response = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': self.author_user.username})
        )
        self.assertFalse(response.context['following'])

    def test_correct_show_new_post_in_follows(self):
        """Созданный пользователем пост отображается только в ленте тех,
        кто на него подписан"""
        Follow.objects.create(user=self.user, author=self.author_user)
        unfollower_user = User.objects.create(username='UnfollowUser')
        unfollower_client = Client()
        unfollower_client.force_login(unfollower_user)
        Post.objects.create(
            text='Post for testing following',
            author=self.author_user
        )
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertEqual(
            len(response.context['page_obj']),
            1,
        )
        response = unfollower_client.get(reverse('posts:follow_index'))
        self.assertEqual(
            len(response.context['page_obj']),
            0,
        )


class CacheTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_index_page_cache(self):
        """Тестирование кэша главной страницы"""
        post = Post.objects.create(
            text='Post for testing cache',
            author=User.objects.create_user(username='SomeName'),
        )
        response = (self.guest_client.get(reverse('posts:index')))
        response_content = response.content
        post.delete()
        response = (self.guest_client.get(reverse('posts:index')))
        self.assertEqual(
            response_content,
            response.content
        )
