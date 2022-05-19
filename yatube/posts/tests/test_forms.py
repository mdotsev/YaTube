from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Comment, Post

from .presets import TestCasePresets

User = get_user_model()


class PostCreateFormTests(TestCasePresets):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.form = PostForm()

    def test_create_post(self):
        """Валидная форма создает запись в Post."""

        text = 'Я создал пост'

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        posts_count = Post.objects.count()

        form_data = {
            'text': text,
            'group': self.group.pk,
            'image': uploaded,
        }
        # Отправляем POST-запрос
        response = self.author_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.author}))
        # Проверяем, увеличилось ли количество постов
        self.assertEqual(Post.objects.count(), posts_count + 1,
                         ('Количество постов не увеличилось'))

    def test_edit_post(self):
        """Валидная форма изменяет запись."""

        text = 'Пост успешно отредактирован'

        edit_data = {
            'text': text,
            'group': self.group.pk
        }
        self.author_client.post(
            reverse(
                'posts:post_edit', kwargs={'post_id': self.post.id}
            ),
            data=edit_data,
            follow=True
        )

        self.assertTrue(
            Post.objects.filter(
                group=self.group,
                text=text,
            ).exists()
        )


class CommentCreateFormTests(TestCasePresets):

    def test_create_comment(self):
        """
        После успешной отправки комментария создается запись в Comment
        """

        text = 'Клевая статья, чел'
        form_data = {
            'text': text,
        }
        self.user_client.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': self.post.id}
            ),
            data=form_data,
            follow=True
        )

        self.assertTrue(
            Comment.objects.filter(
                post_id=self.post.id,
                text=text,
            ).exists()
        )
