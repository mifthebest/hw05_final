from django.contrib.auth import get_user_model
from django.test import TestCase
from ..models import Group, Post


User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Post for testing model',
        )

    def test_post_model_have_correct_object_name(self):
        """У модели Post корректно работает __str__."""
        post_str = str(PostModelTest.post)
        post_text = PostModelTest.post.text[:15]

        self.assertEqual(
            post_str,
            post_text,
            'Текстовое представление модели Post не соответствует ожидаемому'
        )

    def test_post_model_verbose_names(self):
        """У модели Post корректно отображаются названия полей."""
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name,
                    expected_value,
                    'verbose_name модели Post не соответствует ожидаемому'
                )

    def test_post_model_help_text(self):
        """У модели Post корректно отображаются вспомогательные сообщения."""
        post = PostModelTest.post
        field_help = {
            'text': 'Введите текст поста',
            'group': 'Выберите группу',
        }
        for field, expected_value in field_help.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text,
                    expected_value,
                    'help_text модели Post не соответствует ожидаемому'
                )


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )

    def test_group_model_have_correct_object_name(self):
        """У модели Group корректно работает __str__."""
        group_str = str(GroupModelTest.group)
        group_title = GroupModelTest.group.title
        self.assertEqual(
            group_str,
            group_title,
            'Текстовое представление модели Group не соответствует ожидаемому'
        )

    def test_group_model_verbose_names(self):
        """У модели Group корректно отображаются названия полей."""
        group = GroupModelTest.group
        field_verboses = {
            'title': 'Название группы',
            'slug': 'Относительный адрес группы',
            'description': 'Описание',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).verbose_name,
                    expected_value,
                    'verbose_name модели Group не соответствует ожидаемому'
                )
