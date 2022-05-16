import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings

from posts.models import Comment, Follow, Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TestCasePresets(TestCase):
    """
    Заранее подготовленные тестовые объекты
    (исключают дублирование в каждом файле)
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.img = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.guest = User.objects.create_user(username='guest')
        cls.user = User.objects.create_user(username='user')
        cls.author = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='title',
            slug='slug',
            description='description'
        )
        cls.post = Post.objects.create(
            text=(
                '«Печален ты; признайся, что с тобой».'
                '— Люблю, мой друг! — «Но кто ж тебя пленила?»'
                '— Она.— «Да кто ж? Глидера ль, Хлоя, Лила?»'
                '— О, нет! — «Кому ж ты жертвуешь душой?»'
                '— Ах! ей! — «Ты скромен, друг сердечный!'
                'Но почему ж ты столько огорчен?'
                'И кто виной? Супруг, отец, конечно…»'
                '— Не то, мой друг! — «Но что ж!» — Я ей не он.'
            ),
            author=cls.author,
            group=cls.group,
            image=cls.img
        )
        cls.comment = Comment.objects.create(
            text=(
                'Вот это я понимаю пост'
            ),
            author=cls.user,
            post=cls.post
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем авторизованный клиент
        self.user_client = Client()
        # Авторизуем пользователя
        self.user_client.force_login(self.user)
        # Создаем клиент автора
        self.author_client = Client()
        # Авторизуем атвора
        self.author_client.force_login(self.author)

        self.follow = Follow.objects.create(
            user=self.user,
            author=self.author,
        )
