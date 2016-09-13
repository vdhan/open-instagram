from django.db import models


class User(models.Model):
    email = models.EmailField()
    password = models.CharField(max_length=255)
    verified = models.BooleanField(default=0)
    access_token = models.CharField(max_length=255)

    class Meta:
        db_table = 'user'


class Image(models.Model):
    email = models.EmailField()
    image = models.ImageField(upload_to='img/%Y/%m/%d')
    title = models.CharField(max_length=255)
    count = models.IntegerField(default=0)

    class Meta:
        db_table = 'image'


class Comment(models.Model):
    img_id = models.IntegerField()
    email = models.EmailField()
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'comment'


class WaitVerify(models.Model):
    email = models.EmailField()
    code = models.CharField(max_length=255)

    class Meta:
        db_table = 'wait_verify'
