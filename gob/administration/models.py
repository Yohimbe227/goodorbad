from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class PlaceType(models.Model):
    name = models.CharField(
        max_length=30,
        unique=True,
    )

    class Meta:
        verbose_name = ('тип заведения',)

    def __str__(self):
        return self.name


class Place(models.Model):

    name = models.CharField(
        verbose_name='имя',
        max_length=60,
    )
    city = models.CharField(
        verbose_name='город',
        max_length=30,
    )
    place_type = models.ManyToManyField(
        PlaceType,
        verbose_name='вид заведения',
        max_length=30,
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
    sponsored = models.BooleanField(default=False, verbose_name='проплачено')
    latitude = models.FloatField('широта', blank=True, null=True)
    longitude = models.FloatField('долгота', blank=True, null=True)

    class Meta:
        verbose_name = 'заведение'
        verbose_name_plural = 'заведения'
        default_related_name = 'places'
        constraints = [
            models.UniqueConstraint(
                fields=[
                    'name',
                    'address_name',
                    'city',
                ],
                name='%(app_label)s_%(class)s_unique_relationships',
            ),
        ]

    def __str__(self):
        return self.name


class Review(models.Model):
    place = models.ForeignKey(
        Place, on_delete=models.CASCADE, related_name='reviews'
    )
    text = models.TextField(
        verbose_name='отзывы',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="автор",
        null=True,
    )
    date = models.DateTimeField(
        'Дата добавления',
        auto_now_add=True,
        db_index=True,
        blank=True,
    )

    def __str__(self):
        return self.text.__str__()


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
