from django.db import models
from django.db.models import Count
from django.views.generic import ListView


class Club(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Player(models.Model):
    name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    club = models.ForeignKey(Club, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Match(models.Model):
    date = models.DateField()
    players = models.ManyToManyField(Player, through='MatchPlayer')
    winner = models.ForeignKey(Player, on_delete=models.SET_NULL, related_name='won_matches', null=True)

    def __str__(self):
        return f"Match on {self.date}"


class MatchPlayer(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    team_number = models.IntegerField()  # 1 or 2 for singles, 1, 2, 3, or 4 for doubles

    class Meta:
        unique_together = ('player', 'match')

    def __str__(self):
        return f"{self.player} in {self.match}"


class PlayerRating(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    trueskill_mu = models.FloatField()
    trueskill_sigma = models.FloatField()
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Rating for {self.player} from {self.start_date} to {self.end_date}"
