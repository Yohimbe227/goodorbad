from django.contrib import admin
from django.db.models import Count

from .forms import PlaceForm
from .models import Place, Category, CategoryPlace, Review


class BaseAdmin(admin.ModelAdmin):
    empty_value_display = '-пусто-'


# @admin.register(Place)
# class PlaceAdmin(BaseAdmin):
#     list_display = (
#         'pk',
#         'name',
#         'city',
#         # 'created',
#         # 'sponsored',
#         'address_name',
#         # 'place_type'
#     )
#     list_editable = (
#         'name',
#         # 'sponsored',
#     )
# form = PlaceForm


class CategoryPlaceInline(admin.TabularInline):
    model = CategoryPlace
    extra = 1


@admin.register(Place)
class PlaceAdmin(BaseAdmin):
    inlines = (CategoryPlaceInline,)
    list_display = (
        'pk',
        'name',
        'show_count',
        # 'created',
        # 'sponsored',
        'city',
        'address',
        # 'place_type',
        'sponsored',
    )
    list_editable = (
        'name',
        'sponsored',
    )
    list_filter = ('city',)
    search_fields = ('name__istartswith',)

    def show_count(self, obj):

        result = Place.objects.filter(name=obj).aggregate(Count('reviews'))
        return result['reviews__count']

    show_count.short_description = 'количество отзывов'
    form = PlaceForm


@admin.register(Category)
class PlaceTypeAdmin(BaseAdmin):
    inlines = (CategoryPlaceInline,)


@admin.register(Review)
class ReviewAdmin(BaseAdmin):

    list_display = (
        'pk',
        'text',
        'author',
        'date',
    )
