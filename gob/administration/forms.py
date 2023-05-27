from django import forms

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
