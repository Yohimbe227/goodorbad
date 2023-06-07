from django import forms
from django.contrib.auth.forms import UserCreationForm

from administration.models import Place


class PlaceForm(forms.ModelForm):

    # place_type = forms.MultipleChoiceField(
    #     required=False,
    #     widget=forms.CheckboxSelectMultiple,
    # )

    class Meta:
        model = Place

        fields = (
            'name',
            'city',
            'category',
            'description',
            'url',
            'latitude',
            'longitude',
            'sponsored',
        )
        widgets = {
            'city': forms.TextInput,
        }


class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = UserCreationForm.Meta.model
        fields = '__all__'
        field_classes = UserCreationForm.Meta.field_classes
