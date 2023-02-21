from django.db import models
from django.utils import timezone


class Place(models.Model):
    CHOICES = (('cf', 'Кафе'), ('br', 'Бар'), ('rs', 'Ресторан'),
               ('ff', 'Фастфуд'), ('pz', 'Пиццерия'),)
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
    review = models.TextField(
        verbose_name='отзыв',
    )
    url = models.URLField(
        verbose_name='ссылка на сайт заведения',
    )
    created = models.DateTimeField(
        'Дата добавления',
        default=timezone.now(),
        db_index=True,
    )
    sponsored = models.BooleanField(
        default=False,
        verbose_name='проплачено'
    )
    readonly_fields = [created, ]

    class Meta:
        verbose_name = 'заведение'
        verbose_name_plural = 'заведения'


