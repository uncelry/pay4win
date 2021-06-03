# Generated by Django 3.2.2 on 2021-05-08 15:03

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('lottery', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='steamuser',
            name='time_registered',
            field=models.DateField(default=django.utils.timezone.now, verbose_name='Дата регистрации на Pay4Win'),
        ),
        migrations.AlterField(
            model_name='steamuser',
            name='profile_url',
            field=models.CharField(max_length=200, verbose_name='Ссылка на профиль steam'),
        ),
    ]
