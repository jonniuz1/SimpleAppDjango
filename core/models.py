from django.contrib.auth import get_user_model
from django.db import models
import uuid
import datetime

User = get_user_model()


class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    id_user = models.IntegerField()
    bio = models.TextField(blank=True)
    profile_img = models.ImageField(upload_to='image/profile', default='blank-profile.png')
    location = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.user


class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='image/post')
    caption = models.TextField()
    created_at = models.DateTimeField(auto_now_add=datetime.datetime.now())
    no_of_likes = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.user.username}\'s post'


class LikePost(models.Model):
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user.username}\'s like'


class Follower(models.Model):
    follower = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username
