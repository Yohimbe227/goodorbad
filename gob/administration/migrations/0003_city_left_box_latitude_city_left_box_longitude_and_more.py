# Generated by Django 4.1.7 on 2023-06-19 11:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("administration", "0002_alter_review_author"),
    ]

    operations = [
        migrations.AddField(
            model_name="city",
            name="left_box_latitude",
            field=models.FloatField(
                blank=True, null=True, verbose_name="широта"
            ),
        ),
        migrations.AddField(
            model_name="city",
            name="left_box_longitude",
            field=models.FloatField(
                blank=True, null=True, verbose_name="долгота"
            ),
        ),
        migrations.AddField(
            model_name="city",
            name="right_box_latitude",
            field=models.FloatField(
                blank=True, null=True, verbose_name="широта"
            ),
        ),
        migrations.AddField(
            model_name="city",
            name="right_box_longitude",
            field=models.FloatField(
                blank=True, null=True, verbose_name="долгота"
            ),
        ),
    ]
