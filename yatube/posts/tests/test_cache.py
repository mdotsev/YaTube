from django.core.cache import cache
from django.urls import reverse

from posts.models import Post

from .presets import TestCasePresets


class IndexCacheTests(TestCasePresets):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post_delete = Post.objects.create(
            text='Какой-то текст',
            author=cls.author,
            group=cls.group,
        )

    def test_index_page_cache(self):
        """Пост пропадает со страницы только после очистки кэша"""
        response = self.author_client.get(reverse('posts:index'))
        self.post_delete.delete()
        response_deleted = self.author_client.get(reverse('posts:index'))
        self.assertEqual(
            response.content,
            response_deleted.content,
            'При удалении пост пропал со страницы до очистки кэша'
        )
        cache.clear()
        response_deleted_cache_cleared = self.author_client.get(
            reverse('posts:index')
        )
        self.assertNotEqual(
            response.content,
            response_deleted_cache_cleared.content,
            'При удалении пост не пропал со страницы после очистки кэша'
        )
