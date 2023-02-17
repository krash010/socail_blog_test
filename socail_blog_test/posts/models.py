from django.db import models

# Create your models here.
from django.contrib.auth import get_user_model

# Определяем модель User
User = get_user_model()

#  Добавим модель групп
class Group(models.Model):
    title = models.TextField()
    slug = models.SlugField()
    description = models.TextField()

    def __str__(self):
        return self.title


# Добавим модель постов
class Post(models.Model):
    text = models.TextField()
    pub_date = models.DateTimeField("date published", auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, blank=True, null=True, related_name="group")
    image = models.ImageField(upload_to='posts/', blank=True, null=True)

# Добавим модель комментарирев
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.SET_NULL, blank=True, null=True, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    created = models.DateTimeField('date published', auto_now_add=True)

# Добавим модель подписчиков
class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='follower')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='following')
