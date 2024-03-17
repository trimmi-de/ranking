from django import forms

from .models import Player


class CreateMatchForm(forms.Form):
    players = forms.ModelMultipleChoiceField(queryset=Player.objects.all(), widget=forms.CheckboxSelectMultiple)
    winner = forms.ModelChoiceField(queryset=Player.objects.all())
