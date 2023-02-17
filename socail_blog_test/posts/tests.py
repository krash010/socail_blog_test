from functools import cache
from django.test import Client
from django.test import TestCase
from django.contrib.auth.models import User
from django.test import override_settings
import shutil
from django.core.cache import cache

from .models import Post, Group


class TestProfileCreate(TestCase):    #После регистрации пользователя создается его персональная страница (profile)
    def setUp(self) -> None:
        self.client = Client()
        user = User.objects.create(username='test_profile')
        user.set_password('Love1029')
        user.save()


    def test_create(self):
        responce = self.client.get('/test_profile/')
        self.assertEqual(responce.status_code, 200)


    def tearDown(self) -> None:
        User.objects.filter(username='test_profile').delete()


class TestProfileAuthNew(TestCase):    #Авторизованный пользователь может опубликовать пост (new)
    def setUp(self) -> None:
        self.client = Client()
        user = User.objects.create(username='testprofile')
        user.set_password('Love1029')
        user.save()
        self.client.login(username='testprofile', password='Love1029')
        group = Group.objects.create(title='test', slug='test_group', description='empty')
        self.group_id=f'{group.id}'


    def test_newpost(self):
        self.client.post('/new', data={'text': 'test text', 'group': self.group_id})
        self.assertTrue(Post.objects.filter(text='test text', group=self.group_id).exists())


    def tearDown(self) -> None:
        User.objects.filter(username='test_profile').delete()
        Group.objects.filter(title='test', slug='test_group', description='empty').delete()


class TestProfileNoneAuthNew(TestCase):    #Неавторизованный посетитель не может опубликовать пост (его редиректит на страницу входа)
    def setUp(self) -> None:
        self.client = Client()


    def test_newpost_noneauth(self):
        response = self.client.get('/new')
        self.assertRedirects(response, '/auth/login/?next=/new', status_code=302, target_status_code=200)


    def tearDown(self) -> None:
        pass

class TestPostView(TestCase):    #После публикации поста новая запись появляется на главной странице сайта (index), на персональной странице пользователя (profile), и на отдельной странице поста (post)
    def setUp(self) -> None:
        self.client = Client()
        user = User.objects.create(username='testprofile')
        user.set_password('Love1029')
        user.save()
        self.client.login(username='testprofile', password='Love1029')
        group = Group.objects.create(title='test', slug='test_group', description='empty')
        self.group_id=f'{group.id}'
        self.client.post('/new', data={'text': 'test text', 'group': self.group_id})


    def test_postview_index(self):
        cache.clear()
        response = self.client.get('')
        self.assertContains(response, 'test text')


    def test_postview_profile(self):
        response = self.client.get('/testprofile/')
        self.assertContains(response, 'test text')


    def test_postview_post(self):
        post = Post.objects.filter(text='test text').get()
        response = self.client.get(f'/testprofile/{post.id}/')
        self.assertContains(response, 'test text')


    def tearDown(self) -> None:
        User.objects.filter(username='testprofile').delete()
        Group.objects.filter(title='test', slug='test_group', description='empty').delete()


class TestEditPost(TestCase):    #Авторизованный пользователь может отредактировать свой пост и его содержимое изменится на всех связанных страницах
    def setUp(self) -> None:
        self.client = Client()
        user = User.objects.create(username='testprofile')
        user.set_password('Love1029')
        user.save()
        self.client.login(username='testprofile', password='Love1029')
        group = Group.objects.create(title='test', slug='test_group', description='empty')
        self.group_id=f'{group.id}'
        self.client.post('/new', data={'text': 'test text', 'group': self.group_id})
        self.post = Post.objects.filter(text='test text').get()


    def test_edit_post(self):
        self.client.post(f'/testprofile/{self.post.id}/edit/', data={'text': 'test text test', 'group': self.group_id})
        self.post_edit = Post.objects.filter(text='test text test').get()
        self.assertIs(self.post.id, self.post_edit.id)


    def test_edit_post_index(self):
        self.client.post(f'/testprofile/{self.post.id}/edit/', data={'text': 'test text test', 'group': self.group_id})
        cache.clear()
        response = self.client.get('')
        self.assertContains(response, 'test text test')


    def test_edit_post_profile(self):
        self.client.post(f'/testprofile/{self.post.id}/edit/', data={'text': 'test text test', 'group': self.group_id})
        response = self.client.get('/testprofile/')
        self.assertContains(response, 'test text test')


    def test_edit_post_profile_post(self):
        self.client.post(f'/testprofile/{self.post.id}/edit/', data={'text': 'test text test', 'group': self.group_id})
        response = self.client.get(f'/testprofile/{self.post.id}/')
        self.assertContains(response, 'test text test')


    def tearDown(self) -> None:
        User.objects.filter(username='testprofile').delete()
        Group.objects.filter(title='test', slug='test_group', description='empty').delete()


