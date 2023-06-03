from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import CheckConstraint, Q

User = get_user_model()


class City(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True,
    )
    latitude = models.FloatField('широта', blank=True, null=True)
    longitude = models.FloatField('долгота', blank=True, null=True)

    class Meta:
        verbose_name = 'город'
        verbose_name_plural = 'города'

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True,
    )

    class Meta:
        verbose_name = 'тип заведения'
        verbose_name_plural = 'типы заведений'

    def __str__(self):
        return self.name


class Place(models.Model):

    name = models.CharField(
        verbose_name='имя',
        max_length=60,
    )
    city = models.ForeignKey(
        City,
        verbose_name='город',
        related_name='places',
        on_delete=models.CASCADE,
    )
    category = models.ManyToManyField(
        Category,
        verbose_name='вид заведения',
        max_length=30,
        through='CategoryPlace',
    )
    address = models.TextField(
        verbose_name='Адрес',
        blank=True,
        null=True,
    )
    phone = models.TextField(
        verbose_name='телефонный номер',
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
        max_length=400,
        verbose_name='ссылка на сайт заведения',
        null=True,
        blank=True,
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
                    'address',
                    'city',
                ],
                name='%(app_label)s_%(class)s_unique_relationships',
            ),
        ]

    def __str__(self):
        return self.name

    def clean(self) -> None:
        if len(self.url) > 198:
            self.url = ''
        super().clean()


class Review(models.Model):
    place = models.ForeignKey(
        Place,
        on_delete=models.CASCADE,
        related_name='reviews',
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
        return self.text

    class Meta:
        verbose_name = 'отзыв'
        verbose_name_plural = 'отзывы'


class CategoryPlace(models.Model):
    place = models.ForeignKey(
        Place,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
    )
