from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from http import HTTPStatus
from ..models import Post, Group
from django.core.cache import cache


User = get_user_model()


class PostURLTests(TestCase):
    def setUp(self):
        cache.clear()
        self.guest_client = Client()

        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        self.author = User.objects.create_user(username='AuthorName')
        self.author_client = Client()
        self.author_client.force_login(self.author)

        self.post = Post.objects.create(
            text='Тестовый текст',
            author=self.author,
        )

        self.group = Group.objects.create(
            title='Test group',
            slug='test-group-urls',
            description='Group for testing urls',
        )

    def test_unexisting_page(self):
        """Не найдено страницы с несуществующим в проекте URL-адресом"""
        address = '/unexisting-page/'

        response = self.guest_client.get(address)
        self.assertEqual(
            response.status_code,
            HTTPStatus.NOT_FOUND,
            ('Найдена несуществующая страница для '
             'неавторизованного пользователя')
        )

        response = self.authorized_client.get(address)
        self.assertEqual(
            response.status_code,
            HTTPStatus.NOT_FOUND,
            ('Найдена несуществующая страница для '
             'авторизованного пользователя')
        )

        response = self.author_client.get(address)
        self.assertEqual(
            response.status_code,
            HTTPStatus.NOT_FOUND,
            ('Найдена несуществующая страница для '
             'авторизованного пользователя(автора поста)')
        )

    def test_urls_posts_edit(self):
        """URL-адрес /posts/<int>/edit/ использует соответствующий шаблон."""
        post_id = self.post.pk
        address = reverse('posts:post_edit', kwargs={'post_id': post_id})

        response = self.guest_client.get(address)
        self.assertRedirects(
            response,
            (
                f'{reverse("users:login")}'
                '?next='
                f'{reverse("posts:post_edit", kwargs={"post_id": post_id})}'
            ),
            msg_prefix=(
                'URL-адрес /posts/<int>/edit/ не перенаправляет '
                'неавторизованного пользователя'
            )
        )

        response = self.authorized_client.get(address)
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': post_id}),
            msg_prefix=(
                'URL-адрес /posts/<int>/edit/ не перенаправляет '
                'авторизованного пользователя не являющегося создателем поста'
            )
        )

        response = self.author_client.get(address)
        self.assertTemplateUsed(
            response,
            'posts/post_create.html',
            'URL-адрес /posts/<int>/edit/ использует некорректный шаблон'
        )
        self.assertEqual(
            response.status_code,
            HTTPStatus.OK,
            ('Страница с URL-адресом /posts/<int>/edit/ '
             'не найдена для автора поста')
        )

    def test_urls_posts_create(self):
        """URL-адрес /create/ использует соответствующий шаблон."""
        address = reverse('posts:post_create')

        response = self.guest_client.get(address)
        self.assertRedirects(
            response,
            (
                f'{reverse("users:login")}'
                '?next='
                f'{reverse("posts:post_create")}'
            ),
            msg_prefix=(
                'URL-адрес /create/ не перенаправляет '
                'неавторизованного пользователя'
            )
        )

        response = self.authorized_client.get(address)
        self.assertTemplateUsed(
            response,
            'posts/post_create.html',
            ('URL-адрес /create/ использует некорректный '
             'шаблон для авторизованного пользователя')
        )
        self.assertEqual(
            response.status_code,
            HTTPStatus.OK,
            ('Страница с URL-адресом /create/ '
             'не найдена для авторизованного пользователя')
        )

        response = self.author_client.get(address)
        self.assertTemplateUsed(
            response,
            'posts/post_create.html',
            ('URL-адрес /create/ использует некорректный '
             'шаблон для авторизованного пользователя (автора поста)')
        )
        self.assertEqual(
            response.status_code,
            HTTPStatus.OK,
            ('Страница с URL-адресом /create/ '
             'не найдена для авторизованного пользователя (автора поста)')
        )

    def test_index_uses_correct_template(self):
        """URL-адрес / использует соответствующий шаблон."""
        cache.clear()
        response = self.guest_client.get(reverse('posts:index'))
        self.assertTemplateUsed(
            response,
            'posts/index.html',
            ('URL-адрес / использует некорректный '
             'шаблон для неавторизованного пользователя')
        )
        self.assertEqual(
            response.status_code,
            HTTPStatus.OK,
            ('Страница с URL-адресом не найдена для неавторизованного '
             'пользователя')
        )

    def test_urls_uses_correct_template(self):
        cache.clear()
        """URL-адрес /, /group/<slug>/, /profile/<slug>/, /posts/<int>/
        использует соответствующий шаблон."""
        slug = self.group.slug
        username = self.user.username
        post_id = self.post.pk
        templates_url_names = {
            reverse(
                'posts:group_list',
                kwargs={'slug': slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': username}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': post_id}
            ): 'posts/post_detail.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(adress=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(
                    response,
                    template,
                    ('URL-адрес использует некорректный '
                     'шаблон для неавторизованного пользователя')
                )
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK,
                    ('Страница с URL-адресом не найдена для неавторизованного '
                     'пользователя')
                )

                response = self.authorized_client.get(address)
                self.assertTemplateUsed(
                    response,
                    template,
                    ('URL-адрес использует некорректный '
                     'шаблон для авторизованного пользователя')
                )
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK,
                    ('Страница с URL-адресом не найдена для авторизованного '
                     'пользователя')
                )

                response = self.author_client.get(address)
                self.assertTemplateUsed(
                    response,
                    template,
                    ('URL-адрес использует некорректный '
                     'шаблон для авторизованного пользователя (автора поста)')
                )
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK,
                    ('Страница с URL-адресом не найдена для авторизованного '
                     'пользователя (автора поста)')
                )