class TestPageNotFound(TestCase):
    def setUp(self) -> None:
        self.client = Client()


    def test_page_not_found(self):
        response = self.client.get('/nopage/')
        self.assertEqual(response.status_code, 404)


    def tearDown(self) -> None:
        pass

TEST_DIR = 'test_data'    # Проверка страниц на наличие изображения и защиты от загрузки "неправильных" файлов. С использованием тестовой директории
class TestCreateImg(TestCase):
    @override_settings (MEDIA_ROOT = ( TEST_DIR + '/media'))
    def setUp(self) -> None:
        self.client = Client()
        user = User.objects.create(username='testprofile')
        user.set_password('Love1029')
        user.save()
        self.client.login(username='testprofile', password='Love1029')
        self.group = Group.objects.create(title='test', slug='test_group', description='empty')
        self.group_id=f'{self.group.id}'
        with open('media/posts/cat.jpg', 'rb') as img:
            self.post_new = self.client.post('/new', data={'author': user, 'text': 'test text image', 'group': self.group_id, 'image': img}, follow=True)


    def test_create_img(self):
        self.assertEqual(self.post_new.status_code, 200)


    def test_post_profile_img(self):
        response = self.client.get('/testprofile/')
        self.assertContains(response, 'img')


    def test_post_index(self):
        cache.clear()
        response = self.client.get('')
        self.assertContains(response, 'img')


    def test_post_group(self):
        response = self.client.get(f'/group/{self.group.slug}/')
        self.assertContains(response, 'img')


    def test_create_no_img(self):
        with open('media/posts/no_img.txt', 'rb') as img:
            self.post_new = self.client.post('/new', data={'text': 'test text no image', 'group': self.group_id, 'image': img}, follow=True)
        self.assertFalse(Post.objects.filter(text='test text no img').exists())


    def tearDown(self) -> None:
        User.objects.filter(username='testprofile').delete()
        Group.objects.filter(title='test', slug='test_group', description='empty').delete()
        try:
            shutil.rmtree(TEST_DIR)
        except OSError:
            pass



class TestCashIndex(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        user = User.objects.create(username='testprofile')
        user.set_password('Love1029')
        user.save()
        self.client.login(username='testprofile', password='Love1029')
        group = Group.objects.create(title='test', slug='test_group', description='empty')
        self.group_id=f'{group.id}'
        

    def test_cash(self):
        response = self.client.get('')
        self.assertNotContains(response, 'testmy')


    def test_cash_notclear(self):
        response = self.client.post('/new', data={'text': 'testnotclear', 'group': self.group_id}, follow=True)
        self.assertEqual(response.status_code, 200)
        responses = self.client.get('')
        self.assertNotContains(responses, 'testnotclear')


    def test_cash_clear(self):
        response = self.client.post('/new', data={'text': 'testclear', 'group': self.group_id}, follow=True)
        self.assertEqual(response.status_code, 200)
        cache.clear()
        responses = self.client.get('')
        self.assertContains(responses, 'testclear')



    def tearDown(self) -> None:
        User.objects.filter(username='testprofile').delete()
        Group.objects.filter(title='test', slug='test_group', description='empty').delete()