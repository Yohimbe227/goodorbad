from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db.models import Count

from .forms import CustomUserCreationForm, PlaceForm
from .models import Category, CategoryPlace, City, Place, Review

User = get_user_model()
admin.site.unregister(User)


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
        'created',
        'city',
        'address',
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


@admin.register(User)
class UserAdmin(BaseUserAdmin):

    list_display = (
        'pk',
        'username',
        'first_name',
        'last_name',
        'show_count',
    )

    def show_count(self, obj):
        result = Place.objects.filter(reviews__author=obj).aggregate(
            Count('reviews')
        )
        return result['reviews__count']


@admin.register(City)
class CityAdmin(BaseAdmin):

    list_display = (
        'pk',
        'name',
        'latitude',
        'longitude',
        'show_count_places',
        'show_count_reviews',
    )

    def show_count_places(self, obj):
        result = Place.objects.filter(city=obj).aggregate(Count('city'))
        return result['city__count']

    def show_count_reviews(self, obj):
        result = Review.objects.filter(place__city=obj).aggregate(
            Count('place__city')
        )
        return result['place__city__count']

    show_count_places.short_description = 'количество заведений'
    show_count_reviews.short_description = 'количество отзывов'
