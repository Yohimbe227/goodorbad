# Generated by Django 3.2.16 on 2023-01-16 12:17

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('bot_admin', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='place',
            options={'verbose_name': 'заведение', 'verbose_name_plural': 'заведения'},
        ),
        migrations.AddField(
            model_name='place',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='Дата публикации'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='place',
            name='sponsored',
            field=models.BooleanField(default=False, verbose_name='проплачено'),
            preserve_default=False,
        ),
    ]
