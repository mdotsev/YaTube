from django.conf import settings
from django import forms
from django.contrib.auth import get_user_model
from django.urls import reverse


from posts.models import Post, Group, Follow
from .presets import TestCasePresets

import time

User = get_user_model()


class PostsPagesTests(TestCasePresets):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.posts = []
        cls.groups = []

        # посты для паджинатора
        for i in range(15):
            post = Post.objects.create(
                text='Post ' + str(i),
                author=cls.author,
                group=cls.group
            )
            cls.posts.append(post)
            time.sleep(0.1)

            group = Group.objects.create(
                title='Group ' + str(i),
                slug='slug' + str(i),
                description=i
            )
            cls.groups.append(group)

        cls.post = Post.objects.create(
            text='Какой-то текст',
            author=cls.author,
            group=cls.group,
        )

    def setUp(self):
        super().setUp()
        self.pages = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.author})
        ]

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""

        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}): 'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': self.author}): 'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}):
            'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}):
            'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }

        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.author_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_with_page_obj_context(self):
        """Шаблоны с паджинатором сформированы с правильным контекстом."""

        contexts = {
            reverse('posts:index'): [None],
            reverse('posts:group_list', kwargs={'slug': self.group.slug}):
            ['group', self.group],
            reverse('posts:profile', kwargs={'username': self.author}):
            ['author', self.author],
        }
        for reverse_name, context in contexts.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.author_client.get(reverse_name)
                post = response.context['page_obj'][0]
                self.assertEqual(post.image, self.post.image)
                self.assertEqual(
                    post,
                    self.post,
                    'post передается неверный'
                )
                if context[0] is not None:
                    self.assertEqual(
                        response.context[context[0]], context[1], (
                            f'{context[0]} передается неверный'
                        )
                    )

    def test_pages_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.author_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id})
        )
        self.assertEqual(
            response.context['post'], self.post, ('post передается неверный')
        )

    def test_forms_pages_context(self):
        """Проверка контекста страниц с формами"""

        names = [
            self.author_client.get(reverse('posts:post_create')),
            self.author_client.get(reverse('posts:post_edit',
                                           kwargs={'post_id': self.post.id}))
        ]

        for response in names:
            form_fields = {
                'text': forms.fields.CharField,
                'group': forms.fields.ChoiceField
            }

            for value, expected in form_fields.items():
                with self.subTest(value=value):
                    form_field = response.context.get('form').fields.get(value)
                    self.assertIsInstance(form_field, expected)

    def test_pages_paginator(self):
        """Проверка паджинатора для всех страниц"""

        for page in self.pages:
            response = self.guest_client.get(page)
            self.assertEqual(
                len(response.context['page_obj']), settings.POSTS_AMOUNT,
                'На первой странице количество объекотов != заданному'
            )

            response = self.guest_client.get(page + '?page=2')
            self.assertEqual(
                len(response.context['page_obj']),
                Post.objects.all().count() - settings.POSTS_AMOUNT,
                'На второй странице количество объекотов != заданному'
            )

    def test_post_exists_everywhere(self):
        """Проверка наличия нового поста на всех страницах"""

        for page in self.pages:
            response = self.author_client.get(page)
            self.assertIn(self.post, response.context['page_obj'])

    def test_post_belongs_to_group(self):
        """Пост есть только на странице своей группы"""

        for group in self.groups:
            response = self.author_client.get(
                reverse('posts:group_list', kwargs={'slug': group.slug})
            )
            self.assertNotIn(self.post, response.context['page_obj'])

    
    
    
class FollowingsTests(TestCasePresets):
    
    def test_following(self):
        """
        Авторизованный пользователь может подписываться 
        на других пользователей и удалять их из подписок
        """
        self.user_client.get(reverse(
            'posts:profile_follow', 
            kwargs={'username': self.author}
        ))
        self.assertTrue(
            Follow.objects.filter(
                user=self.user,
                author=self.author
            ).exists(),
            'Подписка не удалась'
        )

        self.user_client.get(reverse(
            'posts:profile_unfollow', 
            kwargs={'username': self.author}
        ))
        self.assertFalse(
            Follow.objects.filter(
                user=self.user,
                author=self.author
            ).exists(),
            'Отписка не удалась'
        )

    def test_index_following(self):
        """
        Новая запись пользователя появляется в ленте тех, кто на 
        него подписан и не появляется в ленте тех, кто не подписан
        """
        self.user_client.get(reverse(
            'posts:profile_follow', 
            kwargs={'username': self.author}
        ))

        response= self.user_client.get(
            reverse('posts:follow_index')
        )

        self.assertIn(self.post, response.context['page_obj'])

        response=self.guest_client.get(reverse(
            'posts:follow_index'
        ))

        self.assertIsNone(
            response.context,
            'Не должно быть записей'
        )