from django.core.cache import cache
from django.urls import reverse

from .presets import TestCasePresets
from posts.models import Post, Group, Follow


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
