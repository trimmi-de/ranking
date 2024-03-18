from django import forms
from .models import Team, Player

class CreateMatchForm(forms.Form):
    # date = forms.DateTimeField()
    singles = forms.BooleanField(required=False, initial=False)  # Optional field to indicate singles match
    team1 = forms.ModelChoiceField(queryset=Team.objects.all(), label='Team 1')
    team2 = forms.ModelChoiceField(queryset=Team.objects.all(), label='Team 2')
    winner = forms.ModelChoiceField(queryset=Team.objects.all(), required=False, label='Winner')

    def clean(self):
        cleaned_data = super().clean()
        team1 = cleaned_data.get('team1')
        team2 = cleaned_data.get('team2')

        # Ensure team1 and team2 are distinct
        if team1 == team2:
            raise forms.ValidationError("Team 1 and Team 2 must be different.")
