import trueskill
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver


class Club(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Player(models.Model):
    name = models.CharField(max_length=100)
    club = models.ForeignKey('Club', on_delete=models.SET_NULL, null=True)
    trueskill_mu = models.FloatField(default=trueskill.Rating().mu)
    trueskill_sigma = models.FloatField(default=trueskill.Rating().sigma)

    def __str__(self):
        return self.name


class Team(models.Model):
    players = models.ManyToManyField('Player')

    def clean(self):
        """
        Validate that the team has exactly one or two players and no player is repeated.
        """
        num_players = self.players.count()
        if num_players not in [1, 2]:
            raise ValidationError("A team must have exactly one or two players.")


class Match(models.Model):
    date = models.DateTimeField(auto_now=True)
    singles = models.BooleanField(default=False)  # Indicates whether the match is a singles or doubles match
    teams = models.ManyToManyField('Team', related_name='matches', blank=True)
    winner = models.ForeignKey('Team', on_delete=models.SET_NULL, related_name='won_matches', null=True)

    def __str__(self):
        return f"Match on {self.date}"

    def clean(self):
        """
        Validate that the match has exactly two teams and no player is part of both teams.
        Validate that the match does not have the same player in two different teams
        """
        num_teams = self.teams.count()
        if num_teams != 2:
            raise ValidationError("A match must have exactly two teams.")

        # Get all players across both teams
        all_players = []
        for team in self.teams.all():
            all_players.extend(team.players.all())

        # Check if any player is part of both teams
        player_count = {}
        for player in all_players:
            player_count[player] = player_count.get(player, 0) + 1
            if player_count[player] > 1:
                raise ValidationError(f"Player '{player.name}' cannot be part of both teams.")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Calculate TrueSkill ratings if all conditions are met
        if self.teams.count() == 2 and self.winner_id:
            players = []
            for team in self.teams.all():
                for player in team.players.all():
                    players.append(player)
            team_ratings = []
            if len(players) == 2:  # Singles match
                team_ratings = (
                    ({players[0]: trueskill.Rating(mu=players[0].trueskill_mu, sigma=players[0].trueskill_sigma)}),
                    ({players[1]: trueskill.Rating(mu=players[1].trueskill_mu, sigma=players[1].trueskill_sigma)})
                )
            elif len(players) == 4:  # Doubles match
                for i in range(0, len(players), 2):  # Group players into pairs for doubles match
                    team_ratings.append(
                        ({players[i]: trueskill.Rating(mu=players[i].trueskill_mu, sigma=players[i].trueskill_sigma),
                          players[i + 1]: trueskill.Rating(mu=players[i + 1].trueskill_mu,
                                                           sigma=players[i + 1].trueskill_sigma)}))

            ranks = [0 if team == self.winner else 1 for team in self.teams.all()]
            new_ratings = trueskill.rate(team_ratings, ranks=ranks)

            for team_rating in new_ratings:
                # Iterate over each player and their rating in the team's ratings dictionary
                for player, rating in team_rating.items():
                    # Update the player's mu and sigma attributes
                    player.trueskill_mu = rating.mu
                    player.trueskill_sigma = rating.sigma
                    player.save()

                    player_rating = PlayerRating.objects.create(
                        player=player,
                        trueskill_mu=rating.mu,
                        trueskill_sigma=rating.sigma,
                    )


class PlayerRating(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    trueskill_mu = models.FloatField(default=trueskill.Rating().mu)
    trueskill_sigma = models.FloatField(default=trueskill.Rating().sigma)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Rating for {self.player} at {self.last_updated}"
