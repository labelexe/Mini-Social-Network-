from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField(unique=True)
    status = models.BooleanField(default=False)


class Profil(models.Model):
    profil = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    text = models.TextField()
    image = models.ImageField(upload_to='users')

    def __str__(self):
        return self.name


class Comment(models.Model):
    profil = models.ForeignKey(Profil, on_delete=models.CASCADE)
    author = models.CharField(max_length=30, verbose_name='Автор')
    content = models.TextField(verbose_name='Коментарий')
    created_date = models.DateTimeField(auto_now_add=True, db_index=True,
                                      verbose_name='Опубликован')

    class Meta:
        verbose_name_plural = 'Комментарии'
        verbose_name = 'Комментарий'
        ordering = ['created_date']


