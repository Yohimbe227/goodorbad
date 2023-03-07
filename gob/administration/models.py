from django.db import models

from gob.settings import CHOICES


class Review(models.Model):
    text = models.TextField(
        verbose_name='отзывы',
    )
    date = models.DateTimeField(
        'Дата добавления',
        auto_now_add=True,
        db_index=True,
        blank=True,
    )


class Place(models.Model):

    name = models.CharField(
        verbose_name='имя',
        max_length=30,
    )
    city = models.CharField(
        verbose_name='город',
        max_length=20,
    )
    place_type = models.CharField(
        verbose_name='Вид заведения',
        choices=CHOICES,
        max_length=15,
    )
    description = models.TextField(
        verbose_name='описание',
        blank=True,
    )
    url = models.URLField(
        verbose_name='ссылка на сайт заведения',
        null=True,
    )
    created = models.DateTimeField(
        'Дата добавления',
        auto_now_add=True,
        db_index=True,
        blank=True,
    )
    sponsored = models.BooleanField(
        default=False,
        verbose_name='проплачено'
    )
    latitude = models.FloatField('широта', blank=True, null=True)
    longitude = models.FloatField('долгота', blank=True, null=True)
    review = models.ForeignKey(
        Review,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='отзывы',
        help_text='отзывы пользователей',
    )

    class Meta:
        verbose_name = 'заведение'
        verbose_name_plural = 'заведения'
