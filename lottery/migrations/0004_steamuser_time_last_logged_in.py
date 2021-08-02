# Generated by Django 3.2.2 on 2021-05-08 15:17

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('lottery', '0003_alter_steamuser_time_registered'),
    ]

    operations = [
        migrations.AddField(
            model_name='steamuser',
            name='time_last_logged_in',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Последняя дата и время входа на Pay4Win'),
        ),
    ]