from django.test import TestCase

from posts.models import Group


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        Group.objects.create(
            title='Название сообщества',
            slug='test-group',
            description='Описание'
        )
        cls.group = Group.objects.get(slug='test-group')

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        group = GroupModelTest.group
        field_verboses = {
            'title': 'Название группы',
            'slug': 'Уникальное имя',
            'description': 'Описание'
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).verbose_name, expected)

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        group = GroupModelTest.group
        field_help_texts = {
            'title': 'Дайте короткое название группе',
            'slug': 'Укажите адрес для страницы задачи.',
            'description': 'Дайте описание группе'
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).help_text, expected)

    def test_name_is_title(self):
        group = GroupModelTest.group
        title_name = group.title
        self.assertEqual(title_name, str(group))
