from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from posts.models import Group

User = get_user_model()


class TaskURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        Group.objects.create(
            title='Название сообщества',
            slug='test-group',
            description='Описание'
        )
        cls.group = Group.objects.get(slug='test-group')

    def setUp(self):
        """Создаем неавторизованный клиент"""
        self.guest_client = Client()
        """Создаем авторизованый клиент"""
        self.user = User.objects.create_user(username='RuslanSitnov')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_home_url_exists_at_desired_location(self):
        """Страница / доступна любому пользователю."""
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_task_list_url_exists_at_desired_location(self):
        """Страница /new доступна авторизованному пользователю."""
        response = self.authorized_client.get('/new/')
        self.assertEqual(response.status_code, 200)

    def test_task_detail_url_exists_at_desired_location_authorized(self):
        """Страница /group/<slug>/ доступна авторизованному пользователю."""
        response = self.authorized_client.get('/group/test-group/')
        self.assertEqual(response.status_code, 200)

    def test_task_list_url_redirect_anonymous_on_admin_login(self):
        """Страница /new/ перенаправит анонимного пользователя
        на страницу логина.
        """
        response = self.guest_client.get('/new/', follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=/new/')

    def test_task_detail_url_redirect_anonymous_on_admin_login(self):
        """Страница /group/<slug>/ перенаправит анонимного пользователя
        на страницу логина.
        """
        response = self.guest_client.get('/new/', follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=/new/')

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            'index.html': '/',
            'group.html': '/group/test-group/',
            'new.html': '/new/',
        }
        for template, reverse_name in templates_url_names.items():
            with self.subTest():
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    """возвращает ли сервер код 404, если страница не найдена."""
    def test_urls_handler404(self):
        response = self.authorized_client.get('nonameerror')
        self.assertEqual(response.status_code, 404)
