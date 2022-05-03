# Generated by Django 4.0.3 on 2022-05-03 08:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('author', models.CharField(max_length=30, verbose_name='Автор')),
                ('content', models.TextField(verbose_name='Содержание')),
                ('created_date', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Опубликован')),
                ('profil', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='blog.profil')),
            ],
            options={
                'verbose_name': 'Комментарий',
                'verbose_name_plural': 'Комментарии',
                'ordering': ['created_date'],
            },
        ),
    ]