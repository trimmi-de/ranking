import trueskill
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.edit import FormView

from .forms import CreateMatchForm
from .models import PlayerRating


class PlayerRatingListView(ListView):
    model = PlayerRating
    template_name = 'player_rating_list.html'
    context_object_name = 'player_ratings'

    def get_queryset(self):
        return PlayerRating.objects.all()


class CreateMatchView(FormView):
    template_name = 'create_match.html'
    form_class = CreateMatchForm
    success_url = reverse_lazy('rankings:player_ratings')

    def form_valid(self, form):
        # Assuming form data is submitted with player IDs and a winner
        home_team_players = list(form.cleaned_data.get('home_team_players'))
        guest_team_players = list(form.cleaned_data.get('guest_team_players'))
        print(home_team_players)
        players = []
        players.extend(home_team_players)
        players.extend(guest_team_players)
        winner = form.cleaned_data.get('winner')
        # Create the match
        match = Match.objects.create()

        # Add players to the match
        for i, player in enumerate(players):
            # match_player = MatchPlayer.objects.create(player=player, match=match, team_number=i + 1)
            pass

        # Set the winner of the match
        if winner == 'home':
            match.winner = home_team_players
        else:
            match.winner = guest_team_players
        match.save()

        # Calculate and update Trueskill ratings
        self.calculate_trueskill_ratings(match)

        return super().form_valid(form)

    def calculate_trueskill_ratings(self, match):
        # Retrieve all players involved in the match
        players = match.players.all()
        team_ratings = []

        # Get Trueskill ratings for each player
        for player in players:
            rating = trueskill.Rating(mu=player.trueskill_mu, sigma=player.trueskill_sigma)
            team_ratings.append(rating)

        # Create artificial teams for all players
        num_players = len(players)
        team1_ratings = team_ratings[:num_players // 2]
        team2_ratings = team_ratings[num_players // 2:]

        # Assign ranks based on the winner of the match
        ranks = [1] * (num_players // 2) + [0] * (
                    num_players - num_players // 2)  # Assuming first half are winners, second half are losers

        # Ensure multiple rating groups
        rating_groups = [team1_ratings, team2_ratings]
        print("===================================")
        print("rating_groups", rating_groups)
        print("team1_ratings", team1_ratings)
        print("ranks", ranks)

        # Calculate the new ratings based on the match outcome
        new_ratings = trueskill.rate(rating_groups, ranks=ranks)

        # Flatten the new ratings
        new_ratings_flat = [rating for team in new_ratings for rating in team]

        # Update the ratings in the database
        for i, player in enumerate(players):
            # Get or create PlayerRating object for the player
            player_rating = PlayerRating.objects.create(
                player=player,
            )
            # Update the ratings with new Trueskill ratings (history view)
            player_rating.trueskill_mu = new_ratings_flat[i].mu
            player_rating.trueskill_sigma = new_ratings_flat[i].sigma
            player_rating.save()
            # Update player
            print(i, player)
            player.trueskill_mu = new_ratings_flat[i].mu
            player.trueskill_sigma = new_ratings_flat[i].sigma
            player.save()
