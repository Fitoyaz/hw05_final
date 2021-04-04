import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post

User = get_user_model()


class ViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )

        uploaded = SimpleUploadedFile(
            name='very_small.gif',
            content=small_gif,
            content_type='image/gif'
        )

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
            image=uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        """ Удалаем временные папки"""
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Собираем в словарь пары "имя_html_шаблона: reverse(name)"
        templates_page_names = {
            'index.html': reverse('index'),
            'new.html': reverse('new_post'),
            'group.html': reverse('group', kwargs={'slug': 'test-group'}),
        }

        for template, reverse_name in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('index'))
        post_text_0 = response.context.get('page')[0]
        self.assertEqual(post_text_0, self.post)

    def test_group_page_show_correct_context(self):
        """Шаблон group сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('group', kwargs={'slug': self.group.slug}))

        group_context_1 = response.context.get('group').slug
        self.assertEqual(group_context_1, 'test-group')
        group_context_2 = response.context.get('posts')[0]
        self.assertEqual(group_context_2, self.post)

    def test_post_page_show_correct_context(self):
        """Шаблон post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('new_post'))
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertIsInstance(form_field, expected)

    def test_post_index_page_show_correct_context(self):
        """Пост отображается на главной странице."""
        response = self.authorized_client.get(reverse('index'))
        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым
        first_object = response.context['page'][0]
        task_text_0 = first_object.text
        self.assertEqual(task_text_0, 'Тестовый пост')

    def test_test_group_pages_show_correct_context(self):
        """Шаблон test-group сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('group', kwargs={'slug': 'test-group'})
        )
        self.assertEqual(
            response.context['group'].title, 'Название сообщества'
        )
        self.assertEqual(response.context['group'].slug, 'test-group')
        self.assertEqual(response.context['group'].description, 'Описание')

    def test_image_view_index(self):
        """Проверем, что изображение отображается на главной странице"""
        # Проверка, что при выводе поста с картинкой изображение передаётся
        response = self.authorized_client.get(reverse('index'))
        self.assertTrue(response.context['page'][0].image)

    def test_image_view_profile(self):
        """Проверем, что изображение отображается на странице профайла"""
        response = self.authorized_client.get(
            reverse('profile', kwargs={'username': self.user}))
        self.assertTrue(response.context['page'][0].image)

    def test_image_view_group(self):
        """Проверем, что изображение отображается на странице поста"""
        response = self.authorized_client.get(
            reverse('group', kwargs={'slug': self.group.slug}))
        self.assertTrue(response.context['page'][0].image)

    def test_image_view_post_view(self):
        response = self.authorized_client.get(
            reverse('post', kwargs={'username': self.user,
                                    'post_id': self.post.id}))
        self.assertTrue(response.context['post'].image)

    def test_image_view_post_form(self):
        """Создаем еще один пост с картинкой, проверяем,
        что при отправке поста с картинкой через форму
        PostForm создаётся запись в базе данных. """
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )

        uploaded = SimpleUploadedFile(
            name='very_small2.gif',
            content=small_gif,
            content_type='image/gif'
        )

        self.post = Post.objects.create(
            text='Тестовый пост',
            author=self.user,
            group=self.group,
            image=uploaded,
        )
        response = self.authorized_client.get(
            reverse('profile', kwargs={'username': self.user}))
        self.assertTrue(response.context['page'][1].image)
