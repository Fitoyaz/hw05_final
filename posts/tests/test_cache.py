
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Post, User, Group


class CacheTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Создаем неавторизованный клиент
        cls.guest_client = Client()
        # Создаем авторизованый клиент
        cls.user = User.objects.create_user(username='RuslanSitnov')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

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

    def test_index_page_cache(self):
        """Testing correct caching the index template"""
        response = self.authorized_client.get(reverse('index'))
        last_post = response.context['page'][0]
        post = Post.objects.create(
            text='Кэш пост',
            author=self.user,
        )
        response = self.authorized_client.get(reverse('index'))
        current_post = response.context['page'][0]
        self.assertNotEqual(last_post, current_post, 'Caching is not working.')
        cache.clear()
        response = self.authorized_client.get(reverse('index'))
        current_post = response.context['page'][0]
        self.assertEqual(current_post, post, 'Caching is not working.')
