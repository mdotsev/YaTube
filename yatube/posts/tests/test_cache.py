from django.core.cache import cache
from django.urls import reverse

from posts.models import Post

from .presets import TestCasePresets


class IndexCacheTests(TestCasePresets):

    def setUp(self):
        super().setUp()
        self.post_delete = Post.objects.create(
            text='Какой-то текст',
            author=self.author,
            group=self.group,
        )

    def test_index_page_cache(self):
        """Пост не пропадает со страницы, если не очистить кэш"""
        response = self.author_client.get(reverse('posts:index'))
        self.post_delete.delete()
        response_deleted = self.author_client.get(reverse('posts:index'))
        self.assertEqual(
            response.content,
            response_deleted.content,
            'При удалении пост пропал со страницы до очистки кэша'
        )

    def test_index_clear_cache(self):
        """Пост пропадает со страницы только после очистки кэша"""

        self.author_client.get(reverse('posts:index'))
        self.post_delete.delete()
        response_deleted = self.author_client.get(reverse('posts:index'))
        cache.clear()
        response_deleted_cache_cleared = self.author_client.get(
            reverse('posts:index')
        )

        self.assertNotEqual(
            response_deleted.content,
            response_deleted_cache_cleared.content,
            'При удалении пост не пропал со страницы после очистки кэша'
        )
