from django.contrib.auth import get_user_model

from .presets import TestCasePresets

User = get_user_model()


class PostsURLTests(TestCasePresets):

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/slug/': 'posts/group_list.html',
            '/profile/user/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_guest_redirect(self):
        """
        Проверка прав доступа: перенаправление при запросе неавторизованного
        """
        urls = [
            f'/posts/{self.post.id}/edit/',
            '/create/'
        ]
        for url in urls:
            response = self.guest_client.get(url, follow=True)
            self.assertRedirects(
                response, (f'/auth/login/?next={url}'))

    def test_user_redirect(self):
        """
        Проверка прав доступа: перенаправление при запросе авторизованного
        """
        url = f'/posts/{self.post.id}/edit/'
        response = self.user_client.get(url, follow=True)

        self.assertRedirects(
            response, (f'/posts/{self.post.id}/'))

    def test_author_edit(self):
        """Проверка доступности редактирования поста для автора"""
        url = f'/posts/{self.post.id}/edit/'

        response = self.author_client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_unexisting_page(self):
        """Запрос к несуществующей странице должен выдать 404"""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, 404)
