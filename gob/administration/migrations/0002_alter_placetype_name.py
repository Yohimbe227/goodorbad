# Generated by Django 4.1.7 on 2023-04-27 17:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("administration", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="placetype",
            name="name",
            field=models.CharField(max_length=50, unique=True),
        ),
    ]
