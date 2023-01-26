from django import forms

from bot_admin.models import Place


class PlaceForm(forms.ModelForm):

    class Meta:
        model: Place
        fields = (
            'name',
            'city',
            'place_type',
            'url',
            'created',
            'sponsored',
        )
        widgets = {
            'name': forms.TextInput,
            'created': forms.DateTimeInput,
            'city': forms.TextInput,
        }
