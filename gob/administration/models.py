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


class PlaceType(models.Model):
    name = models.CharField(
        verbose_name='тип заведения',
        max_length=30,
    )

    def __str__(self):
        return self.name


class Place(models.Model):

    name = models.CharField(
        verbose_name='имя',
        max_length=30,
    )
    city = models.CharField(
        verbose_name='город',
        max_length=20,
    )
    place_type = models.ManyToManyField(
        PlaceType,
        verbose_name='вид заведения',
        max_length=15,
        through='PlaceTypePlace',
    )
    address_name = models.TextField(
        verbose_name='описание',
        blank=True,
        null=True,
    )
    description = models.TextField(
        verbose_name='описание',
        blank=True,
        null=True,
    )
    worktime_from = models.TimeField(
        'Время работы, с',
        db_index=True,
        blank=True,
        null=True,
        default=None,
    )
    worktime_to = models.TimeField(
        'Время работы, до',
        db_index=True,
        blank=True,
        null=True,
        default=None,
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
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'city', ],
                name='%(app_label)s_%(class)s_unique_relationships',
            ),
        ]

    def __str__(self):
        return self.name


class PlaceTypePlace(models.Model):
    place = models.ForeignKey(
        Place,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    place_type = models.ForeignKey(
        PlaceType,
        on_delete=models.CASCADE,
    )
    verbose_name = 'тип заведения'
