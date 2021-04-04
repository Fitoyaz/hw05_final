
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Comment, Follow, Group, Post
User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='Djalyarim')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.user_unfollow = User.objects.create_user(username='Unfollow')
        cls.authorized_client_unfollow = Client()
        cls.authorized_client_unfollow.force_login(cls.user_unfollow)
        cls.group = Group.objects.create(
            title='future', description='про фьюче', slug='test_slug'
        )
        cls.post = Post.objects.create(
            text='Поле для текста',
            author=cls.user,
            group=cls.group,
        )
        cls.follow = Follow.objects.create(user=cls.user,
                                           author=cls.user)

    def test_check_authorized_user_can_follow(self):
        """ Авторизованный пользователь может подписаться на автора """
        count_before_auth = Follow.objects.count()
        self.authorized_client_unfollow.get(
            reverse('profile_follow', kwargs={'username': self.user.username}))
        count_after_auth = Follow.objects.all().count()
        self.assertEqual(count_after_auth, count_before_auth + 1)

    def test_check_authorized_user_can_unfollow(self):
        """ Авторизованный пользователь может отписаться от автора """
        Follow.objects.create(user=self.user_unfollow, author=self.user)
        count_before_auth = Follow.objects.count()
        self.authorized_client_unfollow.get(
            reverse('profile_unfollow',
                    kwargs={'username': self.user.username}))
        count_after_auth = Follow.objects.all().count()
        self.assertEqual(count_after_auth, count_before_auth - 1)

    def test_check_new_post_appears_in_follow_index(self):
        """ Пост появляется в ленте подписчика при подписке """
        Follow.objects.create(user=self.user_unfollow, author=self.user)
        response = PostPagesTests.authorized_client_unfollow.get(
            reverse('follow_index'))
        check_post = response.context['page'][0].text
        self.assertEqual(check_post, self.post.text)

    def test_check_new_post_dont_appears_in_follow_index(self):
        """ Пост не появляется в ленте того, кто не подписался """
        response = PostPagesTests.authorized_client_unfollow.get(
            reverse('follow_index'))
        check_post = response.context['page'].object_list
        self.assertFalse(check_post)

    # Блок комментариев
    def test_check_authorized_user_can_commens_post(self):
        """ Авторизованный клиент может оставлять комментарии """
        Comment.objects.create(text='Тестовый камментарий',
                               author=self.user, post=self.post)
        response = PostPagesTests.authorized_client.get(
            reverse(
                'post', kwargs={'username': self.user.username,
                                'post_id': self.post.id}
            )
        )
        comment = response.context['comments'][0].author
        self.assertEqual(comment, self.user)
