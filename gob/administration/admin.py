from django.contrib import admin

from .forms import PlaceForm
from .models import Place


class BaseAdmin(admin.ModelAdmin):
    empty_value_display = '-пусто-'


@admin.register(Place)
class PlaceAdmin(BaseAdmin):
    list_display = (
    'pk', 'name', 'city', 'place_type', 'review', 'url', 'created',
    'sponsored',
    )
    list_editable = ('name', 'sponsored',)
    form = PlaceForm
