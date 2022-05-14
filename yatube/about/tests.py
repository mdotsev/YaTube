from django.test import Client, TestCase


class AboutPagesTests(TestCase):

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()

    def test_about_urls_uses_correct_template(self):
        """URL-адрес about использует соответствующий шаблон."""
        templates_url_names = {
            '/about/tech/': 'about/tech.html',
            '/about/author/': 'about/author.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)
