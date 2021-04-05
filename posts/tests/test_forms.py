import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Group, Post, Comment
from posts.tests.test_follow import PostPagesTests

User = get_user_model()


class TaskCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаем временную папку для медиа-файлов;
        # на момент теста медиа папка будет перопределена
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

        # Создаем запись в базе данных для проверки сушествующего slug
        cls.group = Group.objects.create(
            title='Название сообщества',
            slug='test-group',
            description='Описание'
        )
        cls.user = get_user_model().objects.create(username='RuslanS')
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.user,
            group=cls.group,
        )
        # Создаем форму, если нужна проверка атрибутов
        cls.form = PostForm()
        cls.authorized_client = Client()

    @classmethod
    def tearDownClass(cls):

        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем авторизованый клиент
        self.user = User.objects.create_user(username='RuslanSitnov')
        self.authorized_client.force_login(self.user)

    def test_create_task(self):
        """Валидная форма создает запись"""
        # Подсчитаем количество записей
        tasks_count = Post.objects.count()

        form_data = {
            'text': 'Тестовый текст',
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )

        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Post.objects.count(), tasks_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый текст'
            ).exists()
        )

    def test_check_authorized_user_can_commens_post(self):
        """ Авторизованный клиент может оставлять комментарии """
        Comment.objects.create(text='Тестовый камментарий',
                               author=self.user, post=self.post)
        response = TaskCreateFormTests.authorized_client.get(
            reverse(
                'post', kwargs={'username': self.user.username,
                                'post_id': self.post.id}
            )
        )
        comment = response.context['comments'][0].author
        self.assertEqual(comment, self.user)
