from administration.models import Place
from django import forms

from gob.settings import CHOICES


class PlaceForm(forms.ModelForm):

    place_type = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        choices=CHOICES,
    )

    class Meta:
        model = Place

        fields = (
            'name',
            'city',
            'place_type',
            'url',
            'latitude',
            'longitude',
            'sponsored',
        )
        widgets = {
            'name': forms.TextInput,
            'city': forms.TextInput,
        }
