from django.test import Client, TestCase


class ErrorPagesTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_404_page_uses_correct_template(self):
        """URL-адрес использует шаблон posts/index.html."""
        response = self.guest_client.get('/unexisting-page/')
        self.assertTemplateUsed(response, 'core/404.html')
