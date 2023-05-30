# Generated by Django 4.1.7 on 2023-05-29 16:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("administration", "0005_city_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="place",
            name="url",
            field=models.URLField(
                blank=True,
                max_length=400,
                null=True,
                verbose_name="ссылка на сайт заведения",
            ),
        ),
    ]
